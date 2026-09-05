from importlib.metadata import EntryPoint
import sys
import types

import pytest

from genesis_core import DomainDescriptor, RuleLoader, list_domains, load_domain
from genesis_core.plugin_registry import discover_entry_points


class FakeDescriptor(DomainDescriptor):
    def get_rule_loader(self) -> RuleLoader:
        raise NotImplementedError


def install_helper(monkeypatch, descriptor):
    helper = types.ModuleType("genesis_core.plugin_registry_test_helpers")
    helper.descriptor = lambda: descriptor
    monkeypatch.setitem(sys.modules, helper.__name__, helper)
    points = (
        EntryPoint(
            name=descriptor.name,
            value="genesis_core.plugin_registry_test_helpers:descriptor",
            group="genesis.domains",
        ),
    )
    monkeypatch.setattr(
        "genesis_core.plugin_registry.entry_points",
        lambda group: points,
    )
    return points


def make_descriptor(name="medical"):
    return FakeDescriptor(name, "genesis_medical", "0.2.1")


def test_discover_entry_points_reads_registered_entry_points(monkeypatch):
    descriptor = make_descriptor()
    points = install_helper(monkeypatch, descriptor)
    assert discover_entry_points() == points


def test_list_domains_returns_registered_names(monkeypatch):
    descriptor = make_descriptor("medical")
    points = (
        EntryPoint("construction", "x:y", "genesis.domains"),
        EntryPoint("medical", "x:y", "genesis.domains"),
    )
    monkeypatch.setattr(
        "genesis_core.plugin_registry.entry_points",
        lambda group: points,
    )
    assert list_domains() == ("construction", "medical")


def test_load_domain_returns_strict_descriptor(monkeypatch):
    descriptor = make_descriptor()
    install_helper(monkeypatch, descriptor)
    result = load_domain("medical")
    assert isinstance(result, DomainDescriptor)
    assert result.name == "medical"
    assert result.version == "0.2.1"
    assert hasattr(result, "get_rule_loader")


def test_load_domain_rejects_unknown_domain(monkeypatch):
    monkeypatch.setattr(
        "genesis_core.plugin_registry.entry_points",
        lambda group: (),
    )
    with pytest.raises(LookupError, match="Genesis domain is not installed"):
        load_domain("fake")


def test_load_domain_rejects_empty_name():
    with pytest.raises(ValueError, match="cannot be empty"):
        load_domain("")
