from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests

from .logger import get_logger
from .retry import retryable

log = get_logger(__name__)

class HttpError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, payload: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

@dataclass
class HttpClient:
    base_url: str
    token: Optional[str] = None
    timeout_s: float = 3.0

    def _headers(self) -> Dict[str, str]:
        h = {"accept": "application/json"}
        if self.token:
            h["authorization"] = f"Bearer {self.token}"
        return h

    @retryable(attempts=3, exception_types=(requests.RequestException,))
    def request(self, method: str, path: str, json: Any | None = None, timeout_s: float | None = None) -> Any:
        url = self.base_url.rstrip("/") + path
        t = timeout_s if timeout_s is not None else self.timeout_s
        log.info(f"HTTP {method} {url}")
        try:
            r = requests.request(method, url, headers=self._headers(), json=json, timeout=t)
        except requests.RequestException as e:
            log.warning(f"HTTP error: {e}")
            raise

        if r.status_code >= 400:
            try:
                payload = r.json()
            except Exception:
                payload = r.text
            raise HttpError(f"HTTP {r.status_code} {method} {path}", status_code=r.status_code, payload=payload)
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        return r.text
