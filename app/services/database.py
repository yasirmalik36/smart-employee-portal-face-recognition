import pyodbc
from app.config import settings  # Import global settings

def get_db_connection():
    """ Establishes a connection to SQL Server """
    conn = pyodbc.connect(settings.DB_CONNECTION_STRING)
    return conn



def execute_query(query, params):
    """Executes an SQL query with optional parameters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def fetch_all(query, params=None):
    """Fetches all results for a given query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()

def execute_query_with_output(query, params):
    """
    Executes a stored procedure with output parameters and returns the result.

    Args:
        query: The SQL query (stored procedure call) with output parameters.
        params: A tuple or list of parameters for the query.

    Returns:
        A dictionary containing (Code, Message, Desc) or None on error.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the stored procedure only once
        cursor.execute(query, params)

        # Fetch the result set containing the output parameters
        result = cursor.fetchone()
        print(result)

        # Commit the transaction
        conn.commit()

        cursor.close()
        conn.close()

        if result:
            # Assuming the result tuple has columns in the order: Code, Message, Desc
            return {
                'Code': result[0],  # Access the first element (Code)
                'Message': result[1], # Access the second element (Message)
                'Description': result[2]    # Access the third element (Desc)
            }
        else:
            return None

    except pyodbc.Error as ex:
        conn.rollback()
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}, {ex}")
        return None
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None



def delete_record(table_name: str, conditions: str, values: tuple):
    """
    Generic function to delete a record from a database table.

    :param table_name: The name of the table
    :param conditions: The WHERE clause conditions (e.g., "EmployeeID=? AND IsDeleted=0")
    :param values: Tuple of values to pass into the query
    :return: Number of rows affected
    """
    try:
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        return execute_query(query, values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database deletion error: {str(e)}")


def execute_query_with_output(query, params):
    """
    Executes a stored procedure with output parameters and returns the result.

    Args:
        query: The SQL query (stored procedure call) with output parameters.
        params: A tuple or list of parameters for the query.

    Returns:
        A dictionary containing (Code, Message, Desc) or None on error.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the stored procedure only once
        cursor.execute(query, params)

        # Fetch the result set containing the output parameters
        result = cursor.fetchone()
        print(result)

        # Commit the transaction
        conn.commit()

        cursor.close()
        conn.close()

        if result:
            # Assuming the result tuple has columns in the order: Code, Message, Desc
            return {
                'Code': result[0],  # Access the first element (Code)
                'Message': result[1], # Access the second element (Message)
                'Description': result[2]    # Access the third element (Desc)
            }
        else:
            return None

    except pyodbc.Error as ex:
        conn.rollback()
        sqlstate = ex.args[0]
        print(f"Database error: {sqlstate}, {ex}")
        return None
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None
