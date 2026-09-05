import logging
import yaml
from pathlib import Path
from typing import List
from genesis_medical.domain.rule_version import RuleVersion, RuleTier
from medical_app.application.ports.rule_repository import RuleRepository
from medical_app.domain.exceptions import VersionNotFoundError
from genesis_medical.sources.clinical_interpretation_mapper import ClinicalInterpretationMapper

logger = logging.getLogger(__name__)

class VersionManager:
    def __init__(self, rule_repo: RuleRepository, config_dir: str):
        self.rule_repo = rule_repo
        self.config_dir = Path(config_dir)
        self.interpretation_mapper = ClinicalInterpretationMapper()

    def load_from_yaml(self, rule_id: str, yaml_path: Path, created_by: str = "system") -> RuleVersion:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # РћРїСЂРµРґРµР»СЏРµРј tier РїРѕ РёРјРµРЅРё С„Р°Р№Р»Р° (Р±РµР· СЂР°СЃС€РёСЂРµРЅРёСЏ)
        base_name = yaml_path.stem
        tier = RuleTier.ENRICHED if self.interpretation_mapper.is_enriched(base_name) else RuleTier.BASIC
        version = RuleVersion.from_yaml(rule_id, data, created_by, tier=tier)
        return self.rule_repo.save(version)

    def activate_version(self, rule_id: str, version_id: int) -> None:
        version = self.rule_repo.get_by_id(rule_id, version_id)
        if not version:
            raise VersionNotFoundError(f"Version {version_id} for rule {rule_id} not found")
        self.rule_repo.activate_version(rule_id, version_id)

    def get_history(self, rule_id: str) -> List[RuleVersion]:
        return self.rule_repo.get_version_history(rule_id)

    def hot_reload(self, created_by: str = "system") -> List[RuleVersion]:
        new_versions = []
        for yaml_file in self.config_dir.rglob("*.yaml"):
            # РСЃРїРѕР»СЊР·СѓРµРј РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅС‹Р№ РїСѓС‚СЊ РєР°Рє rule_id РґР»СЏ СЃРѕС…СЂР°РЅРµРЅРёСЏ РІ Р‘Р”
            rule_id = str(yaml_file.relative_to(self.config_dir)).replace("\\", "/").replace(".yaml", "")
            try:
                version = self.load_from_yaml(rule_id, yaml_file, created_by)
                new_versions.append(version)
                logger.info(f"Loaded {rule_id} (version {version.version_id}, tier={version.tier.value})")
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")
        return new_versions
