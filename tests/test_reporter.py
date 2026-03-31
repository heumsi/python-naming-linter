from python_naming_linter.checkers import Violation
from python_naming_linter.reporter import format_violations


def test_format_single_violation():
    violations = [
        Violation(
            rule_name="attr-naming",
            file_path="src/domain/models.py",
            lineno=15,
            name="repo",
            message="expected: subscription_repository",
        )
    ]
    output = format_violations("src/domain/models.py", violations)
    assert "src/domain/models.py:15" in output
    assert "[attr-naming]" in output
    assert "repo" in output
    assert "subscription_repository" in output


def test_format_violation_with_description():
    violations = [
        Violation(
            rule_name="bool-method-prefix",
            file_path="src/service.py",
            lineno=4,
            name="validate",
            message="expected prefix: is_ | has_ | should_",
            rule_description="Bool-returning functions must use a semantic prefix",
        )
    ]
    output = format_violations("src/service.py", violations)
    lines = output.strip().split("\n")
    assert lines[0] == "src/service.py:4"
    expected = (
        "    [bool-method-prefix] Bool-returning functions must use a semantic prefix"
    )
    assert lines[1] == expected
    assert lines[2] == "    validate (expected prefix: is_ | has_ | should_)"


def test_format_violation_without_description():
    violations = [
        Violation(
            rule_name="attr-naming",
            file_path="src/models.py",
            lineno=15,
            name="repo",
            message="expected: subscription_repository",
        )
    ]
    output = format_violations("src/models.py", violations)
    lines = output.strip().split("\n")
    assert lines[0] == "src/models.py:15"
    assert lines[1] == "    [attr-naming]"
    assert lines[2] == "    repo (expected: subscription_repository)"


def test_format_multiple_violations():
    violations = [
        Violation("r1", "f.py", 1, "a", "msg1"),
        Violation("r2", "f.py", 5, "b", "msg2"),
    ]
    output = format_violations("f.py", violations)
    assert "f.py:1" in output
    assert "f.py:5" in output


def test_format_empty():
    output = format_violations("f.py", [])
    assert output == ""
