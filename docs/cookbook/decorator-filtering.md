# Decorator Filtering

## Purpose

Some naming conventions only apply to a specific kind of function or class. Decorator-based filtering lets you target `@staticmethod` methods, `@dataclass` classes, or any other decorated construct without affecting the rest of the codebase.

## Configuration

### Example 1 — `@staticmethod` methods must start with `create_` or `build_`

```yaml
rules:
  - name: static-factory-prefix
    description: Static factory methods must start with create_ or build_
    type: function
    filter: { decorator: staticmethod }
    naming: { prefix: [create_, build_] }

apply:
  - name: all
    rules: [static-factory-prefix]
    modules: "**"
```

### Example 2 — `@dataclass` classes must use PascalCase and end with `Data` or `Config`

```yaml
rules:
  - name: dataclass-naming
    description: Dataclass names must end with Data or Config
    type: class
    filter: { decorator: dataclass }
    naming: { suffix: [Data, Config] }

apply:
  - name: all
    rules: [dataclass-naming]
    modules: "**"
```

## Violation Example

```python
# src/domain/order.py
from dataclasses import dataclass

class OrderRepository:
    @staticmethod
    def from_dict(raw: dict) -> "OrderRepository":   # missing create_/build_ prefix
        return OrderRepository(**raw)

@dataclass
class OrderPayload:   # missing Data/Config suffix
    order_id: str
    amount: float
```

## Passing Example

```python
# src/domain/order.py
from dataclasses import dataclass

class OrderRepository:
    @staticmethod
    def create_from_dict(raw: dict) -> "OrderRepository":
        return OrderRepository(**raw)

@dataclass
class OrderData:
    order_id: str
    amount: float
```

## Output

```text
$ pnl check
src/domain/order.py:5
    [static-factory-prefix] Static factory methods must start with create_ or build_
    from_dict (expected prefix: create_ | build_)

src/domain/order.py:9
    [dataclass-naming] Dataclass names must end with Data or Config
    OrderPayload (expected suffix: Data | Config)

Found 2 violation(s).
```
