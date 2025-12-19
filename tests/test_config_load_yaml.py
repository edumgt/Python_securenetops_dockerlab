from src.core.config import load_yaml, ConfigError
from pathlib import Path

def test_load_yaml_missing(tmp_path: Path):
    try:
        load_yaml(tmp_path / "missing.yml")
        assert False, "should raise"
    except ConfigError:
        assert True
