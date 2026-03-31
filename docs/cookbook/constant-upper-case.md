# Constant Upper Case

## Purpose

Module-level constants are easier to distinguish from regular variables when they follow the UPPER_CASE convention. This rule catches constants that were accidentally written in snake_case and flags them for renaming.

## Configuration

```yaml
rules:
  - name: constant-upper-case
    description: "Module-level constants must use UPPER_CASE"
    type: variable
    filter: { target: constant }
    naming: { case: UPPER_CASE }

apply:
  - name: all
    rules: [constant-upper-case]
    modules: "**"
```

## Violation Example

```python
# src/config.py

max_retry_count = 3          # constant in snake_case
default_timeout_seconds = 30 # constant in snake_case
```

## Passing Example

```python
# src/config.py

MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT_SECONDS = 30
```

## Output

```
$ pnl check
src/config.py:3
    [constant-upper-case] Module-level constants must use UPPER_CASE
    max_retry_count (expected case: UPPER_CASE)

src/config.py:4
    [constant-upper-case] Module-level constants must use UPPER_CASE
    default_timeout_seconds (expected case: UPPER_CASE)

Found 2 violation(s).
```
