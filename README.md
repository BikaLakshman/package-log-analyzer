# Package Log Analyzer

A Python script that analyzes a campus mail room package log. It reports weekly volume for incoming and forwarded packages, how long packages wait before pickup, and which packages are overdue, and exports an Excel report with charts.

## What it does
- Counts **weekly incoming vs. forwarded** packages
- Calculates **average, median, and maximum days until pickup** by residence hall and carrier
- Flags **overdue packages** (waiting more than 5 days)
- Exports an Excel report (Weekly Volume, Pickup by Hall, Pickup by Carrier, Overdue) and two charts

## How to run
```
pip install pandas openpyxl matplotlib
python generate_sample_data.py   # creates fake package_log.csv
python analyze_packages.py       # creates the Excel report and charts
```

To use your own log, provide a CSV with columns:
`package_id, type, carrier, hall, date_received, date_completed`.

## Automating it
Schedule it to run weekly, e.g. Monday morning:
- Windows: Task Scheduler running `python analyze_packages.py`
- Mac/Linux: cron job such as `0 8 * * 1 python /path/to/analyze_packages.py`

## Tools
Python, pandas, openpyxl, matplotlib

*All data is randomly generated sample data. No real resident information is used.*
