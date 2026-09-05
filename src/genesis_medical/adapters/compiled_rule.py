from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from genesis_core import Rule
from genesis_medical.domain.rule_version import RuleVersion


@dataclass(frozen=True)
class CompiledRule:
    """
    РСЃРїРѕР»РЅСЏРµРјРѕРµ generic rule СЃ СЃРѕС…СЂР°РЅС‘РЅРЅС‹Рј РёСЃС…РѕРґРЅС‹Рј
    medical context.

    Generic Rule РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ RuleEngine.
    Source condition Рё RuleVersion РЅСѓР¶РЅС‹ medical layer
    РґР»СЏ РїРѕСЃР»РµРґСѓСЋС‰РµР№ РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё СЂРµР·СѓР»СЊС‚Р°С‚Р°.
    """

    rule: Rule
    condition: dict[str, Any]
    rule_version: RuleVersion
