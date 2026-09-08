from pydantic import BaseModel, Field


class CriterionEvaluation(BaseModel):
    parameter: str = Field(
        ...,
        description="Каноническое имя параметра",
    )
    value: float | None = Field(
        None,
        description="Значение параметра у пациента",
    )
    unit: str = Field(
        ...,
        description="Единица измерения",
    )
    threshold: float | None = Field(
        None,
        description="Пороговое значение",
    )
    condition: str | None = Field(
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
    description: str | None = None
    criteria: list[CriterionEvaluation] = Field(default_factory=list)
    differentials: list[DifferentialSuggestion] = Field(default_factory=list)
    red_flags: list[RedFlag] = Field(default_factory=list)
    treatment_hints: list[TreatmentHint] = Field(default_factory=list)
    references: list[str] | None = None
