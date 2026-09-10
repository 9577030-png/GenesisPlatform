import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

# Р вЂќР С•Р В±Р В°Р Р†Р В»РЎРЏР ВµР С Р С”Р С•РЎР‚Р ВµР Р…РЎРЉ Р С—РЎР‚Р С•Р ВµР С”РЎвЂљР В° Р Р† PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# ---------- Р ВР СР С—Р С•РЎР‚РЎвЂљРЎвЂ№ Р С”Р С•Р СР С—Р С•Р Р…Р ВµР Р…РЎвЂљР С•Р Р† (Р В±Р ВµР В· SQLite) ----------
from genesis_medical.application.services.inference_engine import InferenceEngine
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.parsers.regex_parser import RegexParser
from genesis_medical.services import ActionMapper, ClinicalInterpreter, PostProcessor, ReportBuilder
from genesis_medical.sources.clinical_logic_loader import ClinicalLogicLoader
from genesis_medical.sources.merged_guideline_provider import MergedGuidelineProvider
from genesis_medical.sources.yaml_guideline_provider import YamlGuidelineProvider
from genesis_medical.sources.yaml_recommendation_loader import YamlRecommendationLoader
from genesis_medical.sources.yaml_threshold_loader import YamlThresholdLoader

# ---------- Р СњР В°РЎРѓРЎвЂљРЎР‚Р С•Р в„–Р С”Р С‘ ----------
# Р вЂ”Р В°Р СР ВµР Р…РЎРЏР ВµР С Р Р…Р В°РЎРѓРЎвЂљРЎР‚Р С•Р в„–Р С”Р С‘ Р вЂР вЂќ Р Р…Р В° :memory: (РЎвЂЎРЎвЂљР С•Р В±РЎвЂ№ Р Р…Р Вµ Р В±РЎвЂ№Р В»Р С• Р С•РЎв‚¬Р С‘Р В±Р С•Р С”)
os.environ["DB_PATH"] = ":memory:"


# ---------- Р ВР Р…Р С‘РЎвЂ Р С‘Р В°Р В»Р С‘Р В·Р В°РЎвЂ Р С‘РЎРЏ Р С”Р С•Р СР С—Р С•Р Р…Р ВµР Р…РЎвЂљР С•Р Р† ----------
@st.cache_resource
def init_services():
    """Р ВР Р…Р С‘РЎвЂ Р С‘Р В°Р В»Р С‘Р В·Р С‘РЎР‚РЎС“Р ВµРЎвЂљ Р Р†РЎРѓР Вµ РЎРѓР ВµРЎР‚Р Р†Р С‘РЎРѓРЎвЂ№ Р В±Р ВµР В· SQLite."""
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


# ---------- Р В¤РЎС“Р Р…Р С”РЎвЂ Р С‘РЎРЏ Р В°Р Р…Р В°Р В»Р С‘Р В·Р В° ----------
def run_analysis(patient: PatientProfile, raw_text: str):
    """Р вЂ”Р В°Р С—РЎС“РЎРѓР С”Р В°Р ВµРЎвЂљ Р С—Р С•Р В»Р Р…РЎвЂ№Р в„– Р С—Р В°Р в„–Р С—Р В»Р В°Р в„–Р Р… Р В°Р Р…Р В°Р В»Р С‘Р В·Р В° (Р В±Р ВµР В· Р С‘РЎРѓРЎвЂљР С•РЎР‚Р С‘Р С‘)."""
    try:
        # 1. Р СџР В°РЎР‚РЎРѓР С‘Р Р…Р С–
        parameters = parser.parse(raw_text)

        # 2. Р ВР Р…РЎвЂћР ВµРЎР‚Р ВµР Р…РЎРѓ
        findings = inference_engine.infer(patient, parameters)

        # 3. Р вЂќР ВµР в„–РЎРѓРЎвЂљР Р†Р С‘РЎРЏ
        actions = action_mapper.map_to_actions(findings)

        # 4. Р С›РЎвЂљРЎвЂЎРЎвЂРЎвЂљ
        report = report_builder.build(findings, actions)

        # 5. Р СџР С•РЎРѓРЎвЂљР С•Р В±РЎР‚Р В°Р В±Р С•РЎвЂљР С”Р В°
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


# ---------- Р вЂ”Р В°Р С–РЎР‚РЎС“Р В·Р С”Р В° Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚Р С•Р Р† ----------
@st.cache_data
def load_parameters():
    """Р вЂ”Р В°Р С–РЎР‚РЎС“Р В¶Р В°Р ВµРЎвЂљ РЎРѓР С—Р С‘РЎРѓР С•Р С” Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚Р С•Р Р† Р С‘Р В· aliases.yaml"""
    try:
        aliases_path = Path("knowledge/laboratory/aliases.yaml")
        with open(aliases_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        aliases = data.get("aliases", {})
        all_names = set()
        for canonical, synonyms in aliases.items():
            all_names.add(canonical)
            for syn in synonyms:
                all_names.add(syn)
        return sorted(all_names)
    except Exception:
        return [
            "Р С–Р В»РЎР‹Р С”Р С•Р В·Р В°",
            "Р С”РЎР‚Р ВµР В°РЎвЂљР С‘Р Р…Р С‘Р Р…",
            "Р С–Р ВµР СР С•Р С–Р В»Р С•Р В±Р С‘Р Р…",
            "РЎвЂћР ВµРЎР‚РЎР‚Р С‘РЎвЂљР С‘Р Р…",
            "Р С”Р В°Р В»Р С‘Р в„–",
            "Р Р…Р В°РЎвЂљРЎР‚Р С‘Р в„–",
            "Р С’Р вЂєР Сћ",
            "Р С’Р РЋР Сћ",
            "Р СћР СћР вЂњ",
            "Р Р†Р С‘РЎвЂљР В°Р СР С‘Р Р… D",
            "Р вЂєР СџР СњР Сџ",
            "РЎвЂљРЎР‚Р С‘Р С–Р В»Р С‘РЎвЂ Р ВµРЎР‚Р С‘Р Т‘РЎвЂ№",
            "Р вЂєР СџР вЂ™Р Сџ",
            "Р СР С•РЎвЂЎР ВµР Р†Р В°РЎРЏ Р С”Р С‘РЎРѓР В»Р С•РЎвЂљР В°",
        ]


parameters_list = load_parameters()

# ---------- Session State ----------
if "added_params" not in st.session_state:
    st.session_state.added_params = []
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""

# ---------- Р ВР Р…РЎвЂљР ВµРЎР‚РЎвЂћР ВµР в„–РЎРѓ ----------
st.set_page_config(
    page_title="Р РЋР С‘РЎРѓРЎвЂљР ВµР СР В° Р С‘Р Р…РЎвЂљР ВµРЎР‚Р С—РЎР‚Р ВµРЎвЂљР В°РЎвЂ Р С‘Р С‘ Р В»Р В°Р В±Р С•РЎР‚Р В°РЎвЂљР С•РЎР‚Р Р…РЎвЂ№РЎвЂ¦ Р Т‘Р В°Р Р…Р Р…РЎвЂ№РЎвЂ¦",
    layout="wide",
)
st.title(
    "СЂСџВ§Р„ Р РЋР С‘РЎРѓРЎвЂљР ВµР СР В° Р С‘Р Р…РЎвЂљР ВµРЎР‚Р С—РЎР‚Р ВµРЎвЂљР В°РЎвЂ Р С‘Р С‘ Р В»Р В°Р В±Р С•РЎР‚Р В°РЎвЂљР С•РЎР‚Р Р…РЎвЂ№РЎвЂ¦ Р Т‘Р В°Р Р…Р Р…РЎвЂ№РЎвЂ¦"
)

# Р вЂР С•Р С”Р С•Р Р†Р В°РЎРЏ Р С—Р В°Р Р…Р ВµР В»РЎРЉ
with st.sidebar:
    st.header(
        "СЂСџВ§вЂРІР‚РЊРІС™вЂўРїС‘РЏ Р вЂќР В°Р Р…Р Р…РЎвЂ№Р Вµ Р С—Р В°РЎвЂ Р С‘Р ВµР Р…РЎвЂљР В°"
    )
    patient_id = st.text_input("ID Р С—Р В°РЎвЂ Р С‘Р ВµР Р…РЎвЂљР В°", value="P001")
    gender = st.selectbox("Р СџР С•Р В»", ["male", "female", "other"])
    age = st.number_input("Р вЂ™Р С•Р В·РЎР‚Р В°РЎРѓРЎвЂљ", min_value=0, max_value=150, value=45)
    complaints = st.text_area(
        "Р вЂ“Р В°Р В»Р С•Р В±РЎвЂ№ (РЎвЂЎР ВµРЎР‚Р ВµР В· Р В·Р В°Р С—РЎРЏРЎвЂљРЎС“РЎР‹)",
        value="fatigue, weakness",
    )
    medications = st.text_area(
        "Р СџРЎР‚Р С‘Р Р…Р С‘Р СР В°Р ВµР СРЎвЂ№Р Вµ Р В»Р ВµР С”Р В°РЎР‚РЎРѓРЎвЂљР Р†Р В° (РЎвЂЎР ВµРЎР‚Р ВµР В· Р В·Р В°Р С—РЎРЏРЎвЂљРЎС“РЎР‹)",
        value="",
    )

    st.markdown("---")
    st.markdown(
        "### СЂСџвЂњвЂ№ Р вЂќР С•Р В±Р В°Р Р†Р С‘РЎвЂљРЎРЉ Р В»Р В°Р В±Р С•РЎР‚Р В°РЎвЂљР С•РЎР‚Р Р…РЎвЂ№Р в„– Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚"
    )

    param_name = st.selectbox(
        "Р СџР В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚", options=parameters_list, key="param_select"
    )
    col_val, col_unit = st.columns([3, 2])
    with col_val:
        param_value = st.number_input(
            "Р вЂ”Р Р…Р В°РЎвЂЎР ВµР Р…Р С‘Р Вµ",
            value=0.0,
            step=0.1,
            format="%.2f",
            key="param_value",
        )
    with col_unit:
        param_unit = st.text_input(
            "Р вЂўР Т‘Р С‘Р Р…Р С‘РЎвЂ Р В° (Р С•Р С—РЎвЂ Р С‘Р С•Р Р…Р В°Р В»РЎРЉР Р…Р С•)",
            value="",
            placeholder="Р Р…Р В°Р С—РЎР‚. Р СР СР С•Р В»РЎРЉ/Р В»",
            key="param_unit",
        )

    if st.button(
        "РІС›вЂў Р вЂќР С•Р В±Р В°Р Р†Р С‘РЎвЂљРЎРЉ Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚",
        use_container_width=True,
    ):
        if param_name and param_value is not None:
            st.session_state.added_params.append((param_name, param_value, param_unit))
            st.rerun()
        else:
            st.warning(
                "Р вЂ™РЎвЂ№Р В±Р ВµРЎР‚Р С‘РЎвЂљР Вµ Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚ Р С‘ Р Р†Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ Р В·Р Р…Р В°РЎвЂЎР ВµР Р…Р С‘Р Вµ."
            )

    if st.session_state.added_params:
        st.markdown("#### Р Р€Р В¶Р Вµ Р Т‘Р С•Р В±Р В°Р Р†Р В»Р ВµР Р…РЎвЂ№:")
        for i, (pname, pval, punit) in enumerate(st.session_state.added_params):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{pname}**")
            with col2:
                st.write(f"{pval}")
            with col3:
                if punit:
                    st.write(f"{punit}")
            if st.button("СЂСџвЂ”вЂРїС‘РЏ", key=f"del_{i}"):
                st.session_state.added_params.pop(i)
                st.rerun()
        if st.button("Р С›РЎвЂЎР С‘РЎРѓРЎвЂљР С‘РЎвЂљРЎРЉ Р Р†РЎРѓР Вµ", use_container_width=True):
            st.session_state.added_params = []
            st.rerun()
    else:
        st.info(
            "Р СџР С•Р С”Р В° Р Р…Р ВµРЎвЂљ Р Т‘Р С•Р В±Р В°Р Р†Р В»Р ВµР Р…Р Р…РЎвЂ№РЎвЂ¦ Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚Р С•Р Р†."
        )

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

    analyze_btn = st.button(
        "СЂСџвЂќРЊ Р С’Р Р…Р В°Р В»Р С‘Р В·Р С‘РЎР‚Р С•Р Р†Р В°РЎвЂљРЎРЉ",
        type="primary",
        use_container_width=True,
    )

# ---------- Р С›РЎРѓР Р…Р С•Р Р†Р Р…Р В°РЎРЏ Р С•Р В±Р В»Р В°РЎРѓРЎвЂљРЎРЉ ----------
if analyze_btn and st.session_state.raw_text.strip():
    try:
        gender_enum = map_gender(gender)
        patient = PatientProfile(
            id=patient_id,
            gender=gender_enum,
            age=age,
            complaints=[c.strip() for c in complaints.split(",") if c.strip()],
            medications=[m.strip() for m in medications.split(",") if m.strip()],
        )

        with st.spinner(
            "Р вЂ™РЎвЂ№Р С—Р С•Р В»Р Р…РЎРЏР ВµРЎвЂљРЎРѓРЎРЏ Р В°Р Р…Р В°Р В»Р С‘Р В·..."
        ):
            result = run_analysis(patient, st.session_state.raw_text)

        if result:
            st.session_state.analysis_result = result
            st.success("РІСљвЂ¦ Р С’Р Р…Р В°Р В»Р С‘Р В· Р В·Р В°Р Р†Р ВµРЎР‚РЎв‚¬РЎвЂР Р…")

            # ----- Р С›Р В±РЎвЂ°Р С‘Р в„– РЎР‚Р С‘РЎРѓР С” -----
            risk_level = result.get(
                "overall_risk_level", "Р СњР ВµР С‘Р В·Р Р†Р ВµРЎРѓРЎвЂљР Р…Р С•"
            )
            color_map = {
                "Р СњР С•РЎР‚Р СР В°": "green",
                "Р СњР С‘Р В·Р С”Р С‘Р в„–": "blue",
                "Р РЋРЎР‚Р ВµР Т‘Р Р…Р С‘Р в„–": "orange",
                "Р вЂ™РЎвЂ№РЎРѓР С•Р С”Р С‘Р в„–": "red",
                "Р С™РЎР‚Р С‘РЎвЂљР С‘РЎвЂЎР ВµРЎРѓР С”Р С‘Р в„–": "darkred",
            }
            color = color_map.get(risk_level, "gray")
            st.markdown(
                f"<div style='background-color:{color}; padding:10px; border-radius:10px; text-align:center;'>"
                f"<h2 style='color:white; margin:0;'>СЂСџС™РЃ Р С›Р В±РЎвЂ°Р С‘Р в„– РЎС“РЎР‚Р С•Р Р†Р ВµР Р…РЎРЉ РЎР‚Р С‘РЎРѓР С”Р В°: {risk_level}</h2>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # ----- Р вЂќР С‘Р В°Р С–Р Р…Р С•Р В·РЎвЂ№ -----
            diagnoses = result.get("diagnoses", [])
            if diagnoses:
                st.markdown(
                    "### СЂСџвЂњРЉ Р вЂ™РЎвЂ№РЎРЏР Р†Р В»Р ВµР Р…Р Р…РЎвЂ№Р Вµ РЎРѓР С•РЎРѓРЎвЂљР С•РЎРЏР Р…Р С‘РЎРЏ"
                )
                for d in diagnoses:
                    label = d.get("label", d.get("id", "Р СњР ВµР С‘Р В·Р Р†Р ВµРЎРѓРЎвЂљР Р…Р С•"))
                    risk = d.get("risk", "Р СњР С•РЎР‚Р СР В°")
                    combined = d.get("combined", False)
                    desc = d.get("description")
                    card_color = color_map.get(risk, "gray")
                    st.markdown(
                        f"""
                        <div style="border-left: 5px solid {card_color}; padding-left: 15px; margin-bottom: 10px;">
                            <strong>{label}</strong>
                            <span style="background-color:{card_color}; color:white; padding:2px 8px; border-radius:12px; font-size:0.8rem;">{risk}</span>
                            {"РІС™вЂўРїС‘РЏ (Р С”Р С•Р СР В±Р С‘Р Р…Р С‘РЎР‚Р С•Р Р†Р В°Р Р…Р Р…РЎвЂ№Р в„–)" if combined else ""}
                            <br>
                            <span style="font-size:0.9rem; color:#555;">{desc or ""}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info(
                    "Р вЂ”Р Р…Р В°РЎвЂЎР С‘Р СРЎвЂ№РЎвЂ¦ Р С•РЎвЂљР С”Р В»Р С•Р Р…Р ВµР Р…Р С‘Р в„– Р Р…Р Вµ Р С•Р В±Р Р…Р В°РЎР‚РЎС“Р В¶Р ВµР Р…Р С•."
                )

            # ----- Р вЂњРЎР‚РЎС“Р С—Р С—Р С‘РЎР‚Р С•Р Р†Р С”Р В° -----
            grouped = result.get("grouped_findings", {})
            if grouped:
                st.markdown(
                    "### СЂСџВ§В¬ Р В Р В°РЎРѓР С—РЎР‚Р ВµР Т‘Р ВµР В»Р ВµР Р…Р С‘Р Вµ Р С—Р С• РЎРѓР С‘РЎРѓРЎвЂљР ВµР СР В°Р С Р С•РЎР‚Р С–Р В°Р Р…Р С•Р Р†"
                )
                for system, findings in grouped.items():
                    with st.expander(f"**{system}** ({len(findings)})"):
                        for f in findings:
                            label = f.get(
                                "title", f.get("id", "Р СњР ВµР С‘Р В·Р Р†Р ВµРЎРѓРЎвЂљР Р…Р С•")
                            )
                            risk = f.get("risk", "Р СњР С•РЎР‚Р СР В°")
                            desc = f.get("description")
                            card_color = color_map.get(risk, "gray")
                            st.markdown(
                                f"""
                                <div style="border-left: 3px solid {card_color}; padding-left: 10px; margin: 5px 0;">
                                    <strong>{label}</strong> <span style="color:{card_color};">({risk})</span>
                                    <br><span style="font-size:0.85rem; color:#555;">{desc or ""}</span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

            # ----- Р В Р ВµР С”Р С•Р СР ВµР Р…Р Т‘Р В°РЎвЂ Р С‘Р С‘ -----
            recommendations = result.get("recommendations_by_specialty", {})
            if recommendations:
                st.markdown(
                    "### СЂСџвЂРЃРІР‚РЊРІС™вЂўРїС‘РЏ Р В Р ВµР С”Р С•Р СР ВµР Р…Р Т‘Р В°РЎвЂ Р С‘Р С‘ Р С—Р С• РЎРѓР С—Р ВµРЎвЂ Р С‘Р В°Р В»РЎРЉР Р…Р С•РЎРѓРЎвЂљРЎРЏР С"
                )
                for specialty, recs in recommendations.items():
                    with st.expander(f"**{specialty}** ({len(recs)})"):
                        for r in recs:
                            urgency = r.get("urgency", "unknown")
                            tests = r.get("tests", [])
                            st.markdown(f"- **Р РЋРЎР‚Р С•РЎвЂЎР Р…Р С•РЎРѓРЎвЂљРЎРЉ:** {urgency}")
                            if tests:
                                st.markdown(f"  **Р СћР ВµРЎРѓРЎвЂљРЎвЂ№:** {', '.join(tests)}")
                            st.markdown("---")
            else:
                st.info("Р СњР ВµРЎвЂљ РЎР‚Р ВµР С”Р С•Р СР ВµР Р…Р Т‘Р В°РЎвЂ Р С‘Р в„–.")

            # ----- Р С™Р В»Р С‘Р Р…Р С‘РЎвЂЎР ВµРЎРѓР С”Р С‘Р Вµ Р С‘Р Р…РЎРѓР В°Р в„–РЎвЂљРЎвЂ№ -----
            try:
                parameters = parser.parse(st.session_state.raw_text)
                insights = interpreter.interpret(diagnoses, parameters, patient)
                if insights:
                    st.markdown(
                        "### СЂСџВ§В  Р С™Р В»Р С‘Р Р…Р С‘РЎвЂЎР ВµРЎРѓР С”Р С‘Р Вµ Р С‘Р Р…РЎРѓР В°Р в„–РЎвЂљРЎвЂ№ (Р С—Р С•Р Т‘РЎР‚Р С•Р В±Р Р…Р В°РЎРЏ Р С‘Р Р…РЎвЂљР ВµРЎР‚Р С—РЎР‚Р ВµРЎвЂљР В°РЎвЂ Р С‘РЎРЏ)"
                    )
                    for diag_id, insight in insights.items():
                        label = getattr(insight, "label", diag_id)
                        with st.expander(f"**{label}** (ID: {diag_id})"):
                            if hasattr(insight, "criteria") and insight.criteria:
                                st.markdown(
                                    "#### СЂСџвЂњР‰ Р С™РЎР‚Р С‘РЎвЂљР ВµРЎР‚Р С‘Р С‘ Р Т‘Р С‘Р В°Р С–Р Р…Р С•Р В·Р В°"
                                )
                                df_data = []
                                for c in insight.criteria:
                                    df_data.append(
                                        {
                                            "Р СџР В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚": getattr(
                                                c, "parameter", ""
                                            ),
                                            "Р вЂ”Р Р…Р В°РЎвЂЎР ВµР Р…Р С‘Р Вµ": getattr(
                                                c, "value", ""
                                            ),
                                            "Р СњР С•РЎР‚Р СР В°": f"{getattr(c, 'threshold', '')} ({getattr(c, 'condition', '')})",
                                            "Р С™Р С•Р СР СР ВµР Р…РЎвЂљР В°РЎР‚Р С‘Р в„–": getattr(
                                                c, "comment", ""
                                            ),
                                        }
                                    )
                                if df_data:
                                    st.dataframe(
                                        pd.DataFrame(df_data),
                                        use_container_width=True,
                                        hide_index=True,
                                    )
                            if hasattr(insight, "differentials") and insight.differentials:
                                st.markdown(
                                    "#### СЂСџвЂќРЊ Р вЂќР С‘РЎвЂћРЎвЂћР ВµРЎР‚Р ВµР Р…РЎвЂ Р С‘Р В°Р В»РЎРЉР Р…Р В°РЎРЏ Р Т‘Р С‘Р В°Р С–Р Р…Р С•РЎРѓРЎвЂљР С‘Р С”Р В°"
                                )
                                for diff in insight.differentials:
                                    condition = getattr(diff, "condition", "")
                                    text = getattr(diff, "text", "")
                                    st.markdown(
                                        f"- **Р Р€РЎРѓР В»Р С•Р Р†Р С‘Р Вµ:** `{condition}` РІвЂ вЂ™ {text}"
                                    )
                            if hasattr(insight, "red_flags") and insight.red_flags:
                                st.markdown(
                                    "#### РІС™В РїС‘РЏ Р С™РЎР‚Р В°РЎРѓР Р…РЎвЂ№Р Вµ РЎвЂћР В»Р В°Р С–Р С‘"
                                )
                                for rf in insight.red_flags:
                                    condition = getattr(rf, "condition", "")
                                    text = getattr(rf, "text", "")
                                    st.markdown(f"- **{condition}** РІвЂ вЂ™ {text}")
                            if hasattr(insight, "treatment_hints") and insight.treatment_hints:
                                st.markdown(
                                    "#### СЂСџвЂ™Р‰ Р РЃР С—Р В°РЎР‚Р С–Р В°Р В»Р С”Р В° Р С—Р С• РЎвЂљР В°Р С”РЎвЂљР С‘Р С”Р Вµ"
                                )
                                for hint in insight.treatment_hints:
                                    step = getattr(hint, "step", "")
                                    note = getattr(hint, "note", "")
                                    st.markdown(f"- **{step}** РІР‚вЂќ {note}")
                            if hasattr(insight, "references") and insight.references:
                                st.markdown("#### СЂСџвЂњС™ Р РЋРЎРѓРЎвЂ№Р В»Р С”Р С‘")
                                for ref in insight.references:
                                    st.markdown(f"- {ref}")
                else:
                    st.info(
                        "Р вЂќР В»РЎРЏ Р Р†РЎвЂ№РЎРЏР Р†Р В»Р ВµР Р…Р Р…РЎвЂ№РЎвЂ¦ Р Т‘Р С‘Р В°Р С–Р Р…Р С•Р В·Р С•Р Р† Р Р…Р ВµРЎвЂљ Р Т‘Р С•Р С—Р С•Р В»Р Р…Р С‘РЎвЂљР ВµР В»РЎРЉР Р…РЎвЂ№РЎвЂ¦ Р С”Р В»Р С‘Р Р…Р С‘РЎвЂЎР ВµРЎРѓР С”Р С‘РЎвЂ¦ Р С‘Р Р…РЎРѓР В°Р в„–РЎвЂљР С•Р Р†."
                    )
            except Exception as e:
                st.info(
                    f"Р ВР Р…РЎРѓР В°Р в„–РЎвЂљРЎвЂ№ Р Р†РЎР‚Р ВµР СР ВµР Р…Р Р…Р С• Р Р…Р ВµР Т‘Р С•РЎРѓРЎвЂљРЎС“Р С—Р Р…РЎвЂ№: {e}"
                )

            # ----- Р вЂ”Р В°Р С”Р В»РЎР‹РЎвЂЎР ВµР Р…Р С‘Р Вµ (РЎвЂљР ВµР С”РЎРѓРЎвЂљР С•Р Р†Р С•Р Вµ) -----
            conclusion = result.get("conclusion", "")
            if conclusion:
                with st.expander(
                    "СЂСџвЂњвЂћ Р СџР С•Р В»Р Р…Р С•Р Вµ РЎвЂљР ВµР С”РЎРѓРЎвЂљР С•Р Р†Р С•Р Вµ Р В·Р В°Р С”Р В»РЎР‹РЎвЂЎР ВµР Р…Р С‘Р Вµ"
                ):
                    st.text(conclusion)

    except Exception as e:
        st.error(f"РІСњРЉ Р С›РЎв‚¬Р С‘Р В±Р С”Р В°: {e}")

elif analyze_btn:
    st.warning(
        "Р вЂќР С•Р В±Р В°Р Р†РЎРЉРЎвЂљР Вµ РЎвЂ¦Р С•РЎвЂљРЎРЏ Р В±РЎвЂ№ Р С•Р Т‘Р С‘Р Р… Р В»Р В°Р В±Р С•РЎР‚Р В°РЎвЂљР С•РЎР‚Р Р…РЎвЂ№Р в„– Р С—Р В°РЎР‚Р В°Р СР ВµРЎвЂљРЎР‚."
    )

# ----- Р В¤РЎС“РЎвЂљР ВµРЎР‚ -----
st.markdown("---")
st.caption(
    "Р РЋР С‘РЎРѓРЎвЂљР ВµР СР В° Р С‘Р Р…РЎвЂљР ВµРЎР‚Р С—РЎР‚Р ВµРЎвЂљР В°РЎвЂ Р С‘Р С‘ Р В»Р В°Р В±Р С•РЎР‚Р В°РЎвЂљР С•РЎР‚Р Р…РЎвЂ№РЎвЂ¦ Р Т‘Р В°Р Р…Р Р…РЎвЂ№РЎвЂ¦ v1.0 | Р вЂќР ВµР СР С•-Р Р†Р ВµРЎР‚РЎРѓР С‘РЎРЏ"
)
