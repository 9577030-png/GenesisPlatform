from abc import ABC, abstractmethod

from genesis_medical.domain.entities.recommendation import Recommendation


class RecommendationProvider(ABC):
    @abstractmethod
    def get_recommendation(self, finding_id: str) -> Recommendation | None:
        pass
