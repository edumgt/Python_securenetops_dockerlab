from __future__ import annotations
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

def retryable(
    attempts: int = 3,
    min_s: float = 0.2,
    max_s: float = 2.0,
    exception_types: tuple[type[BaseException], ...] = (Exception,),
):
    return retry(
        reraise=True,
        stop=stop_after_attempt(attempts),
        wait=wait_exponential_jitter(initial=min_s, max=max_s),
        retry=retry_if_exception_type(exception_types),
    )
