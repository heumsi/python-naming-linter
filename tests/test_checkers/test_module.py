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


# --- match: suffix + strip_prefix: parent_dir (outbound adapter naming) ---

_SUFFIX_RULE = Rule(
    name="outbound-module-naming",
    type="module",
    naming={
        "source": "class_name",
        "transform": "snake_case",
        "match": "suffix",
        "strip_prefix": "parent_dir",
    },
)


def test_suffix_strips_tech_prefix_matching_parent_dir_pass():
    source = "class PostgresOrganizationRepository:\n    pass\n"
    violations = check_module(
        _parse(source),
        _SUFFIX_RULE,
        "adapters/outbound/persistence/postgres/organization_repository.py",
    )
    assert violations == []


def test_suffix_compound_tech_prefix_normalizes_against_dir_pass():
    # BigQuery -> big_query, directory 'bigquery' -> compared with separators dropped
    source = "class BigQueryMetricRepository:\n    pass\n"
    violations = check_module(
        _parse(source),
        _SUFFIX_RULE,
        "adapters/outbound/warehouse/bigquery/metric_repository.py",
    )
    assert violations == []


def test_suffix_tech_in_filename_violation():
    # Tech qualifier sits in the filename with no matching tech directory.
    source = "class HttpxImageFetcher:\n    pass\n"
    violations = check_module(
        _parse(source),
        _SUFFIX_RULE,
        "adapters/outbound/httpx_image_fetcher.py",
    )
    assert len(violations) == 1


def test_suffix_stutter_tech_in_both_dir_and_filename_violation():
    source = "class RedisCacheStore:\n    pass\n"
    violations = check_module(
        _parse(source),
        _SUFFIX_RULE,
        "adapters/outbound/cache/redis/redis_cache_store.py",
    )
    assert len(violations) == 1


def test_suffix_inverted_port_as_dir_tech_as_file_violation():
    # Port is the directory, tech is the filename — filename is a prefix, not a suffix.
    source = "class GoogleSheetPropertySyncFetcher:\n    pass\n"
    violations = check_module(
        _parse(source),
        _SUFFIX_RULE,
        "adapters/outbound/property_sync_fetcher/google_sheet.py",
    )
    assert len(violations) == 1


def test_suffix_without_strip_prefix_allows_any_qualifier_pass():
    rule = Rule(
        name="suffix-only",
        type="module",
        naming={"source": "class_name", "transform": "snake_case", "match": "suffix"},
    )
    source = "class HttpxImageFetcher:\n    pass\n"
    violations = check_module(_parse(source), rule, "some/dir/image_fetcher.py")
    assert violations == []
