from __future__ import annotations

import re

from python_naming_linter.checkers import Violation
from python_naming_linter.config import Rule


def check_package(rule: Rule, package_name: str) -> list[Violation]:
    naming = rule.naming
    violations = []

    if "case" in naming:
        if naming["case"] == "snake_case" and package_name != package_name.lower():
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=package_name,
                    lineno=0,
                    name=package_name,
                    message="expected: snake_case",
                    rule_description=rule.description,
                )
            )

    if "regex" in naming:
        if not re.match(naming["regex"], package_name):
            violations.append(
                Violation(
                    rule_name=rule.name,
                    file_path=package_name,
                    lineno=0,
                    name=package_name,
                    message=f"expected pattern: {naming['regex']}",
                    rule_description=rule.description,
                )
            )

    return violations
