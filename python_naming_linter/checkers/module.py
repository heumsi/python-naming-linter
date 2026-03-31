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


def check_module(tree: ast.Module, rule: Rule, file_path: str) -> list[Violation]:
    """Check module filename against the given rule."""
    module_name = Path(file_path).stem

    # Skip __init__ files
    if module_name == "__init__":
        return []

    naming = rule.naming
    violations: list[Violation] = []

    if "source" in naming and naming.get("source") == "class_name":
        transform = naming.get("transform", "snake_case")
        if transform == "snake_case":
            # Find the first ClassDef at module level (or anywhere via walk)
            first_class: ast.ClassDef | None = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    first_class = node
                    break

            if first_class is None:
                return []

            expected = _to_snake_case(first_class.name)
            if module_name != expected:
                msg = f"Expected module name '{expected}', got '{module_name}'"
                violations.append(
                    Violation(
                        rule_name=rule.name,
                        file_path=file_path,
                        lineno=0,
                        name=module_name,
                        message=msg,
                        rule_description=rule.description,
                    )
                )

    elif "regex" in naming:
        pattern = naming["regex"]
        if not re.fullmatch(pattern, module_name):
            msg = f"Expected module name to match '{pattern}', got '{module_name}'"
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=file_path,
                    lineno=0,
                    name=module_name,
                    message=msg,
                    rule_description=rule.description,
                )
            )

    elif "case" in naming:
        case = naming["case"]
        msg: str | None = None
        if case == "snake_case":
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", module_name):
                msg = f"Expected snake_case module name, got '{module_name}'"
        elif case == "UPPER_CASE":
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", module_name):
                msg = f"Expected UPPER_CASE module name, got '{module_name}'"
        elif case == "PascalCase":
            if not re.fullmatch(r"[A-Z][a-zA-Z0-9]*", module_name):
                msg = f"Expected PascalCase module name, got '{module_name}'"
        if msg is not None:
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=file_path,
                    lineno=0,
                    name=module_name,
                    message=msg,
                    rule_description=rule.description,
                )
            )

    return violations
