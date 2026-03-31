# Rules

Rules are the core building blocks of `pnl`. Each rule targets a specific kind of Python name, optionally narrows its scope with filters, and then enforces a naming constraint.

## Rule Structure

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

## `variable`

Targets variable names — any assignment that introduces a name into a scope.

**Sub-targets** (set via `filter.target`):

| Value | What it covers |
|-------|---------------|
| `attribute` | Class-level attributes (`self.x`, `x: int = ...`) |
| `parameter` | Function/method parameters |
| `local_variable` | Variables declared inside a function body |
| `constant` | Module-level constants (typically `ALL_CAPS`) |

**Supported filter fields:** `target`

**Supported naming fields:** `prefix`, `suffix`, `regex`, `source` + `transform`, `case`

**Example — enforce UPPER_CASE for module-level constants:**

```yaml
rules:
  - name: constant-upper-case
    type: variable
    filter: { target: constant }
    naming: { case: UPPER_CASE }

apply:
  - name: all
    rules: [constant-upper-case]
    modules: "**"
```

**Example — enforce attribute names match their type annotation:**

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

---

## `function`

Targets function and method definitions — any `def` statement at any scope level.

**Supported filter fields:** `target`, `return_type`, `decorator`

**Supported naming fields:** `prefix`, `suffix`, `regex`, `case`

**Example — require `is_` / `has_` / `should_` prefix on boolean-returning methods:**

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

**Example — require `_impl` suffix on `@staticmethod` functions:**

```yaml
rules:
  - name: static-impl-suffix
    type: function
    filter: { decorator: staticmethod }
    naming: { suffix: [_impl] }

apply:
  - name: all
    rules: [static-impl-suffix]
    modules: "**"
```

---

## `class`

Targets class definitions — any `class` statement.

**Supported filter fields:** `base_class`, `decorator`

**Supported naming fields:** `prefix`, `suffix`, `regex`, `case`

**Example — enforce a specific pattern for exception classes:**

```yaml
rules:
  - name: exception-naming
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }

apply:
  - name: all
    rules: [exception-naming]
    modules: "**"
```

**Example — require `DTO` suffix on dataclasses:**

```yaml
rules:
  - name: dataclass-dto-suffix
    type: class
    filter: { decorator: dataclass }
    naming: { suffix: [DTO] }

apply:
  - name: all
    rules: [dataclass-dto-suffix]
    modules: "**"
```

---

## `module`

Targets the filename of each `.py` file (without the `.py` extension). Useful for enforcing that module names reflect their contents.

**Supported filter fields:** none

**Supported naming fields:** `prefix`, `suffix`, `regex`, `source` + `transform`, `case`

**Example — enforce that a module's filename matches the primary class it contains:**

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

A file `custom.py` that contains only `class CustomObject` is a violation — the file should be named `custom_object.py`.

---

## `package`

Targets the directory name of each Python package (a directory containing `__init__.py`).

**Supported filter fields:** none

**Supported naming fields:** `prefix`, `suffix`, `regex`, `case`

**Example — require all package names to be lowercase:**

```yaml
rules:
  - name: package-snake-case
    type: package
    naming: { case: snake_case }

apply:
  - name: all
    rules: [package-snake-case]
    modules: "**"
```

---

## Summary

| Type | What it targets | Supported filters | Notes |
|------|----------------|-------------------|-------|
| `variable` | Variables by scope/role | `target` | Use `target` to narrow to attributes, parameters, etc. |
| `function` | Function and method definitions | `target`, `return_type`, `decorator` | |
| `class` | Class definitions | `base_class`, `decorator` | |
| `module` | Module (file) names | none | Supports `source` + `transform` |
| `package` | Package (directory) names | none | |
