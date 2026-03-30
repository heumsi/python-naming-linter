from python_naming_linter.matcher import match_pattern_with_captures, matches_pattern


def test_exact_match():
    assert matches_pattern("contexts.boards.domain", "contexts.boards.domain")


def test_no_match():
    assert not matches_pattern("contexts.boards.domain", "contexts.auth.domain")


def test_wildcard_single_level():
    assert matches_pattern("contexts.*.domain", "contexts.boards.domain")
    assert not matches_pattern("contexts.*.domain", "contexts.boards.sub.domain")


def test_globstar_multi_level():
    assert matches_pattern("contexts.**.domain", "contexts.boards.domain")
    assert matches_pattern("contexts.**.domain", "contexts.boards.sub.domain")


def test_named_capture():
    captures = match_pattern_with_captures(
        "contexts.{ctx}.domain", "contexts.boards.domain"
    )
    assert captures == {"ctx": "boards"}


def test_named_capture_consistency():
    captures = match_pattern_with_captures(
        "contexts.{ctx}.{ctx}", "contexts.boards.boards"
    )
    assert captures == {"ctx": "boards"}


def test_named_capture_inconsistency():
    captures = match_pattern_with_captures(
        "contexts.{ctx}.{ctx}", "contexts.boards.auth"
    )
    assert captures is None


def test_match_all():
    assert matches_pattern("**", "anything.at.all")


def test_submodule_match():
    from python_naming_linter.matcher import matches_pattern_or_submodule

    assert matches_pattern_or_submodule(
        "contexts.*.domain", "contexts.boards.domain.models"
    )
    assert not matches_pattern_or_submodule(
        "contexts.*.domain", "contexts.boards.application.service"
    )
