# Quick Start

Get `pnl` running in your project in three steps.

## Step 1: Create a Config File

Create `.python-naming-linter.yaml` in your project root and define your naming rules:

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

This config defines two rules:

- `bool-method-prefix` — functions that return `bool` must start with `is_`, `has_`, or `should_`.
- `exception-naming` — classes that extend `Exception` must follow the given regex pattern.

Both rules are applied to all modules (`**`).

## Step 2: Run the Linter

From your project root, run:

```bash
pnl check
```

`pnl` automatically discovers the config file by searching upward from the current working directory.

## Step 3: Review the Output

Violations are reported with the file path, line number, rule name, and what was expected:

```
src/domain/service.py:12
    [bool-method-prefix]
    validate (expected prefix: is_ | has_ | should_)

src/domain/exceptions.py:8
    [exception-naming]
    FilterError (expected pattern: ^[A-Z][a-zA-Z]+(NotFound|Invalid|...)Error$)

Found 2 violation(s).
```

Fix the reported names and re-run `pnl check` until no violations remain.

## Next Steps

- Learn all available config options in [Configuration](./configuration.md).
- See rule type details and naming constraint options in the full reference.
