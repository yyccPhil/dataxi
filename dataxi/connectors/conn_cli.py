from .mysql_connector import MySQLConnector


class Connector:
    def __init__(self, connector_type=None, **kwargs):
        """Connects to the database using the specified connector.

        Args:
            connector_type: Type of connector to be used. Default is None.
            **kwargs: Keyword arguments for the connector.
        """
        if connector_type == 'mysql':
            self.connector = MySQLConnector(**kwargs)
        else:
            raise ValueError(f"Connector type {connector_type} is not supported.")

    def get_connection(self):
        """Return the connection object."""
        return self.connector.get_connection()

    def execute_query(self, query):
        """Execute the query and return the result.

        Args:
            query: Query to be executed
        """
        return self.connector.execute_query(query)
    
if __name__ == '__main__':
    # Example usage
    conn = 1
