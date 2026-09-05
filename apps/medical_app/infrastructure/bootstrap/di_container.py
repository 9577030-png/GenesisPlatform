import os
import logging
from medical_app.config import settings
from genesis_medical import knowledge_dir
from genesis_medical.sources.yaml_threshold_loader import YamlThresholdLoader
from genesis_medical.sources.yaml_recommendation_loader import YamlRecommendationLoader
from genesis_medical.sources.merged_guideline_provider import MergedGuidelineProvider
from genesis_medical.sources.yaml_guideline_provider import YamlGuidelineProvider
from genesis_medical.sources.clinical_logic_loader import ClinicalLogicLoader
from genesis_medical.parsers.regex_parser import RegexParser
from medical_app.infrastructure.adapters.renderers.console_renderer import ConsoleRenderer
from medical_app.infrastructure.adapters.storage.sql_history_repository import SqlHistoryRepository
from medical_app.infrastructure.adapters.storage.sql_user_repository import SqlUserRepository
from medical_app.application.services.inference_engine import InferenceEngine
from genesis_medical.services import ActionMapper
from genesis_medical.services import ReportBuilder
from medical_app.application.services.analysis_pipeline import AnalysisPipeline
from genesis_medical.services import PostProcessor

# РќРѕРІС‹Рµ РёРјРїРѕСЂС‚С‹
from medical_app.application.ports.rule_repository import RuleRepository
from medical_app.infrastructure.repositories.sqlalchemy_rule_repository import SQLAlchemyRuleRepository
from medical_app.infrastructure.repositories.audit_repository import AuditRepository
from medical_app.infrastructure.cache.redis_cache import RedisCache
from genesis_medical.services import PhysiologicalValidator
from medical_app.application.services.version_manager import VersionManager

logger = logging.getLogger(__name__)

class DIContainer:
    def __init__(self, probability_threshold: float = 0.3):
        logger.info("DIContainer initializing...")

        # --- РЎСѓС‰РµСЃС‚РІСѓСЋС‰РёРµ РєРѕРјРїРѕРЅРµРЅС‚С‹ ---
        self.user_repo = SqlUserRepository(settings.DB_PATH)
        self.threshold_loader = YamlThresholdLoader()
        self.recommendation_loader = YamlRecommendationLoader()
        self.logic_loader = ClinicalLogicLoader()
        self.merged_guideline_provider = MergedGuidelineProvider(self.threshold_loader)
        self.guideline_provider = YamlGuidelineProvider(self.merged_guideline_provider)
        self.parser = RegexParser()
        self.renderer = ConsoleRenderer()
        self.history_repo = SqlHistoryRepository(settings.DB_PATH)

        # --- РќРћР’Р«Р• РљРћРњРџРћРќР•РќРўР« (СѓР»СѓС‡С€РµРЅРЅС‹Р№ РґРІРёР¶РѕРє) ---

        # 1. Р РµРїРѕР·РёС‚РѕСЂРёР№ РїСЂР°РІРёР» (SQLAlchemy)
        self.rule_repo = SQLAlchemyRuleRepository(settings.DATABASE_URL)

        # 2. Р РµРїРѕР·РёС‚РѕСЂРёР№ Р°СѓРґРёС‚Р°
        self.audit_repo = AuditRepository(settings.DATABASE_URL)

        # 3. РљСЌС€ Redis вЂ“ РёРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј С‚РѕР»СЊРєРѕ РµСЃР»Рё URL Р·Р°РґР°РЅ Рё СЃРѕРµРґРёРЅРµРЅРёРµ СѓСЃРїРµС€РЅРѕ
        self.cache = None
        if settings.REDIS_URL:
            try:
                cache = RedisCache(settings.REDIS_URL)
                # РџСЂРѕРІРµСЂСЏРµРј СЃРѕРµРґРёРЅРµРЅРёРµ
                cache.client.ping()
                self.cache = cache
                logger.info("Redis cache enabled")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Cache disabled.")
                self.cache = None

               # 4. Р’Р°Р»РёРґР°С‚РѕСЂ С„РёР·РёРѕР»РѕРіРёС‡РµСЃРєРёС… РґРёР°РїР°Р·РѕРЅРѕРІ (РµСЃР»Рё С„Р°Р№Р» СЃСѓС‰РµСЃС‚РІСѓРµС‚)
        config_dir = knowledge_dir() / "configs"
        physiological_ranges_path = config_dir / "physiological_ranges.yaml"
        if os.path.exists(physiological_ranges_path):
            try:
                self.validator = PhysiologicalValidator(physiological_ranges_path)
                logger.info("Physiological validator enabled")
            except Exception as e:
                logger.warning(f"Failed to load physiological validator: {e}. Validator disabled.")
                self.validator = None
        else:
            logger.warning(f"Physiological ranges file not found: {physiological_ranges_path}. Validator disabled.")
            self.validator = None

        # 5. РњРµРЅРµРґР¶РµСЂ РІРµСЂСЃРёР№ РїСЂР°РІРёР»
        guidelines_dir = knowledge_dir() / "guidelines"
        self.version_manager = VersionManager(self.rule_repo, guidelines_dir)
         # Р—Р°РіСЂСѓР¶Р°РµРј РІСЃРµ РїСЂР°РІРёР»Р° РёР· YAML РІ Р‘Р” Рё Р°РєС‚РёРІРёСЂСѓРµРј РёС…
        try:
            logger.info("Loading rules from YAML into database...")
            new_versions = self.version_manager.hot_reload(created_by="system")
            # РђРєС‚РёРІРёСЂСѓРµРј РІСЃРµ Р·Р°РіСЂСѓР¶РµРЅРЅС‹Рµ РІРµСЂСЃРёРё
            for version in new_versions:
                self.version_manager.activate_version(version.rule_id, version.version_id)
            logger.info(f"Activated {len(new_versions)} rule versions")
        except Exception as e:
            logger.error(f"Failed to load rules: {e}", exc_info=True)

        # --- Р”РІРёР¶РѕРє РІС‹РІРѕРґР° СЃ РЅРѕРІС‹РјРё Р·Р°РІРёСЃРёРјРѕСЃС‚СЏРјРё ---
        self.inference_engine = InferenceEngine(
            rule_repo=self.rule_repo,
            threshold_provider=self.threshold_loader,
            guideline_provider=self.guideline_provider
        )

        self.action_mapper = ActionMapper(self.recommendation_loader)
        self.report_builder = ReportBuilder()

        self.post_processor = PostProcessor(
            logic_loader=self.logic_loader,
            probability_threshold=probability_threshold
        )

        # --- Р“Р»Р°РІРЅС‹Р№ РїР°Р№РїР»Р°Р№РЅ СЃ РѕРїС†РёРѕРЅР°Р»СЊРЅС‹РјРё СѓР»СѓС‡С€РµРЅРёСЏРјРё ---
        self.pipeline = AnalysisPipeline(
            parser=self.parser,
            inference_engine=self.inference_engine,
            action_mapper=self.action_mapper,
            report_builder=self.report_builder,
            history_repo=self.history_repo,
            renderer=self.renderer,
            post_processor=self.post_processor,
            cache=self.cache,                 # РјРѕР¶РµС‚ Р±С‹С‚СЊ None
            audit_repo=self.audit_repo,       # РІСЃРµРіРґР° РµСЃС‚СЊ
            rule_repo=self.rule_repo,         # РІСЃРµРіРґР° РµСЃС‚СЊ
            validator=self.validator          # РјРѕР¶РµС‚ Р±С‹С‚СЊ None
        )

        logger.info("DIContainer initialized successfully")

    def reload_configuration(self) -> None:
        logger.info("Reloading all configurations...")
        self.threshold_loader.reload()
        self.recommendation_loader.reload()
        self.logic_loader.reload()
        self.guideline_provider.reload()

        self.post_processor = PostProcessor(
            logic_loader=self.logic_loader,
            probability_threshold=self.post_processor.threshold
        )

        self.inference_engine = InferenceEngine(
            rule_repo=self.rule_repo,
            threshold_provider=self.threshold_loader,
            guideline_provider=self.guideline_provider
        )
        self.action_mapper = ActionMapper(self.recommendation_loader)

        self.pipeline = AnalysisPipeline(
            parser=self.parser,
            inference_engine=self.inference_engine,
            action_mapper=self.action_mapper,
            report_builder=self.report_builder,
            history_repo=self.history_repo,
            renderer=self.renderer,
            post_processor=self.post_processor,
            cache=self.cache,
            audit_repo=self.audit_repo,
            rule_repo=self.rule_repo,
            validator=self.validator
        )

        logger.info("All configurations reloaded successfully.")
