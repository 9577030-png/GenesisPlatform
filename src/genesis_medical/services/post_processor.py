import logging
from typing import List, Dict, Any, Set
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.value_objects.severity import Severity
from genesis_medical.sources.clinical_logic_loader import ClinicalLogicLoader

logger = logging.getLogger(__name__)

class PostProcessor:
    def __init__(self, logic_loader: ClinicalLogicLoader = None, probability_threshold: float = 0.3):
        self.threshold = probability_threshold
        self.logic_loader = logic_loader or ClinicalLogicLoader()
        self.config = self.logic_loader.get_config()
        self.groups = self.config.get("groups", {})
        self.priority = self.config.get("priority", {})
        self.exclusions = self.config.get("exclusions", [])
        self.combinations = self.config.get("combinations", [])

        # Р—Р°РіСЂСѓР¶Р°РµРј РјР°РїРїРёРЅРіРё РёР· РєРѕРЅС„РёРіР°
        self.diagnosis_labels = self.logic_loader.get_diagnosis_labels()
        self.system_groups = self.logic_loader.get_system_groups()
        self.allowed_primary = self.logic_loader.get_allowed_primary()

        if "probability_threshold" in self.config:
            self.threshold = self.config["probability_threshold"].get("default", self.threshold)

        logger.info(f"PostProcessor initialized with threshold {self.threshold}")
        logger.info(f"Loaded {len(self.diagnosis_labels)} labels, {len(self.system_groups)} system groups, {len(self.allowed_primary)} primary diagnoses")

    def process(self, report: AnalysisReport) -> Dict[str, Any]:
        # 1. РћС‚С„РёР»СЊС‚СЂРѕРІС‹РІР°РµРј РїРѕ РїРѕСЂРѕРіСѓ
        significant = [f for f in report.findings if f.probability >= self.threshold]
        logger.info(f"Significant findings (raw): {len(significant)}")
        for f in significant:
            logger.info(f"  Finding: {f.id} prob={f.probability} risk={f.risk}")

        # 2. РџСЂРёРјРµРЅСЏРµРј РёСЃРєР»СЋС‡РµРЅРёСЏ РёР· clinical_logic.yaml
        significant = self._apply_exclusions(significant)
        logger.info(f"After exclusions: {len(significant)}")

        # 3. Р–С‘СЃС‚РєРёР№ С„РёР»СЊС‚СЂ РїРѕ Р±РµР»РѕРјСѓ СЃРїРёСЃРєСѓ вЂ“ Р’Р Р•РњР•РќРќРћ РћРўРљР›Р®Р§Р•Рќ
        # РџСЂРѕРїСѓСЃРєР°РµРј РІСЃРµ РЅР°С…РѕРґРєРё Р±РµР· С„РёР»СЊС‚СЂР°С†РёРё
        filtered = significant
        logger.info(f"After white-list filter (disabled): {len(filtered)}")

        # РЎС‚Р°СЂС‹Р№ РєРѕРґ С„РёР»СЊС‚СЂР°С†РёРё (Р·Р°РєРѕРјРјРµРЅС‚РёСЂРѕРІР°РЅ)
        # filtered = []
        # if any(f.id == "diabetes_mellitus_type_2" for f in significant):
        #     allowed = {"diabetes_mellitus_type_2", "severe_hyperglycemia"}
        #     filtered = [f for f in significant if f.id in allowed]
        # elif any(f.id == "iron_deficiency" for f in significant):
        #     allowed = {"iron_deficiency"}
        #     filtered = [f for f in significant if f.id in allowed]
        # else:
        #     filtered = [f for f in significant if f.id in self.allowed_primary]
        # logger.info(f"After white-list filter: {len(filtered)}")

        significant = filtered

        # 4. Р“СЂСѓРїРїРёСЂРѕРІРєР° РїРѕ СЃРёСЃС‚РµРјР°Рј (РёСЃРїРѕР»СЊР·СѓРµРј Р·Р°РіСЂСѓР¶РµРЅРЅС‹Р№ СЃР»РѕРІР°СЂСЊ)
        grouped = self._build_grouped(significant)

        # 5. РљРѕРјР±РёРЅРёСЂРѕРІР°РЅРЅС‹Рµ РґРёР°РіРЅРѕР·С‹
        combined_diagnoses, combined_recommendations = self._apply_combinations(significant)

        # 6. Р¤РѕСЂРјРёСЂСѓРµРј diagnoses (Р±РµР· probability)
        diagnoses = []
        for f in significant:
            label = self.diagnosis_labels.get(f.id, f.id)
            diagnoses.append({
                "id": f.id,
                "label": label,
                "risk": f.risk.label if hasattr(f.risk, 'label') else str(f.risk),
                "combined": False,
                "description": f.description
            })
        diagnoses.extend(combined_diagnoses)

        # 7. Р”РµР№СЃС‚РІРёСЏ (СЂРµРєРѕРјРµРЅРґР°С†РёРё)
        base_actions = report.actions
        combined_actions = self._create_actions_from_combinations(combined_recommendations)
        all_actions = base_actions + combined_actions

        recommendations_by_specialty = {}
        for action in all_actions:
            spec = action.doctor_specialty
            if spec not in recommendations_by_specialty:
                recommendations_by_specialty[spec] = []
            recommendations_by_specialty[spec].append({
                "urgency": action.urgency.value,
                "tests": action.additional_tests
            })

        # 8. РћР±С‰РёР№ СѓСЂРѕРІРµРЅСЊ СЂРёСЃРєР°
        max_risk = max((f.risk for f in significant), key=lambda r: r.value if hasattr(r, 'value') else 0, default=None)
        overall_risk_level = max_risk.label if max_risk and hasattr(max_risk, 'label') else "РќРѕСЂРјР°"

        # 9. Р—Р°РєР»СЋС‡РµРЅРёРµ
        conclusion = self._build_conclusion(diagnoses, grouped, recommendations_by_specialty, max_risk)

        return {
            "diagnoses": diagnoses,
            "grouped_findings": grouped,
            "recommendations_by_specialty": recommendations_by_specialty,
            "overall_risk_level": overall_risk_level,
            "conclusion": conclusion,
            "full_report": report
        }

    def _apply_exclusions(self, findings: List[ClinicalFinding]) -> List[ClinicalFinding]:
        ids = {f.id for f in findings}

        def _matches(base_id: str) -> bool:
            # id РЅР°С…РѕРґРєРё Р±С‹РІР°РµС‚ Р»РёР±Рѕ СЃР°РјРёРј base_id (С„Р°Р№Р» СЃ РѕРґРЅРёРј РїР°СЂР°РјРµС‚СЂРѕРј),
            # Р»РёР±Рѕ "{base_id}_{parameter}" (С„Р°Р№Р» СЃ РЅРµСЃРєРѕР»СЊРєРёРјРё РїР°СЂР°РјРµС‚СЂР°РјРё,
            # СЃРј. domain/rule_version.py::_convert_old_format). exclusions/priority
            # РІ clinical_logic.yaml РІСЃРµРіРґР° РѕРїРёСЃР°РЅС‹ РІ С‚РµСЂРјРёРЅР°С… base_id, РїРѕСЌС‚РѕРјСѓ
            # РїСЂРѕРІРµСЂСЏРµРј РѕР±Р° РІР°СЂРёР°РЅС‚Р°, Р° РЅРµ С‚РѕР»СЊРєРѕ С‚РѕС‡РЅРѕРµ СЃРѕРІРїР°РґРµРЅРёРµ.
            if base_id in ids:
                return True
            prefix = base_id + "_"
            return any(fid.startswith(prefix) for fid in ids)

        def _remove(base_id: str):
            if base_id in ids:
                to_remove.add(base_id)
            prefix = base_id + "_"
            for fid in ids:
                if fid.startswith(prefix):
                    to_remove.add(fid)

        to_remove = set()
        for rule in self.exclusions:
            if_condition = rule.get("if")
            if _matches(if_condition):
                for excluded in rule.get("then", []):
                    _remove(excluded)
        return [f for f in findings if f.id not in to_remove]

    def _build_grouped(self, findings: List[ClinicalFinding]) -> Dict[str, List[Dict]]:
        grouped = {}
        for system, ids in self.system_groups.items():
            found = [f for f in findings if f.id in ids]
            if found:
                grouped[system] = [
                    {
                        "id": f.id,
                        "title": f.title,
                        "probability": f.probability,
                        "risk": f.risk.label if hasattr(f.risk, 'label') else str(f.risk),
                        "description": f.description,
                        "doctor_specialty": f.doctor_specialty,
                        "tests": f.tests,
                        "evidence": f.evidence
                    }
                    for f in found
                ]
        return grouped

    def _apply_combinations(self, findings: List[ClinicalFinding]) -> tuple:
        findings_dict = {f.id: f for f in findings}
        combined_diagnoses = []
        combined_recommendations = []

        for combo in self.combinations:
            conditions = combo.get("conditions", [])
            if not all(cond in findings_dict for cond in conditions):
                continue

            probs = [findings_dict[cond].probability for cond in conditions]
            avg_prob = sum(probs) / len(probs)
            factor = combo.get("probability_factor", 1.0)
            combo_prob = min(avg_prob * factor, 1.0)

            if combo_prob < self.threshold:
                continue

            combined_diagnoses.append({
                "id": combo["id"],
                "label": combo["label"],
                "risk": "Р’С‹СЃРѕРєРёР№",
                "combined": True,
                "conditions": conditions,
                "description": combo.get("recommendation") or combo.get("description") or "РљРѕРјР±РёРЅРёСЂРѕРІР°РЅРЅРѕРµ СЃРѕСЃС‚РѕСЏРЅРёРµ"
            })

            try:
                urgency_str = combo.get("urgency", "moderate").upper()
                urgency = Severity[urgency_str] if urgency_str in Severity.__members__ else Severity.MODERATE
                rec = Recommendation(
                    doctor_specialty=combo.get("doctor_specialty", "General Practitioner"),
                    urgency=urgency,
                    additional_tests=combo.get("additional_tests", [])
                )
                combined_recommendations.append(rec)
            except Exception as e:
                logger.error(f"Failed to create recommendation for combination {combo['id']}: {e}")

        return combined_diagnoses, combined_recommendations

    def _create_actions_from_combinations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        return recommendations

    def _build_conclusion(self, diagnoses, grouped, recommendations_by_specialty, max_risk) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("РљР›РРќРР§Р•РЎРљРћР• Р—РђРљР›Р®Р§Р•РќРР•")
        lines.append("=" * 60)

        if not diagnoses:
            lines.append("Р—РЅР°С‡РёРјС‹С… РѕС‚РєР»РѕРЅРµРЅРёР№ РЅРµ РѕР±РЅР°СЂСѓР¶РµРЅРѕ.")
            return "\n".join(lines)

        lines.append("\nв–¶ Р’С‹СЏРІР»РµРЅРЅС‹Рµ СЃРѕСЃС‚РѕСЏРЅРёСЏ:")
        for d in diagnoses:
            label = d.get('label', d['id'])
            risk_label = d['risk']
            desc = d.get('description')
            if desc:
                lines.append(f"  - {label}: {desc}")
            else:
                lines.append(f"  - {label} (СЂРёСЃРє {risk_label})")
            if d.get("combined", False):
                lines.append("    (РєРѕРјР±РёРЅРёСЂРѕРІР°РЅРЅРѕРµ Р·Р°РєР»СЋС‡РµРЅРёРµ)")

        lines.append("\nв–¶ РџРѕ СЃРёСЃС‚РµРјР°Рј РѕСЂРіР°РЅРѕРІ:")
        for system, findings in grouped.items():
            lines.append(f"  {system}:")
            for f in findings:
                desc = f.get('description') or f.get('title', f['id'])
                lines.append(f"    - {desc} (СЂРёСЃРє {f['risk']})")

        lines.append("\nв–¶ Р РµРєРѕРјРµРЅРґР°С†РёРё РїРѕ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅРѕРјСѓ РѕР±СЃР»РµРґРѕРІР°РЅРёСЋ:")
        if recommendations_by_specialty:
            for spec, recs in recommendations_by_specialty.items():
                lines.append(f"  {spec}:")
                for r in recs:
                    lines.append(f"    - РЎСЂРѕС‡РЅРѕСЃС‚СЊ: {r['urgency']}, С‚РµСЃС‚С‹: {', '.join(r['tests'])}")
        else:
            lines.append("  РќРµС‚ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹С… СЂРµРєРѕРјРµРЅРґР°С†РёР№.")

        if max_risk:
            risk_label = max_risk.label if hasattr(max_risk, 'label') else str(max_risk)
            lines.append(f"\nв–¶ РћР±С‰РёР№ СѓСЂРѕРІРµРЅСЊ СЂРёСЃРєР°: {risk_label}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
