from src.core.logger import MaskingFormatter
import logging

def test_masking_formatter_masks_token():
    fmt = "%(message)s"
    formatter = MaskingFormatter(fmt, extra_secrets=["secret123"])
    r = logging.LogRecord("x", logging.INFO, __file__, 1, "token=secret123", args=(), exc_info=None)
    out = formatter.format(r)
    assert "***" in out
    assert "secret123" not in out
