from abc import ABC, abstractmethod

from genesis_medical.domain.entities.parameter import Parameter


class ParserInterface(ABC):
    @abstractmethod
    def parse(self, raw_text: str) -> list[Parameter]:
        pass
