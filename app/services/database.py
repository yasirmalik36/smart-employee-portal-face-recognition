import pyodbc
from fastapi import HTTPException

from app.config import settings  # Import global settings


def get_db_connection():
    """ Establishes a connection to SQL Server """
    return pyodbc.connect(settings.DB_CONNECTION_STRING)


def execute_query(query, params):
    """Executes an SQL query with optional parameters. Returns the number of rows affected."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
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
    Executes a stored procedure that returns a single (Code, Message, Description) row.

    Returns:
        A dictionary containing Code, Message, Description, or None on error.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.commit()
        cursor.close()

        if result:
            return {
                'Code': result[0],
                'Message': result[1],
                'Description': result[2],
            }
        return None

    except pyodbc.Error as ex:
        if conn is not None:
            conn.rollback()
        print(f"Database error: {ex.args[0]}, {ex}")
        return None
    except Exception as e:
        if conn is not None:
            conn.rollback()
        print(f"An error occurred: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()


def delete_record(table_name: str, conditions: str, values: tuple):
    """
    Generic function to delete records from a database table.

    NOTE: table_name and conditions are inserted into the SQL text directly, so they must
    only ever come from code, never from user input. Pass user values through `values`.

    :return: Number of rows affected
    """
    try:
        query = f"DELETE FROM {table_name} WHERE {conditions}"
        return execute_query(query, values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database deletion error: {str(e)}")
