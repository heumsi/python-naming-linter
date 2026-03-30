from __future__ import annotations

import re

_CAPTURE_RE = re.compile(r"^\{(\w+)\}$")


def matches_pattern(pattern: str, module: str) -> bool:
    return match_pattern_with_captures(pattern, module) is not None


def match_pattern_with_captures(pattern: str, module: str) -> dict[str, str] | None:
    pattern_parts = pattern.split(".")
    module_parts = module.split(".")
    captures: dict[str, str] = {}
    if _match_with_captures(pattern_parts, module_parts, captures):
        return captures
    return None


def _match_with_captures(
    pattern_parts: list[str],
    module_parts: list[str],
    captures: dict[str, str],
) -> bool:
    if not pattern_parts and not module_parts:
        return True
    if not pattern_parts:
        return False

    if pattern_parts[0] == "**":
        for i in range(1, len(module_parts) + 1):
            snapshot = dict(captures)
            if _match_with_captures(pattern_parts[1:], module_parts[i:], captures):
                return True
            captures.clear()
            captures.update(snapshot)
        return False

    if not module_parts:
        return False

    m = _CAPTURE_RE.match(pattern_parts[0])
    if m:
        name = m.group(1)
        value = module_parts[0]
        if name in captures:
            if captures[name] != value:
                return False
        else:
            captures[name] = value
        return _match_with_captures(pattern_parts[1:], module_parts[1:], captures)

    if pattern_parts[0] == "*" or pattern_parts[0] == module_parts[0]:
        return _match_with_captures(pattern_parts[1:], module_parts[1:], captures)

    return False


def matches_pattern_or_submodule(pattern: str, module: str) -> bool:
    if matches_pattern(pattern, module):
        return True
    module_parts = module.split(".")
    pattern_parts = pattern.split(".")
    if len(module_parts) > len(pattern_parts):
        prefix = ".".join(module_parts[: len(pattern_parts)])
        if matches_pattern(pattern, prefix):
            return True
    return False
