import pandas as pd


REQUIRED_COLUMNS = {
    "case_id",
    "jurisdiction",
    "title",
    "status",
    "filing_date",
    "next_deadline",
    "owner",
}


def load_cases(csv_path: str) -> pd.DataFrame:
    """Load case data from a CSV file and parse date columns."""
    if not csv_path:
        raise ValueError("csv_path is required")

    df = pd.read_csv(csv_path, sep=None, engine="python")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_list}")

    df = df[
        [
            "case_id",
            "jurisdiction",
            "title",
            "status",
            "filing_date",
            "next_deadline",
            "owner",
        ]
    ].copy()

    for date_column in ["filing_date", "next_deadline"]:
        df[date_column] = pd.to_datetime(
            df[date_column],
            format="mixed",
            dayfirst=True,
            errors="coerce",
        )
        if df[date_column].isna().any():
            raise ValueError(f"Invalid values found in date column: {date_column}")

    return df


def add_deadline_metrics(df: pd.DataFrame, today: str = "2026-03-12") -> pd.DataFrame:
    """Add days_left and deadline_flag columns to a copy of the data."""
    if df is None or df.empty:
        return df.copy()

    if "next_deadline" not in df.columns:
        raise ValueError("DataFrame must include a 'next_deadline' column")

    result = df.copy()
    today_ts = pd.Timestamp(today)
    result["next_deadline"] = pd.to_datetime(result["next_deadline"])
    result["days_left"] = (result["next_deadline"] - today_ts).dt.days

    result["deadline_flag"] = "On Track"
    result.loc[result["days_left"] < 0, "deadline_flag"] = "Overdue"
    result.loc[result["days_left"].between(0, 7), "deadline_flag"] = "Due Soon"
    result.loc[result["days_left"].between(8, 30), "deadline_flag"] = "Upcoming"

    return result


def get_summary_counts(df: pd.DataFrame) -> dict:
    """Return basic counts for each deadline category."""
    if df is None:
        raise ValueError("DataFrame is required")

    if "deadline_flag" not in df.columns:
        raise ValueError("DataFrame must include a 'deadline_flag' column")

    flag_counts = df["deadline_flag"].value_counts()

    return {
        "total_cases": int(len(df)),
        "overdue": int(flag_counts.get("Overdue", 0)),
        "due_soon": int(flag_counts.get("Due Soon", 0)),
        "upcoming": int(flag_counts.get("Upcoming", 0)),
        "on_track": int(flag_counts.get("On Track", 0)),
    }


def filter_cases_by_flag(df: pd.DataFrame, flag: str) -> pd.DataFrame:
    """Return cases for one deadline flag, sorted by next deadline."""
    if df is None:
        raise ValueError("DataFrame is required")

    if "deadline_flag" not in df.columns:
        raise ValueError("DataFrame must include a 'deadline_flag' column")

    if "next_deadline" not in df.columns:
        raise ValueError("DataFrame must include a 'next_deadline' column")

    if not flag:
        raise ValueError("flag is required")

    filtered_df = df[df["deadline_flag"] == flag].copy()
    return filtered_df.sort_values("next_deadline", ascending=True)
