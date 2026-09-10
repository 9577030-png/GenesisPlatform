from abc import ABC, abstractmethod

from genesis_medical.domain.entities.threshold import Threshold
from genesis_medical.domain.value_objects.gender import Gender


class ThresholdProvider(ABC):
    @abstractmethod
    def get_global_thresholds(self) -> dict[str, Threshold]:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃР»РѕРІР°СЂСЊ РїРѕСЂРѕРіРѕРІ (Р±РµР· СѓС‡С‘С‚Р° РїРѕР»Р°) вЂ” СѓСЃС‚Р°СЂРµРІР°РµС‚, РёСЃРїРѕР»СЊР·СѓР№С‚Рµ get_threshold."""
        pass

    @abstractmethod
    def get_threshold(self, parameter: str, gender: Gender) -> Threshold | None:
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ РїРѕСЂРѕРі РґР»СЏ РїР°СЂР°РјРµС‚СЂР° СЃ СѓС‡С‘С‚РѕРј РїРѕР»Р° РїР°С†РёРµРЅС‚Р°."""
        pass
