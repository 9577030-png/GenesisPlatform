from abc import ABC, abstractmethod
from typing import List
from genesis_medical.domain.entities.guideline import SpecialtyGuideline

class GuidelineProvider(ABC):
    @abstractmethod
    def get_all(self) -> List[SpecialtyGuideline]:
        pass
