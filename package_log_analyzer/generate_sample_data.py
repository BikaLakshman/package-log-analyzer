"""Creates a made-up package log (package_log.csv). All data is fake - no real residents."""
import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(7)
WEEKS = 8
carriers = ["USPS", "UPS", "FedEx", "Amazon"]
halls = ["Hall A", "Hall B", "Hall C", "Hall D"]
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = today - timedelta(weeks=WEEKS)

rows, pid = [], 1
for week in range(WEEKS):
    week_start = start + timedelta(weeks=week)
    # incoming packages: 60-120 per week, forwarded packages: 10-20 per week
    for kind, count in (("Incoming", random.randint(60, 120)), ("Forwarded", random.randint(10, 20))):
        for _ in range(count):
            received = week_start + timedelta(days=random.randint(0, 6), hours=random.randint(9, 16))
            if kind == "Incoming":
                picked = received + timedelta(days=random.choice([0, 0, 1, 1, 2, 3, 4, 6, 9]))
                # a few recent packages are still waiting
                if picked > today or random.random() < 0.01:
                    picked = pd.NaT
            else:
                picked = received + timedelta(days=1)   # forwarded = shipped out next day
                if picked > today:
                    picked = pd.NaT
            rows.append({
                "package_id": f"PKG{pid:05d}",
                "type": kind,
                "carrier": random.choice(carriers),
                "hall": random.choice(halls) if kind == "Incoming" else "Campus Out",
                "date_received": received,
                "date_completed": picked,   # pickup date (incoming) or ship date (forwarded)
            })
            pid += 1

pd.DataFrame(rows).to_csv("package_log.csv", index=False)
print(f"Created package_log.csv with {len(rows)} packages")
