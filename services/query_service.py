import logging
from config import SQL_TEMPLATES

logger = logging.getLogger(__name__)

def generate_query(query_type, table_name, columns='', conditions='', 
                  join_table='', join_condition='', order_by='', 
                  group_by='', limit=''):
    """
    Generate a PostgreSQL query based on input parameters
    
    Args:
        query_type (str): Type of query (select, insert, update, delete, create_table)
        table_name (str): Name of the table
        columns (str): Column names (comma-separated)
        conditions (str): WHERE conditions
        join_table (str): Table to join with
        join_condition (str): JOIN condition
        order_by (str): ORDER BY clause
        group_by (str): GROUP BY clause
        limit (str): LIMIT clause
        
    Returns:
        str: Generated SQL query
    """
    logger.debug(f"Generating {query_type} query for table {table_name}")
    
    if not table_name:
        return "-- Error: Table name is required"
    
    if query_type not in SQL_TEMPLATES:
        return f"-- Error: Unsupported query type: {query_type}"
    
    try:
        template = SQL_TEMPLATES[query_type]
        
        # Process different query types
        if query_type == 'create_table':
            # Format columns for CREATE TABLE statement
            if not columns:
                columns = "column_name data_type"
            
            return template.format(
                table_name=table_name,
                columns=columns
            )
            
        elif query_type == 'select':
            # Set defaults for SELECT
            if not columns:
                columns = "*"
                
            # Build clauses
            join_clause = f"JOIN {join_table} ON {join_condition}" if join_table and join_condition else ""
            where_clause = f"WHERE {conditions}" if conditions else ""
            group_by_clause = f"GROUP BY {group_by}" if group_by else ""
            order_by_clause = f"ORDER BY {order_by}" if order_by else ""
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            return template.format(
                columns=columns,
                table_name=table_name,
                join_clause=join_clause,
                where_clause=where_clause,
                group_by_clause=group_by_clause,
                order_by_clause=order_by_clause,
                limit_clause=limit_clause
            )
            
        elif query_type == 'insert':
            # Handle INSERT query
            if not columns:
                return "-- Error: Column names are required for INSERT statement"
                
            # Generate placeholders for values
            col_list = [col.strip() for col in columns.split(',')]
            values = ', '.join(['%s' for _ in col_list])
            
            returning_clause = "RETURNING id" if 'id' in columns else ""
            
            return template.format(
                table_name=table_name,
                columns=columns,
                values=values,
                returning_clause=returning_clause
            )
            
        elif query_type == 'update':
            # Handle UPDATE query
            if not columns:
                return "-- Error: SET clause is required for UPDATE statement"
                
            # Format SET clause
            if '=' not in columns:
                # Convert comma-separated list to SET format
                col_list = [col.strip() for col in columns.split(',')]
                set_clause = ', '.join([f"{col} = %s" for col in col_list])
            else:
                set_clause = columns
                
            where_clause = f"WHERE {conditions}" if conditions else ""
            returning_clause = "RETURNING id" if conditions else ""
            
            return template.format(
                table_name=table_name,
                set_clause=set_clause,
                where_clause=where_clause,
                returning_clause=returning_clause
            )
            
        elif query_type == 'delete':
            # Handle DELETE query
            where_clause = f"WHERE {conditions}" if conditions else ""
            
            # Safety check - require WHERE clause for DELETE
            if not where_clause:
                where_clause = "WHERE 1=0 -- WARNING: Add a WHERE clause to prevent deleting all rows"
                
            returning_clause = "RETURNING id" if where_clause and where_clause != "WHERE 1=0 -- WARNING: Add a WHERE clause to prevent deleting all rows" else ""
            
            return template.format(
                table_name=table_name,
                where_clause=where_clause,
                returning_clause=returning_clause
            )
            
    except Exception as e:
        logger.error(f"Error generating query: {str(e)}")
        return f"-- Error generating query: {str(e)}"
        
    return "-- Error: Unable to generate query"

def get_query_templates():
    """
    Get query templates with explanations
    
    Returns:
        dict: A dictionary of query templates with explanations
    """
    templates = {
        'select': {
            'title': 'SELECT - Retrieve Data',
            'template': SQL_TEMPLATES['select'],
            'explanation': (
                'SELECT queries retrieve data from one or more tables. You can filter rows with WHERE, '
                'sort with ORDER BY, limit results with LIMIT, and join tables to combine related data.'
            ),
            'example': (
                'SELECT first_name, last_name, email\n'
                'FROM customers\n'
                'WHERE status = \'active\'\n'
                'ORDER BY last_name ASC\n'
                'LIMIT 10;'
            )
        },
        'insert': {
            'title': 'INSERT - Add Data',
            'template': SQL_TEMPLATES['insert'],
            'explanation': (
                'INSERT queries add new rows to a table. You specify the table name, columns, and values. '
                'The RETURNING clause can return the newly created data.'
            ),
            'example': (
                'INSERT INTO customers (first_name, last_name, email)\n'
                'VALUES (\'John\', \'Doe\', \'john.doe@example.com\')\n'
                'RETURNING id;'
            )
        },
        'update': {
            'title': 'UPDATE - Modify Data',
            'template': SQL_TEMPLATES['update'],
            'explanation': (
                'UPDATE queries modify existing rows in a table. You specify the table name, column-value '
                'pairs to update, and conditions to identify which rows to update.'
            ),
            'example': (
                'UPDATE customers\n'
                'SET status = \'inactive\', last_updated = NOW()\n'
                'WHERE last_login < \'2023-01-01\'\n'
                'RETURNING id;'
            )
        },
        'delete': {
            'title': 'DELETE - Remove Data',
            'template': SQL_TEMPLATES['delete'],
            'explanation': (
                'DELETE queries remove rows from a table. You specify the table name and conditions to '
                'identify which rows to delete. Always use a WHERE clause to avoid deleting all rows.'
            ),
            'example': (
                'DELETE FROM customers\n'
                'WHERE status = \'cancelled\' AND last_updated < NOW() - INTERVAL \'1 year\'\n'
                'RETURNING id;'
            )
        },
        'create_table': {
            'title': 'CREATE TABLE - Define Schema',
            'template': SQL_TEMPLATES['create_table'],
            'explanation': (
                'CREATE TABLE statements define the structure of a new table. You specify column names, '
                'data types, constraints, and indexes.'
            ),
            'example': (
                'CREATE TABLE customers (\n'
                '    id SERIAL PRIMARY KEY,\n'
                '    first_name VARCHAR(50) NOT NULL,\n'
                '    last_name VARCHAR(50) NOT NULL,\n'
                '    email VARCHAR(100) UNIQUE NOT NULL,\n'
                '    status VARCHAR(20) DEFAULT \'active\',\n'
                '    created_at TIMESTAMP DEFAULT NOW()\n'
                ');'
            )
        }
    }
    
    return templates

def get_join_examples():
    """
    Get examples of different types of JOIN operations
    
    Returns:
        list: A list of JOIN examples with explanations
    """
    join_examples = [
        {
            'title': 'INNER JOIN',
            'example': 'SELECT o.order_id, c.customer_name\nFROM orders o\nINNER JOIN customers c ON o.customer_id = c.id',
            'explanation': 'Returns only the rows where there is a match in both tables.'
        },
        {
            'title': 'LEFT JOIN',
            'example': 'SELECT c.customer_name, o.order_id\nFROM customers c\nLEFT JOIN orders o ON c.id = o.customer_id',
            'explanation': 'Returns all rows from the left table and matching rows from the right table. If no match, NULL values are returned for right table columns.'
        },
        {
            'title': 'RIGHT JOIN',
            'example': 'SELECT c.customer_name, o.order_id\nFROM orders o\nRIGHT JOIN customers c ON o.customer_id = c.id',
            'explanation': 'Returns all rows from the right table and matching rows from the left table. If no match, NULL values are returned for left table columns.'
        },
        {
            'title': 'FULL OUTER JOIN',
            'example': 'SELECT c.customer_name, o.order_id\nFROM customers c\nFULL OUTER JOIN orders o ON c.id = o.customer_id',
            'explanation': 'Returns all rows when there is a match in either the left or right table. If no match, NULL values are returned for columns from the table without a match.'
        }
    ]
    
    return join_examples
