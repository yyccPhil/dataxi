# File: ./src/connectors/mysql_connector.py

# Creator: Yuan Yuan (yyccPhil)

# Version:

# 2024.12.11:
#     1. Initial version.


import time
import pymysql.cursors


class MySQLConnector:
    def __init__(self, host=None, port=None, user=None, password=None, database=None, cursorclass='dict', conn_id=None):
        """Connects to the MySQL. The connection will be retried for 5 times if it fails.

        Args:
            host: MySQL host.
            port: MySQL port.
            user: MySQL user.
            password: MySQL password.
            database: MySQL database. Default is None.
            cursorclass: cursor class for MySQL. Default is 'dict'.
        """
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
