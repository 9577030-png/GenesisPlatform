import os
import streamlit as st
import requests
import json
import pandas as pd
from medical_app.config import settings
import jwt
from typing import List, Dict, Any

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# ---------- Р’СЃРїРѕРјРѕРіР°С‚РµР»СЊРЅС‹Рµ С„СѓРЅРєС†РёРё ----------
def get_token(username, password):
    resp = requests.post(f"{API_BASE}/token", data={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None

def analyze_data(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_BASE}/analyze_structured", json=payload, headers=headers, timeout=30)
    return resp

def generate_pdf(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_BASE}/export_pdf", json=payload, headers=headers, timeout=30)
    return resp

def reload_config(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_BASE}/reload_config", headers=headers)
    return resp

def get_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_BASE}/users", headers=headers)
    return resp

def register_user(token, username, password, role="user"):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"username": username, "password": password, "role": role}
    resp = requests.post(f"{API_BASE}/register", json=payload, headers=headers)
    return resp

def delete_user(token, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(f"{API_BASE}/admin/user/{user_id}", headers=headers)
    return resp

def get_history(token, patient_id):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_BASE}/admin/history/{patient_id}", headers=headers)
    return resp

def get_config_file(token, path):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_BASE}/admin/config/file", params={"path": path}, headers=headers)
    return resp

def save_config_file(token, path, content):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"path": path, "content": content}
    resp = requests.post(f"{API_BASE}/admin/config/file", json=payload, headers=headers)
    return resp

# ---------- Р—Р°РіСЂСѓР·РєР° СЃРїРёСЃРєР° РїР°СЂР°РјРµС‚СЂРѕРІ РґР»СЏ Р°РІС‚РѕРїРѕРґСЃС‚Р°РЅРѕРІРєРё ----------
@st.cache_data(ttl=3600)
def load_parameter_list():
    """Р—Р°РіСЂСѓР¶Р°РµС‚ РІСЃРµ РёР·РІРµСЃС‚РЅС‹Рµ РїР°СЂР°РјРµС‚СЂС‹ РёР· aliases.yaml (РєР°РЅРѕРЅРёС‡РµСЃРєРёРµ Рё СЃРёРЅРѕРЅРёРјС‹)"""
    try:
        import yaml
        aliases_path = os.path.join("knowledge", "laboratory", "aliases.yaml")
        with open(aliases_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        aliases = data.get("aliases", {})
        all_names = set()
        for canonical, synonyms in aliases.items():
            all_names.add(canonical)
            for syn in synonyms:
                all_names.add(syn)
        return sorted(all_names)
    except Exception as e:
        st.warning(f"РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ СЃРїРёСЃРѕРє РїР°СЂР°РјРµС‚СЂРѕРІ: {e}")
        return []

# ---------- РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ СЃРµСЃСЃРёРё ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "РђРЅР°Р»РёР·"
if "last_payload" not in st.session_state:
    st.session_state.last_payload = None
if "parameters_list" not in st.session_state:
    st.session_state.parameters_list = load_parameter_list()
if "added_params" not in st.session_state:
    st.session_state.added_params = []  # СЃРїРёСЃРѕРє РєРѕСЂС‚РµР¶РµР№ (name, value, unit)
# --- Р”РѕР±Р°РІР»РµРЅР° РёРЅРёС†РёР°Р»РёР·Р°С†РёСЏ patient_id ---
if "patient_id" not in st.session_state:
    st.session_state.patient_id = "P001"

# ---------- РђСѓС‚РµРЅС‚РёС„РёРєР°С†РёСЏ ----------
if not st.session_state.token:
    st.sidebar.markdown("### рџ”ђ Р’С…РѕРґ")
    username = st.sidebar.text_input("Р›РѕРіРёРЅ")
    password = st.sidebar.text_input("РџР°СЂРѕР»СЊ", type="password")
    if st.sidebar.button("Р’РѕР№С‚Рё"):
        token = get_token(username, password)
        if token:
            try:
               payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
               role = payload.get("role", "user")
            except jwt.InvalidTokenError:
               role = "user"
            st.session_state.token = token
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
        else:
            st.sidebar.error("РќРµРІРµСЂРЅС‹Рµ Р»РѕРіРёРЅ/РїР°СЂРѕР»СЊ")
    st.stop()
else:
    st.sidebar.markdown(f"вњ… Р’С‹ РІРѕС€Р»Рё РєР°Рє **{st.session_state.username}** (СЂРѕР»СЊ: {st.session_state.role})")
    if st.sidebar.button("Р’С‹Р№С‚Рё"):
        st.session_state.token = None
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.analysis_result = None
        st.session_state.last_payload = None
        st.rerun()

# ---------- РќР°РІРёРіР°С†РёСЏ ----------
page = st.sidebar.radio("Р’С‹Р±РµСЂРёС‚Рµ СЂР°Р·РґРµР»", ["РђРЅР°Р»РёР·", "РђРґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ"])
st.session_state.current_page = page

# =====================================================
# РЎРўР РђРќРР¦Рђ РђРќРђР›РР—Рђ
# =====================================================
if page == "РђРЅР°Р»РёР·":
    st.title("рџ§Є РЎРёСЃС‚РµРјР° РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹С… РґР°РЅРЅС‹С…")
    st.markdown("Р’РІРµРґРёС‚Рµ РґР°РЅРЅС‹Рµ РїР°С†РёРµРЅС‚Р° Рё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹Рµ РїРѕРєР°Р·Р°С‚РµР»Рё РґР»СЏ РїРѕР»СѓС‡РµРЅРёСЏ РєР»РёРЅРёС‡РµСЃРєРѕРіРѕ Р·Р°РєР»СЋС‡РµРЅРёСЏ.")

    with st.sidebar:
        st.header("рџ§‘вЂЌвљ•пёЏ Р”Р°РЅРЅС‹Рµ РїР°С†РёРµРЅС‚Р°")
        patient_id = st.text_input("ID РїР°С†РёРµРЅС‚Р°", value=st.session_state.patient_id)
        gender = st.selectbox("РџРѕР»", ["male", "female", "other"])
        age = st.number_input("Р’РѕР·СЂР°СЃС‚", min_value=0, max_value=150, value=45)
        complaints = st.text_area("Р–Р°Р»РѕР±С‹ (С‡РµСЂРµР· Р·Р°РїСЏС‚СѓСЋ)", value="fatigue, weakness")
        medications = st.text_area("РџСЂРёРЅРёРјР°РµРјС‹Рµ Р»РµРєР°СЂСЃС‚РІР° (С‡РµСЂРµР· Р·Р°РїСЏС‚СѓСЋ)", value="")

        st.markdown("---")
        st.markdown("### рџ“‹ Р”РѕР±Р°РІРёС‚СЊ Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹Р№ РїР°СЂР°РјРµС‚СЂ")

        param_options = st.session_state.parameters_list
        param_name = st.selectbox(
            "РџР°СЂР°РјРµС‚СЂ",
            options=param_options,
            format_func=lambda x: x,
            placeholder="РќР°С‡РЅРёС‚Рµ РІРІРѕРґРёС‚СЊ РЅР°Р·РІР°РЅРёРµ...",
            key="param_select"
        )

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

    # ---- РћСЃРЅРѕРІРЅР°СЏ РѕР±Р»Р°СЃС‚СЊ ----
    with st.expander("рџ“ќ РЎС„РѕСЂРјРёСЂРѕРІР°РЅРЅС‹Р№ С‚РµРєСЃС‚ РґР»СЏ Р°РЅР°Р»РёР·Р°", expanded=False):
        st.code(st.session_state.raw_text or "(РїСѓСЃС‚Рѕ)", language="text")

    # ---- Р›РѕРіРёРєР° Р°РЅР°Р»РёР·Р° ----
    if analyze_btn:
        if not st.session_state.raw_text.strip():
            st.error("РџРѕР¶Р°Р»СѓР№СЃС‚Р°, РґРѕР±Р°РІСЊС‚Рµ С…РѕС‚СЏ Р±С‹ РѕРґРёРЅ Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹Р№ РїР°СЂР°РјРµС‚СЂ.")
            st.stop()

        payload = {
            "patient": {
                "id": patient_id,
                "gender": gender,
                "age": age,
                "complaints": [c.strip() for c in complaints.split(",") if c.strip()],
                "medications": [m.strip() for m in medications.split(",") if m.strip()]
            },
            "raw_text": st.session_state.raw_text
        }

        try:
            with st.spinner("Р’С‹РїРѕР»РЅСЏРµС‚СЃСЏ Р°РЅР°Р»РёР·..."):
                response = analyze_data(payload, st.session_state.token)
            if response.status_code == 200:
                data = response.json()
                st.session_state.analysis_result = data
                st.session_state.last_payload = payload
                # --- РЎРѕС…СЂР°РЅСЏРµРј patient_id РІ session_state ---
                st.session_state.patient_id = patient_id
                st.success("вњ… РђРЅР°Р»РёР· Р·Р°РІРµСЂС€С‘РЅ")

                with st.expander("рџ“¦ РћС‚Р»Р°РґРѕС‡РЅР°СЏ РёРЅС„РѕСЂРјР°С†РёСЏ (Р·Р°РїСЂРѕСЃ Рё РѕС‚РІРµС‚)", expanded=False):
                    st.markdown("**РћС‚РїСЂР°РІР»РµРЅРЅС‹Р№ С‚РµРєСЃС‚ (raw_text):**")
                    st.code(repr(st.session_state.raw_text), language="text")
                    st.markdown("**Payload (JSON):**")
                    st.json(payload)
                    st.markdown("**РћС‚РІРµС‚ API:**")
                    st.json(data)

                risk_level = data.get("overall_risk_level", "РќРµРёР·РІРµСЃС‚РЅРѕ")
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

                diagnoses = data.get("diagnoses", [])
                if diagnoses:
                    st.markdown("### рџ“Њ Р’С‹СЏРІР»РµРЅРЅС‹Рµ СЃРѕСЃС‚РѕСЏРЅРёСЏ")
                    for d in diagnoses:
                        label = d.get("label", d.get("id", "РќРµРёР·РІРµСЃС‚РЅРѕ"))
                        risk = d.get("risk", "РќРѕСЂРјР°")
                        combined = d.get("combined", False)
                        desc = d.get("description")
                        card_color = color_map.get(risk, "gray")
                        with st.container():
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

                grouped = data.get("grouped_findings", {})
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

                recommendations = data.get("recommendations_by_specialty", {})
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

                insights = data.get("clinical_insights", {})
                if insights:
                    st.markdown("### рџ§  РљР»РёРЅРёС‡РµСЃРєРёРµ РёРЅСЃР°Р№С‚С‹ (РїРѕРґСЂРѕР±РЅР°СЏ РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёСЏ)")
                    for diag_id, insight in insights.items():
                        label = insight.get("label", diag_id)
                        with st.expander(f"**{label}** (ID: {diag_id})"):
                            criteria = insight.get("criteria", [])
                            if criteria:
                                st.markdown("#### рџ“Љ РљСЂРёС‚РµСЂРёРё РґРёР°РіРЅРѕР·Р°")
                                df_criteria = pd.DataFrame([
                                    {
                                        "РџР°СЂР°РјРµС‚СЂ": c.get("parameter", ""),
                                        "Р—РЅР°С‡РµРЅРёРµ": c.get("value", ""),
                                        "РќРѕСЂРјР°": f"{c.get('threshold', '')} ({c.get('condition', '')})",
                                        "РљРѕРјРјРµРЅС‚Р°СЂРёР№": c.get("comment", "")
                                    }
                                    for c in criteria
                                ])
                                st.dataframe(df_criteria, use_container_width=True, hide_index=True)
                            differentials = insight.get("differentials", [])
                            if differentials:
                                st.markdown("#### рџ”Ќ Р”РёС„С„РµСЂРµРЅС†РёР°Р»СЊРЅР°СЏ РґРёР°РіРЅРѕСЃС‚РёРєР°")
                                for diff in differentials:
                                    st.markdown(f"- **РЈСЃР»РѕРІРёРµ:** `{diff.get('condition', '')}` в†’ {diff.get('text', '')}")
                            red_flags = insight.get("red_flags", [])
                            if red_flags:
                                st.markdown("#### вљ пёЏ РљСЂР°СЃРЅС‹Рµ С„Р»Р°РіРё")
                                for rf in red_flags:
                                    st.markdown(f"- **{rf.get('condition', '')}** в†’ {rf.get('text', '')}")
                            treatment_hints = insight.get("treatment_hints", [])
                            if treatment_hints:
                                st.markdown("#### рџ’Љ РЎРѕРІРµС‚С‹ РїРѕ С‚Р°РєС‚РёРєРµ")
                                for hint in treatment_hints:
                                    st.markdown(f"- **{hint.get('step', '')}** вЂ” {hint.get('note', '')}")
                            references = insight.get("references", [])
                            if references:
                                st.markdown("#### рџ“љ РЎСЃС‹Р»РєРё")
                                for ref in references:
                                    st.markdown(f"- {ref}")
                else:
                    st.info("Р”Р»СЏ РІС‹СЏРІР»РµРЅРЅС‹С… РґРёР°РіРЅРѕР·РѕРІ РЅРµС‚ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹С… РєР»РёРЅРёС‡РµСЃРєРёС… РёРЅСЃР°Р№С‚РѕРІ.")

                conclusion = data.get("conclusion", "")
                if conclusion:
                    with st.expander("рџ“„ РџРѕР»РЅРѕРµ С‚РµРєСЃС‚РѕРІРѕРµ Р·Р°РєР»СЋС‡РµРЅРёРµ "):
                        lines = conclusion.split("\n")
                        filtered = []
                        skip = False
                        for line in lines:
                            if "в–¶ Р РµРєРѕРјРµРЅРґР°С†РёРё РїРѕ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅРѕРјСѓ РѕР±СЃР»РµРґРѕРІР°РЅРёСЋ:" in line:
                                skip = True
                                continue
                            if not skip:
                                filtered.append(line)
                        st.text("\n".join(filtered).strip())

            elif response.status_code == 401:
                st.error("вќЊ РЎРµСЃСЃРёСЏ РёСЃС‚РµРєР»Р°. Р’РѕР№РґРёС‚Рµ Р·Р°РЅРѕРІРѕ.")
                st.session_state.token = None
                st.rerun()
            else:
                st.error(f"РћС€РёР±РєР° API: {response.status_code}")
                st.json(response.text)
        except Exception as e:
            st.error(f"вќЊ РћС€РёР±РєР°: {e}")

    # ----- PDF -----
    if st.session_state.last_payload is not None and st.session_state.token is not None:
        st.markdown("---")
        if st.button("рџ“„ РЎРєР°С‡Р°С‚СЊ PDF", use_container_width=True):
            with st.spinner("Р“РµРЅРµСЂР°С†РёСЏ PDF..."):
                pdf_resp = generate_pdf(st.session_state.last_payload, st.session_state.token)
                if pdf_resp.status_code == 200:
                    st.download_button(
                        label="рџ’ѕ РЎРѕС…СЂР°РЅРёС‚СЊ PDF",
                        data=pdf_resp.content,
                        file_name=f"report_{st.session_state.patient_id}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF РіРѕС‚РѕРІ! РљРЅРѕРїРєР° СЃРѕС…СЂР°РЅРµРЅРёСЏ РЅРёР¶Рµ.")
                elif pdf_resp.status_code == 401:
                    st.error("вќЊ РЎРµСЃСЃРёСЏ РёСЃС‚РµРєР»Р°. Р’РѕР№РґРёС‚Рµ Р·Р°РЅРѕРІРѕ.")
                    st.session_state.token = None
                    st.rerun()
                else:
                    st.error(f"РћС€РёР±РєР° РіРµРЅРµСЂР°С†РёРё PDF: {pdf_resp.status_code}")
                    st.json(pdf_resp.text)

# =====================================================
# РЎРўР РђРќРР¦Рђ РђР”РњРРќРРЎРўР РР РћР’РђРќРРЇ (Р±РµР· РёР·РјРµРЅРµРЅРёР№)
# =====================================================
elif page == "РђРґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ":
    st.title("рџ› пёЏ РђРґРјРёРЅРёСЃС‚СЂРёСЂРѕРІР°РЅРёРµ СЃРёСЃС‚РµРјС‹")
    if st.session_state.role != "admin":
        st.error("РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ Р°РґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂР°.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["рџ‘¤ РџРѕР»СЊР·РѕРІР°С‚РµР»Рё", "рџ“њ РСЃС‚РѕСЂРёСЏ", "вљ™пёЏ РџСЂР°РІРёР»Р°"])

    with tab1:
        st.subheader("РЈРїСЂР°РІР»РµРЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏРјРё")
        if st.button("РћР±РЅРѕРІРёС‚СЊ СЃРїРёСЃРѕРє"):
            st.rerun()

        resp = get_users(st.session_state.token)
        if resp.status_code == 200:
            users = resp.json()
            for u in users:
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                with col1:
                    st.write(u["id"])
                with col2:
                    st.write(u["username"])
                with col3:
                    st.write(u["role"])
                with col4:
                    if u["username"] not in ("admin", "doctor"):
                        if st.button(f"РЈРґР°Р»РёС‚СЊ {u['id']}", key=f"del_{u['id']}"):
                            del_resp = delete_user(st.session_state.token, u["id"])
                            if del_resp.status_code == 200:
                                st.success(f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ {u['username']} СѓРґР°Р»С‘РЅ")
                                st.rerun()
                            else:
                                st.error(f"РћС€РёР±РєР°: {del_resp.text}")
        else:
            st.error(f"РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№: {resp.text}")

        st.markdown("---")
        st.subheader("Р”РѕР±Р°РІРёС‚СЊ РЅРѕРІРѕРіРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ")
        with st.form("register_form"):
            new_username = st.text_input("Р›РѕРіРёРЅ")
            new_password = st.text_input("РџР°СЂРѕР»СЊ", type="password")
            new_role = st.selectbox("Р РѕР»СЊ", ["user", "admin", "doctor"])
            submitted = st.form_submit_button("РЎРѕР·РґР°С‚СЊ")
            if submitted:
                if new_username and new_password:
                    reg_resp = register_user(st.session_state.token, new_username, new_password, new_role)
                    if reg_resp.status_code == 200:
                        st.success(f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ {new_username} СЃРѕР·РґР°РЅ")
                        st.rerun()
                    else:
                        st.error(f"РћС€РёР±РєР°: {reg_resp.text}")
                else:
                    st.warning("Р—Р°РїРѕР»РЅРёС‚Рµ РІСЃРµ РїРѕР»СЏ")

        if st.button("РџРµСЂРµР·Р°РіСЂСѓР·РёС‚СЊ РєРѕРЅС„РёРіСѓСЂР°С†РёСЋ (РїСЂР°РІРёР»Р°)"):
            with st.spinner("РџРµСЂРµР·Р°РіСЂСѓР·РєР°..."):
                reload_resp = reload_config(st.session_state.token)
                if reload_resp.status_code == 200:
                    st.success("РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ РїРµСЂРµР·Р°РіСЂСѓР¶РµРЅР°")
                else:
                    st.error(f"РћС€РёР±РєР°: {reload_resp.text}")

    with tab2:
        st.subheader("РџСЂРѕСЃРјРѕС‚СЂ РёСЃС‚РѕСЂРёРё РїР°С†РёРµРЅС‚Р°")
        history_patient_id = st.text_input("ID РїР°С†РёРµРЅС‚Р°", value="P001")
        if st.button("РџРѕРєР°Р·Р°С‚СЊ РёСЃС‚РѕСЂРёСЋ"):
            if history_patient_id:
                with st.spinner("Р—Р°РіСЂСѓР·РєР°..."):
                    hist_resp = get_history(st.session_state.token, history_patient_id)
                    if hist_resp.status_code == 200:
                        data = hist_resp.json()
                        st.json(data)
                    else:
                        st.error(f"РћС€РёР±РєР°: {hist_resp.text}")

    with tab3:
        st.subheader("Р РµРґР°РєС‚РёСЂРѕРІР°РЅРёРµ РєРѕРЅС„РёРіСѓСЂР°С†РёРѕРЅРЅС‹С… С„Р°Р№Р»РѕРІ")
        config_path = st.text_input("РџСѓС‚СЊ Рє С„Р°Р№Р»Сѓ (РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ knowledge/)", value="configs/clinical_thresholds.yaml")
        if st.button("Р—Р°РіСЂСѓР·РёС‚СЊ С„Р°Р№Р»"):
            with st.spinner("Р—Р°РіСЂСѓР·РєР°..."):
                file_resp = get_config_file(st.session_state.token, config_path)
                if file_resp.status_code == 200:
                    file_data = file_resp.json()
                    st.session_state.current_config_content = file_data["content"]
                    st.session_state.current_config_path = file_data["path"]
                    st.success(f"Р¤Р°Р№Р» {file_data['path']} Р·Р°РіСЂСѓР¶РµРЅ")
                else:
                    st.error(f"РћС€РёР±РєР°: {file_resp.text}")

        if "current_config_content" in st.session_state:
            new_content = st.text_area("РЎРѕРґРµСЂР¶РёРјРѕРµ С„Р°Р№Р»Р°", value=st.session_state.current_config_content, height=400)
            if st.button("РЎРѕС…СЂР°РЅРёС‚СЊ С„Р°Р№Р»"):
                save_resp = save_config_file(
                    st.session_state.token,
                    st.session_state.current_config_path,
                    new_content
                )
                if save_resp.status_code == 200:
                    st.success("Р¤Р°Р№Р» СЃРѕС…СЂР°РЅС‘РЅ")
                    st.session_state.current_config_content = new_content
                    if st.button("РџРµСЂРµР·Р°РіСЂСѓР·РёС‚СЊ РїСЂР°РІРёР»Р° РїРѕСЃР»Рµ СЃРѕС…СЂР°РЅРµРЅРёСЏ"):
                        reload_resp = reload_config(st.session_state.token)
                        if reload_resp.status_code == 200:
                            st.success("РљРѕРЅС„РёРіСѓСЂР°С†РёСЏ РїРµСЂРµР·Р°РіСЂСѓР¶РµРЅР°")
                        else:
                            st.error(f"РћС€РёР±РєР° РїРµСЂРµР·Р°РіСЂСѓР·РєРё: {reload_resp.text}")
                else:
                    st.error(f"РћС€РёР±РєР° СЃРѕС…СЂР°РЅРµРЅРёСЏ: {save_resp.text}")

st.markdown("---")
st.caption("РЎРёСЃС‚РµРјР° РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёРё Р»Р°Р±РѕСЂР°С‚РѕСЂРЅС‹С… РґР°РЅРЅС‹С… v1.0 | API: localhost:8000")
