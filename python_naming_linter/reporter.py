from __future__ import annotations

from python_naming_linter.checkers import Violation


def format_violations(file_path: str, violations: list[Violation]) -> str:
    if not violations:
        return ""

    lines = []
    for v in violations:
        lines.append(f"{file_path}:{v.lineno}")
        lines.append(f"    [{v.rule_name}] {v.name} ({v.message})")
        lines.append("")

    return "\n".join(lines)
