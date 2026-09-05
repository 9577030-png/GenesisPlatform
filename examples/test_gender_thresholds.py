import requests
import json

url = "http://localhost:8000/analyze"

# Тест для мужчины (гемоглобин 125 – ниже мужской нормы 130)
payload_male = {
    "patient": {
        "id": "M001",
        "gender": "male",
        "age": 40,
        "complaints": ["fatigue"],
        "medications": []
    },
    "raw_text": "Hemoglobin 125 g/L"
}

# Тест для женщины (гемоглобин 125 – в норме для женщин 120-150)
payload_female = {
    "patient": {
        "id": "F001",
        "gender": "female",
        "age": 35,
        "complaints": ["fatigue"],
        "medications": []
    },
    "raw_text": "Hemoglobin 125 g/L"
}

print("=" * 60)
print("ТЕСТ 1: Мужчина, Hemoglobin 125")
print("=" * 60)
resp_m = requests.post(url, json=payload_male)
print("Status:", resp_m.status_code)
if resp_m.status_code == 200:
    data = resp_m.json()
    print("Explanation:")
    print(data.get("explanation", "Нет объяснения"))
    # Ищем отклонения
    for f in data.get("findings", []):
        if f["probability"] > 0:
            print(f"  - {f['title']} (prob {f['probability']:.0%}, risk {f['risk']})")
else:
    print("Error:", resp_m.text)

print("\n" + "=" * 60)
print("ТЕСТ 2: Женщина, Hemoglobin 125")
print("=" * 60)
resp_f = requests.post(url, json=payload_female)
print("Status:", resp_f.status_code)
if resp_f.status_code == 200:
    data = resp_f.json()
    print("Explanation:")
    print(data.get("explanation", "Нет объяснения"))
    for f in data.get("findings", []):
        if f["probability"] > 0:
            print(f"  - {f['title']} (prob {f['probability']:.0%}, risk {f['risk']})")
else:
    print("Error:", resp_f.text)