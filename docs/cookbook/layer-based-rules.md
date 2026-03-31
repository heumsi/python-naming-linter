# Layer-Based Rules

## Purpose

Real projects have distinct layers — domain, infrastructure, API — each with its own naming conventions. Instead of applying every rule globally, you can scope each rule set to the layer where it belongs, reducing false positives and making the intent of each rule explicit.

## Configuration

```yaml
rules:
  - name: attribute-matches-type
    description: "Attribute names must match their type annotation in snake_case"
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }

  - name: bool-method-prefix
    description: "Bool-returning functions must start with is_, has_, or should_"
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }

  - name: domain-module-naming
    description: "Module filename must match the primary class name in snake_case"
    type: module
    naming: { source: class_name, transform: snake_case }

  - name: constant-upper-case
    description: "Module-level constants must use UPPER_CASE"
    type: variable
    filter: { target: constant }
    naming: { case: UPPER_CASE }

  - name: exception-naming
    description: "Exception classes must follow the <Noun><Reason>Error pattern"
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }

apply:
  - name: domain-layer
    rules:
      - attribute-matches-type
      - bool-method-prefix
      - domain-module-naming
      - constant-upper-case
    modules: contexts.*.domain

  - name: global-exceptions
    rules: [exception-naming]
    modules: "**"
```

The `domain-layer` apply block targets every `contexts/<context>/domain` package, while `global-exceptions` runs the exception naming rule across the entire codebase.

## Violation Example

```python
# contexts/billing/domain/service.py

max_retry = 3                          # constant not in UPPER_CASE

class BillingService:
    def validate(self) -> bool:        # bool method missing prefix
        return self._status == "active"
```

```python
# contexts/billing/domain/exceptions.py

class BillingError(Exception):         # exception missing semantic suffix
    pass
```

## Passing Example

```python
# contexts/billing/domain/service.py

MAX_RETRY = 3

class BillingService:
    def is_valid(self) -> bool:
        return self._status == "active"
```

```python
# contexts/billing/domain/exceptions.py

class BillingNotFoundError(Exception):
    pass
```

## Output

```
$ pnl check
contexts/billing/domain/service.py:3
    [constant-upper-case] Module-level constants must use UPPER_CASE
    max_retry (expected case: UPPER_CASE)

contexts/billing/domain/service.py:6
    [bool-method-prefix] Bool-returning functions must start with is_, has_, or should_
    validate (expected prefix: is_ | has_ | should_)

contexts/billing/domain/exceptions.py:3
    [exception-naming] Exception classes must follow the <Noun><Reason>Error pattern
    BillingError (expected pattern: ^[A-Z][a-zA-Z]+(NotFound|Invalid|...)Error$)

Found 3 violation(s).
```
