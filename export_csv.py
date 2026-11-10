import csv
import sqlite3
import sys
from pathlib import Path

db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("adb_ngo_notices.db")
csv_path = Path(sys.argv[2]) if len(sys.argv) > 2 else db_path.with_suffix(".csv")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM notices").fetchall()

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(list(row))

print(f"Wrote {len(rows)} rows to {csv_path}")
