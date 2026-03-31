# Configuration

`pnl` supports two config file formats: a standalone YAML file or an inline section inside `pyproject.toml`.

## Config File Discovery

When you run `pnl check` without `--config`, the tool searches **upward from the current working directory** for one of:

- `.python-naming-linter.yaml`
- `pyproject.toml` (containing a `[tool.python-naming-linter]` section)

The first matching file is used, and its parent directory becomes the project root.

To use a specific config file, pass it explicitly:

```bash
pnl check --config path/to/config.yaml
```

## YAML Format

Create `.python-naming-linter.yaml` in your project root:

```yaml
rules:
  - name: bool-method-prefix
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }

apply:
  - name: all
    rules: [bool-method-prefix]
    modules: "**"
```

## pyproject.toml Format

You can embed the same configuration inside `pyproject.toml` using the `[tool.python-naming-linter]` namespace:

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

Both formats are equivalent — use whichever fits your project's conventions.

## Top-Level Keys

| Key | Description |
|-----|-------------|
| `rules` | List of naming rule definitions |
| `apply` | List of rule-to-module mappings |
| `include` | Paths to include when scanning (optional) |
| `exclude` | Paths to exclude when scanning (optional) |

### include / exclude

Control which files are scanned:

```yaml
include:
  - src
exclude:
  - src/generated/**
```

Behavior:

- **Neither** — all `.py` files under the project root are scanned.
- **`include` only** — only files matching the given paths are scanned.
- **`exclude` only** — all files except those matching the given paths are scanned.
- **Both** — `include` is applied first, then `exclude` filters within that result.
