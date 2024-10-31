import psycopg2
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import registry
from contextlib import contextmanager

mapper_registry = registry()

# Connection details for the test database
test_metadata_db_connection = {
    "host": "localhost",
    "database": "Pokemon",
    "user": "postgres",
    "password": "gai3905",
}

from sqlalchemy import create_engine

def get_engine():
    """Create and return a SQLAlchemy engine for the test database."""
    DATABASE_URL = "postgresql://postgres:gai3905@localhost/Pokemon"  # Replace with your actual connection details
    engine = create_engine(DATABASE_URL)
    return engine

@contextmanager
def get_db_connection():
    """Context manager to get a database connection."""
    conn = psycopg2.connect(**test_metadata_db_connection)
    try:
        yield conn
    finally:
        conn.close()

def create_test_tables(engine):
    """Create the tables in the test database based on the ORM models."""
    with get_db_connection() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            for table in mapper_registry.metadata.tables.values():
                ddl_string = str(
                    CreateTable(table).compile(dialect=postgresql.dialect())
                )
                formatted_ddl = " ".join(ddl_string.split())
                cur.execute(formatted_ddl)

def drop_test_tables(engine):
    """Drop all tables in the test database."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for table in mapper_registry.metadata.tables.keys():
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            conn.commit()
