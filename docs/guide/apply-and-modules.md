# Apply & Modules

The `apply` block connects rules to the parts of your codebase where they should be enforced. Without an `apply` entry, a rule is defined but never executed.

---

## The `apply` Block

Each entry in `apply` is a named group that maps one or more rules to one or more modules:

```yaml
apply:
  - name: domain-layer        # A label for this group (used in output)
    rules:                    # Rules to enforce in this group
      - attribute-matches-type
      - bool-method-prefix
    modules: contexts.*.domain  # Module path pattern to match
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable label for this application group |
| `rules` | Yes | List of rule names to enforce (must be defined in the `rules` block) |
| `modules` | Yes | A module path pattern that selects which files to check |

### Inline syntax

For short rule lists, you can use inline YAML syntax:

```yaml
apply:
  - name: all
    rules: [bool-method-prefix, exception-naming]
    modules: "**"
```

---

## Module Path Patterns

Module paths use Python's dotted notation — the same way you would import them. For example, `src/domain/service.py` becomes `src.domain.service`.

### Exact match

To target a single module, write its full dotted path:

```yaml
modules: myapp.core.utils
```

This matches only the file `myapp/core/utils.py`.

---

## Wildcards

### `*` — Single level

`*` matches exactly one segment in a dotted module path. It cannot match across dots.

```yaml
modules: contexts.*.domain
```

This matches:

- `contexts.boards.domain`
- `contexts.auth.domain`
- `contexts.payments.domain`

But **not:**

- `contexts.domain` (missing the middle segment)
- `contexts.boards.sub.domain` (too many levels between `contexts` and `domain`)

**Example:**

```yaml
apply:
  - name: domain-layer
    rules: [attribute-matches-type]
    modules: contexts.*.domain
```

---

### `**` — One or more levels

`**` matches one or more segments. Use it to select all modules under a path, regardless of depth.

```yaml
modules: contexts.**.domain
```

This matches:

- `contexts.boards.domain`
- `contexts.boards.sub.domain`
- `contexts.a.b.c.domain`

**Example — apply a rule to the entire codebase:**

```yaml
apply:
  - name: all
    rules: [bool-method-prefix]
    modules: "**"
```

The `"**"` pattern matches every module in the project. Use quotes to avoid YAML parsing issues.

**Example — apply rules to all modules under a sub-package:**

```yaml
apply:
  - name: services
    rules: [function-snake-case]
    modules: myapp.services.**
```

---

## Named Capture

`{name}` captures a single path segment (equivalent to `*`) and makes the captured value available for back-referencing within the same pattern.

```yaml
modules: contexts.{context}.domain
```

This behaves like `contexts.*.domain` but the captured value (e.g. `boards`) is bound to the name `context`. You can reference it later in the same pattern using `{context}`.

### Back-referencing example

Named captures are useful when you want to enforce that two parts of a path are related — for example, that a submodule name must match its parent package name:

```yaml
apply:
  - name: domain-isolation
    rules: [attribute-matches-type]
    modules: contexts.{context}.domain
```

In this example, every module matching `contexts.<anything>.domain` is selected, and the middle segment is captured as `context`. This can be used in rule logic that references the captured value, enabling context-aware enforcement.

---

## Multiple Apply Groups

You can define multiple `apply` groups to apply different rules to different parts of your codebase:

```yaml
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

Here, the domain-specific rules are enforced only in `contexts.*.domain`, while `exception-naming` is enforced everywhere. A single module can be matched by multiple groups — all matching rules will be applied.
