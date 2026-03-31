from python_naming_linter.checkers import Violation
from python_naming_linter.ignore import filter_violations, parse_ignore_comments


class TestParseIgnoreComments:
    def test_no_comments(self):
        source = "x: int = 1\ny: str = 'hello'\n"
        assert parse_ignore_comments(source) == {}

    def test_ignore_all(self):
        source = "x: int = 1  # pnl: ignore\n"
        assert parse_ignore_comments(source) == {1: None}

    def test_ignore_single_rule(self):
        source = "x: int = 1  # pnl: ignore=my-rule\n"
        assert parse_ignore_comments(source) == {1: {"my-rule"}}

    def test_ignore_multiple_rules(self):
        source = "x: int = 1  # pnl: ignore=rule-a,rule-b\n"
        assert parse_ignore_comments(source) == {1: {"rule-a", "rule-b"}}

    def test_ignore_multiple_rules_with_spaces(self):
        source = "x: int = 1  # pnl: ignore=rule-a, rule-b\n"
        assert parse_ignore_comments(source) == {1: {"rule-a", "rule-b"}}

    def test_multiple_lines(self):
        source = (
            "x: int = 1  # pnl: ignore\n"
            "y: str = 'hello'\n"
            "z = 3  # pnl: ignore=my-rule\n"
        )
        result = parse_ignore_comments(source)
        assert result == {1: None, 3: {"my-rule"}}

    def test_comment_only_line(self):
        source = "# pnl: ignore\nx: int = 1\n"
        assert parse_ignore_comments(source) == {1: None}

    def test_no_space_after_hash(self):
        source = "x: int = 1  #pnl: ignore\n"
        assert parse_ignore_comments(source) == {1: None}

    def test_extra_space_after_pnl(self):
        source = "x: int = 1  # pnl:  ignore\n"
        assert parse_ignore_comments(source) == {1: None}

    def test_ignore_rule_with_dot(self):
        source = "x: int = 1  # pnl: ignore=shared.domain\n"
        assert parse_ignore_comments(source) == {1: {"shared.domain"}}

    def test_ignore_multiple_rules_with_dots(self):
        source = "x: int = 1  # pnl: ignore=shared.domain,context.adapters\n"
        assert parse_ignore_comments(source) == {
            1: {"shared.domain", "context.adapters"}
        }


class TestFilterViolations:
    def _make_violation(self, rule_name: str, lineno: int) -> Violation:
        return Violation(
            rule_name=rule_name,
            file_path="test.py",
            lineno=lineno,
            name="x",
            message="bad name",
        )

    def test_no_ignores(self):
        violations = [self._make_violation("rule-a", 1)]
        result = filter_violations(violations, {})
        assert len(result) == 1

    def test_ignore_all_on_line(self):
        violations = [
            self._make_violation("rule-a", 1),
            self._make_violation("rule-b", 1),
        ]
        result = filter_violations(violations, {1: None})
        assert result == []

    def test_ignore_specific_rule(self):
        violations = [
            self._make_violation("rule-a", 1),
            self._make_violation("rule-b", 1),
        ]
        result = filter_violations(violations, {1: {"rule-a"}})
        assert len(result) == 1
        assert result[0].rule_name == "rule-b"

    def test_ignore_does_not_affect_other_lines(self):
        violations = [
            self._make_violation("rule-a", 1),
            self._make_violation("rule-a", 2),
        ]
        result = filter_violations(violations, {1: None})
        assert len(result) == 1
        assert result[0].lineno == 2

    def test_ignore_multiple_rules(self):
        violations = [
            self._make_violation("rule-a", 1),
            self._make_violation("rule-b", 1),
            self._make_violation("rule-c", 1),
        ]
        result = filter_violations(violations, {1: {"rule-a", "rule-b"}})
        assert len(result) == 1
        assert result[0].rule_name == "rule-c"
