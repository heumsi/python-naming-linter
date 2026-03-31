# Rules

Rules are the core building blocks of `pnl`. Each rule targets a specific kind of Python name, optionally narrows its scope with filters, and then enforces a naming constraint.

## Structure

Every rule has three required fields and two optional ones:

```yaml
rules:
  - name: my-rule          # Unique identifier for this rule
    type: variable         # What kind of name to lint
    filter: { ... }        # (optional) Narrow which names are checked
    naming: { ... }        # How the name must be formed
```

The `name` is used to reference the rule in `apply` blocks and in `# pnl: ignore` comments.

---

## Summary

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, referenced in `apply` and `# pnl: ignore` |
| `type` | Yes | What kind of name to lint (`variable`, `function`, `class`, `module`, `package`) |
| `filter` | No | Narrow which names are checked (see [Filters](filters.md)) |
| `naming` | Yes | How the name must be formed (see [Naming Constraints](naming-constraints.md)) |
