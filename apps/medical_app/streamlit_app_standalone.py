import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os
import yaml

# Р”РѕР±Р°РІР»СЏРµРј РєРѕСЂРµРЅСЊ РїСЂРѕРµРєС‚Р° РІ PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# ---------- РРјРїРѕСЂС‚С‹ РєРѕРјРїРѕРЅРµРЅС‚РѕРІ (Р±РµР· SQLite) ----------
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.severity import Severity
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.entities.report import AnalysisReport

from genesis_medical.parsers.regex_parser import RegexParser
from genesis_medical.sources.yaml_threshold_loader import YamlThresholdLoader
from genesis_medical.sources.yaml_recommendation_loader import YamlRecommendationLoader
from genesis_medical.sources.merged_guideline_provider import MergedGuidelineProvider
from genesis_medical.sources.yaml_guideline_provider import YamlGuidelineProvider
from genesis_medical.sources.clinical_logic_loader import ClinicalLogicLoader

from medical_app.application.services.inference_engine import InferenceEngine
from genesis_medical.services import ActionMapper
from genesis_medical.services import ReportBuilder
from genesis_medical.services import PostProcessor
from genesis_medical.services import ClinicalInterpreter

# ---------- РќР°СЃС‚СЂРѕР№РєРё ----------
# Р—Р°РјРµРЅСЏРµРј РЅР°СЃС‚СЂРѕР№РєРё Р‘Р” РЅР° :memory: (С‡С‚РѕР±С‹ РЅРµ Р±С‹Р»Рѕ РѕС€РёР±РѕРє)
os.environ["DB_PATH"] = ":memory:"

# ---------- РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РєРѕРјРїРѕРЅРµРЅС‚РѕРІ ----------
@st.cache_resource
def init_services():
    """РРЅРёС†РёР°Р»РёР·РёСЂСѓРµС‚ РІСЃРµ СЃРµСЂРІРёСЃС‹ Р±РµР· SQLite."""
    threshold_loader = YamlThresholdLoader()
    recommendation_loader = YamlRecommendationLoader()
    logic_loader = ClinicalLogicLoader()
    
    merged_provider = MergedGuidelineProvider(threshold_loader)
    guideline_provider = YamlGuidelineProvider(merged_provider)
    
    inference_engine = InferenceEngine(guideline_provider, threshold_loader)
    action_mapper = ActionMapper(recommendation_loader)
    report_builder = ReportBuilder()
    post_processor = PostProcessor(logic_loader=logic_loader, probability_threshold=0.3)
    
    return {
        "inference_engine": inference_engine,
        "action_mapper": action_mapper,
        "report_builder": report_builder,
        "post_processor": post_processor,
        "parser": RegexParser(),
        "interpreter": ClinicalInterpreter(),
    }

services = init_services()
parser = services["parser"]
inference_engine = services["inference_engine"]
action_mapper = services["action_mapper"]
report_builder = services["report_builder"]
post_processor = services["post_processor"]
interpreter = services["interpreter"]

# ---------- Р¤СѓРЅРєС†РёСЏ Р°РЅР°Р»РёР·Р° ----------
def run_analysis(patient: PatientProfile, raw_text: str):
    """Р—Р°РїСѓСЃРєР°РµС‚ РїРѕР»РЅС‹Р№ РїР°Р№РїР»Р°Р№РЅ Р°РЅР°Р»РёР·Р° (Р±РµР· РёСЃС‚РѕСЂРёРё)."""
    try:
        # 1. РџР°СЂСЃРёРЅРі
        parameters = parser.parse(raw_text)
        
        # 2. РРЅС„РµСЂРµРЅСЃ
        findings = inference_engine.infer(patient, parameters)
        
        # 3. Р”РµР№СЃС‚РІРёСЏ
        actions = action_mapper.map_to_actions(findings)
        
        # 4. РћС‚С‡С‘С‚
        report = report_builder.build(findings, actions)
        
        # 5. РџРѕСЃС‚РѕР±СЂР°Р±РѕС‚РєР°
        result = post_processor.process(report)
        
        return result
    except Exception as e:
        raise e

def map_gender(gender_str: str) -> Gender:
    g = gender_str.lower()
    if g == "male":
        return Gender.MALE
    elif g == "female":
        return Gender.FEMALE
    return Gender.MALE

# ---------- Р—Р°РіСЂСѓР·РєР° РїР°СЂР°РјРµС‚СЂРѕРІ ----------
@st.cache_data
def load_parameters():
    """Р—Р°РіСЂСѓР¶Р°РµС‚ СЃРїРёСЃРѕРє РїР°СЂР°РјРµС‚СЂРѕРІ РёР· aliases.yaml"""
    try:
        aliases_path = Path("knowledge/laboratory/aliases.yaml")
        with open(aliases_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        aliases = data.get("aliases", {})
        all_names = set()
        for canonical, synonyms in aliases.items():
            all_names.add(canonical)
            for syn in synonyms:
                all_names.add(syn)
        return sorted(all_names)
    except:
        return ["РіР»СЋРєРѕР·Р°", "РєСЂРµР°С‚РёРЅРёРЅ", "РіРµРјРѕРіР»РѕР±РёРЅ", "С„РµСЂСЂРёС‚РёРЅ", "РєР°Р»РёР№", "РЅР°С‚СЂРёР№", "РђР›Рў", "РђРЎРў", "РўРўР“", "РІРёС‚Р°РјРёРЅ D", "Р›РџРќРџ", "С‚СЂРёРіР»РёС†РµСЂРёРґС‹", "Р›РџР’Рџ", "РјРѕС‡РµРІР°СЏ РєРёСЃР»РѕС‚Р°"]

parameters_list = load_parameters()

# ---------- Session State ----------
if "added_params" not in st.session_state:
    st.session_state.added_params = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""

# ---------- РРЅС‚РµСЂС„РµР№СЃ ----------
st.set_page_config(page_title="РЎРёСЃС‚РµРјР° РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹С… РґР°РЅРЅС‹С…", layout="wide")
st.title("рџ§Є РЎРёСЃС‚РµРјР° РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹С… РґР°РЅРЅС‹С…")

# Р‘РѕРєРѕРІР°СЏ РїР°РЅРµР»СЊ
with st.sidebar:
    st.header("рџ§‘вЂЌвљ•пёЏ Р”Р°РЅРЅС‹Рµ РїР°С†РёРµРЅС‚Р°")
    patient_id = st.text_input("ID РїР°С†РёРµРЅС‚Р°", value="P001")
    gender = st.selectbox("РџРѕР»", ["male", "female", "other"])
    age = st.number_input("Р’РѕР·СЂР°СЃС‚", min_value=0, max_value=150, value=45)
    complaints = st.text_area("Р–Р°Р»РѕР±С‹ (С‡РµСЂРµР· Р·Р°РїСЏС‚СѓСЋ)", value="fatigue, weakness")
    medications = st.text_area("РџСЂРёРЅРёРјР°РµРјС‹Рµ Р»РµРєР°СЂСЃС‚РІР° (С‡РµСЂРµР· Р·Р°РїСЏС‚СѓСЋ)", value="")

    st.markdown("---")
    st.markdown("### рџ“‹ Р”РѕР±Р°РІРёС‚СЊ Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹Р№ РїР°СЂР°РјРµС‚СЂ")

    param_name = st.selectbox("РџР°СЂР°РјРµС‚СЂ", options=parameters_list, key="param_select")
    col_val, col_unit = st.columns([3, 2])
    with col_val:
        param_value = st.number_input("Р—РЅР°С‡РµРЅРёРµ", value=0.0, step=0.1, format="%.2f", key="param_value")
    with col_unit:
        param_unit = st.text_input("Р•РґРёРЅРёС†Р° (РѕРїС†РёРѕРЅР°Р»СЊРЅРѕ)", value="", placeholder="РЅР°РїСЂ. РјРјРѕР»СЊ/Р»", key="param_unit")

    if st.button("вћ• Р”РѕР±Р°РІРёС‚СЊ РїР°СЂР°РјРµС‚СЂ", use_container_width=True):
        if param_name and param_value is not None:
            st.session_state.added_params.append((param_name, param_value, param_unit))
            st.rerun()
        else:
            st.warning("Р’С‹Р±РµСЂРёС‚Рµ РїР°СЂР°РјРµС‚СЂ Рё РІРІРµРґРёС‚Рµ Р·РЅР°С‡РµРЅРёРµ.")

    if st.session_state.added_params:
        st.markdown("#### РЈР¶Рµ РґРѕР±Р°РІР»РµРЅС‹:")
        for i, (pname, pval, punit) in enumerate(st.session_state.added_params):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{pname}**")
            with col2:
                st.write(f"{pval}")
            with col3:
                if punit:
                    st.write(f"{punit}")
            if st.button("рџ—‘пёЏ", key=f"del_{i}"):
                st.session_state.added_params.pop(i)
                st.rerun()
        if st.button("РћС‡РёСЃС‚РёС‚СЊ РІСЃРµ", use_container_width=True):
            st.session_state.added_params = []
            st.rerun()
    else:
        st.info("РџРѕРєР° РЅРµС‚ РґРѕР±Р°РІР»РµРЅРЅС‹С… РїР°СЂР°РјРµС‚СЂРѕРІ.")

    if st.session_state.added_params:
        raw_text_lines = []
        for pname, pval, punit in st.session_state.added_params:
            if punit:
                raw_text_lines.append(f"{pname} {pval} {punit}")
            else:
                raw_text_lines.append(f"{pname} {pval}")
        st.session_state.raw_text = "\n".join(raw_text_lines)
    else:
        st.session_state.raw_text = ""

    analyze_btn = st.button("рџ”Ќ РђРЅР°Р»РёР·РёСЂРѕРІР°С‚СЊ", type="primary", use_container_width=True)

# ---------- РћСЃРЅРѕРІРЅР°СЏ РѕР±Р»Р°СЃС‚СЊ ----------
if analyze_btn and st.session_state.raw_text.strip():
    try:
        gender_enum = map_gender(gender)
        patient = PatientProfile(
            id=patient_id,
            gender=gender_enum,
            age=age,
            complaints=[c.strip() for c in complaints.split(",") if c.strip()],
            medications=[m.strip() for m in medications.split(",") if m.strip()]
        )

        with st.spinner("Р’С‹РїРѕР»РЅСЏРµС‚СЃСЏ Р°РЅР°Р»РёР·..."):
            result = run_analysis(patient, st.session_state.raw_text)

        if result:
            st.session_state.analysis_result = result
            st.success("вњ… РђРЅР°Р»РёР· Р·Р°РІРµСЂС€С‘РЅ")

            # ----- РћР±С‰РёР№ СЂРёСЃРє -----
            risk_level = result.get("overall_risk_level", "РќРµРёР·РІРµСЃС‚РЅРѕ")
            color_map = {
                "РќРѕСЂРјР°": "green",
                "РќРёР·РєРёР№": "blue",
                "РЎСЂРµРґРЅРёР№": "orange",
                "Р’С‹СЃРѕРєРёР№": "red",
                "РљСЂРёС‚РёС‡РµСЃРєРёР№": "darkred"
            }
            color = color_map.get(risk_level, "gray")
            st.markdown(
                f"<div style='background-color:{color}; padding:10px; border-radius:10px; text-align:center;'>"
                f"<h2 style='color:white; margin:0;'>рџљЁ РћР±С‰РёР№ СѓСЂРѕРІРµРЅСЊ СЂРёСЃРєР°: {risk_level}</h2>"
                f"</div>",
                unsafe_allow_html=True
            )

            # ----- Р”РёР°РіРЅРѕР·С‹ -----
            diagnoses = result.get("diagnoses", [])
            if diagnoses:
                st.markdown("### рџ“Њ Р’С‹СЏРІР»РµРЅРЅС‹Рµ СЃРѕСЃС‚РѕСЏРЅРёСЏ")
                for d in diagnoses:
                    label = d.get("label", d.get("id", "РќРµРёР·РІРµСЃС‚РЅРѕ"))
                    risk = d.get("risk", "РќРѕСЂРјР°")
                    combined = d.get("combined", False)
                    desc = d.get("description")
                    card_color = color_map.get(risk, "gray")
                    st.markdown(
                        f"""
                        <div style="border-left: 5px solid {card_color}; padding-left: 15px; margin-bottom: 10px;">
                            <strong>{label}</strong> 
                            <span style="background-color:{card_color}; color:white; padding:2px 8px; border-radius:12px; font-size:0.8rem;">{risk}</span>
                            { 'вљ•пёЏ (РєРѕРјР±РёРЅРёСЂРѕРІР°РЅРЅС‹Р№)' if combined else '' }
                            <br>
                            <span style="font-size:0.9rem; color:#555;">{desc or ''}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("Р—РЅР°С‡РёРјС‹С… РѕС‚РєР»РѕРЅРµРЅРёР№ РЅРµ РѕР±РЅР°СЂСѓР¶РµРЅРѕ.")

            # ----- Р“СЂСѓРїРїРёСЂРѕРІРєР° -----
            grouped = result.get("grouped_findings", {})
            if grouped:
                st.markdown("### рџ§¬ Р Р°СЃРїСЂРµРґРµР»РµРЅРёРµ РїРѕ СЃРёСЃС‚РµРјР°Рј РѕСЂРіР°РЅРѕРІ")
                for system, findings in grouped.items():
                    with st.expander(f"**{system}** ({len(findings)})"):
                        for f in findings:
                            label = f.get("title", f.get("id", "РќРµРёР·РІРµСЃС‚РЅРѕ"))
                            risk = f.get("risk", "РќРѕСЂРјР°")
                            desc = f.get("description")
                            card_color = color_map.get(risk, "gray")
                            st.markdown(
                                f"""
                                <div style="border-left: 3px solid {card_color}; padding-left: 10px; margin: 5px 0;">
                                    <strong>{label}</strong> <span style="color:{card_color};">({risk})</span>
                                    <br><span style="font-size:0.85rem; color:#555;">{desc or ''}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

            # ----- Р РµРєРѕРјРµРЅРґР°С†РёРё -----
            recommendations = result.get("recommendations_by_specialty", {})
            if recommendations:
                st.markdown("### рџ‘ЁвЂЌвљ•пёЏ Р РµРєРѕРјРµРЅРґР°С†РёРё РїРѕ СЃРїРµС†РёР°Р»СЊРЅРѕСЃС‚СЏРј")
                for specialty, recs in recommendations.items():
                    with st.expander(f"**{specialty}** ({len(recs)})"):
                        for r in recs:
                            urgency = r.get("urgency", "unknown")
                            tests = r.get("tests", [])
                            st.markdown(f"- **РЎСЂРѕС‡РЅРѕСЃС‚СЊ:** {urgency}")
                            if tests:
                                st.markdown(f"  **РўРµСЃС‚С‹:** {', '.join(tests)}")
                            st.markdown("---")
            else:
                st.info("РќРµС‚ СЂРµРєРѕРјРµРЅРґР°С†РёР№.")

            # ----- РљР»РёРЅРёС‡РµСЃРєРёРµ РёРЅСЃР°Р№С‚С‹ -----
            try:
                parameters = parser.parse(st.session_state.raw_text)
                insights = interpreter.interpret(diagnoses, parameters, patient)
                if insights:
                    st.markdown("### рџ§  РљР»РёРЅРёС‡РµСЃРєРёРµ РёРЅСЃР°Р№С‚С‹ (РїРѕРґСЂРѕР±РЅР°СЏ РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёСЏ)")
                    for diag_id, insight in insights.items():
                        label = getattr(insight, 'label', diag_id)
                        with st.expander(f"**{label}** (ID: {diag_id})"):
                            if hasattr(insight, 'criteria') and insight.criteria:
                                st.markdown("#### рџ“Љ РљСЂРёС‚РµСЂРёРё РґРёР°РіРЅРѕР·Р°")
                                df_data = []
                                for c in insight.criteria:
                                    df_data.append({
                                        "РџР°СЂР°РјРµС‚СЂ": getattr(c, 'parameter', ''),
                                        "Р—РЅР°С‡РµРЅРёРµ": getattr(c, 'value', ''),
                                        "РќРѕСЂРјР°": f"{getattr(c, 'threshold', '')} ({getattr(c, 'condition', '')})",
                                        "РљРѕРјРјРµРЅС‚Р°СЂРёР№": getattr(c, 'comment', '')
                                    })
                                if df_data:
                                    st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
                            if hasattr(insight, 'differentials') and insight.differentials:
                                st.markdown("#### рџ”Ќ Р”РёС„С„РµСЂРµРЅС†РёР°Р»СЊРЅР°СЏ РґРёР°РіРЅРѕСЃС‚РёРєР°")
                                for diff in insight.differentials:
                                    condition = getattr(diff, 'condition', '')
                                    text = getattr(diff, 'text', '')
                                    st.markdown(f"- **РЈСЃР»РѕРІРёРµ:** `{condition}` в†’ {text}")
                            if hasattr(insight, 'red_flags') and insight.red_flags:
                                st.markdown("#### вљ пёЏ РљСЂР°СЃРЅС‹Рµ С„Р»Р°РіРё")
                                for rf in insight.red_flags:
                                    condition = getattr(rf, 'condition', '')
                                    text = getattr(rf, 'text', '')
                                    st.markdown(f"- **{condition}** в†’ {text}")
                            if hasattr(insight, 'treatment_hints') and insight.treatment_hints:
                                st.markdown("#### рџ’Љ РЁРїР°СЂРіР°Р»РєР° РїРѕ С‚Р°РєС‚РёРєРµ")
                                for hint in insight.treatment_hints:
                                    step = getattr(hint, 'step', '')
                                    note = getattr(hint, 'note', '')
                                    st.markdown(f"- **{step}** вЂ” {note}")
                            if hasattr(insight, 'references') and insight.references:
                                st.markdown("#### рџ“љ РЎСЃС‹Р»РєРё")
                                for ref in insight.references:
                                    st.markdown(f"- {ref}")
                else:
                    st.info("Р”Р»СЏ РІС‹СЏРІР»РµРЅРЅС‹С… РґРёР°РіРЅРѕР·РѕРІ РЅРµС‚ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹С… РєР»РёРЅРёС‡РµСЃРєРёС… РёРЅСЃР°Р№С‚РѕРІ.")
            except Exception as e:
                st.info(f"РРЅСЃР°Р№С‚С‹ РІСЂРµРјРµРЅРЅРѕ РЅРµРґРѕСЃС‚СѓРїРЅС‹: {e}")

            # ----- Р—Р°РєР»СЋС‡РµРЅРёРµ (С‚РµРєСЃС‚РѕРІРѕРµ) -----
            conclusion = result.get("conclusion", "")
            if conclusion:
                with st.expander("рџ“„ РџРѕР»РЅРѕРµ С‚РµРєСЃС‚РѕРІРѕРµ Р·Р°РєР»СЋС‡РµРЅРёРµ"):
                    st.text(conclusion)

    except Exception as e:
        st.error(f"вќЊ РћС€РёР±РєР°: {e}")

elif analyze_btn:
    st.warning("Р”РѕР±Р°РІСЊС‚Рµ С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹Р№ РїР°СЂР°РјРµС‚СЂ.")

# ----- Р¤СѓС‚РµСЂ -----
st.markdown("---")
st.caption("РЎРёСЃС‚РµРјР° РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹С… РґР°РЅРЅС‹С… v1.0 | Р”РµРјРѕ-РІРµСЂСЃРёСЏ")
