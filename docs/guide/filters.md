# Filters

Filters let you narrow the scope of a rule so it only applies to a specific subset of names. Without a filter, a rule matches every name of its `type`. With a filter, only names that satisfy all filter conditions are checked.

---

## Structure

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

## Types

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

## Summary

| Filter | `variable` | `function` | `class` | `module` | `package` |
|--------|-----------|-----------|---------|---------|---------|
| `target` | `attribute`, `parameter`, `local_variable`, `constant` | `method`, `function` | — | — | — |
| `return_type` | — | any type string | — | — | — |
| `decorator` | — | any decorator name | any decorator name | — | — |
| `base_class` | — | — | any class name | — | — |
