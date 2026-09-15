from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException
from genesis_app.infrastructure.bootstrap.di_container import DIContainer
from pydantic import BaseModel, Field

from genesis_core import Fact, discover_domains

router = APIRouter()
_container: DIContainer | None = None


class FactRequest(BaseModel):
    name: str
    value: Any
    unit: str | None = None


class DomainEvaluateRequest(BaseModel):
    facts: list[FactRequest] = Field(default_factory=list)


class DomainEvaluationResponse(BaseModel):
    domain: str
    results: list[dict[str, Any]]


class DomainDescriptorResponse(BaseModel):
    name: str
    package: str
    version: str


def set_container(container: DIContainer) -> None:
    global _container
    _container = container


def _get_container() -> DIContainer:
    if _container is None:
        raise RuntimeError("Genesis domain API container is not configured")
    return _container


@router.get("/domains", response_model=list[DomainDescriptorResponse])
async def list_genesis_domains() -> list[DomainDescriptorResponse]:
    try:
        return [
            DomainDescriptorResponse(
                name=descriptor.name,
                package=descriptor.package,
                version=descriptor.version,
            )
            for descriptor in discover_domains()
        ]
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error") from None


@router.post(
    "/domains/{domain_name}/evaluate",
    response_model=DomainEvaluationResponse,
)
async def evaluate_domain(
    domain_name: str,
    request: DomainEvaluateRequest,
) -> DomainEvaluationResponse:
    try:
        facts = tuple(Fact(fact.name, fact.value, fact.unit) for fact in request.facts)
        runtime = _get_container().create_domain_runtime(domain_name)
        result = runtime.evaluate(facts)

        return DomainEvaluationResponse(
            domain=domain_name,
            results=[asdict(item) for item in result],
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error") from None
