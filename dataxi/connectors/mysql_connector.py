# File: mysql_connector.py

# Description: This Package aims to provide some reusable functions for connecting to MySQL.

# Creator: Yuan Yuan (yyccphil@gmail.com)

# Change Log:

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
# 2024.05.23:
#     1. added cursorclass parameter for MySQLConnector class
# 2024.09.10:
#     1. changed 'db' default value to None for ClickHouseConnector class
#     2. added 'verify' parameter for ClickHouseConnector class
# 2024.09.18:
#     1. added 3 sec time sleep when query in CH after insertion
# 2024.10.01:
#     1. added the count_table() func for ClickHouseConnector class
# 2025.02.24:
#     1. fix: convert NaN and NaT in a list of tuples to None in insert_tuple_data() func


import time
import pymysql.cursors

import json
from pathlib import Path
from ..cred_mgr import CredSender

class MySQLConnector:
    def __init__(self, host=None, port=None, user=None, password=None, database=None, cursorclass=None, conn_id=None, retries=3, **kwargs):
        """Initialize the MySQL connection object.
        
        Args:
            host: MySQL host.
            port: MySQL port.
            user: MySQL user.
            password: MySQL password.
            database: MySQL database.
            cursorclass: MySQL cursor class.
            conn_id: Connection ID to load the credentials from the credential manager.
            **kwargs: Additional keyword arguments. Especially for db_type.
        """
        
        if conn_id:
            print(f"[connect_history]Connecting to MySQL with connection ID: {conn_id}")
            
            config_dir = Path.home() / ".dataxi"
            cred_path = config_dir / "creds.json"
            with open(cred_path, "r") as f:
                cred_data = json.load(f)
                if conn_id in cred_data:
                    cred_dict = cred_data[conn_id]
                else:
                    print(f"conn_id: '{conn_id}' does not exist.")
                    return None
            self.get_connection(**cred_dict)
        else:
            self.get_connection(host=host, port=port, user=user, password=password, database=database, cursorclass=cursorclass)
        
        
    def with_reconnection(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[connect_history] Connection failed: {e}")
                
                try:
                    self.mysql_connection.ping(reconnect=True)
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"[connect_history] Ping old connection failed: {e}")
                    
                    self.get_connection()
                    return func(*args, **kwargs)
                    
        return wrapper
        

    def get_connection(self, host=None, port=None, user=None, password=None, database=None, cursorclass=None):
        """Return the MySQL connection object."""
        max_attempts = 5  # Set the maximum number of attempts
        cur_attempt = 0  # Current attempt number
        self.flag_connected = False  # Flag to indicate connection status

        while cur_attempt < max_attempts and not self.flag_connected:
            try:
                cur_attempt += 1
                print(f"[connect_history]Attempting to connect to MySQL, attempt number: {cur_attempt}.")
                if cursorclass == 'dict':
                    self.mysql_connection = pymysql.connect(host=host,
                                                            port=port,
                                                            user=user,
                                                            password=password,
                                                            database=database,
                                                            cursorclass=pymysql.cursors.DictCursor)
                else:
                    self.mysql_connection = pymysql.connect(host=host,
                                                        port=port,
                                                        user=user,
                                                        password=password,
                                                        database=database)
                print("[connect_history]Successfully connected to MySQL.")
                # Automatically reconnect if connection is lost
                self.mysql_connection.ping(reconnect=True)
                self.flag_connected = True  # Mark as successfully connected
            except Exception as e:
                print(f"[connect_history]Exception thrown. connect_history for {cur_attempt} attempt: " + str(e))
                time.sleep(2)  # Wait for 2 seconds before retrying

        if not self.flag_connected:
            raise Exception("[connect_history]Unable to connect to the MySQL.")
        if self.flag_connected:
            return self.mysql_connection, self.flag_connected
        else:
            return None, self.flag_connected

    @with_reconnection
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
    
    @with_reconnection
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

    @with_reconnection
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
        try:
            self.mysql_connection.cursor().close()
            self.mysql_connection.close()
            print("[connect_history]MySQL connection closed.")
        except Exception as e:
            print(f"[connect_history]Error while closing the connection: {e}")
