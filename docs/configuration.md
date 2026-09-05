# Конфигурация системы

Все конфигурационные файлы находятся в папке `knowledge/`. Редактировать их можно вручную или через веб-интерфейс администратора (раздел «Правила»).

---

## 1. Лабораторные пороги (`clinical_thresholds.yaml`)

**Путь:** `knowledge/configs/clinical_thresholds.yaml`

Определяет нормальные значения для параметров, которые используются в текстовых интерпретациях (`comment_template` в `clinical_interpretations.yaml`). Поддерживает разделение по полу (ключи `male`/`female`).

**Пример:**

```yaml
thresholds:
  hemoglobin:
    male:
      low: 130
      high: 170
    female:
      low: 120
      high: 150
    unit: "g/L"
    risk_level: HIGH
  glucose:
    low: 3.9
    high: 5.5
    unit: "mmol/L"
    risk_level: HIGH
```

Значения из этого файла продублированы (для тех же 6 параметров) в `knowledge/configs/medical_data.json` в формате, который читает `MedicalReferenceLoader` — при изменении порога здесь стоит проверить и синхронизировать `medical_data.json`, чтобы не разойтись.

---

## 2. Клинические правила (`guidelines/`)

**Путь:** `knowledge/guidelines/**/*.yaml`

**Актуальный формат** — `conditions:`. Каждое условие проверяется независимо (логика «ИЛИ» между условиями одного файла — если нужна логика «И» между несколькими параметрами, оформляйте синдром как `combination` в `clinical_logic.yaml`, а не одним условием):

```yaml
id: iron_deficiency
description: "Снижение ферритина, железа и/или повышение MCV указывает на железодефицитную анемию."
conditions:
  - id: iron_deficiency_ferritin
    label: "Сниженный ферритин"
    parameter: ferritin
    max: 30
    scoring: 5
    risk: HIGH
    recommendations:
      - "Проверить сывороточное железо и ОЖСС"
```

**Поля условия:**
- `id` — уникальный id находки (используется для меток, исключений, интерпретаций)
- `label` — человекочитаемое название
- `parameter` — имя лабораторного параметра (должно совпадать с каноническим именем после нормализации)
- `min` / `max` — пороги срабатывания (можно оба сразу для диапазона)
- `gender` — опционально, если условие специфично для пола
- `scoring` — вес (влияет на вычисляемую вероятность, `probability = min(scoring/10, 1.0)`)
- `risk` — `NORMAL` / `MEDIUM` / `HIGH` / `CRITICAL`
- `recommendations` — список рекомендаций

**Устаревший формат** (`thresholds:`/`scoring:`/`override_thresholds:`) по-прежнему поддерживается — `RuleVersion.from_yaml()` конвертирует его на лету через `_convert_old_format()`, чтобы не ломать уже существующие 230 файлов. Для новых правил используйте `conditions:` — устаревший формат сложнее читать и легче ошибиться в семантике `low`/`high`.

---

## 3. Логика постобработки (`clinical_logic.yaml`)

**Путь:** `knowledge/configs/clinical_logic.yaml`

Настройка группировки, исключений, приоритетов, комбинированных диагнозов и меток.

**Группы и приоритеты:**
```yaml
groups:
  kidney_disease:
    - ckd_stage3
    - ckd_stage4
    - ckd_stage5
    - acute_kidney_injury

priority:
  kidney_disease:
    - ckd_stage5
    - ckd_stage4
    - ckd_stage3
```

**Исключения** (более специфичный диагноз вытесняет менее специфичный):
```yaml
exclusions:
  - if: ckd_stage5
    then:
      - ckd_stage4
      - ckd_stage3
      - chronic_kidney_disease
```
`if`/значения в `then` матчатся и по id самого правила (`ckd_stage5`), и по id отдельного условия внутри многопараметрового правила (`ckd_stage5_egfr`) — эквивалентность проверяется в `PostProcessor._apply_exclusions`.

**Комбинированные диагнозы:**
```yaml
combinations:
  - id: primary_hyperparathyroidism
    label: "Первичный гиперпаратиреоз (предположительно)"
    conditions:
      - hypercalcemia
      - vitamin_d_deficiency
    probability_factor: 0.8
    urgency: high
    doctor_specialty: Endocrinologist
    additional_tests:
      - PTH
      - Calcium 24h urine
```

**Метки и группировка:**
```yaml
diagnosis_labels:
  diabetes_mellitus_type_2: "Сахарный диабет 2 типа"
  iron_deficiency: "Железодефицитная анемия"

system_groups:
  Эндокринная система:
    - diabetes_mellitus_type_2
  Гематология:
    - iron_deficiency

allowed_primary:
  - diabetes_mellitus_type_2
  - iron_deficiency
```

---

## 4. Клинические инсайты (`clinical_interpretations.yaml`)

**Путь:** `knowledge/configs/clinical_interpretations.yaml`

Подробные интерпретации для enriched-уровня (шпаргалка для врача). Наличие записи здесь **и есть** критерий, по которому правило получает `tier: enriched` — отдельно нигде это не нужно проставлять.

```yaml
interpretations:
  diabetes_mellitus_type_2:
    id: diabetes_mellitus_type_2
    label: "Сахарный диабет 2 типа"
    category: "Эндокринология"
    description: "Хроническое метаболическое заболевание..."
    criteria:
      - parameter: glucose
        threshold: 7.0
        unit: "ммоль/л"
        condition: ">="
        comment_template: |
          Критерий выполнен. Уровень {value} ммоль/л превышает порог (≥ 7.0). {interpretation}
    differentials:
      - condition: "age < 45 AND c_peptide < 0.8"
        text: "Заподозрить LADA..."
    red_flags:
      - condition: "hba1c > 9.0"
        text: "Высокий риск декомпенсации."
    treatment_hints:
      - step: "Метформин 500 мг × 2 раза в день"
        note: "Титровать до 2000 мг/сут."
    references:
      - "ADA Standards of Medical Care in Diabetes 2025"
```

Если `comment_template` использует `{interpretation}` или `{additional}` — параметр должен быть описан в `medical_data.json`, иначе текст интерпретации будет пустым (не крашится, просто ничего не покажет).

---

## 5. Референсы для текстовых интерпретаций (`medical_data.json`)

**Путь:** `knowledge/configs/medical_data.json`

Отдельный, минимальный справочник только для параметров, чьи `comment_template` используют `{interpretation}`/`{additional}` — не полная номенклатура лабораторных показателей.

```json
{
  "norms": {
    "ferritin": {
      "name": "Ферритин",
      "unit": "мкг/Л",
      "group": "blood_count",
      "norms": [
        {"gender": "male", "min": 30, "max": 400},
        {"gender": "female", "min": 15, "max": 150}
      ],
      "low": "снижен - признак истощения запасов железа.",
      "high": "повышен - может отражать перегрузку железом либо воспаление."
    }
  }
}
```

Значения должны быть согласованы с `clinical_thresholds.yaml` для тех же параметров — если правите порог в одном файле, проверьте другой.

---

## 6. Алиасы параметров (`laboratory/aliases.yaml`)

Сопоставляет синонимы с каноническими именами (640 алиасов на текущий момент):

```yaml
aliases:
  hemoglobin:
    - Hb
    - HGB
    - Гемоглобин
```

## 7. Единицы измерения (`laboratory/units.yaml`)

Коэффициенты конвертации в базовую единицу:

```yaml
units:
  "g/L":
    base: "g/L"
    factor: 1.0
  "mg/dL":
    base: "mmol/L"
    factor: 0.0555
```

## 8. Рекомендации врачей (`doctor_recommendations.yaml`)

```yaml
recommendations:
  iron_deficiency:
    doctor_specialty: Hematologist
    urgency: moderate
    additional_tests:
      - Iron
      - TIBC
```

---

## Применение изменений

После правки любого YAML/JSON-файла — `POST /reload_config` (роль admin) или кнопка «Перезагрузить правила» в админ-панели. Перезапуск контейнера не требуется:

```bash
curl -X POST http://localhost:8000/reload_config \
  -H "Authorization: Bearer <admin_token>"
```
