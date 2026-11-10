import re

# Broad capital-intensive / construction exclusion list, matched case-insensitively
# with word boundaries against the notice's title + expertise text.
#
# Caveat: "building" is included per the approved broad list (it catches "school
# building construction"), but it also matches the common, clearly NGO-relevant
# phrase "capacity building". If that turns out to drop too many good notices,
# remove "building" from this list (or special-case "capacity building") and
# re-run.
EXCLUDE_KEYWORDS = [
    "construction",
    "civil works",
    "build",
    "building",
    "bridge",
    "road",
    "highway",
    "bypass",
    "plant",
    "pipeline",
    "irrigation works",
    "drainage works",
    "dam",
    "power transmission",
    "facility design",
]

_EXCLUDE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in EXCLUDE_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def is_excluded(title: str, expertise: str) -> bool:
    """True if the notice looks capital-intensive/construction-heavy and should
    be dropped, based on its title and expertise text."""
    text = f"{title} {expertise}"
    return _EXCLUDE_PATTERN.search(text) is not None
