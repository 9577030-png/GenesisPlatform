from abc import ABC, abstractmethod

from genesis_medical.domain.entities.guideline import SpecialtyGuideline


class GuidelineProvider(ABC):
    @abstractmethod
    def get_all(self) -> list[SpecialtyGuideline]:
        pass
