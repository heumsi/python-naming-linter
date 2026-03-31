# Include / Exclude

The `include` and `exclude` keys control which files `pnl` scans. They are top-level config keys and are applied before any rule matching.

```yaml
include:
  - src

exclude:
  - src/generated/**

rules:
  - name: ...

apply:
  - name: ...
```

Both keys accept a list of file path patterns. Patterns are matched against file paths relative to the project root.

---

## Scenarios

### No `include` or `exclude`

When neither key is present, `pnl` scans all `.py` files under the project root recursively.

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

Every `.py` file in the project is a candidate for scanning. The `apply` block's `modules` pattern then determines which of those files are actually checked by each rule.

---

### `include` only

When only `include` is specified, only files matching the listed paths are scanned. Everything else is ignored.

```yaml
include:
  - src

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

Only `.py` files under `src/` are scanned. Files in `tests/`, `scripts/`, or other top-level directories are not checked, even if they match the `modules` pattern in `apply`.

Use `include` when your project has multiple top-level directories and you only want to lint a specific one.

---

### `exclude` only

When only `exclude` is specified, all `.py` files under the project root are scanned **except** those matching the excluded paths.

```yaml
exclude:
  - tests/**
  - scripts/**

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

All files are scanned by default, but `tests/` and `scripts/` are skipped. This is useful when you want broad coverage but need to exclude generated code, fixtures, or tooling directories.

---

### Both `include` and `exclude`

When both keys are present, `include` is applied first and `exclude` is applied to that result.

```yaml
include:
  - src

exclude:
  - src/generated/**

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

Step-by-step:

1. Start with all `.py` files under the project root.
2. Keep only files under `src/` (apply `include`).
3. Remove files under `src/generated/` (apply `exclude`).

The result is all files under `src/` except those in `src/generated/`.

---

## Summary

| `include` | `exclude` | Files scanned |
|-----------|-----------|--------------|
| Not set | Not set | All `.py` files under project root |
| Set | Not set | Only files matching `include` paths |
| Not set | Set | All files **except** those matching `exclude` paths |
| Set | Set | Files matching `include`, then filtered by `exclude` |

!!! note
    `include` and `exclude` control the file scanning scope. The `modules` patterns in `apply` blocks are evaluated against the scanned files — so a file excluded here will never be checked, regardless of what `modules` patterns are defined.
