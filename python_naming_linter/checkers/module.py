from __future__ import annotations

import ast
import re
from pathlib import Path

from python_naming_linter.checkers import Violation
from python_naming_linter.config import Rule


def _to_snake_case(name: str) -> str:
    """Convert a CamelCase / PascalCase name to snake_case."""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return result.lower()


def _normalize(text: str) -> str:
    """Lowercase and drop separators so compound tokens compare equal.

    ``big_query`` and ``bigquery`` normalize to the same value, which lets a
    stripped class-name prefix be compared against a directory name regardless
    of how each spells a multi-word technology.
    """
    return re.sub(r"[_\-]", "", text.lower())


def _first_class_name(tree: ast.Module) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            return node.name
    return None


def _violation(
    rule: Rule, file_path: str, module_name: str, message: str
) -> Violation:
    return Violation(
        rule_name=rule.name,
        file_path=file_path,
        lineno=0,
        name=module_name,
        message=message,
        rule_description=rule.description,
    )


def _check_class_name_source(
    tree: ast.Module, rule: Rule, file_path: str, module_name: str
) -> list[Violation]:
    """Check a module name derived from a class defined in the module.

    ``match: exact`` (default) requires ``module_name == snake_case(class)``.
    ``match: suffix`` requires ``module_name`` to be a trailing token-slice of
    ``snake_case(class)`` — the dropped leading tokens are a qualifier carried
    by the class name (e.g. a technology). With ``strip_prefix: parent_dir``
    that dropped qualifier must equal the immediate parent directory, so the
    qualifier lives in the directory and not the filename.
    """
    class_name = _first_class_name(tree)
    if class_name is None:
        return []

    naming = rule.naming
    expected = _to_snake_case(class_name)
    match = naming.get("match", "exact")

    if match == "exact":
        if module_name == expected:
            return []
        message = f"Expected module name '{expected}', got '{module_name}'"
        return [_violation(rule, file_path, module_name, message)]

    if match == "suffix":
        expected_tokens = expected.split("_")
        module_tokens = module_name.split("_")
        is_suffix = (
            len(module_tokens) <= len(expected_tokens)
            and expected_tokens[len(expected_tokens) - len(module_tokens) :]
            == module_tokens
        )
        if not is_suffix:
            message = (
                f"Expected module name to be a suffix of '{expected}' "
                f"(class '{class_name}'), got '{module_name}'"
            )
            return [_violation(rule, file_path, module_name, message)]

        if naming.get("strip_prefix") == "parent_dir":
            dropped = expected_tokens[: len(expected_tokens) - len(module_tokens)]
            parent = Path(file_path).parent.name
            if _normalize("".join(dropped)) != _normalize(parent):
                message = (
                    f"Expected the qualifier stripped from '{expected}' "
                    f"('{'_'.join(dropped) or '(none)'}') to match parent "
                    f"directory '{parent}'"
                )
                return [_violation(rule, file_path, module_name, message)]
        return []

    return []


def check_module(tree: ast.Module, rule: Rule, file_path: str) -> list[Violation]:
    """Check module filename against the given rule."""
    module_name = Path(file_path).stem

    # Skip __init__ files
    if module_name == "__init__":
        return []

    naming = rule.naming

    if naming.get("source") == "class_name":
        transform = naming.get("transform", "snake_case")
        if transform != "snake_case":
            return []
        return _check_class_name_source(tree, rule, file_path, module_name)

    if "regex" in naming:
        pattern = naming["regex"]
        if not re.fullmatch(pattern, module_name):
            message = f"Expected module name to match '{pattern}', got '{module_name}'"
            return [_violation(rule, file_path, module_name, message)]
        return []

    if "case" in naming:
        case = naming["case"]
        message: str | None = None
        if case == "snake_case":
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", module_name):
                message = f"Expected snake_case module name, got '{module_name}'"
        elif case == "UPPER_CASE":
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", module_name):
                message = f"Expected UPPER_CASE module name, got '{module_name}'"
        elif case == "PascalCase":
            if not re.fullmatch(r"[A-Z][a-zA-Z0-9]*", module_name):
                message = f"Expected PascalCase module name, got '{module_name}'"
        if message is not None:
            return [_violation(rule, file_path, module_name, message)]
        return []

    return []
