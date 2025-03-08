import pyodbc
from app.config import settings  # Import global settings

def get_db_connection():
    """ Establishes a connection to SQL Server """
    conn = pyodbc.connect(settings.DB_CONNECTION_STRING)
    return conn



def execute_query(query, params=None):
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

