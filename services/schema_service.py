import os
import logging
import sqlalchemy
from sqlalchemy import MetaData, inspect, text
from sqlalchemy.engine import create_engine
from urllib.parse import urlparse

from config import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DATABASE

logger = logging.getLogger(__name__)

def analyze_schema(connection_string, table_name):
    """
    Analyze the schema of a PostgreSQL table
    
    Args:
        connection_string (str): Database connection string or parameters
        table_name (str): The name of the table to analyze
        
    Returns:
        dict: Analysis of the table schema including columns, constraints, etc.
    """
    logger.debug(f"Analyzing schema for table: {table_name}")
    
    try:
        # Create connection
        engine = create_database_connection(connection_string)
        
        if isinstance(engine, dict) and 'error' in engine:
            return engine
        
        # Get table information
        inspector = inspect(engine)
        
        # Ensure the table exists
        if not table_exists(inspector, table_name):
            return {'error': f"Table '{table_name}' not found in the database."}
        
        # Get table details
        columns = get_table_columns(inspector, table_name)
        primary_key = get_primary_key(inspector, table_name)
        foreign_keys = get_foreign_keys(inspector, table_name)
        indexes = get_indexes(inspector, table_name)
        constraints = get_constraints(engine, table_name)
        
        # Generate SQL to recreate the table
        create_table_sql = generate_create_table_sql(engine, table_name, columns, primary_key, foreign_keys, constraints)
        
        # Sample data structure
        sample_data_structure = get_sample_data_structure(columns)
        
        return {
            'table_name': table_name,
            'columns': columns,
            'primary_key': primary_key,
            'foreign_keys': foreign_keys,
            'indexes': indexes,
            'constraints': constraints,
            'create_table_sql': create_table_sql,
            'sample_data_structure': sample_data_structure
        }
        
    except Exception as e:
        logger.error(f"Error analyzing schema: {str(e)}")
        return {'error': f"Error analyzing schema: {str(e)}"}

def create_database_connection(connection_string):
    """
    Create a database connection from connection string or parameters
    
    Args:
        connection_string (str): Database connection string or parameters
        
    Returns:
        Engine or dict: SQLAlchemy engine or error dict
    """
    try:
        # Check if connection_string is a URL or a custom format
        if '://' in connection_string:
            # Parse the URL
            parsed_url = urlparse(connection_string)
            
            # Extract parameters if needed
            if parsed_url.scheme in ('postgresql', 'postgres'):
                engine = create_engine(connection_string)
            else:
                return {'error': 'Unsupported database type. Only PostgreSQL is supported.'}
        else:
            # Assume it's in format host:port/database
            try:
                if '/' in connection_string:
                    host_port, database = connection_string.split('/')
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, PG_PORT
                else:
                    host = connection_string
                    port = PG_PORT
                    database = PG_DATABASE
                
                # Create connection URL
                conn_str = f"postgresql://{PG_USER}:{PG_PASSWORD}@{host}:{port}/{database}"
                engine = create_engine(conn_str)
                
            except Exception:
                return {'error': 'Invalid connection format. Use "host:port/database" or a full connection URL.'}
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
        
    except Exception as e:
        logger.error(f"Error creating database connection: {str(e)}")
        return {'error': f"Error creating database connection: {str(e)}"}

def table_exists(inspector, table_name):
    """
    Check if a table exists in the database
    
    Args:
        inspector (Inspector): SQLAlchemy inspector
        table_name (str): Name of the table
        
    Returns:
        bool: True if the table exists, False otherwise
    """
    # Check if table_name contains schema
    if '.' in table_name:
        schema, table = table_name.split('.')
        return table in inspector.get_table_names(schema=schema)
    else:
        # Check in public schema and all available schemas
        if table_name in inspector.get_table_names():
            return True
            
        for schema in inspector.get_schema_names():
            if table_name in inspector.get_table_names(schema=schema):
                return True
                
    return False

def get_table_columns(inspector, table_name):
    """
    Get column information for a table
    
    Args:
        inspector (Inspector): SQLAlchemy inspector
        table_name (str): Name of the table
        
    Returns:
        list: List of column information dictionaries
    """
    schema = None
    if '.' in table_name:
        schema, table = table_name.split('.')
    else:
        table = table_name
        
    columns = inspector.get_columns(table, schema=schema)
    
    # Format column information
    formatted_columns = []
    for column in columns:
        formatted_columns.append({
            'name': column['name'],
            'type': str(column['type']),
            'nullable': column['nullable'],
            'default': str(column.get('default', 'None')),
            'is_primary': False  # Will be updated later
        })
        
    return formatted_columns

def get_primary_key(inspector, table_name):
    """
    Get primary key information for a table
    
    Args:
        inspector (Inspector): SQLAlchemy inspector
        table_name (str): Name of the table
        
    Returns:
        list: List of primary key column names
    """
    schema = None
    if '.' in table_name:
        schema, table = table_name.split('.')
    else:
        table = table_name
        
    pk_constraint = inspector.get_pk_constraint(table, schema=schema)
    return pk_constraint.get('constrained_columns', [])

def get_foreign_keys(inspector, table_name):
    """
    Get foreign key information for a table
    
    Args:
        inspector (Inspector): SQLAlchemy inspector
        table_name (str): Name of the table
        
    Returns:
        list: List of foreign key information dictionaries
    """
    schema = None
    if '.' in table_name:
        schema, table = table_name.split('.')
    else:
        table = table_name
        
    foreign_keys = inspector.get_foreign_keys(table, schema=schema)
    
    # Format foreign key information
    formatted_fks = []
    for fk in foreign_keys:
        formatted_fks.append({
            'name': fk.get('name', 'unnamed_fk'),
            'columns': fk.get('constrained_columns', []),
            'referred_table': fk.get('referred_table', ''),
            'referred_columns': fk.get('referred_columns', [])
        })
        
    return formatted_fks

def get_indexes(inspector, table_name):
    """
    Get index information for a table
    
    Args:
        inspector (Inspector): SQLAlchemy inspector
        table_name (str): Name of the table
        
    Returns:
        list: List of index information dictionaries
    """
    schema = None
    if '.' in table_name:
        schema, table = table_name.split('.')
    else:
        table = table_name
        
    indexes = inspector.get_indexes(table, schema=schema)
    
    # Format index information
    formatted_indexes = []
    for index in indexes:
        formatted_indexes.append({
            'name': index.get('name', 'unnamed_index'),
            'columns': index.get('column_names', []),
            'unique': index.get('unique', False)
        })
        
    return formatted_indexes

def get_constraints(engine, table_name):
    """
    Get constraint information for a table
    
    Args:
        engine (Engine): SQLAlchemy engine
        table_name (str): Name of the table
        
    Returns:
        list: List of constraint information dictionaries
    """
    schema = None
    if '.' in table_name:
        schema, table = table_name.split('.')
    else:
        table = table_name
        
    try:
        with engine.connect() as conn:
            # Query to get constraints from PostgreSQL information_schema
            query = text("""
                SELECT c.conname AS name,
                       c.contype AS type,
                       a.attname AS column_name,
                       c.condeferrable AS deferrable,
                       c.condeferred AS deferred,
                       c.consrc AS definition
                FROM pg_constraint c
                JOIN pg_namespace n ON n.oid = c.connamespace
                JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
                WHERE c.conrelid = (SELECT oid FROM pg_class WHERE relname = :table_name
                                   AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = :schema_name))
                ORDER BY c.conname, a.attnum;
            """)
            
            schema_name = schema if schema else 'public'
            result = conn.execute(query, {'table_name': table, 'schema_name': schema_name})
            
            constraints = []
            for row in result:
                constraints.append({
                    'name': row.name,
                    'type': translate_constraint_type(row.type),
                    'column': row.column_name,
                    'deferrable': row.deferrable,
                    'deferred': row.deferred,
                    'definition': row.definition if hasattr(row, 'definition') else None
                })
                
            return constraints
            
    except Exception as e:
        logger.error(f"Error getting constraints: {str(e)}")
        return []

def translate_constraint_type(type_code):
    """
    Translate PostgreSQL constraint type code to human-readable format
    
    Args:
        type_code (str): PostgreSQL constraint type code
        
    Returns:
        str: Human-readable constraint type
    """
    types = {
        'c': 'CHECK',
        'f': 'FOREIGN KEY',
        'p': 'PRIMARY KEY',
        'u': 'UNIQUE',
        't': 'TRIGGER',
        'x': 'EXCLUSION'
    }
    
    return types.get(type_code, f'UNKNOWN ({type_code})')

def generate_create_table_sql(engine, table_name, columns, primary_key, foreign_keys, constraints):
    """
    Generate SQL to recreate the table
    
    Args:
        engine (Engine): SQLAlchemy engine
        table_name (str): Name of the table
        columns (list): Column information
        primary_key (list): Primary key columns
        foreign_keys (list): Foreign key information
        constraints (list): Constraint information
        
    Returns:
        str: SQL CREATE TABLE statement
    """
    try:
        with engine.connect() as conn:
            # Use pg_dump to get the CREATE TABLE statement
            meta = MetaData()
            meta.reflect(bind=engine, only=[table_name.split('.')[-1]])
            
            # Check if table exists in metadata
            if table_name.split('.')[-1] not in meta.tables:
                # Fallback to building SQL manually
                return build_create_table_sql(table_name, columns, primary_key, foreign_keys, constraints)
                
            # Get table object
            table = meta.tables[table_name.split('.')[-1]]
            
            # Generate CREATE TABLE statement
            sql = str(sqlalchemy.schema.CreateTable(table).compile(engine))
            
            return sql
            
    except Exception as e:
        logger.error(f"Error generating CREATE TABLE SQL: {str(e)}")
        # Fallback to building SQL manually
        return build_create_table_sql(table_name, columns, primary_key, foreign_keys, constraints)

def build_create_table_sql(table_name, columns, primary_key, foreign_keys, constraints):
    """
    Build CREATE TABLE SQL statement manually
    
    Args:
        table_name (str): Name of the table
        columns (list): Column information
        primary_key (list): Primary key columns
        foreign_keys (list): Foreign key information
        constraints (list): Constraint information
        
    Returns:
        str: SQL CREATE TABLE statement
    """
    sql = f"CREATE TABLE {table_name} (\n"
    
    # Add columns
    column_defs = []
    for column in columns:
        col_def = f"    {column['name']} {column['type']}"
        
        if column['name'] in primary_key:
            # Mark as primary key in column object for reference
            column['is_primary'] = True
            # Only add PRIMARY KEY for single-column primary keys
            if len(primary_key) == 1:
                col_def += " PRIMARY KEY"
                
        if not column['nullable']:
            col_def += " NOT NULL"
            
        if column['default'] != 'None':
            col_def += f" DEFAULT {column['default']}"
            
        column_defs.append(col_def)
    
    # Add multi-column primary key if needed
    if len(primary_key) > 1:
        pk_def = f"    PRIMARY KEY ({', '.join(primary_key)})"
        column_defs.append(pk_def)
    
    # Add foreign keys
    for fk in foreign_keys:
        fk_def = f"    CONSTRAINT {fk['name']} FOREIGN KEY ({', '.join(fk['columns'])}) " \
                 f"REFERENCES {fk['referred_table']} ({', '.join(fk['referred_columns'])})"
        column_defs.append(fk_def)
    
    # Add constraints (except primary key and foreign keys which are already added)
    for constraint in constraints:
        if constraint['type'] not in ['PRIMARY KEY', 'FOREIGN KEY']:
            const_def = f"    CONSTRAINT {constraint['name']} {constraint['type']}"
            
            if constraint['definition']:
                const_def += f" {constraint['definition']}"
                
            column_defs.append(const_def)
    
    sql += ",\n".join(column_defs)
    sql += "\n);"
    
    return sql

def get_sample_data_structure(columns):
    """
    Generate a sample data structure based on column information
    
    Args:
        columns (list): Column information
        
    Returns:
        str: Sample data structure in JSON format
    """
    sample = {}
    
    for column in columns:
        col_type = column['type'].lower()
        
        # Determine appropriate sample value based on type
        if 'int' in col_type:
            sample[column['name']] = 1
        elif 'serial' in col_type:
            sample[column['name']] = 1
        elif 'float' in col_type or 'double' in col_type or 'numeric' in col_type or 'decimal' in col_type:
            sample[column['name']] = 1.0
        elif 'bool' in col_type:
            sample[column['name']] = True
        elif 'date' in col_type:
            sample[column['name']] = "2023-01-01"
        elif 'time' in col_type:
            if 'with time zone' in col_type or 'timezone' in col_type:
                sample[column['name']] = "2023-01-01T12:00:00Z"
            else:
                sample[column['name']] = "2023-01-01T12:00:00"
        elif 'json' in col_type:
            sample[column['name']] = {"key": "value"}
        elif 'array' in col_type:
            sample[column['name']] = [1, 2, 3]
        elif 'char' in col_type or 'text' in col_type or 'varchar' in col_type:
            sample[column['name']] = "sample_text"
        else:
            sample[column['name']] = "unknown_type"
    
    # Format as JSON string
    import json
    return json.dumps(sample, indent=2)

def get_table_info(connection_string):
    """
    Get list of tables and their basic information
    
    Args:
        connection_string (str): Database connection string or parameters
        
    Returns:
        list: List of tables with their information
    """
    try:
        # Create connection
        engine = create_database_connection(connection_string)
        
        if isinstance(engine, dict) and 'error' in engine:
            return []
        
        inspector = inspect(engine)
        tables = []
        
        # Get all schemas
        schemas = inspector.get_schema_names()
        
        for schema in schemas:
            # Skip system schemas
            if schema in ['pg_catalog', 'information_schema']:
                continue
                
            for table_name in inspector.get_table_names(schema=schema):
                # Get basic information about the table
                columns = inspector.get_columns(table_name, schema=schema)
                pk = inspector.get_pk_constraint(table_name, schema=schema)
                
                tables.append({
                    'schema': schema,
                    'name': table_name,
                    'column_count': len(columns),
                    'primary_key': pk.get('constrained_columns', []),
                    'full_name': f"{schema}.{table_name}" if schema != 'public' else table_name
                })
        
        return tables
        
    except Exception as e:
        logger.error(f"Error getting table info: {str(e)}")
        return []
