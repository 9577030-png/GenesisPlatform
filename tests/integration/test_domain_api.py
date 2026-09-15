import asyncio

from genesis_app.api.main import (
    DomainEvaluateRequest,
    DomainEvaluationResponse,
    FactRequest,
    evaluate_domain,
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
