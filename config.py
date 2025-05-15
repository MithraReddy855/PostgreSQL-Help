import os

# PostgreSQL Documentation Resources
POSTGRESQL_DOC_BASE_URL = "https://www.postgresql.org/docs/current/"
POSTGRESQL_ERROR_CODES_URL = "https://www.postgresql.org/docs/current/errcodes-appendix.html"

# Database Connection
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = os.getenv("PGPORT", "5432")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD", "")
PG_DATABASE = os.getenv("PGDATABASE", "postgres")

# Common PostgreSQL error patterns for detection
ERROR_PATTERNS = {
    "connection_refused": [
        "connection refused",
        "could not connect to server",
        "Connection refused"
    ],
    "authentication_failed": [
        "password authentication failed",
        "no password supplied",
        "role .* does not exist"
    ],
    "permission_denied": [
        "permission denied",
        "insufficient privilege"
    ],
    "relation_not_found": [
        "relation .* does not exist",
        "table .* does not exist"
    ],
    "syntax_error": [
        "syntax error",
        "expected but found"
    ],
    "duplicate_key": [
        "duplicate key value violates unique constraint",
        "already exists"
    ],
    "foreign_key_violation": [
        "violates foreign key constraint",
        "is not present in table"
    ],
    "out_of_memory": [
        "out of memory",
        "insufficient memory"
    ],
    "disk_full": [
        "no space left on device",
        "could not extend file"
    ]
}

# SQL Query Templates
SQL_TEMPLATES = {
    "create_table": """CREATE TABLE {table_name} (
    id SERIAL PRIMARY KEY,
    {columns}
);""",
    "select": """SELECT {columns}
FROM {table_name}
{join_clause}
{where_clause}
{group_by_clause}
{order_by_clause}
{limit_clause};""",
    "insert": """INSERT INTO {table_name} ({columns})
VALUES ({values})
{returning_clause};""",
    "update": """UPDATE {table_name}
SET {set_clause}
{where_clause}
{returning_clause};""",
    "delete": """DELETE FROM {table_name}
{where_clause}
{returning_clause};"""
}

# Documentation sections by topic
DOCUMENTATION_SECTIONS = {
    "basics": ["sql-syntax", "ddl", "dml"],
    "advanced": ["queries", "performance", "functions"],
    "administration": ["admin", "backup", "monitoring"],
    "data_types": ["datatype"],
    "extensions": ["contrib"]
}
