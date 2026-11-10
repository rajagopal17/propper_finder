# propper_finder — ADB NGO project scraper

Scrapes ADB's Consultant Management System (`cms.adb.org`) for consulting
notices that NGOs (as firms) could realistically take up — education/training,
health and social protection, agriculture/forestry and rural development, and
multisector social projects — while filtering out capital-intensive,
construction-heavy notices. Results are stored in SQLite with no duplicates
across repeated runs.

## What it actually scrapes

`cms.adb.org` itself is ADB's public portal; the live consulting-opportunities
listing (Consulting Services Recruitment Notices, CSRN) lives on
`selfservice.adb.org`. The scraper drives that listing with these filters:

- **Consultant Type**: Firm only (not Individual).
- **Sector**: Education, Health and social protection, Agriculture and natural
  resources, Multisector.
- Within those, a keyword exclusion list drops construction/civil-works-heavy
  notices (see `src/adb_ngo_scraper/classify.py`).
- **Active** means the notice's deadline (Manila time) has not yet passed.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
playwright install chromium
```

## Run once

```bash
adb-ngo-scraper
```

Writes/updates `adb_ngo_notices.db` (table `notices`) in the project root and
logs to `logs/run_<timestamp>.log`. Each run appends newly found notices to
the same table and skips ones already seen (dedup on title + expertise +
published date), so repeated runs accumulate rather than overwrite. Use
`--headed` to watch the browser while debugging, `--db-path` / `--log-dir` /
`--max-pages` to override defaults.

## Run on a schedule

See [docs/TASK_SCHEDULER.md](docs/TASK_SCHEDULER.md) for registering it as a
recurring Windows Task Scheduler job.

## Schema (`notices` table)

`dedup_hash` (unique), `project_name`, `location` (raw ADB country code, e.g.
`BAN`, `REG`), `sector`, `expertise`, `consultant_type`,
`engagement_period_months`, `published_date`, `deadline`, `related_url`,
`scraped_at`.

Dedup key is a SHA256 hash of (project title + expertise + published date).
