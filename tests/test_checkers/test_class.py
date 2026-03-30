import ast

from python_naming_linter.checkers.class_ import check_class
from python_naming_linter.config import Rule


def _parse(source: str) -> ast.Module:
    return ast.parse(source)


def test_exception_naming_pass():
    source = """\
class MetricNotFoundError(NotFoundError):
    pass
"""
    pattern = r"^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$"
    rule = Rule(
        name="exception-naming",
        type="class",
        filter={"base_class": "Exception"},
        naming={"regex": pattern},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert violations == []


def test_exception_naming_violation():
    source = """\
class FilterError(ValidationError):
    pass
"""
    pattern = r"^[A-Z][a-zA-Z]+(NotFound|Invalid|Denied|Conflict|Failed)Error$"
    rule = Rule(
        name="exception-naming",
        type="class",
        filter={"base_class": "Exception"},
        naming={"regex": pattern},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert len(violations) == 1
    assert violations[0].name == "FilterError"


def test_class_suffix_pass():
    source = """\
class SubscriptionRepository:
    pass
"""
    rule = Rule(
        name="repo-suffix",
        type="class",
        naming={"suffix": ["Repository", "Service"]},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert violations == []


def test_class_suffix_violation():
    source = """\
class SubscriptionRepo:
    pass
"""
    rule = Rule(
        name="repo-suffix",
        type="class",
        naming={"suffix": ["Repository", "Service"]},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert len(violations) == 1


def test_non_exception_class_skipped_by_filter():
    source = """\
class MyService:
    pass
"""
    rule = Rule(
        name="exception-naming",
        type="class",
        filter={"base_class": "Exception"},
        naming={"regex": r"^[A-Z][a-zA-Z]+Error$"},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert violations == []


def test_decorator_filter_pass():
    source = """\
from dataclasses import dataclass

@dataclass
class UserProfile:
    name: str
"""
    rule = Rule(
        name="dataclass-naming",
        type="class",
        filter={"decorator": "dataclass"},
        naming={"case": "PascalCase"},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert violations == []


def test_decorator_filter_violation():
    source = """\
from dataclasses import dataclass

@dataclass
class user_profile:
    name: str
"""
    rule = Rule(
        name="dataclass-naming",
        type="class",
        filter={"decorator": "dataclass"},
        naming={"case": "PascalCase"},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert len(violations) == 1
    assert violations[0].name == "user_profile"


def test_decorator_filter_skips_non_decorated():
    source = """\
from dataclasses import dataclass

@dataclass
class UserProfile:
    name: str

class plain_service:
    pass
"""
    rule = Rule(
        name="dataclass-naming",
        type="class",
        filter={"decorator": "dataclass"},
        naming={"case": "PascalCase"},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    # plain_service has no @dataclass, so it should be skipped
    assert violations == []


def test_no_filter_checks_all_classes():
    source = """\
class myservice:
    pass
"""
    rule = Rule(
        name="class-case",
        type="class",
        naming={"case": "PascalCase"},
    )
    tree = _parse(source)
    violations = check_class(tree, rule, "test.py")
    assert len(violations) == 1
