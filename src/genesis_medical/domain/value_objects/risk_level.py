from enum import Enum

class RiskLevel(Enum):
    """Уровень риска с порядком и текстовым представлением."""
    NORMAL = (0, "Норма")
    LOW     = (1, "Низкий")
    MEDIUM  = (2, "Средний")
    HIGH    = (3, "Высокий")
    CRITICAL= (4, "Критический")

    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = value