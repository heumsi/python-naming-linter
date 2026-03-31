# python-naming-linter

A naming convention linter for Python projects. Define custom naming rules and enforce them with a single CLI command.

## What It Does

- Define naming rules for variables, functions, classes, modules, and packages
- Apply rules to specific modules using pattern matching
- Integrate into CI or pre-commit to keep your naming conventions consistent

For Python developers who want to enforce team-specific naming conventions beyond what PEP 8 and ruff cover.

## Key Features

| Feature | Description |
|---------|-------------|
| **Rule Types** | Variable, function, class, module, and package naming rules |
| **Filters** | Narrow rules by return type, base class, decorator, and more |
| **Naming Constraints** | Prefix, suffix, regex, case convention, or derived from another element |
| **Module Targeting** | Apply rules to specific parts of your codebase using glob-style patterns |
| **Inline Ignore** | Suppress violations on specific lines with `# pnl: ignore` |
| **Pre-commit** | Drop-in integration with pre-commit hooks |

## Quick Start

**Install:**

```bash
pip install python-naming-linter
```

**Create `.python-naming-linter.yaml` in your project root:**

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

**Run:**

```bash
pnl check
```

**Output:**

```
src/domain/service.py:12
    [bool-method-prefix]
    validate (expected prefix: is_ | has_ | should_)

src/domain/exceptions.py:8
    [exception-naming]
    FilterError (expected pattern: ^[A-Z][a-zA-Z]+(NotFound|Invalid|...)Error$)

Found 2 violation(s).
```

## More Examples

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

This catches `repo: SubscriptionRepository` — the name should be `subscription_repository`.

### Combining Rules Per Layer

Apply different rules to different parts of your codebase:

```yaml
apply:
  - name: domain-layer
    rules:
      - attribute-matches-type
      - bool-method-prefix
      - domain-module-naming
    modules: contexts.*.domain

  - name: global-exceptions
    rules: [exception-naming]
    modules: "**"
```

## Next Steps

- [Installation](getting-started/installation.md) — detailed install instructions
- [Quick Start](getting-started/quick-start.md) — step-by-step setup guide
- [Configuration](getting-started/configuration.md) — full configuration reference
- [Cookbook](cookbook/index.md) — real-world usage patterns
