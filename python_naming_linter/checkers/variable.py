from __future__ import annotations

import ast
import re

from python_naming_linter.checkers import Violation
from python_naming_linter.config import Rule


def _to_snake_case(name: str) -> str:
    """Convert a CamelCase / PascalCase name to snake_case."""
    # Insert underscore before sequences of uppercase letters followed by lowercase
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return result.lower()


def _is_upper_case(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Z0-9_]*", name))


def _get_annotation_name(annotation: ast.expr | None) -> str | None:
    """Extract the plain name from a type annotation node."""
    if annotation is None:
        return None
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    # For subscripted types like List[X], use the outer name
    if isinstance(annotation, ast.Subscript):
        return _get_annotation_name(annotation.value)
    return None


def _check_name_against_naming(
    var_name: str,
    annotation: ast.expr | None,
    naming: dict,
) -> str | None:
    """Return error message string if name violates naming rule, else None."""

    if "source" in naming and naming.get("source") == "type_annotation":
        transform = naming.get("transform", "snake_case")
        if transform == "snake_case":
            type_name = _get_annotation_name(annotation)
            if type_name is None:
                # No annotation to derive from; skip
                return None
            expected = _to_snake_case(type_name)
            # Allow exact match or {prefix}_{expected} form
            if var_name == expected:
                return None
            if var_name.endswith("_" + expected):
                return None
            return f"Expected '{expected}' (or '<prefix>_{expected}'), got '{var_name}'"

    if "case" in naming:
        case = naming["case"]
        if case == "UPPER_CASE":
            if _is_upper_case(var_name):
                return None
            return f"Expected UPPER_CASE name, got '{var_name}'"

    if "prefix" in naming:
        prefix = naming["prefix"]
        if not var_name.startswith(prefix):
            return f"Expected name to start with '{prefix}', got '{var_name}'"

    if "suffix" in naming:
        suffix = naming["suffix"]
        if not var_name.endswith(suffix):
            return f"Expected name to end with '{suffix}', got '{var_name}'"

    if "regex" in naming:
        pattern = naming["regex"]
        if not re.fullmatch(pattern, var_name):
            return f"Expected name to match '{pattern}', got '{var_name}'"

    return None


def _collect_attributes(
    tree: ast.Module,
) -> list[tuple[str, ast.expr | None, int]]:
    """Collect annotated assignments inside class bodies."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name):
                        results.append((item.target.id, item.annotation, item.lineno))
    return results


def _collect_parameters(
    tree: ast.Module,
) -> list[tuple[str, ast.expr | None, int]]:
    """Collect function/method parameters, skipping self and cls."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args
            all_args = args.posonlyargs + args.args + args.kwonlyargs
            if args.vararg:
                all_args.append(args.vararg)
            if args.kwarg:
                all_args.append(args.kwarg)
            for arg in all_args:
                if arg.arg in ("self", "cls"):
                    continue
                results.append((arg.arg, arg.annotation, arg.lineno))
    return results


def _collect_local_variables(
    tree: ast.Module,
) -> list[tuple[str, ast.expr | None, int]]:
    """Collect annotated assignments inside function bodies."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for item in ast.walk(node):
                if isinstance(item, ast.AnnAssign) and isinstance(
                    item.target, ast.Name
                ):
                    results.append((item.target.id, item.annotation, item.lineno))
    return results


def _collect_constants(
    tree: ast.Module,
) -> list[tuple[str, ast.expr | None, int]]:
    """Collect module-level assignments with UPPER_CASE names (constants)."""
    results = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    results.append((target.id, None, node.lineno))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            results.append((node.target.id, node.annotation, node.lineno))
    return results


def check_variable(tree: ast.Module, rule: Rule, file_path: str) -> list[Violation]:
    target = rule.filter.get("target", "")
    naming = rule.naming

    if target == "attribute":
        candidates = _collect_attributes(tree)
    elif target == "parameter":
        candidates = _collect_parameters(tree)
    elif target == "local_variable":
        candidates = _collect_local_variables(tree)
    elif target == "constant":
        candidates = _collect_constants(tree)
    else:
        return []

    violations = []
    for var_name, annotation, lineno in candidates:
        msg = _check_name_against_naming(var_name, annotation, naming)
        if msg is not None:
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=file_path,
                    lineno=lineno,
                    name=var_name,
                    message=msg,
                    rule_description=rule.description,
                )
            )
    return violations
