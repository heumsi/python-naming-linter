from __future__ import annotations

import ast
import re

from python_naming_linter.checkers import Violation
from python_naming_linter.config import Rule


def _get_return_type_name(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Return the plain name of the function's return annotation, or None."""
    annotation = node.returns
    if annotation is None:
        return None
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    if isinstance(annotation, ast.Constant):
        return str(annotation.value)
    return None


def _check_name(func_name: str, naming: dict) -> str | None:
    """Return error message if func_name violates naming constraints, else None."""

    if "prefix" in naming:
        prefix = naming["prefix"]
        if isinstance(prefix, list):
            if not any(func_name.startswith(p) for p in prefix):
                msg = (
                    f"Expected name to start with one of {prefix!r}, got '{func_name}'"
                )
                return msg
        else:
            if not func_name.startswith(prefix):
                return f"Expected name to start with '{prefix}', got '{func_name}'"

    if "suffix" in naming:
        suffix = naming["suffix"]
        if isinstance(suffix, list):
            if not any(func_name.endswith(s) for s in suffix):
                return f"Expected name to end with one of {suffix!r}, got '{func_name}'"
        else:
            if not func_name.endswith(suffix):
                return f"Expected name to end with '{suffix}', got '{func_name}'"

    if "regex" in naming:
        pattern = naming["regex"]
        if not re.search(pattern, func_name):
            return f"Expected name to match '{pattern}', got '{func_name}'"

    if "case" in naming:
        case = naming["case"]
        if case == "snake_case":
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", func_name):
                return f"Expected snake_case name, got '{func_name}'"
        elif case == "UPPER_CASE":
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", func_name):
                return f"Expected UPPER_CASE name, got '{func_name}'"

    return None


def _build_parent_map(tree: ast.Module) -> dict[int, ast.AST]:
    """Return a mapping from node id to its parent node."""
    parent_map: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[id(child)] = node
    return parent_map


def check_function(tree: ast.Module, rule: Rule, file_path: str) -> list[Violation]:
    """Check function/method names in tree against the given rule."""
    naming = rule.naming
    filters = rule.filter

    target_filter = filters.get("target")  # "method", "function", or None (both)
    return_type_filter = filters.get("return_type")  # e.g. "bool"
    decorator_filter = filters.get("decorator")  # e.g. "property"

    parent_map = _build_parent_map(tree)

    violations: list[Violation] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        func_name = node.name

        # Skip dunder methods
        if func_name.startswith("__") and func_name.endswith("__"):
            continue

        # Determine if this is a method (direct parent is ClassDef)
        parent = parent_map.get(id(node))
        is_method = isinstance(parent, ast.ClassDef)

        # Apply target filter
        if target_filter == "method" and not is_method:
            continue
        if target_filter == "function" and is_method:
            continue

        # Apply return_type filter
        if return_type_filter is not None:
            actual_return = _get_return_type_name(node)
            if actual_return != return_type_filter:
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
        msg = _check_name(func_name, naming)
        if msg is not None:
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=file_path,
                    lineno=node.lineno,
                    name=func_name,
                    message=msg,
                )
            )

    return violations
