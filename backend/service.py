import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from qdrant_service import get_messages_for_session
load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

def get_schema_info():
    connection = create_connection()
    if connection is None:
        return None

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        if tables==None:
            return {}

        schema_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            if columns==None:
                continue
            schema_info[table_name] = [col[0] for col in columns]

        return schema_info
    except Exception as e:
        print(f"Error retrieving schema: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def execute_query(query):
    connection = create_connection()
    if connection is None:
        raise Exception("Failed to connect to database")

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def search_messages_for_session(client, session_id, query):
    """
    Returns messages for a session where the content contains the query string (case-insensitive).
    """
    messages = get_messages_for_session(client, session_id)
    return [m for m in messages if query.lower() in m["content"].lower()]