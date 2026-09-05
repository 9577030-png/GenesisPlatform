import logging
import os
import json
import io
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import timedelta
from jose import JWTError, jwt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Р”РѕРјРµРЅРЅС‹Рµ Рё РёРЅС„СЂР°СЃС‚СЂСѓРєС‚СѓСЂРЅС‹Рµ РјРѕРґСѓР»Рё
from genesis_medical import knowledge_dir
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.entities.patient import PatientProfile
from medical_app.infrastructure.bootstrap.di_container import DIContainer
from genesis_medical.domain.exceptions import MedicalAIError
from medical_app.api.auth_config import (
    authenticate_user, create_access_token,
    get_password_hash
)
from medical_app.config import settings
from medical_app.infrastructure.logging_config import setup_logging
from dataclasses import asdict

# РРјРїРѕСЂС‚ РёРЅС‚РµСЂРїСЂРµС‚Р°С‚РѕСЂР°
from genesis_medical.services import ClinicalInterpreter

# РРјРїРѕСЂС‚ РјРѕРґРµР»РµР№ РґР»СЏ Р°РґРјРёРЅРєРё
from genesis_medical.domain.rule_version import RuleVersion, RulePriority

setup_logging(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# ---------- РЁСЂРёС„С‚ ----------
FONT_PATH = os.path.join(settings.BASE_DIR, settings.FONTS_DIR, "DejaVuSans.ttf")
try:
    pdfmetrics.registerFont(TTFont('DejaVu', FONT_PATH))
    FONT_NAME = 'DejaVu'
    logger.info(f"РЁСЂРёС„С‚ Р·Р°РіСЂСѓР¶РµРЅ РёР· {FONT_PATH}")
except Exception as e:
    logger.warning(f"РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ С€СЂРёС„С‚ DejaVuSans: {e}. Р‘СѓРґРµС‚ РёСЃРїРѕР»СЊР·РѕРІР°РЅ Helvetica.")
    FONT_NAME = 'Helvetica'

# ---------- РЎРћР—Р”РђРЃРњ РџР РР›РћР–Р•РќРР• ----------
app = FastAPI(
    title=settings.APP_NAME,
    description="РЎРёСЃС‚РµРјР° РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹С… РґР°РЅРЅС‹С…",
    version=settings.APP_VERSION
)

# ---------- Р“Р›РћР‘РђР›Р¬РќР«Р™ РљРћРќРўР•Р™РќР•Р  (СЂР°СЃС€РёСЂРµРЅРЅС‹Р№) ----------
container = DIContainer(probability_threshold=0.3)

# ---------- РџРћР”РљР›Р®Р§РђР•Рњ Р РћРЈРўР•Р  РђР”РњРРќРРЎРўР РР РћР’РђРќРРЇ (РїРѕСЃР»Рµ СЃРѕР·РґР°РЅРёСЏ app Рё container) ----------
from medical_app.api.routes import admin
admin.set_version_manager(container.version_manager)   # РёРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј РіР»РѕР±Р°Р»СЊРЅСѓСЋ РїРµСЂРµРјРµРЅРЅСѓСЋ РІ admin.py
app.include_router(admin.router)

# ---------- Р“Р›РћР‘РђР›Р¬РќР«Р™ РРќРўР•Р РџР Р•РўРђРўРћР  ----------
interpreter = ClinicalInterpreter(
    str(knowledge_dir() / "configs" / "clinical_interpretations.yaml")
)

# ---------- РђРЈРўР•РќРўРР¤РРљРђР¦РРЇ ----------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "user")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = container.user_repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# ---------- РњРћР”Р•Р›Р ----------
class PatientRequest(BaseModel):
    id: str
    gender: str
    age: int
    complaints: Optional[List[str]] = Field(default_factory=list)
    medications: Optional[List[str]] = Field(default_factory=list)

class AnalysisRequest(BaseModel):
    patient: PatientRequest
    raw_text: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: str

class ConfigFileRequest(BaseModel):
    path: str
    content: str

class StructuredDiagnosisResponse(BaseModel):
    id: str
    label: str
    risk: str
    combined: bool = False
    description: Optional[str] = None

class StructuredAnalysisResponse(BaseModel):
    diagnoses: List[StructuredDiagnosisResponse]
    grouped_findings: dict
    recommendations_by_specialty: dict
    overall_risk_level: str
    conclusion: str
    clinical_insights: Optional[Dict[str, Any]] = None

# ---------- Р’РЎРџРћРњРћР“РђРўР•Р›Р¬РќР«Р• Р¤РЈРќРљР¦РР ----------
def map_gender(gender_str: str) -> Gender:
    g = gender_str.lower()
    if g == "male":
        return Gender.MALE
    elif g == "female":
        return Gender.FEMALE
    else:
        raise ValueError(f"Invalid gender: {gender_str}")

# ---------- РЎРЈР©Р•РЎРўР’РЈР®Р©РР• Р­РќР”РџРћРРќРўР« ----------
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, container.user_repo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, admin = Depends(require_admin)):
    existing = container.user_repo.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = get_password_hash(request.password)
    user = container.user_repo.create(request.username, hashed, request.role)
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at.isoformat()
    )

@app.get("/users", response_model=List[UserResponse])
async def list_users(admin = Depends(require_admin)):
    users = container.user_repo.list_all()
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            role=u.role,
            created_at=u.created_at.isoformat()
        )
        for u in users
    ]

@app.delete("/admin/user/{user_id}")
async def delete_user(user_id: int, admin = Depends(require_admin)):
    user = container.user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username in ("admin", "doctor"):
        raise HTTPException(status_code=403, detail="Cannot delete default users")
    container.user_repo.delete(user_id)
    return {"status": "ok", "message": f"User {user_id} deleted"}

@app.get("/admin/config/file")
async def get_config_file(path: str, admin = Depends(require_admin)):
    full_path = str(knowledge_dir() / path)
    real_base = os.path.realpath(str(knowledge_dir()))
    real_path = os.path.realpath(full_path)
    if not real_path.startswith(real_base):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return {"path": path, "content": content}

@app.post("/admin/config/file")
async def save_config_file(request: ConfigFileRequest, admin = Depends(require_admin)):
    full_path = str(knowledge_dir() / request.path)
    real_base = os.path.realpath(str(knowledge_dir()))
    real_path = os.path.realpath(full_path)
    if not real_path.startswith(real_base):
        raise HTTPException(status_code=403, detail="Access denied")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(request.content)
    return {"status": "ok", "message": "File saved"}

@app.get("/admin/history/{patient_id}")
async def get_history(patient_id: str, admin = Depends(require_admin)):
    report = container.history_repo.load(patient_id)
    if report is None:
        raise HTTPException(status_code=404, detail="No history found")
    return {
        "patient_id": patient_id,
        "report": {
            "findings": [asdict(f) for f in report.findings],
            "actions": [asdict(a) for a in report.actions],
            "explanation": report.explanation
        }
    }

@app.post("/analyze")
async def analyze(
    request: AnalysisRequest,
    current_user = Depends(get_current_user)
):
    try:
        gender = map_gender(request.patient.gender)
        patient = PatientProfile(
            id=request.patient.id,
            gender=gender,
            age=request.patient.age,
            complaints=request.patient.complaints or [],
            medications=request.patient.medications or []
        )
        result = container.pipeline.run_with_postprocessing(patient, request.raw_text)
        return result
    except MedicalAIError as e:
        logger.error(f"Domain error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/analyze_structured", response_model=StructuredAnalysisResponse)
async def analyze_structured(
    request: AnalysisRequest,
    current_user = Depends(get_current_user)
):
    try:
        gender = map_gender(request.patient.gender)
        patient = PatientProfile(
            id=request.patient.id,
            gender=gender,
            age=request.patient.age,
            complaints=request.patient.complaints or [],
            medications=request.patient.medications or []
        )

        result = container.pipeline.run_with_postprocessing(patient, request.raw_text)

        raw_diagnoses = result.get("diagnoses", [])
        grouped_findings = result.get("grouped_findings", {})
        recommendations_by_specialty = result.get("recommendations_by_specialty", {})
        overall_risk_level = result.get("overall_risk_level", "РќРѕСЂРјР°")
        conclusion = result.get("conclusion", "")

        diagnoses_list = []
        for d in raw_diagnoses:
            if isinstance(d, dict):
                if "label" not in d and "title" in d:
                    d["label"] = d["title"]
                d.pop("probability", None)
                diagnoses_list.append(d)
            else:
                diagnoses_list.append({
                    "id": d.id,
                    "label": d.title,
                    "risk": d.risk.label if hasattr(d.risk, "label") else str(d.risk),
                    "combined": False,
                    "description": getattr(d, "description", None)
                })

        parameters = container.parser.parse(request.raw_text)

        insights = interpreter.interpret(
            diagnoses=diagnoses_list,
            parameters=parameters,
            patient=patient
        )

        grouped_dict = {}
        for system, items in grouped_findings.items():
            grouped_dict[system] = []
            for item in items:
                if hasattr(item, "__dict__"):
                    grouped_dict[system].append({
                        "id": item.id,
                        "title": item.title,
                        "risk": item.risk.label if hasattr(item.risk, "label") else str(item.risk),
                        "description": getattr(item, "description", None)
                    })
                else:
                    grouped_dict[system].append(item)

        rec_dict = {}
        for specialty, recs in recommendations_by_specialty.items():
            rec_dict[specialty] = []
            for r in recs:
                if hasattr(r, "__dict__"):
                    rec_dict[specialty].append({
                        "urgency": r.urgency.value if hasattr(r.urgency, "value") else str(r.urgency),
                        "tests": r.additional_tests
                    })
                else:
                    rec_dict[specialty].append(r)

        structured_diagnoses = [
            StructuredDiagnosisResponse(
                id=d["id"],
                label=d["label"],
                risk=d["risk"],
                combined=d.get("combined", False),
                description=d.get("description")
            )
            for d in diagnoses_list
        ]

        response_data = StructuredAnalysisResponse(
            diagnoses=structured_diagnoses,
            grouped_findings=grouped_dict,
            recommendations_by_specialty=rec_dict,
            overall_risk_level=overall_risk_level,
            conclusion=conclusion,
            clinical_insights=insights,
        )

        return response_data

    except MedicalAIError as e:
        logger.error(f"Domain error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Error in analyze_structured")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )

@app.post("/reload_config")
async def reload_config(admin = Depends(require_admin)):
    try:
        container.reload_configuration()
        new_versions = container.version_manager.hot_reload(created_by="admin")
        return {
            "status": "ok",
            "message": "Configuration reloaded successfully",
            "new_versions_created": len(new_versions)
        }
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Medical AI service is running"}

@app.post("/debug_pipeline")
async def debug_pipeline(request: AnalysisRequest):
    try:
        gender = map_gender(request.patient.gender)
        patient = PatientProfile(
            id=request.patient.id,
            gender=gender,
            age=request.patient.age,
            complaints=request.patient.complaints or [],
            medications=request.patient.medications or []
        )
        result = container.pipeline.run_with_postprocessing(patient, request.raw_text)
        with open("debug_pipeline_raw.json", "w", encoding="utf-8") as f:
            import json
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        return result
    except Exception as e:
        import traceback
        with open("debug_error.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        return {"error": str(e)}

@app.post("/export_pdf")
async def export_pdf(
    request: AnalysisRequest,
    current_user = Depends(get_current_user)
):
    try:
        gender = map_gender(request.patient.gender)
        patient = PatientProfile(
            id=request.patient.id,
            gender=gender,
            age=request.patient.age,
            complaints=request.patient.complaints or [],
            medications=request.patient.medications or []
        )
        result = container.pipeline.run_with_postprocessing(patient, request.raw_text)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        margin = 20 * mm
        y = height - margin

        c.setFont(FONT_NAME, 16)
        c.drawString(margin, y, "РљР›РРќРР§Р•РЎРљРћР• Р—РђРљР›Р®Р§Р•РќРР•")
        y -= 10 * mm

        c.setFont(FONT_NAME, 12)
        risk_level = result.get("overall_risk_level", "РќРµРёР·РІРµСЃС‚РЅРѕ")
        c.drawString(margin, y, f"РћР±С‰РёР№ СѓСЂРѕРІРµРЅСЊ СЂРёСЃРєР°: {risk_level}")
        y -= 7 * mm

        diagnoses = result.get("diagnoses", [])
        if diagnoses:
            c.setFont(FONT_NAME, 12)
            c.drawString(margin, y, "Р’С‹СЏРІР»РµРЅРЅС‹Рµ СЃРѕСЃС‚РѕСЏРЅРёСЏ:")
            y -= 6 * mm
            c.setFont(FONT_NAME, 11)
            for d in diagnoses:
                label = d.get("label", d.get("id", "РќРµРёР·РІРµСЃС‚РЅРѕ"))
                risk = d.get("risk", "РќРѕСЂРјР°")
                combined = d.get("combined", False)
                desc = d.get("description")
                line = f"- {label} (СЂРёСЃРє: {risk})"
                if combined:
                    line += " (РєРѕРјР±РёРЅРёСЂРѕРІР°РЅРЅС‹Р№)"
                if desc:
                    line += f" вЂ” {desc}"
                lines = simpleSplit(line, FONT_NAME, 11, width - 2*margin)
                for l in lines:
                    if y < margin + 10*mm:
                        c.showPage()
                        y = height - margin
                        c.setFont(FONT_NAME, 11)
                    c.drawString(margin, y, l)
                    y -= 5 * mm
                y -= 2 * mm

        grouped = result.get("grouped_findings", {})
        if grouped:
            c.setFont(FONT_NAME, 12)
            if y < margin + 15*mm:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, "Р Р°СЃРїСЂРµРґРµР»РµРЅРёРµ РїРѕ СЃРёСЃС‚РµРјР°Рј РѕСЂРіР°РЅРѕРІ:")
            y -= 6 * mm
            c.setFont(FONT_NAME, 11)
            for system, findings in grouped.items():
                if y < margin + 10*mm:
                    c.showPage()
                    y = height - margin
                    c.setFont(FONT_NAME, 11)
                c.drawString(margin, y, f"  {system}:")
                y -= 5 * mm
                for f in findings:
                    label = f.get("title", f.get("id", "РќРµРёР·РІРµСЃС‚РЅРѕ"))
                    risk = f.get("risk", "РќРѕСЂРјР°")
                    desc = f.get("description")
                    line = f"    - {label} (СЂРёСЃРє: {risk})"
                    if desc:
                        line += f" вЂ” {desc}"
                    lines = simpleSplit(line, FONT_NAME, 11, width - 2*margin)
                    for l in lines:
                        if y < margin + 5*mm:
                            c.showPage()
                            y = height - margin
                            c.setFont(FONT_NAME, 11)
                        c.drawString(margin, y, l)
                        y -= 5 * mm
                    y -= 1 * mm

        recommendations = result.get("recommendations_by_specialty", {})
        if recommendations:
            c.setFont(FONT_NAME, 12)
            if y < margin + 15*mm:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, "Р РµРєРѕРјРµРЅРґР°С†РёРё РїРѕ СЃРїРµС†РёР°Р»СЊРЅРѕСЃС‚СЏРј:")
            y -= 6 * mm
            c.setFont(FONT_NAME, 11)
            for specialty, recs in recommendations.items():
                if y < margin + 10*mm:
                    c.showPage()
                    y = height - margin
                    c.setFont(FONT_NAME, 11)
                c.drawString(margin, y, f"  {specialty}:")
                y -= 5 * mm
                for r in recs:
                    urgency = r.get("urgency", "unknown")
                    tests = r.get("tests", [])
                    line = f"    - РЎСЂРѕС‡РЅРѕСЃС‚СЊ: {urgency}"
                    if tests:
                        line += f", С‚РµСЃС‚С‹: {', '.join(tests)}"
                    lines = simpleSplit(line, FONT_NAME, 11, width - 2*margin)
                    for l in lines:
                        if y < margin + 5*mm:
                            c.showPage()
                            y = height - margin
                            c.setFont(FONT_NAME, 11)
                        c.drawString(margin, y, l)
                        y -= 5 * mm
                    y -= 1 * mm

        c.save()
        buffer.seek(0)
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{request.patient.id}.pdf"}
        )

    except MedicalAIError as e:
        logger.error(f"Domain error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------- РќРћР’Р«Р• Р­РќР”РџРћРРќРўР« Р”Р›РЇ РЈРџР РђР’Р›Р•РќРРЇ Р’Р•Р РЎРРЇРњР ----------
class ActivateVersionRequest(BaseModel):
    rule_id: str
    version_id: int

class ReloadRulesResponse(BaseModel):
    loaded: int
    versions: List[Dict[str, Any]]

@app.post("/admin/rules/reload", response_model=ReloadRulesResponse)
async def reload_rules(admin = Depends(require_admin)):
    try:
        new_versions = container.version_manager.hot_reload(created_by="admin")
        return ReloadRulesResponse(
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
    except Exception as e:
        logger.error(f"Failed to reload rules: {e}")
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")

@app.post("/admin/rules/activate")
async def activate_version(request: ActivateVersionRequest, admin = Depends(require_admin)):
    try:
        container.version_manager.activate_version(request.rule_id, request.version_id)
        return {"status": "ok", "rule_id": request.rule_id, "version_id": request.version_id}
    except Exception as e:
        logger.error(f"Failed to activate version: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/admin/rules/history/{rule_id}")
async def get_rule_history(rule_id: str, admin = Depends(require_admin)):
    try:
        history = container.version_manager.get_history(rule_id)
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
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/rules/active")
async def get_active_rules(admin = Depends(require_admin)):
    try:
        active = container.rule_repo.get_active_versions()
        return [
            {
                "rule_id": r.rule_id,
                "version_id": r.version_id,
                "name": r.name,
                "priority": r.priority.name,
                "created_at": r.created_at.isoformat()
            }
            for r in active
        ]
    except Exception as e:
        logger.error(f"Failed to get active rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Р—РђРџРЈРЎРљ ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
