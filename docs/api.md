# API-эндпоинты

Базовый URL: `http://localhost:8000`

## Аутентификация

Большинство эндпоинтов защищены JWT-токеном. Для получения токена выполните запрос к `/token`.

**Пример запроса** (замените на реальный пароль — при первом запуске он генерируется случайно, см. [`installation.md`](installation.md)):

```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=<ваш_пароль>" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Далее при вызове защищённых эндпоинтов передавайте токен в заголовке `Authorization: Bearer <токен>`.

---

### 1. `POST /token` — получение токена
Защита: нет

Параметры (form-data): `username`, `password`

Ответ: `{"access_token": "...", "token_type": "bearer"}`

---

### 2. `POST /analyze` — сырой отчёт
Защита: JWT (любая роль)

Тело запроса:
```json
{
  "patient": {
    "id": "P123",
    "gender": "male",
    "age": 45
  },
  "raw_text": "Hb 130 g/L\nMCV 85 fL\nFerritin 12 ug/L"
}
```

Ответ — строковое заключение с находками и рекомендациями (не структурированный JSON — см. `/analyze_structured` для этого).

---

### 3. `POST /analyze_structured` — структурированное заключение
Защита: JWT (любая роль)

Тело запроса — аналогично `/analyze`.

Ответ (сокращённо, реальная структура зависит от того, что сработало):
```json
{
  "diagnoses": [
    {
      "id": "diabetes_mellitus_type_2",
      "label": "Сахарный диабет 2 типа",
      "risk": "Высокий",
      "combined": false,
      "description": "Уровень глюкозы ≥ 7.0 ммоль/л."
    }
  ],
  "grouped_findings": {
    "Эндокринная система": [
      {"id": "diabetes_mellitus_type_2", "title": "Сахарный диабет 2 типа", "risk": "Высокий"}
    ]
  },
  "recommendations_by_specialty": {
    "Endocrinologist": [
      {"urgency": "high", "tests": ["Oral glucose tolerance test", "C-peptide"]}
    ]
  },
  "overall_risk_level": "Высокий",
  "conclusion": "текстовое резюме для печати",
  "clinical_insights": {
    "diabetes_mellitus_type_2": {
      "criteria": ["..."],
      "differentials": ["..."],
      "red_flags": ["..."],
      "treatment_hints": ["..."],
      "references": ["..."]
    }
  }
}
```

`clinical_insights` заполняется только для enriched-правил (13 из 243, см. [`clinical_rules.md`](clinical_rules.md)) — для остальных находок в `diagnoses` будет только базовое описание, без развёрнутых инсайтов.

---

### 4. `POST /export_pdf` — экспорт заключения в PDF
Защита: JWT (любая роль)

Тело запроса — аналогично `/analyze`. Ответ — бинарный PDF (`Content-Disposition: attachment; filename=report_<patient_id>.pdf`).

---

### 5. `POST /reload_config` — горячая перезагрузка конфигурации
Защита: JWT (только `admin`)

Ответ:
```json
{"status": "ok", "message": "Configuration reloaded successfully"}
```

---

### 6. `POST /register` — создание нового пользователя
Защита: JWT (только `admin`)

Тело запроса:
```json
{"username": "new_doctor", "password": "secure_pass", "role": "doctor"}
```

---

### 7. `GET /users` — список всех пользователей
Защита: JWT (только `admin`)

---

### 8. `DELETE /admin/user/{user_id}` — удаление пользователя
Защита: JWT (только `admin`)

---

### 9. `GET/POST /admin/config/file` — чтение/запись конфигурационных файлов
Защита: JWT (только `admin`)

`GET` — параметр `path` (относительно `knowledge/`).
`POST` — тело `{"path": "configs/clinical_thresholds.yaml", "content": "..."}`.

---

### 10. `GET /admin/history/{patient_id}` — история пациента
Защита: JWT (только `admin`)

---

### 11. `GET /health` — проверка статуса
Защита: нет

Ответ: `{"status": "ok", "message": "Medical AI service is running"}`

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Ошибка валидации входных данных |
| 401 | Неавторизованный запрос (отсутствует или невалидный токен) |
| 403 | Недостаточно прав (требуется роль admin) |
| 404 | Ресурс не найден |
| 500 | Внутренняя ошибка сервера |
