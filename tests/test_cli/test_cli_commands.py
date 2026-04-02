from pathlib import Path

from typer.testing import CliRunner

from redline.cli import app

REPO_ROOT = Path(__file__).parent.parent.parent
runner = CliRunner()


class TestLintCommand:
    def test_lint_passing_file_exits_zero(self):
        fixture = str(
            REPO_ROOT / "fixtures" / "passing" / "aml-policy-good.md"
        )
        result = runner.invoke(app, ["lint", fixture])
        assert result.exit_code == 0

    def test_lint_failing_file_exits_one(self):
        fixture = str(
            REPO_ROOT / "fixtures" / "failing" / "aml-policy-bad.md"
        )
        result = runner.invoke(app, ["lint", fixture])
        assert result.exit_code == 1

    def test_lint_nonexistent_file_exits_two(self):
        result = runner.invoke(app, ["lint", "/nonexistent/file.md"])
        assert result.exit_code == 2


class TestReportCommand:
    def test_report_json_output(self):
        fixture = str(
            REPO_ROOT / "fixtures" / "failing" / "aml-policy-bad.md"
        )
        result = runner.invoke(app, ["report", fixture, "--format", "json"])
        assert result.exit_code == 0
        assert '"findings"' in result.stdout

    def test_report_markdown_output(self):
        fixture = str(
            REPO_ROOT / "fixtures" / "failing" / "aml-policy-bad.md"
        )
        result = runner.invoke(
            app, ["report", fixture, "--format", "markdown"]
        )
        assert result.exit_code == 0
        assert "## Findings" in result.stdout


class TestRegulationsCommand:
    def test_regulations_list(self):
        result = runner.invoke(app, ["regulations", "list"])
        assert result.exit_code == 0
        assert "BSA-SAR" in result.stdout

    def test_regulations_info(self):
        result = runner.invoke(app, ["regulations", "info", "BSA-SAR"])
        assert result.exit_code == 0
        assert "FinCEN" in result.stdout


class TestInitCommand:
    def test_init_creates_config(self, tmp_path):
        result = runner.invoke(app, ["init", "--directory", str(tmp_path)])
        assert result.exit_code == 0
        config_file = tmp_path / ".redline.yml"
        assert config_file.exists()
