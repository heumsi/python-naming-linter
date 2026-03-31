from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_VALID_RULE_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


@dataclass
class Rule:
    name: str
    type: str
    naming: dict
    filter: dict = field(default_factory=dict)


@dataclass
class Apply:
    name: str
    rules: list[str]
    modules: str


@dataclass
class Config:
    rules: list[Rule]
    apply: list[Apply]
    include: list[str] | None = None
    exclude: list[str] | None = None


def _validate_rule_name(name: str) -> None:
    if not _VALID_RULE_NAME_RE.match(name):
        raise ValueError(
            f"Invalid rule name '{name}'. Rule names must match [a-zA-Z0-9_-]+"
        )


def _parse_rules(rules_data: list[dict]) -> list[Rule]:
    rules = []
    for r in rules_data:
        _validate_rule_name(r["name"])
        rules.append(
            Rule(
                name=r["name"],
                type=r["type"],
                naming=r.get("naming", {}),
                filter=r.get("filter", {}),
            )
        )
    return rules


def _parse_apply(apply_data: list[dict]) -> list[Apply]:
    entries = []
    for a in apply_data:
        entries.append(
            Apply(
                name=a["name"],
                rules=a["rules"],
                modules=a["modules"],
            )
        )
    return entries


def _load_yaml(path: Path) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(
        rules=_parse_rules(data.get("rules", [])),
        apply=_parse_apply(data.get("apply", [])),
        include=data.get("include"),
        exclude=data.get("exclude"),
    )


def _load_toml(path: Path) -> dict:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(path, "rb") as f:
        return tomllib.load(f)


def _load_pyproject_toml(path: Path) -> Config:
    data = _load_toml(path)
    tool_config = data["tool"]["python-naming-linter"]
    return Config(
        rules=_parse_rules(tool_config.get("rules", [])),
        apply=_parse_apply(tool_config.get("apply", [])),
        include=tool_config.get("include"),
        exclude=tool_config.get("exclude"),
    )


def _has_pnl_section(path: Path) -> bool:
    data = _load_toml(path)
    return "python-naming-linter" in data.get("tool", {})


_CONFIG_FILENAMES = [".python-naming-linter.yaml", "pyproject.toml"]


def find_config() -> Path | None:
    current = Path.cwd().resolve()
    while True:
        for name in _CONFIG_FILENAMES:
            candidate = current / name
            if candidate.is_file():
                if name == "pyproject.toml" and not _has_pnl_section(candidate):
                    continue
                return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_config(path: Path) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    if path.suffix == ".toml":
        return _load_pyproject_toml(path)
    return _load_yaml(path)
