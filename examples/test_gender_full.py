import requests
import json

url = "http://localhost:8000/analyze"

# Данные анализов
raw_text = "Hemoglobin 125 g/L\nCreatinine 110 umol/L\nFerritin 25 ng/mL\nHDL 0.9 mmol/L"

# Мужской запрос (создаём отдельный словарь)
payload_male = {
    "patient": {
        "id": "M001",
        "gender": "male",
        "age": 45,
        "complaints": ["fatigue", "weakness"],
        "medications": []
    },
    "raw_text": raw_text
}

# Женский запрос (отдельный словарь)
payload_female = {
    "patient": {
        "id": "F001",
        "gender": "female",
        "age": 45,
        "complaints": ["fatigue", "weakness"],
        "medications": []
    },
    "raw_text": raw_text
}

def run_test(payload, label):
    print("=" * 60)
    print(label)
    print("=" * 60)
    resp = requests.post(url, json=payload)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        print("Explanation:")
        print(data.get("explanation", "Нет объяснения"))
        findings = [f for f in data.get("findings", []) if f["probability"] > 0]
        if findings:
            print("Обнаруженные отклонения:")
            for f in findings:
                print(f"  - {f['title']} (prob {f['probability']:.0%}, risk {f['risk']})")
        else:
            print("Отклонений не обнаружено.")
    else:
        print("Error:", resp.text)

run_test(payload_male, "МУЖЧИНА: Hemoglobin 125, Creatinine 110, Ferritin 25, HDL 0.9")
run_test(payload_female, "ЖЕНЩИНА: Hemoglobin 125, Creatinine 110, Ferritin 25, HDL 0.9")