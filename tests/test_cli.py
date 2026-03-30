import shutil
from pathlib import Path

from click.testing import CliRunner

from python_naming_linter.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_check_with_violations(tmp_path, monkeypatch):
    config_content = """\
rules:
  - name: attribute-matches-type
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }

  - name: exception-naming
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }

apply:
  - name: domain-layer
    rules: [attribute-matches-type]
    modules: contexts.*.domain

  - name: global-exceptions
    rules: [exception-naming]
    modules: "**"
"""
    config_file = tmp_path / ".python-naming-linter.yaml"
    config_file.write_text(config_content)

    src = FIXTURES / "sample_project" / "contexts"
    dst = tmp_path / "contexts"
    shutil.copytree(src, dst)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 1
    assert "violation" in result.output.lower()


def test_cli_check_no_violations(tmp_path, monkeypatch):
    config_content = """\
rules:
  - name: pkg-case
    type: package
    naming: { case: snake_case }

apply:
  - name: all
    rules: [pkg-case]
    modules: "**"
"""
    config_file = tmp_path / ".python-naming-linter.yaml"
    config_file.write_text(config_content)

    pkg = tmp_path / "my_package"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 0
    assert "No violations found." in result.output


def test_cli_check_config_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 2


def test_cli_check_explicit_config_not_found():
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--config", "nonexistent.yaml"])
    assert result.exit_code == 2
    assert "not found" in result.output.lower()


def test_cli_check_with_include_exclude(tmp_path, monkeypatch):
    config_content = """\
include:
  - src

exclude:
  - src/generated/**

rules:
  - name: class-case
    type: class
    naming: { case: PascalCase }

apply:
  - name: all
    rules: [class-case]
    modules: "**"
"""
    config_file = tmp_path / ".python-naming-linter.yaml"
    config_file.write_text(config_content)

    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "app.py").write_text("class my_bad_class: pass\n")

    generated = tmp_path / "src" / "generated"
    generated.mkdir()
    (generated / "__init__.py").write_text("")
    (generated / "models.py").write_text("class another_bad_class: pass\n")

    other = tmp_path / "other"
    other.mkdir()
    (other / "__init__.py").write_text("")
    (other / "app.py").write_text("class also_bad: pass\n")

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["check"])
    assert result.exit_code == 1
    assert "src/app.py" in result.output
    assert "generated" not in result.output
    assert "other" not in result.output
