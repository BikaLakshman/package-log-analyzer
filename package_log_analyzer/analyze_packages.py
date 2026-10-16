"""
Package Log Analyzer
Reads package_log.csv and reports weekly volume (incoming vs forwarded),
how long packages wait before pickup, and which packages are overdue.
Outputs an Excel report and charts.

Run:  python analyze_packages.py
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

INPUT_FILE = "package_log.csv"
OUTPUT_FILE = "package_report.xlsx"
OVERDUE_DAYS = 5   # an incoming package waiting longer than this is "overdue"


def load_data(path):
    df = pd.read_csv(path, parse_dates=["date_received", "date_completed"])
    df["week"] = df["date_received"].dt.to_period("W").dt.start_time
    # days between arrival and pickup/ship date (blank if not completed yet)
    df["days_waiting"] = (df["date_completed"] - df["date_received"]).dt.total_seconds() / 86400
    return df


def weekly_volume(df):
    return (df.pivot_table(index="week", columns="type", values="package_id",
                           aggfunc="count", fill_value=0)
              .assign(Total=lambda x: x.sum(axis=1)))


def pickup_stats(df):
    incoming = df[(df["type"] == "Incoming") & df["date_completed"].notna()]
    by_hall = incoming.groupby("hall")["days_waiting"].agg(["count", "mean", "median", "max"]).round(1)
    by_carrier = incoming.groupby("carrier")["days_waiting"].agg(["count", "mean", "max"]).round(1)
    return by_hall, by_carrier


def overdue_packages(df, today):
    waiting = df[(df["type"] == "Incoming") & df["date_completed"].isna()].copy()
    waiting["days_waiting"] = ((today - waiting["date_received"]).dt.total_seconds() / 86400).round(1)
    return (waiting[waiting["days_waiting"] > OVERDUE_DAYS]
            .sort_values("days_waiting", ascending=False)
            [["package_id", "carrier", "hall", "date_received", "days_waiting"]])


def make_charts(volume, by_hall):
    labels = [d.strftime("%b %d") for d in volume.index]   # week start dates as text
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(labels, volume["Incoming"], label="Incoming", color="#2980b9")
    ax.bar(labels, volume["Forwarded"], bottom=volume["Incoming"], label="Forwarded", color="#e67e22")
    ax.set_title("Weekly Package Volume")
    ax.set_xlabel("Week starting")
    ax.set_ylabel("Packages")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("weekly_volume.png", dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(by_hall.index, by_hall["mean"], color="#27ae60")
    ax.set_title("Average Days Until Pickup by Hall")
    ax.set_ylabel("Days")
    plt.tight_layout()
    plt.savefig("pickup_time_by_hall.png", dpi=150)
    plt.close()


def write_excel(volume, by_hall, by_carrier, overdue, path):
    from openpyxl.styles import Font
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        volume.to_excel(writer, sheet_name="Weekly Volume")
        by_hall.to_excel(writer, sheet_name="Pickup by Hall")
        by_carrier.to_excel(writer, sheet_name="Pickup by Carrier")
        overdue.to_excel(writer, sheet_name="Overdue", index=False)
        for ws in writer.sheets.values():
            for cell in ws[1]:
                cell.font = Font(bold=True)
            for col in ws.columns:
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = width + 3
            ws.freeze_panes = "A2"


def main():
    today = pd.Timestamp(datetime.now())
    df = load_data(INPUT_FILE)
    volume = weekly_volume(df)
    by_hall, by_carrier = pickup_stats(df)
    overdue = overdue_packages(df, today)

    make_charts(volume, by_hall)
    write_excel(volume, by_hall, by_carrier, overdue, OUTPUT_FILE)

    print(f"Report saved: {OUTPUT_FILE}")
    print(f"Average weekly incoming: {volume['Incoming'].mean():.0f}")
    print(f"Average weekly forwarded: {volume['Forwarded'].mean():.0f}")
    print(f"Average days to pickup: {df[df['type']=='Incoming']['days_waiting'].mean():.1f}")
    print(f"Overdue packages (> {OVERDUE_DAYS} days): {len(overdue)}")


if __name__ == "__main__":
    main()
