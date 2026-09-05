from pydantic import BaseModel, Field
from typing import List, Optional


class CriterionEvaluation(BaseModel):
    parameter: str = Field(
        ...,
        description="Каноническое имя параметра",
    )
    value: Optional[float] = Field(
        None,
        description="Значение параметра у пациента",
    )
    unit: str = Field(
        ...,
        description="Единица измерения",
    )
    threshold: Optional[float] = Field(
        None,
        description="Пороговое значение",
    )
    condition: Optional[str] = Field(
        None,
        description="Условие сравнения",
    )
    comment: str = Field(
        ...,
        description="Клинический комментарий для врача",
    )


class DifferentialSuggestion(BaseModel):
    condition: str = Field(
        ...,
        description="Условие, при котором актуально",
    )
    text: str = Field(
        ...,
        description="Текст подсказки",
    )


class RedFlag(BaseModel):
    condition: str = Field(
        ...,
        description="Условие срабатывания",
    )
    text: str = Field(
        ...,
        description="Описание риска",
    )


class TreatmentHint(BaseModel):
    step: str = Field(
        ...,
        description="Действие",
    )
    note: str = Field(
        ...,
        description="Пояснение",
    )


class ClinicalInsights(BaseModel):
    diagnosis_id: str
    label: str
    category: str
    description: Optional[str] = None
    criteria: List[CriterionEvaluation] = Field(
        default_factory=list
    )
    differentials: List[DifferentialSuggestion] = Field(
        default_factory=list
    )
    red_flags: List[RedFlag] = Field(
        default_factory=list
    )
    treatment_hints: List[TreatmentHint] = Field(
        default_factory=list
    )
    references: Optional[List[str]] = None