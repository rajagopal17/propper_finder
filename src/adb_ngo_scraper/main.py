import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .scraper import scrape_once


def _setup_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape ADB CMS consulting notices suitable for NGOs into SQLite."
    )
    parser.add_argument("--db-path", type=Path, default=config.DEFAULT_DB_PATH)
    parser.add_argument("--log-dir", type=Path, default=config.DEFAULT_LOG_DIR)
    parser.add_argument("--max-pages", type=int, default=config.MAX_PAGES)
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run with a visible browser window instead of headless (for debugging).",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    log_file = _setup_logging(args.log_dir)
    logger = logging.getLogger(__name__)
    logger.info("Starting ADB NGO scraper run; db=%s log=%s", args.db_path, log_file)

    try:
        counts = scrape_once(args.db_path, headless=not args.headed, max_pages=args.max_pages)
    except Exception:
        logger.exception("Scraper run failed")
        return 1

    # A run that finds zero new notices is a normal outcome, not a failure.
    if counts["inserted"] == 0:
        logger.info("No new notices this run (duplicate=%d, excluded=%d, inactive=%d).",
                     counts["duplicate"], counts["excluded"], counts["inactive"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
