import asyncio

import pytest
from fastapi import HTTPException
from genesis_app.api.routes.domains import (
    DomainDescriptorResponse,
    DomainEvaluateRequest,
    DomainEvaluationResponse,
    FactRequest,
    evaluate_domain,
    list_genesis_domains,
    set_container,
)


class FakeRuntime:
    def evaluate(self, facts):
        assert tuple(facts)
        return ()


class FakeContainer:
    def create_domain_runtime(self, domain_name):
        if domain_name == "does-not-exist":
            raise LookupError(f"Genesis domain is not installed: {domain_name!r}")
        return FakeRuntime()


def test_list_genesis_domains_returns_descriptors() -> None:
    response = asyncio.run(list_genesis_domains())

    assert response
    assert all(isinstance(item, DomainDescriptorResponse) for item in response)


def test_evaluate_domain_uses_configured_container() -> None:
    set_container(FakeContainer())

    response = asyncio.run(
        evaluate_domain(
            "construction",
            DomainEvaluateRequest(facts=[FactRequest(name="steel_capacity_kn", value=120)]),
        )
    )

    assert isinstance(response, DomainEvaluationResponse)
    assert response.domain == "construction"
    assert response.results == []


def test_evaluate_domain_returns_404_for_unknown_domain() -> None:
    set_container(FakeContainer())

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            evaluate_domain(
                "does-not-exist",
                DomainEvaluateRequest(facts=[]),
            )
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == ("Genesis domain is not installed: 'does-not-exist'")
