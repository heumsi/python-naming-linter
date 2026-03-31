# python-naming-linter

A naming convention linter for Python projects. Define custom naming rules and enforce them with a single CLI command.

## What It Does

- Define naming rules for variables, functions, classes, modules, and packages
- Apply rules to specific modules using pattern matching
- Integrate into CI or pre-commit to keep your naming conventions consistent

For Python developers who want to enforce team-specific naming conventions beyond what PEP 8 and ruff cover.

## Installation

```bash
pip install python-naming-linter
```

Or with uv:

```bash
uv add python-naming-linter
```

## Quick Start

Create `.python-naming-linter.yaml` in your project root:

```yaml
rules:
  - name: bool-method-prefix
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }

  - name: exception-naming
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }

apply:
  - name: all
    rules: [bool-method-prefix, exception-naming]
    modules: "**"
```

Run:

```bash
pnl check
```

Output:

```
src/domain/service.py:12
    [bool-method-prefix] validate (expected prefix: is_ | has_ | should_)

src/domain/exceptions.py:8
    [exception-naming] FilterError (expected pattern: ^[A-Z][a-zA-Z]+(NotFound|Invalid|...)Error$)

Found 2 violation(s).
```

## Examples

### Variable Naming — Match Type Annotation

Enforce that variable names match their type annotation in snake_case:

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

This catches `repo: SubscriptionRepository` (should be `subscription_repository`).

The `{prefix}_{expected}` form is also allowed — `source_object_context: ObjectContext` passes because it ends with `_object_context`.

### Module Naming — Match Class Name

Enforce that module filenames match the primary class they contain:

```yaml
rules:
  - name: domain-module-naming
    type: module
    naming: { source: class_name, transform: snake_case }

apply:
  - name: domain-layer
    rules: [domain-module-naming]
    modules: contexts.*.domain
```

A file `custom.py` containing `class CustomObject` is a violation — it should be `custom_object.py`.

### Combining Rules Per Layer

Apply different rules to different parts of your codebase:

```yaml
rules:
  - name: attribute-matches-type
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }

  - name: bool-method-prefix
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }

  - name: exception-naming
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }

  - name: domain-module-naming
    type: module
    naming: { source: class_name, transform: snake_case }

  - name: constant-upper-case
    type: variable
    filter: { target: constant }
    naming: { case: UPPER_CASE }

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

## Configuration

### Rule Types

| Type | Target |
|------|--------|
| `variable` | Variable names (attribute, parameter, local_variable, constant) |
| `function` | Function/method names |
| `class` | Class names (including exceptions) |
| `module` | Module (file) names |
| `package` | Package (directory) names |

### Filter

Each rule can narrow its scope with type-specific filters:

| Type | Filter | Example Values |
|------|--------|----------------|
| `variable` | `target` | `attribute`, `parameter`, `local_variable`, `constant` |
| `function` | `target` | `method`, `function` |
| `function` | `return_type` | `bool` |
| `function` | `decorator` | `staticmethod` |
| `class` | `base_class` | `Exception` |
| `class` | `decorator` | `dataclass` |

### Naming Constraints

| Field | Description | Example |
|-------|-------------|---------|
| `prefix` | Name must start with one of the listed prefixes | `[is_, has_]` |
| `suffix` | Name must end with one of the listed suffixes | `[Repository, Service]` |
| `regex` | Name must match a regular expression | `"^[A-Z][a-zA-Z]+Error$"` |
| `source` + `transform` | Name must be derived from another element | `source: type_annotation`, `transform: snake_case` |
| `case` | Name must follow a casing convention | `snake_case`, `PascalCase`, `UPPER_CASE` |

### Include / Exclude

Control which files are scanned:

```yaml
include:
  - src
exclude:
  - src/generated/**

rules:
  - name: ...
```

- **No `include` or `exclude`** — All `.py` files under the project root are scanned
- **`include` only** — Only files matching the given paths are scanned
- **`exclude` only** — All files except those matching the given paths are scanned
- **Both** — `include` is applied first, then `exclude` filters within that result

### Wildcard

`*` matches a single level in dotted module paths:

```yaml
modules: contexts.*.domain  # matches contexts.boards.domain, contexts.auth.domain, ...
```

`**` matches one or more levels:

```yaml
modules: contexts.**.domain  # matches contexts.boards.domain, contexts.boards.sub.domain, ...
```

### Named Capture

`{name}` captures a single level (like `*`) and allows back-referencing:

```yaml
apply:
  - name: domain-isolation
    rules: [attribute-matches-type]
    modules: contexts.{context}.domain
```

### pyproject.toml

You can also configure in `pyproject.toml`:

```toml
[[tool.python-naming-linter.rules]]
name = "bool-method-prefix"
type = "function"

[tool.python-naming-linter.rules.filter]
return_type = "bool"

[tool.python-naming-linter.rules.naming]
prefix = ["is_", "has_", "should_"]

[[tool.python-naming-linter.apply]]
name = "all"
rules = ["bool-method-prefix"]
modules = "**"
```

### Inline Ignore

Suppress violations on specific lines using `# pnl: ignore` comments:

```python
x: int = 1  # pnl: ignore
```

To suppress only specific rules, specify rule names:

```python
x: int = 1  # pnl: ignore=attribute-matches-type
```

Multiple rules can be listed with commas:

```python
x: int = 1  # pnl: ignore=attribute-matches-type,constant-upper-case
```

## CLI

```bash
# Check with auto-discovered config (searches upward from cwd)
pnl check

# Specify config file (project root = config file's parent directory)
pnl check --config path/to/config.yaml
```

Exit codes:

- `0` — No violations
- `1` — Violations found
- `2` — Config file not found

If no `--config` is given, the tool searches upward from the current directory for `.python-naming-linter.yaml` or `pyproject.toml` (with `[tool.python-naming-linter]`). The config file's parent directory is used as the project root.

## Pre-commit

Add to `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/heumsi/python-naming-linter
  rev: ''  # Use the tag you want to point at (e.g., v0.1.0)
  hooks:
    - id: python-naming-linter
```

To pass custom options:

```yaml
- repo: https://github.com/heumsi/python-naming-linter
  rev: ''
  hooks:
    - id: python-naming-linter
      args: [--config, custom-config.yaml]
```

## License

MIT
