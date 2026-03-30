import ast

from python_naming_linter.checkers.function import check_function
from python_naming_linter.config import Rule


def _parse(source: str) -> ast.Module:
    return ast.parse(source)


def test_bool_method_prefix_pass():
    source = """\
class MyService:
    def is_valid(self) -> bool:
        return True
"""
    rule = Rule(
        name="bool-prefix",
        type="function",
        filter={"return_type": "bool"},
        naming={"prefix": ["is_", "has_", "should_"]},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    assert violations == []


def test_bool_method_prefix_violation():
    source = """\
class MyService:
    def validate(self) -> bool:
        return True
"""
    rule = Rule(
        name="bool-prefix",
        type="function",
        filter={"return_type": "bool"},
        naming={"prefix": ["is_", "has_", "should_"]},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    assert len(violations) == 1
    assert violations[0].name == "validate"


def test_non_bool_method_not_checked():
    source = """\
class MyService:
    def execute(self) -> str:
        return "ok"
"""
    rule = Rule(
        name="bool-prefix",
        type="function",
        filter={"return_type": "bool"},
        naming={"prefix": ["is_", "has_", "should_"]},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    assert violations == []


def test_function_regex_pass():
    source = """\
def find_by_id(id: int) -> None:
    pass
"""
    rule = Rule(
        name="func-regex",
        type="function",
        naming={"regex": "^[a-z]+_"},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    assert violations == []


def test_method_only_filter():
    source = """\
def standalone() -> bool:
    return True

class MyService:
    def is_valid(self) -> bool:
        return True
"""
    rule = Rule(
        name="method-bool",
        type="function",
        filter={"target": "method", "return_type": "bool"},
        naming={"prefix": ["is_", "has_", "should_"]},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    # standalone is a function, not method - should be skipped
    assert violations == []


def test_dunder_methods_skipped():
    source = """\
class MyService:
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return ""
"""
    rule = Rule(
        name="func-regex",
        type="function",
        naming={"regex": "^[a-z]+_[a-z]+"},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    assert violations == []


def test_private_methods_checked():
    source = """\
class MyService:
    def _validate(self) -> bool:
        return True
"""
    rule = Rule(
        name="bool-prefix",
        type="function",
        filter={"return_type": "bool"},
        naming={"prefix": ["is_", "has_", "should_", "_is_", "_has_", "_should_"]},
    )
    tree = _parse(source)
    violations = check_function(tree, rule, "test.py")
    assert len(violations) == 1
    assert violations[0].name == "_validate"
