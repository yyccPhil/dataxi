# File: data_injector.py

# Description: This Package aims to provide some reusable functions for data transfer between different databases.

# Creator: Yuan Yuan (yyuan7@tesla.com)

# Version:

# 2024.02.22:
#     1. finished the transfer from MySQL to ClickHouse
#     2. added the record count check before and after the transfer
# 2024.02.26:
#     1. added docstring to the functions
# 2024.03.25:
#     1. updated the logger info for connection and query history
# 2024.03.29:
#     1. added the MSSQLConnector class to connect to the MS SQL server
#     2. added get_connection() func for each Connector class to return connection object
#     3. added insert_data() func for MySQLConnector class to insert data into MySQL
# 2024.04.01:
#     1. added the SplunkConnector class to connect to the Splunk server
# 2024.04.08:
#     1. changed the original insert_data() func to insert_tuple_data()
#     2. added insert_dict_data() func
# 2024.04.17:
#     1. return the flag_connected in the get_connection() func of each Connector class
# 2024.04.19:
#     1. added the close() func for ClickHouseConnector class
#     2. added the query_df() func for ClickHouseConnector class
# 2024.04.24:
#     1. added the commit() func for MySQLConnector class
# 2024.05.15:
#     1. added the insert df mode for insert() in ClickHouseConnector class


import time
import pymysql.cursors
# becasue of the port default setting, use clickhouse_connect instead of clickhouse_driver
from clickhouse_connect import get_client
import pymssql
import requests
import json
import pandas as pd


class MySQLConnector:
    def __init__(self, host, port, user, password, db=None):
        """Connects to the MySQL. The connection will be retried for 5 times if it fails.

        Args:
            host: MySQL host.
            port: MySQL port.
            user: MySQL user.
            password: MySQL password.
            db: MySQL database. Default is None.
        """
        max_attempts = 5  # Set the maximum number of attempts
        cur_attempt = 0  # Current attempt number
        self.flag_connected = False  # Flag to indicate connection status

        while cur_attempt < max_attempts and not self.flag_connected:
            try:
                cur_attempt += 1
                print(f"[connect_history]Attempting to connect to MySQL, attempt number: {cur_attempt}.")
                self.mysql_connection = pymysql.connect(host=host,
                                                        port=port,
                                                        user=user,
                                                        password=password,
                                                        database=db,
                                                        cursorclass=pymysql.cursors.DictCursor)
                print("[connect_history]Successfully connected to MySQL.")
                # Automatically reconnect if connection is lost
                self.mysql_connection.ping(reconnect=True)
                self.flag_connected = True  # Mark as successfully connected
            except Exception as e:
                print(f"[connect_history]Exception thrown. connect_history for {cur_attempt} attempt: " + str(e))
                time.sleep(2)  # Wait for 2 seconds before retrying

        if not self.flag_connected:
            print("[connect_history]Unable to connect to the MySQL.")

    def get_connection(self):
        """Return the MySQL connection object."""
        if self.flag_connected:
            return self.mysql_connection, self.flag_connected
        else:
            return None, self.flag_connected

    def execute_query(self, query):
        """Execute the query and return the result.

        Args:
            query: MySQL query to be executed.
        
        Returns:
            The result of the query with the format of a list of dictionaries.
        """
        with self.mysql_connection.cursor() as cursor:
            print(f"[query_history]Executing query: {query}")
            cursor.execute(query)
            result = cursor.fetchall()
        
        print(f"[query_history]Query executed successfully. Number of records: {len(result)}")

        return result
    
    def commit(self):
        """Commit the changes to MySQL."""
        self.mysql_connection.commit()
    
    def insert_tuple_data(self, table_name, data):
        """Insert the data in tuple list type into the MySQL table.
 
        Args:
            table_name: target table in MySQL.
            data: data in tuple list type ([(1, 'Alice'), (2, 'Bob'), (3, 'Charlie')]) to be inserted.
        """
        with self.mysql_connection.cursor() as cursor:
            query = f"SHOW COLUMNS FROM {table_name};"
            cursor.execute(query)
            result = cursor.fetchall()
            # fetach all column names
            columns = [column['Field'] for column in result]
            # convert the list of column names into a string
            cols = ', '.join(columns)
 
            insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({', '.join(['%s' for _ in columns])})"
 
            try:
                # Insert data into MySQL using executemany
                cursor.executemany(insert_query, data)
                # Commit the changes to MySQL
                self.mysql_connection.commit()
 
                # Number of rows inserted or replaced
                num_rows_affected = cursor.rowcount
                print(f"[insert_history]Number of rows affected in MySQL: {num_rows_affected}")
                
            except pymysql.Error as e:
                print("Error:", e)

    def insert_dict_data(self, table_name, data):
        """Insert the data in dict list type into the MySQL table.
 
        Args:
            table_name: target table in MySQL.
            data: data in dict list type ([{'id': 921, 'name': '7G2CE', 'created': datetime.datetime(2024, 4, 2, 20, 59, 50)]) to be inserted.
        """
        with self.mysql_connection.cursor() as cursor:
            # fetach all column names in the import data
            columns = data[0].keys()
            # convert the list of column names into a string
            cols = ', '.join(columns)
 
            insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({', '.join(['%s' for _ in columns])})"

            tuple_data = [tuple(record.values()) for record in data]
            try:
                # Insert data into MySQL using executemany
                cursor.executemany(insert_query, tuple_data)
                # Commit the changes to MySQL
                self.mysql_connection.commit()
 
                # Number of rows inserted or replaced
                num_rows_affected = cursor.rowcount
                print(f"[insert_history]Number of rows affected in MySQL: {num_rows_affected}")
                
            except pymysql.Error as e:
                print("Error:", e)

    def close(self):
        """Close the MySQL connection."""
        self.mysql_connection.cursor().close()
        self.mysql_connection.close()


class ClickHouseConnector:
    def __init__(self, host, port, user, password, db):
        """Connects to the ClickHouse. The connection will be retried for 5 times if it fails.

        Args:
            host: ClickHouse host.
            port: ClickHouse port.
            user: ClickHouse user.
            password: ClickHouse password.
            db: ClickHouse database. Default is None.
        """
        # Construct the connection string
        ch_connection_string = f"clickhouse://{user}:{password}@{host}:{port}/{db}"

        max_attempts = 5  # Set the maximum number of attempts
        cur_attempt = 0  # Current attempt number
        self.flag_connected = False  # Flag to indicate connection status

        while cur_attempt < max_attempts and not self.flag_connected:
            try:
                cur_attempt += 1
                print(f"[connect_history]Attempting to connect to ClickHouse, attempt number: {cur_attempt}.")
                self.ch_client = get_client(
                    host=host, user=user, password=password, database=db, port=port)
                print("[connect_history]Successfully connected to ClickHouse.")
                self.flag_connected = True  # Mark as successfully connected
            except Exception as e:
                print(f"[connect_history]Exception thrown. connect_history for {cur_attempt} attempt: " + str(e))
                time.sleep(2)  # Wait for 2 seconds before retrying

        if not self.flag_connected:
            print("[connect_history]Unable to connect to the ClickHouse.")

    def get_connection(self):
        """Return the ClickHouse connection object."""
        if self.flag_connected:
            return self.ch_client, self.flag_connected
        else:
            return None, self.flag_connected

    def execute_query(self, query):
        """Execute the query and return the result.

        Args:
            query: ClickHouse query to be executed.
        
        Returns:
            The result of the query with the format of a list of dictionaries.
        """
        print(f"[query_history]Executing query: {query}")
        result = self.ch_client.query(query).result_rows

        return result
    
    def query_df(self, query):
        """Execute the query and return the result as a DataFrame.

        Args:
            query: ClickHouse query to be executed.
        
        Returns:
            The result of the query with the format of a DataFrame.
        """
        print(f"[query_history]Executing query: {query}")
        result = self.ch_client.query_df(query)

        return result

    def insert(self, table, data, column_names=None, database=None, mode=None):
        """Insert the data into the ClickHouse table. The number of records inserted will be printed.

        Args:
            table: target table in ClickHouse.
            data: data to be inserted.
            column_names: column names of the target table. Default is None.
            database: database name of the target table. Default is None.
            mode: the mode of the data to be inserted. Default is None (support 'df').
        """

        # Check the number of records in the table before inserting
        record_count_query = f"SELECT COUNT(*) FROM {table}"
        result = self.ch_client.query(record_count_query).result_rows
        before_insert = result[0][0]

        if mode == 'df':
            if column_names is None and database is None:
                self.ch_client.insert_df(table, data)
            elif column_names is None and database is not None:
                self.ch_client.insert_df(table, data, database=database)
            elif column_names is not None and database is None:
                self.ch_client.insert_df(table, data, column_names=column_names)
            else:
                self.ch_client.insert_df(table, data, column_names=column_names, database=database)
        else:
            if column_names is None and database is None:
                self.ch_client.insert(table, data)
            elif column_names is None and database is not None:
                self.ch_client.insert(table, data, database=database)
            elif column_names is not None and database is None:
                self.ch_client.insert(table, data, column_names=column_names)
            else:
                self.ch_client.insert(table, data, column_names=column_names, database=database)

        # Check the number of records in the table after inserting
        result = self.ch_client.query(record_count_query).result_rows
        after_insert = result[0][0]
        print(f"[insert_history]Number of records transferred successfully: {after_insert - before_insert}")

    def close(self):
        """Close the ClickHouse connection."""
        self.ch_client.close()


class MSSQLConnector:
    def __init__(self, server, user, password, db=''):
        """Connects to the MS SQL and return connection object. The connection will be retried for 5 times if it fails.

        Args:
            server: MS SQL server.
            user: MS SQL user.
            password: MS SQL password.
            db: MS SQL database. Default is ''.
        """
        max_attempts = 5  # Set the maximum number of attempts
        cur_attempt = 0  # Current attempt number
        self.flag_connected = False  # Flag to indicate connection status

        while cur_attempt < max_attempts and not self.flag_connected:
            try:
                cur_attempt += 1
                print(f"[connect_history]Attempting to connect to MS SQL, attempt number: {cur_attempt}.")
                self.mssql_connection = pymssql.connect(server=server,
                                                        user=user,
                                                        password=password,
                                                        database=db)
                print("[connect_history]Successfully connected to MS SQL.")
                self.flag_connected = True  # Mark as successfully connected
            except Exception as e:
                print(f"[connect_history]Exception thrown. connect_history for {cur_attempt} attempt: " + str(e))
                time.sleep(2)  # Wait for 2 seconds before retrying

        if not self.flag_connected:
            print("[connect_history]Unable to connect to the MS SQL.")
    
    def get_connection(self):
        """Return the MS SQL connection object."""
        if self.flag_connected:
            return self.mssql_connection, self.flag_connected
        else:
            return None, self.flag_connected

    def execute_query(self, query):
        """Execute the query and return the result.

        Args:
            query: MS SQL query to be executed.
        
        Returns:
            The result of the query with the format of a list.
        """
        cursor = self.mssql_connection.cursor()
        print(f"[query_history]Executing query: {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        
        print(f"[query_history]Query executed successfully. Number of records: {len(result)}")

        return result

    def close(self):
        """Close the MS SQL connection."""
        self.mssql_connection.cursor().close()
        self.mssql_connection.close()


class SplunkConnector:
    def __init__(self, splunk_token):
        """Connects to the Splunk server.

        Args:
            token: Splunk token.
        """
        self.headers = {
            "Authorization": "Splunk " + splunk_token,
        }

    def execute_query(self, query):
        """Execute the query and return the result.

        Args:
            query: Splunk query to be executed.
        """
        data = {
            'adhoc_search_level': 'fast',
            'output_mode': 'json',
            'exec_mode': 'oneshot',
            'search': query,
            'count': 0  # Avoid the record limitation of Splunk to retrieve all query records."
        }
        response = requests.post(url='https://splunkapi.teslamotors.com/services/search/jobs',
                                headers=self.headers, data=data)
        result = json.loads(response.content.decode('utf-8'))

        print(f"[Splunk_query_history]Query executed successfully. Number of records: {len(result['results'])}.")

        return result

    def normalize_result(self, result):
        """Normalize the result and return a DataFrame.

        Args:
            result: the result from the Splunk query.
        """
        results = result['results']
        train_df = pd.json_normalize(results)

        return train_df

