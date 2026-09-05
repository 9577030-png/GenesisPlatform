import logging
from genesis_medical.domain.entities.report import AnalysisReport
from medical_app.application.ports.renderer_interface import RendererInterface

logger = logging.getLogger(__name__)

class ConsoleRenderer(RendererInterface):
    """Р РµРЅРґРµСЂРёС‚ РѕС‚С‡С‘С‚ РІ РєРѕРЅСЃРѕР»СЊ СЃ РїСЂРѕСЃС‚С‹Рј С‚РµРєСЃС‚РѕРІС‹Рј С„РѕСЂРјР°С‚РёСЂРѕРІР°РЅРёРµРј."""

    def __init__(self):
        logger.info("ConsoleRenderer initialized")

    def render(self, report: AnalysisReport) -> str:
        logger.info("Rendering report to console")
        lines = []
        lines.append("=" * 50)
        lines.append("MEDICAL ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append("")

        if report.findings:
            lines.append("Findings:")
            for f in report.findings:
                lines.append(f"  - {f.title} (prob: {f.probability:.0%}, risk: {f.risk.label})")
        else:
            lines.append("No findings.")

        lines.append("")
        if report.actions:
            lines.append("Recommendations:")
            for a in report.actions:
                lines.append(f"  - {a.doctor_specialty} (urgency: {a.urgency.value})")
                if a.additional_tests:
                    lines.append(f"    Tests: {', '.join(a.additional_tests)}")
        else:
            lines.append("No recommendations.")

        lines.append("")
        lines.append("Explanation:")
        lines.append(report.explanation or "No explanation provided.")
        lines.append("=" * 50)

        output = "\n".join(lines)
        logger.debug(f"Rendered output: {output[:200]}...")
        logger.info("Report rendered successfully")
        return output
