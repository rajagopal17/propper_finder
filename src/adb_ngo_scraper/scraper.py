import logging
from pathlib import Path

from playwright.sync_api import sync_playwright

from . import browser, classify, config, db, parser
from .retry import with_retry

logger = logging.getLogger(__name__)

_goto = with_retry(lambda page: page.goto(config.CSRN_URL, wait_until="networkidle", timeout=30000))
_ensure_checked = with_retry(browser.ensure_checked)
_extract_rows = with_retry(browser.extract_rows)
_click_next_page = with_retry(browser.click_next_page)


def _process_row(conn, row: dict) -> str:
    title = row["title"]
    expertise = row["expertise"]

    if not classify.is_included(title, expertise):
        return "not_relevant"

    if classify.is_excluded(title, expertise):
        return "excluded"

    deadline_dt = parser.parse_deadline(row["deadline"])
    if deadline_dt is not None and not parser.is_active(deadline_dt):
        return "inactive"

    dedup_hash = parser.compute_dedup_hash(title, expertise, row["published"])
    notice = {
        "dedup_hash": dedup_hash,
        "project_name": title,
        "location": parser.extract_location(title),
        "sector": None,  # not exposed per-row by the site; only as a filter facet
        "expertise": expertise,
        "consultant_type": row["consultantType"],
        "engagement_period_months": row["engagementMonths"],
        "published_date": parser.parse_published_date(row["published"]),
        "deadline": deadline_dt.isoformat() if deadline_dt else row["deadline"],
        "related_url": row["href"],
    }
    inserted = db.upsert_notice(conn, notice)
    return "inserted" if inserted else "duplicate"


def scrape_once(db_path: Path, headless: bool = True, max_pages: int = config.MAX_PAGES) -> dict:
    conn = db.get_connection(db_path)
    db.init_db(conn)

    counts = {
        "inserted": 0,
        "duplicate": 0,
        "excluded": 0,
        "inactive": 0,
        "not_relevant": 0,
        "pages": 0,
    }

    with sync_playwright() as p:
        pw_browser = p.chromium.launch(headless=headless)
        page = pw_browser.new_page()
        try:
            _goto(page)

            for label in config.CONSULTANT_TYPE_LABELS:
                _ensure_checked(page, label)

            page_num = 1
            while True:
                rows = _extract_rows(page)
                for row in rows:
                    outcome = _process_row(conn, row)
                    counts[outcome] += 1
                counts["pages"] = page_num

                if page_num >= max_pages:
                    logger.warning("Hit max_pages safety cap (%d); stopping pagination", max_pages)
                    break

                has_next = _click_next_page(page)
                if not has_next:
                    break
                page_num += 1
        finally:
            pw_browser.close()

    conn.close()
    logger.info(
        "Run complete: inserted=%d duplicate=%d excluded=%d inactive=%d not_relevant=%d pages=%d",
        counts["inserted"],
        counts["duplicate"],
        counts["excluded"],
        counts["inactive"],
        counts["not_relevant"],
        counts["pages"],
    )
    return counts
