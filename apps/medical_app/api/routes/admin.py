from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from medical_app.application.services.version_manager import VersionManager
from medical_app.domain.exceptions import VersionNotFoundError

router = APIRouter(prefix="/admin/rules", tags=["admin"])

# Р“Р»РѕР±Р°Р»СЊРЅР°СЏ РїРµСЂРµРјРµРЅРЅР°СЏ РґР»СЏ С…СЂР°РЅРµРЅРёСЏ VersionManager (СѓСЃС‚Р°РЅР°РІР»РёРІР°РµС‚СЃСЏ РёР· main.py)
_version_manager: VersionManager = None

def set_version_manager(vm: VersionManager):
    """Р’С‹Р·С‹РІР°РµС‚СЃСЏ РёР· main.py РґР»СЏ РёРЅРёС†РёР°Р»РёР·Р°С†РёРё"""
    global _version_manager
    _version_manager = vm

def get_version_manager() -> VersionManager:
    if _version_manager is None:
        raise HTTPException(status_code=500, detail="VersionManager not initialized")
    return _version_manager

class ReloadResponse(BaseModel):
    loaded: int
    versions: List[Dict[str, Any]]

class ActivateRequest(BaseModel):
    rule_id: str
    version_id: int

@router.post("/reload", response_model=ReloadResponse)
async def reload_rules(version_manager: VersionManager = Depends(get_version_manager)):
    """РџРµСЂРµР·Р°РіСЂСѓР·РёС‚СЊ РІСЃРµ РїСЂР°РІРёР»Р° РёР· YAML (СЃРѕР·РґР°С‚СЊ РЅРѕРІС‹Рµ РІРµСЂСЃРёРё)."""
    new_versions = version_manager.hot_reload(created_by="admin")
    return ReloadResponse(
        loaded=len(new_versions),
        versions=[
            {
                "rule_id": v.rule_id,
                "version_id": v.version_id,
                "is_active": v.is_active,
                "created_at": v.created_at.isoformat()
            }
            for v in new_versions
        ]
    )

@router.put("/activate")
async def activate_version(req: ActivateRequest, version_manager: VersionManager = Depends(get_version_manager)):
    """РђРєС‚РёРІРёСЂРѕРІР°С‚СЊ СѓРєР°Р·Р°РЅРЅСѓСЋ РІРµСЂСЃРёСЋ РїСЂР°РІРёР»Р°."""
    try:
        version_manager.activate_version(req.rule_id, req.version_id)
    except VersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": "ok", "rule_id": req.rule_id, "version_id": req.version_id}

@router.get("/history/{rule_id}")
async def get_history(rule_id: str, version_manager: VersionManager = Depends(get_version_manager)):
    """РџРѕР»СѓС‡РёС‚СЊ РёСЃС‚РѕСЂРёСЋ РІРµСЂСЃРёР№ РїСЂР°РІРёР»Р°."""
    history = version_manager.get_history(rule_id)
    if not history:
        raise HTTPException(status_code=404, detail="Rule not found")
    return [
        {
            "version_id": v.version_id,
            "created_at": v.created_at.isoformat(),
            "is_active": v.is_active,
            "comment": v.comment,
            "created_by": v.created_by
        }
        for v in history
    ]

@router.get("/active")
async def get_active_rules(version_manager: VersionManager = Depends(get_version_manager)):
    """РџРѕР»СѓС‡РёС‚СЊ СЃРїРёСЃРѕРє Р°РєС‚РёРІРЅС‹С… РІРµСЂСЃРёР№ РїСЂР°РІРёР»."""
    active = version_manager.rule_repo.get_active_versions()
    return [
        {
            "rule_id": r.rule_id,
            "version_id": r.version_id,
            "name": r.name,
            "priority": r.priority.name,
            "tier": r.tier.value,
            "created_at": r.created_at.isoformat()
        }
        for r in active
    ]
