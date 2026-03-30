import ast

from python_naming_linter.checkers.variable import check_variable
from python_naming_linter.config import Rule


def _parse(source: str) -> ast.Module:
    return ast.parse(source)


def test_attribute_matches_type_pass():
    source = """\
class MyService:
    subscription_repository: SubscriptionRepository
"""
    rule = Rule(
        name="attr-naming",
        type="variable",
        filter={"target": "attribute"},
        naming={"source": "type_annotation", "transform": "snake_case"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    assert violations == []


def test_attribute_matches_type_violation():
    source = """\
class MyService:
    repo: SubscriptionRepository
"""
    rule = Rule(
        name="attr-naming",
        type="variable",
        filter={"target": "attribute"},
        naming={"source": "type_annotation", "transform": "snake_case"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    assert len(violations) == 1
    assert violations[0].name == "repo"
    assert "subscription_repository" in violations[0].message


def test_parameter_matches_type_pass():
    source = """\
def execute(self, subscription_repository: SubscriptionRepository):
    pass
"""
    rule = Rule(
        name="param-naming",
        type="variable",
        filter={"target": "parameter"},
        naming={"source": "type_annotation", "transform": "snake_case"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    assert violations == []


def test_parameter_matches_type_violation():
    source = """\
def execute(self, repo: SubscriptionRepository):
    pass
"""
    rule = Rule(
        name="param-naming",
        type="variable",
        filter={"target": "parameter"},
        naming={"source": "type_annotation", "transform": "snake_case"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    assert len(violations) == 1
    assert violations[0].name == "repo"


def test_constant_case_pass():
    source = "MAX_RETRIES = 3\n"
    rule = Rule(
        name="const-naming",
        type="variable",
        filter={"target": "constant"},
        naming={"case": "UPPER_CASE"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    assert violations == []


def test_constant_case_violation():
    source = "maxRetries = 3\n"
    rule = Rule(
        name="const-naming",
        type="variable",
        filter={"target": "constant"},
        naming={"case": "UPPER_CASE"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    assert len(violations) == 1


def test_self_and_cls_skipped():
    source = """\
class MyService:
    def execute(self, repo: SubscriptionRepository):
        pass

    @classmethod
    def create(cls, repo: SubscriptionRepository):
        pass
"""
    rule = Rule(
        name="param-naming",
        type="variable",
        filter={"target": "parameter"},
        naming={"source": "type_annotation", "transform": "snake_case"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    # self and cls should be skipped, only repo is a violation
    assert len(violations) == 2
    assert all(v.name == "repo" for v in violations)


def test_multiple_context_prefix():
    source = """\
class MyService:
    source_object_context: ObjectContext
    target_object_context: ObjectContext
"""
    rule = Rule(
        name="attr-naming",
        type="variable",
        filter={"target": "attribute"},
        naming={"source": "type_annotation", "transform": "snake_case"},
    )
    tree = _parse(source)
    violations = check_variable(tree, rule, "test.py")
    # {context}_object_context is allowed for multiple instances of same type
    assert violations == []
