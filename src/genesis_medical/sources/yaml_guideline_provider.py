from __future__ import annotations

from typing import List

from ..domain.entities.guideline import SpecialtyGuideline
from .merged_guideline_provider import MergedGuidelineProvider


class YamlGuidelineProvider:
    """Provider facade for normalized medical guidelines."""

    def __init__(self, merged_provider: MergedGuidelineProvider):
        self._merged = merged_provider

    def get_all(self) -> List[SpecialtyGuideline]:
        return self._merged.get_all()

    def reload(self) -> None:
        self._merged.reload()
