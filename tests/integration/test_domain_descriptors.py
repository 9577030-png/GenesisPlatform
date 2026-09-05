from genesis_construction import get_domain_descriptor as get_construction_descriptor
from genesis_medical import get_domain_descriptor as get_medical_descriptor


def test_domain_descriptors_expose_rule_loaders():
    for factory in (get_medical_descriptor, get_construction_descriptor):
        descriptor = factory()
        assert descriptor.name
        assert descriptor.version
        rules = descriptor.get_rule_loader().load().rules
        assert rules
        assert all(rule.id for rule in rules)
