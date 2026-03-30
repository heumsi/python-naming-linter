from __future__ import annotations

import ast
import fnmatch
from pathlib import Path

import click

from python_naming_linter.checkers.class_ import check_class
from python_naming_linter.checkers.function import check_function
from python_naming_linter.checkers.module import check_module
from python_naming_linter.checkers.package import check_package
from python_naming_linter.checkers.variable import check_variable
from python_naming_linter.config import Rule, find_config, load_config
from python_naming_linter.matcher import matches_pattern_or_submodule
from python_naming_linter.reporter import format_violations


def _file_to_module(file_path: Path, root: Path) -> str:
    relative = file_path.relative_to(root)
    parts = relative.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _package_module(file_path: Path, root: Path) -> str:
    """Return the package (directory) module path for a file.

    For ``contexts/boards/domain/models.py`` this returns
    ``contexts.boards.domain``.
    """
    relative = file_path.relative_to(root)
    parts = relative.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    else:
        parts = parts[:-1]
    return ".".join(parts)


def _normalize_pattern(pattern: str, project_root: Path) -> str:
    """Normalize a pattern so that bare directory names match all files within."""
    clean = pattern.rstrip("/")
    candidate = project_root / clean
    if candidate.is_dir() or not any(c in clean for c in ("*", "?")):
        clean = f"{clean}/**"
    return clean


def _matches_any(path: Path, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(str(path), p) for p in patterns)


def _find_python_files(
    root: Path,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Path]:
    all_files = sorted(root.rglob("*.py"))

    if include is not None:
        normalized = [_normalize_pattern(p, root) for p in include]
        all_files = [
            f
            for f in all_files
            if _matches_any(f.relative_to(root), normalized)
        ]

    if exclude is not None:
        normalized = [_normalize_pattern(p, root) for p in exclude]
        all_files = [
            f
            for f in all_files
            if not _matches_any(f.relative_to(root), normalized)
        ]

    return all_files


def _get_rules_for_module(module: str, config) -> list[Rule]:
    """Return the list of Rule objects that apply to a given module."""
    rule_map = {r.name: r for r in config.rules}
    matching_rules: list[Rule] = []
    for entry in config.apply:
        if matches_pattern_or_submodule(entry.modules, module):
            for rule_name in entry.rules:
                rule = rule_map.get(rule_name)
                if rule is not None and rule not in matching_rules:
                    matching_rules.append(rule)
    return matching_rules


def _run_checker(
    tree: ast.Module,
    rule: Rule,
    file_path: str,
    package_name: str,
) -> list:
    """Dispatch to the appropriate checker based on rule.type."""
    if rule.type == "variable":
        return check_variable(tree, rule, file_path)
    if rule.type == "function":
        return check_function(tree, rule, file_path)
    if rule.type == "class":
        return check_class(tree, rule, file_path)
    if rule.type == "module":
        return check_module(tree, rule, file_path)
    if rule.type == "package":
        return check_package(rule, package_name)
    return []


@click.group()
def main() -> None:
    pass


@main.command()
@click.option(
    "--config",
    "config_path",
    default=None,
    help="Path to config file.",
)
def check(config_path: str | None) -> None:
    if config_path is not None:
        config_file = Path(config_path)
        if not config_file.exists():
            click.echo(f"Error: Config file not found: {config_file}")
            raise SystemExit(2)
        root = config_file.resolve().parent
    else:
        config_file = find_config()
        if config_file is None:
            click.echo(
                "Error: Config file not found. "
                "Create .python-naming-linter.yaml or configure "
                "[tool.python-naming-linter] in pyproject.toml."
            )
            raise SystemExit(2)
        root = config_file.resolve().parent

    config = load_config(config_file)

    all_violations = []
    python_files = _find_python_files(root, config.include, config.exclude)

    checked_packages: set[tuple[str, str]] = set()

    for file_path in python_files:
        module = _file_to_module(file_path, root)
        package = _package_module(file_path, root)
        rules = _get_rules_for_module(module, config)
        if not rules:
            continue

        source = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            continue

        rel_path = str(file_path.relative_to(root))
        file_violations = []

        for rule in rules:
            if rule.type == "package":
                # Use the last segment of the package path as the package name
                pkg_segment = package.split(".")[-1] if package else ""
                key = (rule.name, package)
                if key in checked_packages:
                    continue
                checked_packages.add(key)
                violations = check_package(rule, pkg_segment)
                # Use the package path as the file_path for reporting
                pkg_rel = package.replace(".", "/")
                for v in violations:
                    all_violations.append(v)
                    output = format_violations(pkg_rel, [v])
                    if output:
                        click.echo(output)
            else:
                violations = _run_checker(tree, rule, rel_path, package)
                file_violations.extend(violations)

        if file_violations:
            output = format_violations(rel_path, file_violations)
            click.echo(output)
            all_violations.extend(file_violations)

    if all_violations:
        click.echo(f"Found {len(all_violations)} violation(s).")
        raise SystemExit(1)
    else:
        click.echo("No violations found.")
