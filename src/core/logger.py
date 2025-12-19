from __future__ import annotations
import logging
import os
import re
from typing import Iterable, List

DEFAULT_MASK_KEYS = ["token", "authorization", "password", "secret", "api_key"]

def _build_mask_patterns(extra_secrets: Iterable[str] | None = None) -> List[re.Pattern]:
    patterns: List[re.Pattern] = []
    for k in DEFAULT_MASK_KEYS:
        patterns.append(re.compile(rf'({k}\s*[:=]\s*)([^\s,;]+)', re.IGNORECASE))
    if extra_secrets:
        for s in extra_secrets:
            if not s:
                continue
            patterns.append(re.compile(re.escape(s)))
    return patterns

class MaskingFormatter(logging.Formatter):
    def __init__(self, fmt: str, extra_secrets: Iterable[str] | None = None):
        super().__init__(fmt)
        self.patterns = _build_mask_patterns(extra_secrets)

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for p in self.patterns:
            # key=value 형태 마스킹
            msg = p.sub(lambda m: m.group(1) + "***", msg) if p.groups >= 2 else p.sub("***", msg)
        return msg

def get_logger(name: str = "securenetops") -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    h = logging.StreamHandler()
    extra_secrets = [os.getenv("CONTROLLER_API_TOKEN", "")]
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    h.setFormatter(MaskingFormatter(fmt, extra_secrets=extra_secrets))
    logger.addHandler(h)
    logger.propagate = False
    return logger
