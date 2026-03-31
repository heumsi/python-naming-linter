# Bool Method Prefix

## Purpose

Functions that return `bool` are easier to read at call sites when their names read as a question. This rule enforces that any function or method with a `bool` return type annotation starts with `is_`, `has_`, or `should_`.

## Configuration

```yaml
rules:
  - name: bool-method-prefix
    description: "Bool-returning functions must start with is_, has_, or should_"
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }

apply:
  - name: all
    rules: [bool-method-prefix]
    modules: "**"
```

## Violation Example

```python
# src/domain/service.py

class SubscriptionService:
    def validate(self) -> bool:   # missing required prefix
        return self._status == "active"
```

## Passing Example

```python
# src/domain/service.py

class SubscriptionService:
    def is_valid(self) -> bool:
        return self._status == "active"
```

## Output

```
$ pnl check
src/domain/service.py:4
    [bool-method-prefix] Bool-returning functions must start with is_, has_, or should_
    validate (expected prefix: is_ | has_ | should_)

Found 1 violation(s).
```
