# Inline Ignore

Sometimes a specific line legitimately violates a naming rule — a third-party interface, a legacy name you cannot change, or a deliberate exception to your convention. Rather than disabling the rule globally or restructuring your config, you can suppress violations on a per-line basis using inline ignore comments.

---

## Ignore all rules on a line

Add `# pnl: ignore` at the end of a line to suppress all `pnl` violations reported for that line:

```python
x: int = 1  # pnl: ignore
```

Any rule that would have flagged the name on this line is silenced. This is the broadest form of suppression — use it when multiple rules apply and you want to silence all of them at once.

---

## Ignore a specific rule on a line

To suppress only one rule, specify the rule name after `=`:

```python
x: int = 1  # pnl: ignore=attribute-matches-type
```

Only the `attribute-matches-type` rule is suppressed on this line. Any other rules that match this line will still report violations.

The rule name must exactly match the `name` field defined in your config:

```yaml
rules:
  - name: attribute-matches-type   # This is the name to use in ignore comments
    type: variable
    filter: { target: attribute }
    naming: { source: type_annotation, transform: snake_case }
```

---

## Ignore multiple specific rules on a line

To suppress more than one rule on the same line, list rule names separated by commas:

```python
x: int = 1  # pnl: ignore=attribute-matches-type,constant-upper-case
```

Both `attribute-matches-type` and `constant-upper-case` are suppressed on this line. There is no space around the commas.

---

## Practical examples

**Suppressing a legacy attribute name that doesn't match its type:**

```python
class UserService:
    repo: UserRepository  # pnl: ignore=attribute-matches-type
```

**Suppressing a constant that follows a third-party naming convention:**

```python
# Required by the framework to be this exact name
default_app_config = "myapp.apps.MyAppConfig"  # pnl: ignore=constant-upper-case
```

**Suppressing all rules on a generated or protocol-required name:**

```python
def __repr__(self) -> str:  # pnl: ignore
    ...
```

---

## Notes

- Inline ignore comments apply only to the line they appear on. They do not affect other lines.
- Rule names are case-sensitive and must match exactly.
- If you specify a rule name that does not exist in your config, the comment is silently ignored — no error is raised.
- Prefer targeted suppression (`# pnl: ignore=rule-name`) over blanket suppression (`# pnl: ignore`) so that future rules are not accidentally silenced.
