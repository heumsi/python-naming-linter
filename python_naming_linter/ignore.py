from __future__ import annotations

import re

from python_naming_linter.checkers import Violation

_IGNORE_RE = re.compile(r"#\s*pnl:\s*ignore(?:=([a-zA-Z0-9_.,\s-]+))?$")


def parse_ignore_comments(source: str) -> dict[int, set[str] | None]:
    """Parse inline ignore comments from source code.

    Returns a mapping of line number to ignored rule names.
    ``None`` means all rules are ignored on that line.
    """
    ignores: dict[int, set[str] | None] = {}
    for lineno, line in enumerate(source.splitlines(), start=1):
        match = _IGNORE_RE.search(line)
        if match is None:
            continue
        rules_str = match.group(1)
        if rules_str is None:
            ignores[lineno] = None
        else:
            ignores[lineno] = {r.strip() for r in rules_str.split(",")}
    return ignores


def filter_violations(
    violations: list[Violation],
    ignores: dict[int, set[str] | None],
) -> list[Violation]:
    """Remove violations that are suppressed by ignore comments."""
    result = []
    for v in violations:
        ignored = ignores.get(v.lineno)
        if ignored is None and v.lineno not in ignores:
            result.append(v)
        elif ignored is not None and v.rule_name not in ignored:
            result.append(v)
    return result
