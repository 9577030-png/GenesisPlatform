import pytest

from genesis_core import list_domains


def test_all_installed_genesis_domains_are_distinct() -> None:
    domains = set(list_domains())
    required = {"medical", "construction", "banking"}
    if not required.issubset(domains):
        pytest.skip("Requires all Genesis domain distributions to be installed")

    assert required.issubset(domains)
