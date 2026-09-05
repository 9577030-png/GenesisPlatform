from abc import ABC, abstractmethod
from typing import Optional
from genesis_medical.domain.entities.recommendation import Recommendation

class RecommendationProvider(ABC):
    @abstractmethod
    def get_recommendation(self, finding_id: str) -> Optional[Recommendation]:
        pass
