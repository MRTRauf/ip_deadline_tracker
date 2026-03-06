from pathlib import Path

import pandas as pd


ALERT_COLUMNS = [
    "case_id",
    "jurisdiction",
    "title",
    "status",
    "owner",
    "next_deadline",
    "days_left",
    "deadline_flag",
]


def build_alert_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return overdue and due soon cases in a simple report format."""
    if df is None:
        raise ValueError("DataFrame is required")

    missing_columns = [column for column in ALERT_COLUMNS if column not in df.columns]
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_list}")

    report_df = df[df["deadline_flag"].isin(["Overdue", "Due Soon"])].copy()
    report_df = report_df[ALERT_COLUMNS]
    return report_df.sort_values("next_deadline", ascending=True)


def save_alert_report(df: pd.DataFrame, output_path: str = "reports/alert_report.csv") -> str:
    """Save the alert report to CSV and return the output path."""
    if df is None:
        raise ValueError("DataFrame is required")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    return str(output_file)


def generate_notification_message(df: pd.DataFrame) -> str:
    """Create a short summary message for flagged cases."""
    if df is None:
        raise ValueError("DataFrame is required")

    if df.empty:
        return "No overdue or due soon IP cases at this time."

    overdue_count = int((df["deadline_flag"] == "Overdue").sum())
    due_soon_count = int((df["deadline_flag"] == "Due Soon").sum())
    total_flagged = int(len(df))

    return (
        f"Alert summary: {total_flagged} flagged cases, including "
        f"{overdue_count} overdue and {due_soon_count} due soon."
    )
