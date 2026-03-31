# Attribute Matches Type

## Purpose

When an attribute holds a repository, service, or other typed object, keeping the attribute name in sync with the type annotation removes ambiguity and makes dependency injection transparent at a glance. This rule requires each class attribute name to be the snake_case form of its type annotation.

## Configuration

```yaml
rules:
  - name: attribute-matches-type
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }

apply:
  - name: domain-layer
    rules: [attribute-matches-type]
    modules: contexts.*.domain
```

## Violation Example

```python
# contexts/billing/domain/service.py

class BillingService:
    def __init__(self, repo: SubscriptionRepository) -> None:
        self.repo = repo   # should be subscription_repository
```

## Passing Example

```python
# contexts/billing/domain/service.py

class BillingService:
    def __init__(self, repo: SubscriptionRepository) -> None:
        self.subscription_repository = repo
```

The `{prefix}_{expected}` form is also allowed. For example, `source_object_context: ObjectContext` passes because the name ends with `_object_context`.

## Output

```
$ pnl check
contexts/billing/domain/service.py:5
    [attribute-matches-type] repo (expected: subscription_repository)

Found 1 violation(s).
```
