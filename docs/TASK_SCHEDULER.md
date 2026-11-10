# Running on a schedule (Windows Task Scheduler)

The scraper is a one-shot script: it runs, scrapes, writes to SQLite, and exits.
Scheduling is handled by Windows Task Scheduler, not by the script itself.

## 1. One-time setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
playwright install chromium
```

## 2. Verify it runs manually first

```bash
adb-ngo-scraper
```

This writes to `data/adb_ngo_notices.db` and logs to `logs/run_<timestamp>.log`.
Confirm it exits with code 0 and the log shows a "Run complete" line before
scheduling it.

## 3. Register the scheduled task

Open Task Scheduler → Create Task:

- **General**: name it `ADB NGO Scraper`; "Run whether user is logged on or not".
- **Triggers**: New → Daily, repeat every 6 hours (or your preferred interval)
  for a duration of 1 day, indefinitely.
- **Actions**: New → Start a program:
  - Program/script: full path to `.venv\Scripts\python.exe` in this project.
  - Add arguments: `-m adb_ngo_scraper.main`
  - Start in: the full path to this project's root directory (so the default
    `data/` and `logs/` paths resolve correctly).
- **Conditions**: uncheck "Start the task only if the computer is on AC power"
  if this runs on a laptop.
- **Settings**: check "If the task fails, restart every" a few minutes, up to a
  few attempts — the script already retries transient failures internally, but
  this catches a crashed Playwright/browser install.

## Exit codes

- `0`: run completed (a run that found zero new notices still exits `0` — that's
  a normal outcome, not a failure).
- `1`: unrecoverable error after retries were exhausted. Check the latest file
  in `logs/` for the traceback.
