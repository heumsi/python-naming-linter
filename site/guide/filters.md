# Filters

Filters let you narrow the scope of a rule so it only applies to a specific subset of names. Without a filter, a rule matches every name of its `type`. With a filter, only names that satisfy all filter conditions are checked.

Filters are specified in the `filter` block of a rule:

```yaml
rules:
  - name: my-rule
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_] }
```

Multiple filter fields can be combined — a name must satisfy **all** of them to be checked.

---

## `target`

Narrows which names within the rule type are checked based on their role in the code.

### For `variable` rules

| Value | Matches |
|-------|---------|
| `attribute` | Class-level attribute assignments, including annotated attributes (`x: int = 1`) |
| `parameter` | Function or method parameters |
| `local_variable` | Variables assigned inside a function body |
| `constant` | Module-level assignments (typically treated as constants) |

**Supported rule types:** `variable`

**Example — lint only class attributes:**

```yaml
rules:
  - name: attribute-matches-type
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }
```

**Example — lint only module-level constants:**

```yaml
rules:
  - name: constant-upper-case
    type: variable
    filter: { target: constant }
    naming: { case: UPPER_CASE }
```

### For `function` rules

| Value | Matches |
|-------|---------|
| `method` | Functions defined inside a class body |
| `function` | Functions defined at module level or inside other functions |

**Supported rule types:** `function`

**Example — lint only module-level functions (not methods):**

```yaml
rules:
  - name: function-snake-case
    type: function
    filter: { target: function }
    naming: { case: snake_case }
```

---

## `return_type`

Matches functions whose return type annotation equals the specified type name.

**Supported rule types:** `function`

**Accepted values:** any Python type name as a string, e.g. `bool`, `str`, `int`, `None`

**Example — require a boolean-indicating prefix on `bool`-returning functions:**

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

The filter matches functions with `-> bool` in their signature. Functions without a return type annotation, or with a different annotation, are not checked.

---

## `decorator`

Matches functions or classes that are decorated with the specified decorator name.

**Supported rule types:** `function`, `class`

**Accepted values:** any decorator name as a string (without `@`), e.g. `staticmethod`, `classmethod`, `property`, `dataclass`, `abstractmethod`

**Example — require a suffix on static methods:**

```yaml
rules:
  - name: static-method-suffix
    type: function
    filter: { decorator: staticmethod }
    naming: { suffix: [_impl] }

apply:
  - name: all
    rules: [static-method-suffix]
    modules: "**"
```

**Example — require a `DTO` suffix on dataclasses:**

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

The filter matches the decorator by its bare name. Both `@dataclass` and `@dataclasses.dataclass` are matched by the value `dataclass`.

---

## `base_class`

Matches classes that inherit from the specified base class.

**Supported rule types:** `class`

**Accepted values:** any class name as a string, e.g. `Exception`, `BaseModel`, `ABC`

**Example — enforce a naming pattern for all exception classes:**

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

The filter matches the direct base class name. `class MyError(Exception)` matches the value `Exception`.

---

## Filter Support by Rule Type

| Filter | `variable` | `function` | `class` | `module` | `package` |
|--------|-----------|-----------|---------|---------|---------|
| `target` | `attribute`, `parameter`, `local_variable`, `constant` | `method`, `function` | — | — | — |
| `return_type` | — | any type string | — | — | — |
| `decorator` | — | any decorator name | any decorator name | — | — |
| `base_class` | — | — | any class name | — | — |
