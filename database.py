import sqlite3

import pandas as pd


DEFAULT_DB_PATH = "ip_deadlines.db"

CASE_COLUMNS = [
    "case_id",
    "jurisdiction",
    "title",
    "status",
    "filing_date",
    "next_deadline",
    "owner",
]


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    return sqlite3.connect(db_path)


def initialize_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """Create the ip_cases table if it does not already exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ip_cases (
        case_id TEXT PRIMARY KEY,
        jurisdiction TEXT,
        title TEXT,
        status TEXT,
        filing_date TEXT,
        next_deadline TEXT,
        owner TEXT
    )
    """

    with get_connection(db_path) as connection:
        connection.execute(create_table_sql)
        connection.commit()


def save_cases(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH) -> None:
    """Save case data to SQLite, replacing existing table contents."""
    if df is None:
        raise ValueError("DataFrame is required")

    missing_columns = [column for column in CASE_COLUMNS if column not in df.columns]
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_list}")

    initialize_database(db_path)

    data_to_save = df[CASE_COLUMNS].copy()
    data_to_save["filing_date"] = pd.to_datetime(data_to_save["filing_date"]).dt.strftime("%Y-%m-%d")
    data_to_save["next_deadline"] = pd.to_datetime(data_to_save["next_deadline"]).dt.strftime("%Y-%m-%d")

    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM ip_cases")
        data_to_save.to_sql("ip_cases", connection, if_exists="append", index=False)
        connection.commit()


def load_cases_from_db(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """Load all case data from SQLite and parse date columns."""
    initialize_database(db_path)

    query = """
    SELECT case_id, jurisdiction, title, status, filing_date, next_deadline, owner
    FROM ip_cases
    """

    with get_connection(db_path) as connection:
        df = pd.read_sql_query(query, connection)

    if df.empty:
        return df

    df["filing_date"] = pd.to_datetime(df["filing_date"])
    df["next_deadline"] = pd.to_datetime(df["next_deadline"])
    return df
