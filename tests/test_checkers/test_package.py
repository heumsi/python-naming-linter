from python_naming_linter.checkers.package import check_package
from python_naming_linter.config import Rule


def test_package_snake_case_pass():
    rule = Rule(
        name="pkg-case",
        type="package",
        naming={"case": "snake_case"},
    )
    violations = check_package(rule, "my_package")
    assert violations == []


def test_package_snake_case_violation():
    rule = Rule(
        name="pkg-case",
        type="package",
        naming={"case": "snake_case"},
    )
    violations = check_package(rule, "MyPackage")
    assert len(violations) == 1


def test_package_regex_pass():
    rule = Rule(
        name="pkg-regex",
        type="package",
        naming={"regex": r"^[a-z][a-z_]*$"},
    )
    violations = check_package(rule, "my_package")
    assert violations == []


def test_package_regex_violation():
    rule = Rule(
        name="pkg-regex",
        type="package",
        naming={"regex": r"^[a-z][a-z_]*$"},
    )
    violations = check_package(rule, "MyPackage")
    assert len(violations) == 1
