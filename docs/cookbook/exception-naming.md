# Exception Naming

## Purpose

Consistent exception names make error handling code easier to scan and understand. This rule enforces a structured pattern: exceptions must start with an upper-case word, optionally followed by more words, and end with one of the recognised semantic suffixes (`NotFound`, `Invalid`, `Denied`, `Conflict`, or `Failed`) before the mandatory `Error` suffix.

## Configuration

```yaml
rules:
  - name: exception-naming
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }

apply:
  - name: all
    rules: [exception-naming]
    modules: "**"
```

## Violation Example

```python
# src/domain/exceptions.py

class FilterError(Exception):   # missing semantic suffix before Error
    pass
```

## Passing Example

```python
# src/domain/exceptions.py

class FilterNotFoundError(Exception):
    pass
```

## Output

```
$ pnl check
src/domain/exceptions.py:3
    [exception-naming]
    FilterError (expected pattern: ^[A-Z][a-zA-Z]+(NotFound|Invalid|...)Error$)

Found 1 violation(s).
```
