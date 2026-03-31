# Rules

Rules are the core building blocks of `pnl`. Each rule targets a specific kind of Python name, optionally narrows its scope with filters, and then enforces a naming constraint.

## Structure

Every rule has three required fields and three optional ones:

```yaml
rules:
  - name: my-rule          # Unique identifier for this rule
    description: ...       # (optional) Human-readable description shown in violation output
    type: variable         # What kind of name to lint
    filter: { ... }        # (optional) Narrow which names are checked
    naming: { ... }        # How the name must be formed
```

The `name` is used to reference the rule in `apply` blocks and in `# pnl: ignore` comments.

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, referenced in `apply` and `# pnl: ignore`. Must match `[a-zA-Z0-9_.-]+` |
| `description` | No | Human-readable description shown in violation output |
| `type` | Yes | What kind of name to lint (`variable`, `function`, `class`, `module`, `package`) |
| `filter` | No | Narrow which names are checked (see [Filters](#filters) below) |
| `naming` | Yes | How the name must be formed (see [Naming Constraints](#naming-constraints) below) |

---

## Types

### `variable`

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

### `function`

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

### `class`

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

### `module`

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

### `package`

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

## Filters

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

### `target`

Narrows which names within the rule type are checked based on their role in the code.

#### For `variable` rules

| Value | Matches |
|-------|---------|
| `attribute` | Class-level attribute assignments, including annotated attributes (`x: int = 1`) |
| `parameter` | Function or method parameters |
| `local_variable` | Variables assigned inside a function body |
| `constant` | Module-level assignments (typically treated as constants) |

**Supported rule types:** `variable`

**Example — lint only class attributes:**

Matches names that are assigned at the class body level, including annotated attributes.

```yaml
rules:
  - name: attribute-matches-type
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }

apply:
  - name: all
    rules: [attribute-matches-type]
    modules: "**"
```

| Name | Context | Result |
|------|---------|--------|
| `user_id: UserId = ...` | class body | Pass — name matches type annotation in snake_case |
| `userId: UserId = ...` | class body | **Violation** — name does not match `user_id` |
| `user_id = 1` | function body | Not checked — local variables are ignored |

---

**Example — lint only function/method parameters:**

Matches names declared as function or method parameters (including `self` and `cls` by convention — though you may want to exclude them with additional patterns).

```yaml
rules:
  - name: param-snake-case
    type: variable
    filter: { target: parameter }
    naming: { case: snake_case }

apply:
  - name: all
    rules: [param-snake-case]
    modules: "**"
```

| Name | Context | Result |
|------|---------|--------|
| `user_id` | function parameter | Pass — snake_case |
| `userId` | function parameter | **Violation** — camelCase not allowed |
| `MAX_RETRIES` | module level | Not checked — constants are ignored |

---

**Example — lint only local variables inside functions:**

Matches names assigned inside a function or method body (not parameters, not class-level attributes).

```yaml
rules:
  - name: local-var-snake-case
    type: variable
    filter: { target: local_variable }
    naming: { case: snake_case }

apply:
  - name: all
    rules: [local-var-snake-case]
    modules: "**"
```

| Name | Context | Result |
|------|---------|--------|
| `result` | inside function body | Pass — snake_case |
| `tmpVal` | inside function body | **Violation** — camelCase not allowed |
| `MAX_SIZE` | module level | Not checked — constants are ignored |

---

**Example — lint only module-level constants:**

Matches names assigned at module (top-level) scope.

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

| Name | Context | Result |
|------|---------|--------|
| `MAX_RETRIES` | module level | Pass — UPPER_CASE |
| `defaultTimeout` | module level | **Violation** — not UPPER_CASE |
| `count` | function body | Not checked — local variables are ignored |

---

#### For `function` rules

| Value | Matches |
|-------|---------|
| `method` | Functions defined inside a class body |
| `function` | Functions defined at module level or inside other functions |

**Supported rule types:** `function`

**Example — lint only module-level functions (not methods):**

Matches `def` statements at module scope or nested inside other functions, but not methods defined inside a class.

```yaml
rules:
  - name: function-snake-case
    type: function
    filter: { target: function }
    naming: { case: snake_case }

apply:
  - name: all
    rules: [function-snake-case]
    modules: "**"
```

| Name | Context | Result |
|------|---------|--------|
| `process_order` | module-level `def` | Pass — snake_case |
| `processOrder` | module-level `def` | **Violation** — camelCase not allowed |
| `processOrder` | inside a class | Not checked — methods are ignored |

---

**Example — lint only class methods:**

Matches `def` statements inside a class body.

```yaml
rules:
  - name: method-snake-case
    type: function
    filter: { target: method }
    naming: { case: snake_case }

apply:
  - name: all
    rules: [method-snake-case]
    modules: "**"
```

| Name | Context | Result |
|------|---------|--------|
| `get_user` | inside a class | Pass — snake_case |
| `getUser` | inside a class | **Violation** — camelCase not allowed |
| `getUser` | module-level `def` | Not checked — functions are ignored |

---

### `return_type`

Matches functions whose return type annotation equals the specified type name.

**Supported rule types:** `function`

**Accepted values:** any Python type name as a string, e.g. `bool`, `str`, `int`, `None`

The filter matches functions with the given `-> <type>` annotation. Functions without a return type annotation, or with a different annotation, are not checked.

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

| Signature | Result |
|-----------|--------|
| `def is_active(self) -> bool:` | Pass — starts with `is_` |
| `def has_permission(self) -> bool:` | Pass — starts with `has_` |
| `def validate(self) -> bool:` | **Violation** — no matching prefix |
| `def process(self) -> str:` | Not checked — return type is `str`, not `bool` |
| `def run(self):` | Not checked — no return type annotation |

---

**Example — require a descriptive prefix on `str`-returning functions:**

```yaml
rules:
  - name: str-getter-prefix
    type: function
    filter: { return_type: str }
    naming: { prefix: [get_, format_, build_, to_] }

apply:
  - name: all
    rules: [str-getter-prefix]
    modules: "**"
```

| Signature | Result |
|-----------|--------|
| `def get_name(self) -> str:` | Pass — starts with `get_` |
| `def format_label(self) -> str:` | Pass — starts with `format_` |
| `def name(self) -> str:` | **Violation** — no matching prefix |
| `def is_active(self) -> bool:` | Not checked — return type is `bool`, not `str` |

---

**Example — require a `_or_none` suffix on `None`-returning functions:**

```yaml
rules:
  - name: none-returning-suffix
    type: function
    filter: { return_type: None }
    naming: { suffix: [_or_none] }

apply:
  - name: all
    rules: [none-returning-suffix]
    modules: "**"
```

| Signature | Result |
|-----------|--------|
| `def find_user_or_none(self) -> None:` | Pass — ends with `_or_none` |
| `def find_user(self) -> None:` | **Violation** — missing `_or_none` suffix |
| `def find_user(self) -> User:` | Not checked — return type is `User`, not `None` |

---

### `decorator`

Matches functions or classes that are decorated with the specified decorator name.

**Supported rule types:** `function`, `class`

**Accepted values:** any decorator name as a string (without `@`), e.g. `staticmethod`, `classmethod`, `property`, `dataclass`, `abstractmethod`

The filter matches the decorator by its bare name. Both `@dataclass` and `@dataclasses.dataclass` are matched by the value `dataclass`.

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

| Definition | Result |
|------------|--------|
| `@staticmethod` / `def compute_impl(cls):` | Pass — ends with `_impl` |
| `@staticmethod` / `def compute(cls):` | **Violation** — missing `_impl` suffix |
| `def compute(self):` | Not checked — not a static method |

---

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

| Definition | Result |
|------------|--------|
| `@dataclass` / `class UserDTO:` | Pass — ends with `DTO` |
| `@dataclass` / `class User:` | **Violation** — missing `DTO` suffix |
| `class User:` | Not checked — not a dataclass |

---

### `base_class`

Matches classes that inherit from the specified base class.

**Supported rule types:** `class`

**Accepted values:** any class name as a string, e.g. `Exception`, `BaseModel`, `ABC`

The filter matches the direct base class name. `class MyError(Exception)` matches the value `Exception`.

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

| Definition | Result |
|------------|--------|
| `class UserNotFoundError(Exception):` | Pass — matches the regex |
| `class InvalidInputError(Exception):` | Pass — matches the regex |
| `class UserException(Exception):` | **Violation** — does not match the regex |
| `class User:` | Not checked — does not inherit from `Exception` |

---

**Example — require a `Schema` suffix on Pydantic models:**

Matches classes that inherit from `BaseModel` (e.g. Pydantic models).

```yaml
rules:
  - name: pydantic-schema-suffix
    type: class
    filter: { base_class: BaseModel }
    naming: { suffix: [Schema] }

apply:
  - name: all
    rules: [pydantic-schema-suffix]
    modules: "**"
```

| Definition | Result |
|------------|--------|
| `class UserSchema(BaseModel):` | Pass — ends with `Schema` |
| `class CreateUserSchema(BaseModel):` | Pass — ends with `Schema` |
| `class User(BaseModel):` | **Violation** — missing `Schema` suffix |
| `class User:` | Not checked — does not inherit from `BaseModel` |

---

## Naming Constraints

Naming constraints are specified in the `naming` block of a rule:

```yaml
rules:
  - name: my-rule
    type: function
    naming: { prefix: [is_, has_] }
apply:
  - name: all
    rules: [my-rule]
    modules: "**"
```

Each rule must have exactly one naming constraint (or one `source` + `transform` pair). The constraint is evaluated against every name that passes the rule's type and filter checks.

---

### `prefix`

The name must start with one of the listed prefixes.

**Accepted values:** a list of one or more prefix strings.

**Example — bool-returning methods must use a semantic prefix:**

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

| Name | Result |
|------|--------|
| `is_active` | Pass — starts with `is_` |
| `has_permission` | Pass — starts with `has_` |
| `should_retry` | Pass — starts with `should_` |
| `validate` | **Violation** — no matching prefix |
| `check_active` | **Violation** — `check_` is not in the list |

**Example — test functions must start with `test_`:**

```yaml
rules:
  - name: test-function-prefix
    type: function
    filter: { decorator: pytest.mark }
    naming: { prefix: [test_] }
apply:
  - name: all
    rules: [test-function-prefix]
    modules: "**"
```

| Name | Result |
|------|--------|
| `test_login_succeeds` | Pass — starts with `test_` |
| `test_invalid_token` | Pass — starts with `test_` |
| `login_succeeds` | **Violation** — missing `test_` prefix |
| `check_login` | **Violation** — `check_` is not in the list |

---

### `suffix`

The name must end with one of the listed suffixes.

**Accepted values:** a list of one or more suffix strings.

**Example — data-access classes must end with `Repository` or `Service`:**

```yaml
rules:
  - name: repository-suffix
    type: class
    naming: { suffix: [Repository, Service] }
apply:
  - name: all
    rules: [repository-suffix]
    modules: "**"
```

| Name | Result |
|------|--------|
| `UserRepository` | Pass — ends with `Repository` |
| `OrderService` | Pass — ends with `Service` |
| `UserManager` | **Violation** — no matching suffix |
| `User` | **Violation** — no matching suffix |

**Example — exception classes must end with `Error`:**

```yaml
rules:
  - name: exception-suffix
    type: class
    filter: { base_class: Exception }
    naming: { suffix: [Error] }
apply:
  - name: all
    rules: [exception-suffix]
    modules: "**"
```

| Name | Result |
|------|--------|
| `ValidationError` | Pass — ends with `Error` |
| `NotFoundError` | Pass — ends with `Error` |
| `InvalidInput` | **Violation** — does not end with `Error` |
| `NotFoundException` | **Violation** — ends with `Exception`, not `Error` |

---

### `regex`

The name must match a regular expression.

**Accepted values:** a string containing a valid Python regular expression.

This is the most expressive constraint — use it when `prefix`, `suffix`, or `case` are not specific enough.

**Example — exception class names must follow a structured pattern:**

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

| Name | Result |
|------|--------|
| `UserNotFoundError` | Pass — matches the pattern |
| `OrderInvalidError` | Pass — matches the pattern |
| `FilterError` | **Violation** — does not end with the required suffix group |
| `userNotFoundError` | **Violation** — does not start with an uppercase letter |

**Example — module-level constants must be all-uppercase with underscores:**

```yaml
rules:
  - name: constant-regex
    type: variable
    filter: { target: constant }
    naming: { regex: "^[A-Z][A-Z0-9_]*$" }
apply:
  - name: all
    rules: [constant-regex]
    modules: "**"
```

| Name | Result |
|------|--------|
| `MAX_RETRIES` | Pass — all uppercase with underscores |
| `DEFAULT_TIMEOUT` | Pass — all uppercase with underscores |
| `API_V2_URL` | Pass — uppercase with digits and underscores |
| `max_retries` | **Violation** — lowercase |
| `MaxRetries` | **Violation** — mixed case |
| `_PRIVATE` | **Violation** — starts with underscore, not matched by `^[A-Z]` |

---

### `source` + `transform`

The name must be derived from another element in the code, after applying a transformation. This is used for relational naming — where the name of one thing must reflect another.

Both fields must be specified together.

#### `source` values

| Value | What it reads |
|-------|--------------|
| `type_annotation` | The type annotation of the variable (e.g. `SubscriptionRepository` from `x: SubscriptionRepository`) |
| `class_name` | The name of a class defined in the module (used with `type: module`) |

#### `transform` values

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
apply:
  - name: all
    rules: [attribute-matches-type]
    modules: "**"
```

| Declaration | Result |
|-------------|--------|
| `subscription_repository: SubscriptionRepository` | Pass — name matches transformed type |
| `order_service: OrderService` | Pass — name matches transformed type |
| `repo: SubscriptionRepository` | **Violation** — `repo` does not match `subscription_repository` |
| `svc: OrderService` | **Violation** — `svc` does not match `order_service` |
| `source_object_context: ObjectContext` | Pass — name ends with `_object_context` (prefix + expected form is allowed) |

The `{prefix}_{expected}` form is accepted. If the expected derived name is `object_context`, then `source_object_context` passes because it ends with `_object_context`.

**Example — module filename must match the class it contains:**

```yaml
rules:
  - name: domain-module-naming
    type: module
    naming: { source: class_name, transform: snake_case }
apply:
  - name: all
    rules: [domain-module-naming]
    modules: "**"
```

| File | Class | Result |
|------|-------|--------|
| `custom_object.py` | `CustomObject` | Pass — filename matches transformed class name |
| `order_service.py` | `OrderService` | Pass — filename matches transformed class name |
| `custom.py` | `CustomObject` | **Violation** — `custom` does not match `custom_object` |
| `service.py` | `OrderService` | **Violation** — `service` does not match `order_service` |

---

### `case`

The name must follow a specific casing convention.

**Accepted values:**

| Value | Pattern | Example |
|-------|---------|---------|
| `snake_case` | all lowercase, words separated by underscores | `my_variable_name` |
| `PascalCase` | each word starts with uppercase, no separators | `MyClassName` |
| `UPPER_CASE` | all uppercase, words separated by underscores | `MAX_RETRIES` |

**Example — enforce `snake_case` for function names:**

```yaml
rules:
  - name: function-snake-case
    type: function
    naming: { case: snake_case }
apply:
  - name: all
    rules: [function-snake-case]
    modules: "**"
```

| Name | Result |
|------|--------|
| `get_user` | Pass |
| `calculate_total_price` | Pass |
| `getUserById` | **Violation** — camelCase |
| `GetUser` | **Violation** — PascalCase |
| `GETUSER` | **Violation** — all uppercase |

**Example — enforce UPPER_CASE for constants:**

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
apply:
  - name: all
    rules: [class-pascal-case]
    modules: "**"
```

| Name | Result |
|------|--------|
| `MyService` | Pass |
| `my_service` | **Violation** |
| `myService` | **Violation** |

---

## Summary

### Rule fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier, referenced in `apply` and `# pnl: ignore`. Must match `[a-zA-Z0-9_.-]+` |
| `description` | No | Human-readable description shown in violation output |
| `type` | Yes | What kind of name to lint (`variable`, `function`, `class`, `module`, `package`) |
| `filter` | No | Narrow which names are checked |
| `naming` | Yes | How the name must be formed |

### Rule types

| Type | What it targets | Supported filters | Notes |
|------|----------------|-------------------|-------|
| `variable` | Variables by scope/role | `target` | Use `target` to narrow to attributes, parameters, etc. |
| `function` | Function and method definitions | `target`, `return_type`, `decorator` | |
| `class` | Class definitions | `base_class`, `decorator` | |
| `module` | Module (file) names | none | Supports `source` + `transform` |
| `package` | Package (directory) names | none | |

### Filters

| Filter | `variable` | `function` | `class` | `module` | `package` |
|--------|-----------|-----------|---------|---------|---------|
| `target` | `attribute`, `parameter`, `local_variable`, `constant` | `method`, `function` | — | — | — |
| `return_type` | — | any type string | — | — | — |
| `decorator` | — | any decorator name | any decorator name | — | — |
| `base_class` | — | — | any class name | — | — |

### Naming constraints

| Constraint | Value type | Use when |
|-----------|-----------|---------|
| `prefix` | list of strings | Names must start with one of several prefixes |
| `suffix` | list of strings | Names must end with one of several suffixes |
| `regex` | string (regex) | Names must match a complex pattern |
| `source` + `transform` | string + string | Names must be derived from another code element |
| `case` | `snake_case`, `PascalCase`, or `UPPER_CASE` | Names must follow a casing convention |
