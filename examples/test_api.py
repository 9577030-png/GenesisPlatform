import requests
import json

# Получение токена
resp = requests.post("http://localhost:8000/token", data={"username": "admin", "password": "admin"})
token = resp.json()["access_token"]
print("Token получен")

# Запрос на анализ
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "patient": {
        "id": "P001",
        "gender": "male",
        "age": 52,
        "complaints": ["fatigue"],
        "medications": []
    },
    "raw_text": "Глюкоза 8.2 ммоль/л\nHbA1c 7.8 %"
}

# Отправляем на эндпоинт /analyze (он использует глобальный контейнер и точно работал)
response = requests.post("http://localhost:8000/analyze_structured", json=payload, headers=headers)

print("Status:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))