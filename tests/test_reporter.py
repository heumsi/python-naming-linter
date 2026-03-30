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
