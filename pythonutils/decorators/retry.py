from functools import wraps
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class NoTriesRemaining(Exception):
    """ thrown when `retry` has run out of attempts """
    pass


def retry(retryable_vals=None, retryable_exceptions=None, max_attempts=5):
    """a decorator which allows for retrying a function on failure - where failure can be defined in one of two ways, either
    as a bad return result or as a retryable exception being raised - up to `max_attempts` times
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            i = 0
            last_caught_exc = None

            while i < max_attempts:
                try:
                    fn_result = fn(*args, **kwargs)

                    if not retryable_vals or fn_result not in retryable_vals:
                        return fn_result
                except tuple(retryable_exceptions or []) as caught_exc:
                    logger.debug("**a retryable exception has been caught**")
                    last_caught_exc = caught_exc

                i += 1

            # if the last run resulted in an retryable exception, but we have no tries remaining, re-raise the exception
            if last_caught_exc:
                raise last_caught_exc

            raise NoTriesRemaining()

        return decorator

    return wrapper