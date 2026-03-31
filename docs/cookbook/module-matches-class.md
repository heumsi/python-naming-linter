# Module Matches Class

## Purpose

When each module contains one primary class, keeping the filename in sync with the class name makes it immediately obvious what a file exports. This rule requires the module filename (without the `.py` extension) to be the snake_case form of the primary class name in that file.

## Configuration

```yaml
rules:
  - name: domain-module-naming
    description: "Module filename must match the primary class name in snake_case"
    type: module
    naming: { source: class_name, transform: snake_case }

apply:
  - name: domain-layer
    rules: [domain-module-naming]
    modules: contexts.*.domain
```

## Violation Example

```python
# contexts/catalog/domain/custom.py   ← filename does not match class name

class CustomObject:
    pass
```

## Passing Example

```python
# contexts/catalog/domain/custom_object.py   ← matches CustomObject in snake_case

class CustomObject:
    pass
```

## Output

```
$ pnl check
contexts/catalog/domain/custom.py:1
    [domain-module-naming] Module filename must match the primary class name in snake_case
    custom (expected: custom_object)

Found 1 violation(s).
```
