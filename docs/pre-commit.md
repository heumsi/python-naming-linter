# Pre-commit

`pnl` can be used as a [pre-commit](https://pre-commit.com/) hook to enforce naming conventions before every commit.

## Setup

Add the following to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/heumsi/python-naming-linter
  rev: ''  # Use the tag you want to point at (e.g., v0.1.0)
  hooks:
    - id: python-naming-linter
```

## Custom Options

To pass custom options (e.g., a specific config file path), use `args`:

```yaml
- repo: https://github.com/heumsi/python-naming-linter
  rev: ''
  hooks:
    - id: python-naming-linter
      args: [--config, custom-config.yaml]
```
