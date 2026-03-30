import ast

from python_naming_linter.checkers.module import check_module
from python_naming_linter.config import Rule


def _parse(source: str) -> ast.Module:
    return ast.parse(source)


def test_module_matches_class_name_pass():
    source = """\
class CustomObject:
    pass
"""
    rule = Rule(
        name="module-naming",
        type="module",
        naming={"source": "class_name", "transform": "snake_case"},
    )
    violations = check_module(_parse(source), rule, "custom_object.py")
    assert violations == []


def test_module_matches_class_name_violation():
    source = """\
class CustomObject:
    pass
"""
    rule = Rule(
        name="module-naming",
        type="module",
        naming={"source": "class_name", "transform": "snake_case"},
    )
    violations = check_module(_parse(source), rule, "custom.py")
    assert len(violations) == 1
    assert "custom_object" in violations[0].message


def test_module_regex_pass():
    source = ""
    rule = Rule(
        name="module-regex",
        type="module",
        naming={"regex": r"^[a-z]+(_[a-z]+)+$"},
    )
    violations = check_module(_parse(source), rule, "create_organization.py")
    assert violations == []


def test_module_regex_violation():
    source = ""
    rule = Rule(
        name="module-regex",
        type="module",
        naming={"regex": r"^[a-z]+(_[a-z]+)+$"},
    )
    violations = check_module(_parse(source), rule, "createOrganization.py")
    assert len(violations) == 1


def test_module_multiple_classes_uses_first():
    source = """\
class PropertyValueFilter:
    pass

class Operator:
    pass
"""
    rule = Rule(
        name="module-naming",
        type="module",
        naming={"source": "class_name", "transform": "snake_case"},
    )
    violations = check_module(_parse(source), rule, "property_value_filter.py")
    assert violations == []


def test_init_file_skipped():
    source = """\
class Something:
    pass
"""
    rule = Rule(
        name="module-naming",
        type="module",
        naming={"source": "class_name", "transform": "snake_case"},
    )
    violations = check_module(_parse(source), rule, "__init__.py")
    assert violations == []
