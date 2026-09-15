import asyncio

import pytest
from fastapi import HTTPException
from genesis_app.api.main import (
    DomainDescriptorResponse,
    DomainEvaluateRequest,
    DomainEvaluationResponse,
    FactRequest,
    evaluate_domain,
    list_genesis_domains,
)


def test_evaluate_domain_executes_construction() -> None:
    request = DomainEvaluateRequest(
        facts=[
            FactRequest(name="steel_capacity_kn", value=120),
            FactRequest(name="applied_load_kn", value=140),
        ]
    )

    response = asyncio.run(evaluate_domain("construction", request))

    assert isinstance(response, DomainEvaluationResponse)
    assert response.domain == "construction"
    assert [item["rule_id"] for item in response.results] == ["steel_load_reject"]
    assert response.results[0]["result"] == {
        "status": "review",
        "message": "applied load exceeds the demonstration capacity",
    }


def test_list_genesis_domains() -> None:
    response = asyncio.run(list_genesis_domains())

    assert response
    assert all(isinstance(item, DomainDescriptorResponse) for item in response)

    discovered = {(item.name, item.package, item.version) for item in response}

    assert ("banking", "genesis_banking", "0.1.0") in discovered
    assert ("construction", "genesis_construction", "0.2.0") in discovered
    assert ("medical", "genesis_medical", "0.3.0") in discovered


def test_evaluate_domain_returns_404_for_unknown_domain() -> None:
    request = DomainEvaluateRequest(facts=[])

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(evaluate_domain("does-not-exist", request))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Genesis domain is not installed: 'does-not-exist'"
