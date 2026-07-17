# Module Matches Class

## Purpose

When each module contains one primary class, keeping the filename in sync with the class name makes it immediately obvious what a file exports. This rule requires the module filename (without the `.py` extension) to be the snake_case form of the primary class name in that file.

## Configuration

```yaml
rules:
  - name: domain-module-naming
    description: Module filename must match the primary class name in snake_case
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

```text
$ pnl check
contexts/catalog/domain/custom.py:1
    [domain-module-naming] Module filename must match the primary class name in snake_case
    custom (expected: custom_object)

Found 1 violation(s).
```

## Variant: Outbound Adapters (Qualifier in the Directory)

Outbound adapters name the module after the port they implement and let the
directory carry the technology — `postgres/organization_repository.py` holds
`class PostgresOrganizationRepository`. Use `match: suffix` so the filename can be
a trailing slice of the class name, and `strip_prefix: parent_dir` so the dropped
qualifier must equal the parent directory.

```yaml
rules:
  - name: outbound-module-naming
    description: Outbound adapter filename is the port name; technology lives in the directory
    type: module
    naming:
      source: class_name
      transform: snake_case
      match: suffix
      strip_prefix: parent_dir

apply:
  - name: outbound-adapters
    rules: [outbound-module-naming]
    modules: contexts.*.adapters.outbound
```

Passing: `persistence/postgres/organization_repository.py` with
`PostgresOrganizationRepository`. Violations: duplicating the qualifier in the
filename (`postgres/postgres_organization_repository.py`), placing the qualifier
in the filename with no matching directory (`httpx_image_fetcher.py`), or
inverting the layout so the filename is the technology and the directory is the
port (`property_sync_fetcher/google_sheet.py`).
