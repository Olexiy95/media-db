from sqlalchemy import create_engine, Engine
from typing import Optional
import json
import os


default_db_config = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "database": os.getenv("POSTGRES_DB_NAME"),
}


def create_connection_string(
    default_config: bool = True, db_config: Optional[dict] = None
):
    """
    Create a connection string for the database.

    Parameters:
    - default_config (bool): Whether to use the default configuration (True) or a custom configuration (False).
    - db_config (dict, optional): A dictionary containing the database connection details. Required when default_config is set to False.

    Returns:
    - str: The connection string for the database.

    Raises:
    - ValueError: If default_config is False and no db_config is provided.
    - AssertionError: If default_config is True and db_config is provided, or if default_config is False and db_config is not provided.
    """

    if default_config:
        assert (
            db_config is None
        ), "Default configuration is used, so no custom config should be provided."
        db_config = default_db_config
    else:
        assert (
            db_config is not None
        ), "Custom configuration must be provided when default_config is set to False."

    # Extract the database connection details
    user = db_config.get("user")
    password = db_config.get("password")
    host = db_config.get("host")
    port = db_config.get("port")
    database = db_config.get("database")

    # Create the connection string
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return connection_string


def get_db_connection(connection_string) -> Engine:
    """
    Create a database connection using SQLAlchemy.

    Parameters:
    - connection_string (str): The connection string for the database.

    Returns:
    - engine: SQLAlchemy engine object representing the database connection.
    """
    try:
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


def jprint(json_object):
    """
    Pretty-print JSON objects.
    """
    pretty_json = json.dumps(json_object, indent=3)
    return pretty_json
