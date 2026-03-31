from pathlib import Path

import pytest

from python_naming_linter.config import find_config, load_config

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_yaml_config():
    config = load_config(FIXTURES / "sample_config.yaml")
    assert len(config.rules) == 3
    assert len(config.apply) == 2


def test_load_yaml_rule_fields():
    config = load_config(FIXTURES / "sample_config.yaml")
    rule = config.rules[0]
    assert rule.name == "attribute-matches-type"
    assert rule.type == "variable"
    assert rule.filter == {"target": "attribute"}
    assert rule.naming == {"source": "type_annotation", "transform": "snake_case"}
    assert rule.description is None


def test_load_yaml_apply_fields():
    config = load_config(FIXTURES / "sample_config.yaml")
    apply = config.apply[0]
    assert apply.name == "domain-layer"
    assert apply.rules == ["attribute-matches-type", "bool-method-prefix"]
    assert apply.modules == "contexts.*.domain"


def test_load_yaml_rule_with_description(tmp_path):
    config_content = """\
rules:
  - name: bool-method-prefix
    description: "Bool-returning functions must use a semantic prefix"
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }
apply:
  - name: all
    rules: [bool-method-prefix]
    modules: "**"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.rules[0].description == (
        "Bool-returning functions must use a semantic prefix"
    )


def test_load_yaml_with_include_exclude(tmp_path):
    config_content = """\
include:
  - src/**
exclude:
  - src/generated/**
rules:
  - name: test
    type: variable
    naming: { case: snake_case }
apply:
  - name: all
    rules: [test]
    modules: "**"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.include == ["src/**"]
    assert config.exclude == ["src/generated/**"]


def test_load_yaml_without_include_exclude():
    config = load_config(FIXTURES / "sample_config.yaml")
    assert config.include is None
    assert config.exclude is None


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yaml"))


def test_find_config_yaml_in_cwd(tmp_path, monkeypatch):
    (tmp_path / ".python-naming-linter.yaml").write_text("rules: []\napply: []\n")
    monkeypatch.chdir(tmp_path)
    assert find_config() == tmp_path / ".python-naming-linter.yaml"


def test_find_config_yaml_in_parent(tmp_path, monkeypatch):
    (tmp_path / ".python-naming-linter.yaml").write_text("rules: []\napply: []\n")
    child = tmp_path / "sub"
    child.mkdir()
    monkeypatch.chdir(child)
    assert find_config() == tmp_path / ".python-naming-linter.yaml"


def test_find_config_pyproject_toml(tmp_path, monkeypatch):
    toml_content = "[tool.python-naming-linter]\nrules = []\napply = []\n"
    (tmp_path / "pyproject.toml").write_text(toml_content)
    monkeypatch.chdir(tmp_path)
    assert find_config() == tmp_path / "pyproject.toml"


def test_find_config_yaml_preferred_over_toml(tmp_path, monkeypatch):
    (tmp_path / ".python-naming-linter.yaml").write_text("rules: []\napply: []\n")
    toml_content = "[tool.python-naming-linter]\nrules = []\napply = []\n"
    (tmp_path / "pyproject.toml").write_text(toml_content)
    monkeypatch.chdir(tmp_path)
    assert find_config() == tmp_path / ".python-naming-linter.yaml"


def test_find_config_not_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert find_config() is None


def test_find_config_skips_pyproject_without_section(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text("[tool.other]\nfoo = 1\n")
    monkeypatch.chdir(tmp_path)
    assert find_config() is None


@pytest.mark.parametrize(
    "name",
    [
        "attribute-matches-type",
        "bool_method",
        "rule1",
        "My-Rule_2",
        "rule.name",
        "shared.domain",
    ],
)
def test_valid_rule_names(tmp_path, name):
    config_content = f"""\
rules:
  - name: {name}
    type: variable
    naming: {{case: snake_case}}
apply:
  - name: all
    rules: [{name}]
    modules: "**"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    config = load_config(config_file)
    assert config.rules[0].name == name


@pytest.mark.parametrize(
    "name",
    ["my rule", "rule!name", "rule name 123", "rule@name"],
)
def test_invalid_rule_names(tmp_path, name):
    config_content = f"""\
rules:
  - name: "{name}"
    type: variable
    naming: {{case: snake_case}}
apply:
  - name: all
    rules: ["{name}"]
    modules: "**"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    with pytest.raises(ValueError, match="Invalid rule name"):
        load_config(config_file)
