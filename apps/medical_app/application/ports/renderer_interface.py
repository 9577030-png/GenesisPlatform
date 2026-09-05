from abc import ABC, abstractmethod
from genesis_medical.domain.entities.report import AnalysisReport

class RendererInterface(ABC):
    @abstractmethod
    def render(self, report: AnalysisReport) -> str:
        pass
