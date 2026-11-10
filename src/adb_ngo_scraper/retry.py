import logging
import time
from functools import wraps

from . import config

logger = logging.getLogger(__name__)


def with_retry(func):
    """Retries a flaky step (page load, filter click, pagination, extraction)
    with exponential backoff. Re-raises the last exception if all attempts
    fail, so the caller can treat it as a genuine failure."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        last_exc = None
        for attempt in range(1, config.RETRY_MAX_ATTEMPTS + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - deliberately broad, retried
                last_exc = exc
                logger.warning(
                    "%s failed (attempt %d/%d): %s",
                    func.__name__,
                    attempt,
                    config.RETRY_MAX_ATTEMPTS,
                    exc,
                )
                if attempt < config.RETRY_MAX_ATTEMPTS:
                    delay = config.RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                    time.sleep(delay)
        raise last_exc

    return wrapper
