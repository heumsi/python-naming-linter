# Naming Constraints

Naming constraints define how a name must be formed. They are specified in the `naming` block of a rule:

```yaml
rules:
  - name: my-rule
    type: function
    naming: { prefix: [is_, has_] }
```

Each rule must have exactly one naming constraint (or one `source` + `transform` pair). The constraint is evaluated against every name that passes the rule's type and filter checks.

---

## `prefix`

The name must start with one of the listed prefixes.

**Accepted value:** a list of one or more prefix strings.

**Example:**

```yaml
rules:
  - name: bool-method-prefix
    type: function
    filter: { return_type: bool }
    naming: { prefix: [is_, has_, should_] }
```

| Name | Result |
|------|--------|
| `is_active` | Pass — starts with `is_` |
| `has_permission` | Pass — starts with `has_` |
| `should_retry` | Pass — starts with `should_` |
| `validate` | **Violation** — no matching prefix |
| `check_active` | **Violation** — `check_` is not in the list |

**Violation message example:**

```
[bool-method-prefix] validate (expected prefix: is_ | has_ | should_)
```

---

## `suffix`

The name must end with one of the listed suffixes.

**Accepted value:** a list of one or more suffix strings.

**Example:**

```yaml
rules:
  - name: repository-suffix
    type: class
    naming: { suffix: [Repository, Service] }
```

| Name | Result |
|------|--------|
| `UserRepository` | Pass — ends with `Repository` |
| `OrderService` | Pass — ends with `Service` |
| `UserManager` | **Violation** — no matching suffix |
| `User` | **Violation** — no matching suffix |

**Violation message example:**

```
[repository-suffix] UserManager (expected suffix: Repository | Service)
```

---

## `regex`

The name must match a regular expression.

**Accepted value:** a string containing a valid Python regular expression.

This is the most expressive constraint — use it when `prefix`, `suffix`, or `case` are not specific enough.

**Example:**

```yaml
rules:
  - name: exception-naming
    type: class
    filter: { base_class: Exception }
    naming: { regex: "^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$" }
```

| Name | Result |
|------|--------|
| `UserNotFoundError` | Pass — matches the pattern |
| `OrderInvalidError` | Pass — matches the pattern |
| `FilterError` | **Violation** — does not end with the required suffix group |
| `userNotFoundError` | **Violation** — does not start with an uppercase letter |

**Violation message example:**

```
[exception-naming] FilterError (expected pattern: ^[A-Z][a-zA-Z]+(NotFound|Invalid|...)Error$)
```

---

## `source` + `transform`

The name must be derived from another element in the code, after applying a transformation. This is used for relational naming — where the name of one thing must reflect another.

Both fields must be specified together.

### `source` values

| Value | What it reads |
|-------|--------------|
| `type_annotation` | The type annotation of the variable (e.g. `SubscriptionRepository` from `x: SubscriptionRepository`) |
| `class_name` | The name of a class defined in the module (used with `type: module`) |

### `transform` values

| Value | What it does |
|-------|-------------|
| `snake_case` | Converts PascalCase or camelCase to snake_case (e.g. `SubscriptionRepository` → `subscription_repository`) |

**Example — variable name must match its type annotation:**

```yaml
rules:
  - name: attribute-matches-type
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }
```

| Declaration | Result |
|-------------|--------|
| `subscription_repository: SubscriptionRepository` | Pass — name matches transformed type |
| `repo: SubscriptionRepository` | **Violation** — `repo` does not match `subscription_repository` |
| `source_object_context: ObjectContext` | Pass — name ends with `_object_context` (prefix + expected form is allowed) |

The `{prefix}_{expected}` form is accepted. If the expected derived name is `object_context`, then `source_object_context` passes because it ends with `_object_context`.

**Example — module filename must match the class it contains:**

```yaml
rules:
  - name: domain-module-naming
    type: module
    naming: { source: class_name, transform: snake_case }
```

| File | Class | Result |
|------|-------|--------|
| `custom_object.py` | `CustomObject` | Pass — filename matches transformed class name |
| `custom.py` | `CustomObject` | **Violation** — `custom` does not match `custom_object` |

---

## `case`

The name must follow a specific casing convention.

**Accepted values:**

| Value | Pattern | Example |
|-------|---------|---------|
| `snake_case` | all lowercase, words separated by underscores | `my_variable_name` |
| `PascalCase` | each word starts with uppercase, no separators | `MyClassName` |
| `UPPER_CASE` | all uppercase, words separated by underscores | `MAX_RETRIES` |

**Example — enforce UPPER_CASE for constants:**

```yaml
rules:
  - name: constant-upper-case
    type: variable
    filter: { target: constant }
    naming: { case: UPPER_CASE }
```

| Name | Result |
|------|--------|
| `MAX_RETRIES` | Pass |
| `DEFAULT_TIMEOUT` | Pass |
| `max_retries` | **Violation** — lowercase |
| `maxRetries` | **Violation** — camelCase |

**Example — enforce PascalCase for classes:**

```yaml
rules:
  - name: class-pascal-case
    type: class
    naming: { case: PascalCase }
```

| Name | Result |
|------|--------|
| `MyService` | Pass |
| `my_service` | **Violation** |
| `myService` | **Violation** |

---

## Summary Table

| Constraint | Value type | Use when |
|-----------|-----------|---------|
| `prefix` | list of strings | Names must start with one of several prefixes |
| `suffix` | list of strings | Names must end with one of several suffixes |
| `regex` | string (regex) | Names must match a complex pattern |
| `source` + `transform` | string + string | Names must be derived from another code element |
| `case` | `snake_case`, `PascalCase`, or `UPPER_CASE` | Names must follow a casing convention |
