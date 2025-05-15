import os
import logging
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qsl

from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection(connection_string=None):
    """
    Get a PostgreSQL database connection
    
    Args:
        connection_string (str, optional): Database connection string. If not provided,
                                        environment variables will be used.
    
    Yields:
        connection: PostgreSQL database connection
    """
    conn = None
    try:
        if connection_string:
            # Parse connection string to extract parameters
            if '://' in connection_string:
                # SQLAlchemy-style connection string
                url = urlparse(connection_string)
                if url.scheme in ('postgresql', 'postgres'):
                    db_params = dict(parse_qsl(url.query))
                    db_params.update({
                        'host': url.hostname or PG_HOST,
                        'port': url.port or PG_PORT,
                        'user': url.username or PG_USER,
                        'password': url.password or PG_PASSWORD,
                        'database': url.path[1:] if url.path else PG_DATABASE
                    })
                else:
                    raise ValueError(f"Unsupported database type: {url.scheme}")
            else:
                # Custom format (host:port/database)
                parts = connection_string.split('/')
                if len(parts) == 2:
                    host_port, database = parts
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, PG_PORT
                else:
                    host = connection_string
                    port = PG_PORT
                    database = PG_DATABASE
                
                db_params = {
                    'host': host,
                    'port': port,
                    'user': PG_USER,
                    'password': PG_PASSWORD,
                    'database': database
                }
        else:
            # Use environment variables
            db_params = {
                'host': PG_HOST,
                'port': PG_PORT,
                'user': PG_USER,
                'password': PG_PASSWORD,
                'database': PG_DATABASE
            }
        
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        yield conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(connection_string=None):
    """
    Get a PostgreSQL database cursor
    
    Args:
        connection_string (str, optional): Database connection string. If not provided,
                                        environment variables will be used.
    
    Yields:
        cursor: PostgreSQL database cursor
    """
    with get_db_connection(connection_string) as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

def get_sqlalchemy_engine(connection_string=None):
    """
    Get a SQLAlchemy engine for PostgreSQL
    
    Args:
        connection_string (str, optional): Database connection string. If not provided,
                                        environment variables will be used.
    
    Returns:
        Engine: SQLAlchemy engine
    """
    try:
        if connection_string:
            if '://' in connection_string:
                # SQLAlchemy-style connection string
                engine = create_engine(connection_string)
            else:
                # Custom format (host:port/database)
                parts = connection_string.split('/')
                if len(parts) == 2:
                    host_port, database = parts
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, PG_PORT
                else:
                    host = connection_string
                    port = PG_PORT
                    database = PG_DATABASE
                
                conn_str = f"postgresql://{PG_USER}:{PG_PASSWORD}@{host}:{port}/{database}"
                engine = create_engine(conn_str)
        else:
            # Use environment variables
            conn_str = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
            engine = create_engine(conn_str)
        
        return engine
    except Exception as e:
        logger.error(f"Error creating SQLAlchemy engine: {str(e)}")
        raise

def test_connection(connection_string=None):
    """
    Test a PostgreSQL database connection
    
    Args:
        connection_string (str, optional): Database connection string. If not provided,
                                        environment variables will be used.
    
    Returns:
        dict: Connection test results
    """
    try:
        with get_db_connection(connection_string) as conn:
            with conn.cursor() as cursor:
                # Get PostgreSQL version
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                
                # Get current database name
                cursor.execute("SELECT current_database();")
                database = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()));
                """)
                size = cursor.fetchone()[0]
                
                # Get number of tables
                cursor.execute("""
                    SELECT count(*) FROM information_schema.tables 
                    WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
                """)
                table_count = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'version': version,
                    'database': database,
                    'size': size,
                    'table_count': table_count
                }
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
