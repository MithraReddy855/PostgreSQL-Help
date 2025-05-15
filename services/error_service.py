import re
import logging
import requests
from bs4 import BeautifulSoup
from config import POSTGRESQL_ERROR_CODES_URL, ERROR_PATTERNS
from utils.doc_parser import fetch_doc_page

logger = logging.getLogger(__name__)

def analyze_error(error_text):
    """
    Analyze a PostgreSQL error message and provide troubleshooting information
    
    Args:
        error_text (str): The error message to analyze
        
    Returns:
        dict: Analysis results with error type, explanation, and solution
    """
    logger.debug(f"Analyzing error: {error_text[:50]}...")
    
    if not error_text:
        return {
            'error_type': 'Unknown',
            'explanation': 'No error text provided for analysis.',
            'solution': 'Please provide the complete error message for analysis.'
        }
    
    # Extract error code if present
    error_code_match = re.search(r'ERROR:\s+\d+', error_text)
    error_code = None
    
    if error_code_match:
        error_code = error_code_match.group(0).split(':')[1].strip()
    
    # Look for known error patterns
    error_type = 'Unknown'
    for err_type, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, error_text, re.IGNORECASE):
                error_type = err_type
                break
        if error_type != 'Unknown':
            break
    
    # Get detailed explanation and solution based on error type
    explanation, solution = get_error_details(error_type, error_code, error_text)
    
    return {
        'error_type': error_type.replace('_', ' ').title(),
        'explanation': explanation,
        'solution': solution,
        'error_code': error_code
    }

def get_error_details(error_type, error_code=None, error_text=''):
    """
    Get detailed explanation and solution for a specific error type
    
    Args:
        error_type (str): The type of error
        error_code (str, optional): The PostgreSQL error code if available
        error_text (str): The original error text
        
    Returns:
        tuple: (explanation, solution)
    """
    explanations = {
        'connection_refused': (
            "The PostgreSQL server is not accepting connections. This could be because the server is not running, "
            "network connectivity issues, or firewall rules blocking the connection.",
            "1. Verify that the PostgreSQL server is running\n"
            "2. Check network connectivity between your client and the server\n"
            "3. Ensure firewall rules allow connections to the PostgreSQL port (default: 5432)\n"
            "4. Confirm the correct host and port in your connection string"
        ),
        'authentication_failed': (
            "The provided credentials were rejected by the PostgreSQL server. This could be due to incorrect username/password, "
            "or the user may not have permission to connect to the database.",
            "1. Double-check your username and password\n"
            "2. Verify that the user exists in the PostgreSQL server\n"
            "3. Check pg_hba.conf configuration on the server\n"
            "4. Try connecting with a different authentication method if available"
        ),
        'permission_denied': (
            "The authenticated user does not have sufficient privileges to perform the requested operation.",
            "1. Connect as a superuser or the object owner\n"
            "2. Grant the necessary permissions to the user:\n"
            "   - For tables: GRANT SELECT, INSERT, UPDATE, DELETE ON table_name TO username;\n"
            "   - For schemas: GRANT USAGE ON SCHEMA schema_name TO username;\n"
            "3. Check the user's role memberships and privileges"
        ),
        'relation_not_found': (
            "PostgreSQL cannot find the specified table, view, or other relation. This could be because it doesn't exist, "
            "or because it exists in a different schema that is not in your search_path.",
            "1. Check the spelling of the table/relation name\n"
            "2. Verify the schema name and search_path\n"
            "3. Use the fully qualified name: schema_name.table_name\n"
            "4. Check if the table exists with: \\dt schema_name.* (in psql)"
        ),
        'syntax_error': (
            "There is a syntax error in your SQL statement. PostgreSQL cannot parse the statement because it doesn't conform to SQL grammar rules.",
            "1. Check for missing or extra parentheses, commas, or quotes\n"
            "2. Verify keywords are spelled correctly\n"
            "3. Ensure identifiers are properly quoted if they contain special characters\n"
            "4. Compare your syntax with PostgreSQL documentation examples"
        ),
        'duplicate_key': (
            "The operation would create a duplicate value in a unique or primary key constraint. PostgreSQL enforces uniqueness and prevents the operation.",
            "1. Use a different key value that doesn't already exist\n"
            "2. Use ON CONFLICT clause with INSERT statements to handle duplicates\n"
            "3. If appropriate, consider using UPDATE instead of INSERT\n"
            "4. Check if the uniqueness constraint is still necessary for your application"
        ),
        'foreign_key_violation': (
            "The operation would violate a foreign key constraint. This happens when you try to insert a reference to a non-existent parent row, "
            "or delete a parent row that is still referenced by child rows.",
            "1. For INSERTs: Ensure the referenced key exists in the parent table first\n"
            "2. For DELETEs: Either delete child rows first, or use CASCADE option\n"
            "3. Consider using ON DELETE SET NULL in your foreign key definition\n"
            "4. Verify the integrity of your data across related tables"
        ),
        'out_of_memory': (
            "The PostgreSQL server has run out of memory while processing your query. This can happen with complex queries, large data sets, "
            "or if the server's memory parameters are set too low.",
            "1. Optimize your query to use less memory (avoid large IN lists, use JOINs efficiently)\n"
            "2. Increase work_mem parameter in postgresql.conf\n"
            "3. Add more physical memory to your server\n"
            "4. Consider partitioning large tables to reduce memory requirements"
        ),
        'disk_full': (
            "The PostgreSQL server has run out of disk space. This prevents it from writing new data or temporary files needed for query execution.",
            "1. Free up disk space by removing unnecessary files\n"
            "2. Add additional storage to the server\n"
            "3. Move the PostgreSQL data directory to a larger volume\n"
            "4. Enable table autovacuum to reclaim space from deleted rows"
        ),
        'unknown': (
            "This is an unrecognized PostgreSQL error that doesn't match common error patterns.",
            "1. Check the PostgreSQL documentation for specific error codes\n"
            "2. Search PostgreSQL mailing lists or forums for similar errors\n"
            "3. Review server logs for additional context\n"
            "4. Try simplifying your operation to isolate the issue"
        )
    }
    
    if error_type not in explanations:
        error_type = 'unknown'
    
    explanation, solution = explanations[error_type]
    
    # If we have an error code, try to get more specific information
    if error_code:
        specific_info = get_error_code_info(error_code)
        if specific_info:
            explanation += f"\n\nError Code Details: {specific_info}"
    
    # Add specific advice based on error text if possible
    if error_type == 'syntax_error':
        # Extract the specific syntax error location and suggestion
        syntax_hint_match = re.search(r'ERROR:[^\n]*\n[^\n]*', error_text)
        if syntax_hint_match:
            explanation += f"\n\nSpecific Error: {syntax_hint_match.group(0)}"
    
    return explanation, solution

def get_error_code_info(error_code):
    """
    Get information about a specific PostgreSQL error code
    
    Args:
        error_code (str): The PostgreSQL error code
        
    Returns:
        str: Description of the error code or None if not found
    """
    try:
        html_content = fetch_doc_page(POSTGRESQL_ERROR_CODES_URL)
        
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for the error code in the table
        for table in soup.find_all('table', class_='table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2 and error_code in cells[0].get_text():
                    return cells[1].get_text(strip=True)
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting error code info: {str(e)}")
        return None

def get_common_errors():
    """
    Get a list of common PostgreSQL errors and their solutions
    
    Returns:
        list: A list of common errors with their descriptions and solutions
    """
    common_errors = [
        {
            'title': 'Connection Refused',
            'description': 'Unable to connect to the PostgreSQL server.',
            'solution': 'Check if the server is running, verify network connectivity, and ensure firewall rules allow connections.'
        },
        {
            'title': 'Authentication Failed',
            'description': 'Server rejected the provided credentials.',
            'solution': 'Verify username and password, ensure the user exists, and check pg_hba.conf configuration.'
        },
        {
            'title': 'Permission Denied',
            'description': 'User lacks privileges for the requested operation.',
            'solution': 'Grant necessary permissions to the user or connect as a superuser/object owner.'
        },
        {
            'title': 'Relation Not Found',
            'description': 'The specified table or view does not exist.',
            'solution': 'Check spelling, verify schema name, and use fully qualified names (schema.table).'
        },
        {
            'title': 'Syntax Error',
            'description': 'SQL statement contains grammar errors.',
            'solution': 'Check for missing/extra punctuation, verify keywords, and ensure proper quoting of identifiers.'
        },
        {
            'title': 'Duplicate Key Violation',
            'description': 'Operation would create a duplicate in a unique constraint.',
            'solution': 'Use different values, implement ON CONFLICT clauses, or update existing rows instead.'
        },
        {
            'title': 'Foreign Key Violation',
            'description': 'Operation would break referential integrity.',
            'solution': 'Ensure referenced keys exist in parent tables or delete child rows first.'
        },
        {
            'title': 'Out of Memory',
            'description': 'Server ran out of memory processing a query.',
            'solution': 'Optimize queries, increase work_mem parameter, or add more physical memory.'
        },
        {
            'title': 'Disk Full',
            'description': 'Server has run out of disk space.',
            'solution': 'Free up disk space, add storage, or move data directory to a larger volume.'
        }
    ]
    
    return common_errors
