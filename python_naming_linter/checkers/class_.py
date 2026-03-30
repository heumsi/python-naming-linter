from __future__ import annotations

import ast
import re

from python_naming_linter.checkers import Violation
from python_naming_linter.config import Rule

# Common built-in exception base classes used for the "Exception" heuristic
_EXCEPTION_BASE_CLASSES = {
    "Exception",
    "BaseException",
    "ValueError",
    "TypeError",
    "RuntimeError",
    "KeyError",
    "IndexError",
    "AttributeError",
    "NotImplementedError",
    "OSError",
    "IOError",
    "FileNotFoundError",
    "PermissionError",
    "TimeoutError",
    "StopIteration",
    "GeneratorExit",
    "SystemExit",
    "ArithmeticError",
    "LookupError",
    "EnvironmentError",
    "ConnectionError",
    "ImportError",
    "NameError",
    "OverflowError",
    "RecursionError",
    "MemoryError",
    "UnicodeError",
    "Warning",
}


def _is_exception_like(name: str) -> bool:
    """Return True if the name looks like an exception class."""
    return (
        name in _EXCEPTION_BASE_CLASSES
        or name.endswith("Error")
        or name.endswith("Exception")
    )


def _base_names(node: ast.ClassDef) -> list[str]:
    """Return the plain names of all direct base classes."""
    names = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _matches_base_class_filter(node: ast.ClassDef, base_class_filter: str) -> bool:
    """Return True if the class satisfies the base_class filter."""
    bases = _base_names(node)
    if base_class_filter == "Exception":
        return any(_is_exception_like(b) for b in bases)
    return base_class_filter in bases


def _check_name(class_name: str, naming: dict) -> str | None:
    """Return an error message if class_name violates naming constraints, else None."""

    if "prefix" in naming:
        prefix = naming["prefix"]
        if isinstance(prefix, list):
            if not any(class_name.startswith(p) for p in prefix):
                msg = (
                    f"Expected name to start with one of {prefix!r}, got '{class_name}'"
                )
                return msg
        else:
            if not class_name.startswith(prefix):
                return f"Expected name to start with '{prefix}', got '{class_name}'"

    if "suffix" in naming:
        suffix = naming["suffix"]
        if isinstance(suffix, list):
            if not any(class_name.endswith(s) for s in suffix):
                msg = f"Expected name to end with one of {suffix!r}, got '{class_name}'"
                return msg
        else:
            if not class_name.endswith(suffix):
                return f"Expected name to end with '{suffix}', got '{class_name}'"

    if "regex" in naming:
        pattern = naming["regex"]
        if not re.search(pattern, class_name):
            return f"Expected name to match '{pattern}', got '{class_name}'"

    if "case" in naming:
        case = naming["case"]
        if case == "PascalCase":
            if not re.fullmatch(r"[A-Z][a-zA-Z0-9]*", class_name):
                return f"Expected PascalCase name, got '{class_name}'"
        elif case == "snake_case":
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", class_name):
                return f"Expected snake_case name, got '{class_name}'"
        elif case == "UPPER_CASE":
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", class_name):
                return f"Expected UPPER_CASE name, got '{class_name}'"

    return None


def check_class(tree: ast.Module, rule: Rule, file_path: str) -> list[Violation]:
    """Check class names in tree against the given rule."""
    naming = rule.naming
    filters = rule.filter

    base_class_filter = filters.get("base_class")
    decorator_filter = filters.get("decorator")

    violations: list[Violation] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        class_name = node.name

        # Apply base_class filter
        if base_class_filter is not None:
            if not _matches_base_class_filter(node, base_class_filter):
                continue

        # Apply decorator filter
        if decorator_filter is not None:
            decorator_names = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    decorator_names.append(dec.id)
                elif isinstance(dec, ast.Attribute):
                    decorator_names.append(dec.attr)
            if decorator_filter not in decorator_names:
                continue

        # Check naming
        msg = _check_name(class_name, naming)
        if msg is not None:
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=file_path,
                    lineno=node.lineno,
                    name=class_name,
                    message=msg,
                )
            )

    return violations
