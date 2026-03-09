import pandas as pd
import streamlit as st

from database import initialize_database, load_cases_from_db, save_cases
from deadline_utils import (
    add_deadline_metrics,
    filter_cases_by_flag,
    get_summary_counts,
    load_cases,
)
from notifier import (
    build_alert_report,
    generate_notification_message,
    save_alert_report,
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

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e4e7ec;
        border-radius: 0.75rem;
        padding: 0.85rem 1rem;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
    }
    [data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {
        background: #fef3f2;
        border-color: #f3d0cc;
    }
    [data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {
        background: #fff8e8;
        border-color: #ead8b5;
    }
    [data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {
        background: #eff8ff;
        border-color: #bfdcff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div[data-baseweb="select"] > div {
        background-color: #f8fafc;
        border: 1px solid #d0d5dd;
        border-radius: 0.5rem;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
        font-weight: 600;
        color: #344054;
    }
    </style>
    """,
    unsafe_allow_html=True,
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

alert_report_df = build_alert_report(filtered_df)
overdue_count = int((alert_report_df["deadline_flag"] == "Overdue").sum())
due_soon_count = int((alert_report_df["deadline_flag"] == "Due Soon").sum())


st.subheader("Alert Center")

st.markdown(
    """
    <style>
    .alert-summary {
        border: 1px solid #e6dcc2;
        border-left: 4px solid #b7791f;
        background: #faf6e8;
        border-radius: 0.5rem;
        padding: 0.8rem 1rem;
        margin-bottom: 0.75rem;
        color: #5f4b1b;
    }
    .alert-summary.alert-summary-overdue {
        border: 1px solid #f3d0cc;
        border-left: 4px solid #d92d20;
        background: #fef3f2;
        color: #912018;
    }
    .alert-summary.alert-summary-overdue strong {
        color: #7a271a;
    }
    .alert-summary.alert-summary-due-soon {
        border: 1px solid #ead8b5;
        border-left: 4px solid #c47f00;
        background: #fff8e8;
        color: #7a4b00;
    }
    .alert-summary strong {
        display: block;
        margin-bottom: 0.15rem;
        color: #3f3520;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if overdue_count > 0:
    st.markdown(
        f"""
        <div class="alert-summary alert-summary-overdue">
            <strong>Immediate attention needed</strong>
            {overdue_count} overdue case(s) are past the deadline in the current view.
        </div>
        """,
        unsafe_allow_html=True,
    )
elif due_soon_count > 0:
    st.markdown(
        f"""
        <div class="alert-summary alert-summary-due-soon">
            <strong>Upcoming deadlines to review</strong>
            {due_soon_count} case(s) are due soon and should be reviewed this week.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.success("There are no urgent deadline alerts in the current view.")

if not alert_report_df.empty:
    urgent_cases_display = alert_report_df.copy()
    urgent_cases_display["next_deadline"] = urgent_cases_display["next_deadline"].dt.strftime("%Y-%m-%d")
    urgent_cases_styler = (
        urgent_cases_display.style
        .format({"days_left": "{:.0f}"})
        .set_properties(
            subset=["case_id", "jurisdiction", "title", "status", "owner", "next_deadline", "days_left", "deadline_flag"],
            **{"padding": "0.45rem 0.55rem"}
        )
        .set_properties(
            subset=["title"],
            **{"font-weight": "500"}
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#f5f7fa"),
                        ("color", "#475467"),
                        ("font-weight", "600"),
                        ("letter-spacing", "0.01em"),
                        ("border-bottom", "1px solid #d0d5dd"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("border-bottom", "1px solid #eaecf0"),
                    ],
                },
            ]
        )
    )

    def style_deadline_flag(value):
        if value == "Overdue":
            return "background-color: #fff1f0; color: #b42318; font-weight: 600;"
        if value == "Due Soon":
            return "background-color: #fff7e8; color: #b54708; font-weight: 600;"
        return ""

    def style_urgent_row(row):
        if row["deadline_flag"] == "Overdue":
            return ["background-color: #fffafa;"] * len(row)
        if row["deadline_flag"] == "Due Soon":
            return ["background-color: #fffdf7;"] * len(row)
        return [""] * len(row)

    urgent_cases_styler = (
        urgent_cases_styler
        .apply(style_urgent_row, axis=1)
        .map(style_deadline_flag, subset=["deadline_flag"])
    )

    st.dataframe(urgent_cases_styler, use_container_width=True)

st.caption("Notification Preview")
st.write(generate_notification_message(alert_report_df))

col1, col2, col3 = st.columns([1,1,6])

with col1:
    if st.button("Generate Alert Report",  type="primary"):
        saved_report_path = save_alert_report(alert_report_df)

with col2:
    st.download_button(
        "Download Alert Report",
        data=alert_report_df.to_csv(index=False),
        file_name="alert_report.csv",
        mime="text/csv"
    )

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
