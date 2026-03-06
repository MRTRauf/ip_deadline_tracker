# IP Deadline Tracker

## Project Overview
IP Deadline Tracker is a small prototype that demonstrates how lightweight data tools can support Intellectual Property (IP) workflow monitoring. It loads patent/IP case data from CSV, stores it in SQLite, calculates deadline urgency, and presents the results in a simple Streamlit dashboard.

The project is designed as an internal-tool style demo: practical, readable, and easy to explain in an interview or portfolio setting.

## Problem Motivation
IP teams often manage multiple cases across jurisdictions, each with important filing and prosecution deadlines. Even in a small workflow, it is useful to quickly answer questions such as:

- Which cases are already overdue?
- Which deadlines need attention this week?
- Which cases are coming up next?
- How can teams filter cases by owner or jurisdiction?

This prototype shows how Python, Pandas, SQLite, and Streamlit can be combined to create a simple operational dashboard for deadline monitoring.

## Features
- Load IP case data from a CSV dataset
- Store case records in SQLite
- Calculate deadline urgency using `days_left`
- Classify deadlines into business-friendly categories
- Display results in a Streamlit dashboard
- Highlight urgent cases separately
- Filter by owner
- Filter by jurisdiction
- Filter by deadline category
- Export filtered results to CSV

## Deadline Categories
The dashboard uses the following deadline logic:

- `Overdue`: deadline has already passed (`days_left < 0`)
- `Due Soon`: deadline within the next 7 days
- `Upcoming`: deadline within the next 8-30 days
- `On Track`: deadline more than 30 days away

The dashboard highlights `Overdue` and `Due Soon` cases separately because these are the most urgent and actionable categories for IP operations. The other categories are mainly useful for forward-looking monitoring and planning.

## Project Structure
```text
IP_DEADLINE_TRACKER/
├── app.py
├── deadline_utils.py
├── database.py
├── notifier.py
├── requirements.txt
├── data/
│   └── sample_ip_cases.csv
```

## How to Run the Project
Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

## Example Dashboard
The dashboard provides:

- top-level case summary metrics
- a full case table
- urgent case sections for `Overdue` and `Due Soon`
- deadline category overview chart
- filtering by owner
- filtering by jurisdiction
- filtering by deadline category
- CSV export of filtered results

Screenshot placeholder:

```text
[ Add dashboard screenshot here ]
```

## Future Improvements
- Add file upload support for user-provided CSV data
- Add automated notification/report generation from flagged cases
- Add simple trend views for deadline workload over time
- Add validation feedback for missing or malformed input data
- Expand the dataset and business rules for more realistic IP workflows
