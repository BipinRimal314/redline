import tempfile
from pathlib import Path

from redline.config import RedlineConfig, load_config, DEFAULT_CONFIG


class TestDefaultConfig:
    def test_has_default_regulations(self):
        assert len(DEFAULT_CONFIG["regulations"]) > 0

    def test_default_output_format_is_json(self):
        assert DEFAULT_CONFIG["output"]["format"] == "json"

    def test_default_ai_disabled(self):
        assert DEFAULT_CONFIG["ai"]["enabled"] is False


class TestLoadConfig:
    def test_loads_from_yaml_file(self):
        content = """
regulations:
  - bsa-aml

output:
  format: markdown
  directory: reports

ai:
  enabled: false
  confidence_threshold: 0.8
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(content)
            f.flush()
            config = load_config(Path(f.name))

        assert config.regulations == ["bsa-aml"]
        assert config.output_format == "markdown"
        assert config.ai_enabled is False
        assert config.confidence_threshold == 0.8

    def test_uses_defaults_when_no_file(self):
        config = load_config(Path("/nonexistent/.redline.yml"))
        assert config.regulations == DEFAULT_CONFIG["regulations"]
        assert config.output_format == "json"

    def test_merges_partial_config_with_defaults(self):
        content = """
regulations:
  - bsa-aml
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write(content)
            f.flush()
            config = load_config(Path(f.name))

        assert config.regulations == ["bsa-aml"]
        assert config.output_format == "json"  # default
        assert config.ai_enabled is False  # default
