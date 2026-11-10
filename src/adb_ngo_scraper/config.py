from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CSRN_URL = "https://selfservice.adb.org/OA_HTML/OA.jsp?OAFunc=XXCRS_CSRN_HOME_PAGE"

# Consultant Type facet: NGOs apply as organizations, not individual consultants.
CONSULTANT_TYPE_LABELS = ["Firm"]

# Sector facet: covers education/training, medical/social welfare, forestry/rural
# development, and cross-cutting social notices. Deliberately excludes Energy,
# Finance, Industry and trade, Public sector management, Transport/ICT, Water and
# other Municipal Infrastructure, and Uncategorized.
SECTOR_LABELS = [
    "Education",
    "Health and social protection",
    "Agriculture and natural resources",
    "Multisector",
]

DEFAULT_DB_PATH = REPO_ROOT / "data" / "adb_ngo_notices.db"
DEFAULT_LOG_DIR = REPO_ROOT / "logs"

# Safety cap on pagination loops regardless of what the site reports.
MAX_PAGES = 50

# Retry/backoff for flaky browser steps (page load, filter click, pagination).
RETRY_MAX_ATTEMPTS = 4
RETRY_BASE_DELAY_SECONDS = 2

# Politeness delay after each filter click / pagination click, letting the
# page's AJAX partial-page-render settle before we read the table.
ACTION_SETTLE_SECONDS = 1.5
