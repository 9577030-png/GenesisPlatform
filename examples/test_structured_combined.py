# test_structured_combined.py
import requests
import json

url = "http://localhost:8000/analyze_structured"

payload = {
    "patient": {
        "id": "T003",
        "gender": "male",
        "age": 55,
        "complaints": ["fatigue", "fever", "weight loss", "bone pain", "polyuria", "polydipsia"],
        "medications": []
    },
    "raw_text": (
        "WBC 14 10^9/L\n"
        "CRP 80 mg/L\n"
        "Procalcitonin 1.2 ng/mL\n"
        "Creatinine 180 umol/L\n"
        "eGFR 45\n"
        "Vitamin_D 15 ng/mL\n"
        "Triglycerides 2.8 mmol/L\n"
        "HDL 0.8 mmol/L\n"
        "Ferritin 350 ug/L\n"
        "Iron 8 umol/L\n"
        "Transferrin 1.8 g/L\n"
        "Indirect_bilirubin 25 umol/L\n"
        "Albumin 30 g/L\n"
        "Fecal_calprotectin 150 ug/g\n"
        "LDL 3.5 mmol/L\n"
        "Total_cholesterol 6.0 mmol/L\n"
        "Urine_leukocytes 10 cells/HPF\n"
        "Urine_nitrites 1\n"
        "Calcium_total 2.7 mmol/L\n"
        "Haptoglobin 0.2 g/L\n"
        "LDH 300 U/L\n"
        "Glucose 6.0 mmol/L\n"
        "ALT 60 U/L\n"
        "GGT 80 U/L"
    )
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    data = response.json()
    print("\n" + "=" * 70)
    print("СТРУКТУРИРОВАННОЕ ЗАКЛЮЧЕНИЕ С КОМБИНАЦИЯМИ")
    print("=" * 70)
    print(data["conclusion"])

    print("\n▶ Диагнозы (с флагом combined):")
    for d in data["diagnoses"]:
        combined_mark = " [КОМБИНИРОВАННЫЙ]" if d.get("combined", False) else ""
        print(f"  - {d['label']} (prob {d['probability']:.0%}, risk {d['risk']}){combined_mark}")

    print(f"\n▶ Общий риск: {data['overall_risk_level']}")
    print("=" * 70)
else:
    print("Error:", response.status_code, response.text)