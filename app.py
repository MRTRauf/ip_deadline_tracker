import pandas as pd
import streamlit as st

from database import initialize_database, load_cases_from_db, save_cases
from deadline_utils import (
    add_deadline_metrics,
    filter_cases_by_flag,
    get_summary_counts,
    load_cases,
)


CSV_PATH = "data/sample_ip_cases.csv"
DISPLAY_COLUMNS = [
    "case_id",
    "jurisdiction",
    "title",
    "status",
    "owner",
    "filing_date",
    "next_deadline",
    "days_left",
    "deadline_flag",
]


st.set_page_config(page_title="IP Deadline Tracker", layout="wide")

st.title("IP Deadline Tracker & Automation Dashboard")
st.write(
    "A simple internal-tool prototype for monitoring patent and IP case deadlines, "
    "highlighting urgent work, and reviewing upcoming actions."
)


initialize_database()

csv_df = load_cases(CSV_PATH)
csv_df = add_deadline_metrics(csv_df, today="2026-03-12")
save_cases(csv_df)

db_df = load_cases_from_db()
df = add_deadline_metrics(db_df, today="2026-03-12")

summary = get_summary_counts(df)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Total Cases", summary["total_cases"])
metric_col2.metric("Overdue", summary["overdue"])
metric_col3.metric("Due Soon", summary["due_soon"])
metric_col4.metric("Upcoming", summary["upcoming"])

st.caption(
    "Deadline categories: Overdue (<0 days), Due Soon (0-7 days), "
    "Upcoming (8-30 days), On Track (>30 days)."
)


st.sidebar.header("Filters")

owner_options = ["All"] + sorted(df["owner"].dropna().unique().tolist())
jurisdiction_options = ["All"] + sorted(df["jurisdiction"].dropna().unique().tolist())
flag_options = ["All", "Overdue", "Due Soon", "Upcoming", "On Track"]

selected_owner = st.sidebar.selectbox("Owner", owner_options)
selected_jurisdiction = st.sidebar.selectbox("Jurisdiction", jurisdiction_options)
selected_flag = st.sidebar.selectbox("Deadline Flag", flag_options)


filtered_df = df.copy()

if selected_owner != "All":
    filtered_df = filtered_df[filtered_df["owner"] == selected_owner]

if selected_jurisdiction != "All":
    filtered_df = filtered_df[filtered_df["jurisdiction"] == selected_jurisdiction]

if selected_flag != "All":
    filtered_df = filtered_df[filtered_df["deadline_flag"] == selected_flag]

filtered_df = filtered_df.sort_values("next_deadline", ascending=True)


st.subheader("All Cases")
all_cases_display = filtered_df[DISPLAY_COLUMNS].copy()
all_cases_display["filing_date"] = all_cases_display["filing_date"].dt.strftime("%Y-%m-%d")
all_cases_display["next_deadline"] = all_cases_display["next_deadline"].dt.strftime("%Y-%m-%d")
st.dataframe(all_cases_display, use_container_width=True)

st.write(
    "Overdue and Due Soon cases are shown separately below because they are the most "
    "urgent and actionable categories for daily workflow monitoring."
)

st.subheader("Overdue Cases")
overdue_df = filter_cases_by_flag(filtered_df, "Overdue")
overdue_display = overdue_df[DISPLAY_COLUMNS].copy()
overdue_display["filing_date"] = overdue_display["filing_date"].dt.strftime("%Y-%m-%d")
overdue_display["next_deadline"] = overdue_display["next_deadline"].dt.strftime("%Y-%m-%d")
st.dataframe(overdue_display, use_container_width=True)

st.subheader("Due Soon Cases")
due_soon_df = filter_cases_by_flag(filtered_df, "Due Soon")
due_soon_display = due_soon_df[DISPLAY_COLUMNS].copy()
due_soon_display["filing_date"] = due_soon_display["filing_date"].dt.strftime("%Y-%m-%d")
due_soon_display["next_deadline"] = due_soon_display["next_deadline"].dt.strftime("%Y-%m-%d")
st.dataframe(due_soon_display, use_container_width=True)


st.subheader("Deadline Flag Overview")
flag_counts = filtered_df["deadline_flag"].value_counts().reindex(
    ["Overdue", "Due Soon", "Upcoming", "On Track"],
    fill_value=0,
)
st.bar_chart(flag_counts)


st.subheader("Export Filtered Data")
csv_bytes = filtered_df[DISPLAY_COLUMNS].to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered CSV",
    data=csv_bytes,
    file_name="filtered_ip_cases.csv",
    mime="text/csv",
)
