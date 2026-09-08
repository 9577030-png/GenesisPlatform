import logging
import sys

from medical_app.config import settings


def setup_logging(level: str | None = None, log_file: str | None = None) -> None:
    """РќР°СЃС‚СЂР°РёРІР°РµС‚ Р»РѕРіРёСЂРѕРІР°РЅРёРµ РґР»СЏ РІСЃРµРіРѕ РїСЂРёР»РѕР¶РµРЅРёСЏ."""
    if level is None:
        level = settings.LOG_LEVEL
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
