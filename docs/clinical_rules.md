# Клинические правила

## Обзор

243 файла правил в `knowledge/guidelines/**`, 14 специальностей, 455 диагностических критериев. Из них **13 правил — enriched** (полная клиническая интерпретация: критерии, дифдиагноз, красные флаги, тактика, ссылки на гайдлайны), **230 — basic** (только пороговое срабатывание + список рекомендаций). Деление явно закодировано в системе через `RuleTier` и определяется тем, есть ли для правила запись в `clinical_interpretations.yaml` — не ручная пометка, обновляется автоматически при добавлении новых интерпретаций.

Таблица ниже сгенерирована напрямую из `knowledge/guidelines/**` — актуальна на момент последнего обновления этого файла, но при добавлении/удалении правил её нужно перегенерировать (см. команду в конце файла), а не редактировать руками, чтобы не разойтись со схемой знаний.

---

### Нефрология (50)

| ID правила | Метка | Уровень |
|---|---|---|
| `acute_glomerulonephritis` | acute_glomerulonephritis | basic |
| `acute_kidney_injury` | Острое повреждение почек | ✅ enriched |
| `acute_kidney_injury_stage2` | acute_kidney_injury_stage2 | basic |
| `acute_kidney_injury_stage3` | acute_kidney_injury_stage3 | basic |
| `acute_pyelonephritis` | acute_pyelonephritis | basic |
| `acute_rejection` | acute_rejection | basic |
| `acute_tubulointerstitial_nephritis` | acute_tubulointerstitial_nephritis | basic |
| `adpkd` | adpkd | basic |
| `alport_syndrome` | alport_syndrome | basic |
| `atheroembolic_kidney_disease` | atheroembolic_kidney_disease | basic |
| `chronic_interstitial_nephritis` | chronic_interstitial_nephritis | basic |
| `chronic_pyelonephritis` | chronic_pyelonephritis | basic |
| `chronic_rejection` | chronic_rejection | basic |
| `ckd_stage3` | ckd_stage3 | basic |
| `ckd_stage4` | ckd_stage4 | basic |
| `ckd_stage5` | ckd_stage5 | basic |
| `contrast_nephropathy` | contrast_nephropathy | basic |
| `cystinuria` | cystinuria | basic |
| `diabetic_nephropathy` | diabetic_nephropathy | basic |
| `fabry_disease` | fabry_disease | basic |
| `focal_segmental_glomerulosclerosis` | focal_segmental_glomerulosclerosis | basic |
| `goodpasture_syndrome` | goodpasture_syndrome | basic |
| `gouty_nephropathy` | gouty_nephropathy | basic |
| `hypercalcemia_severe` | hypercalcemia_severe | basic |
| `hyperkalemia` | Гиперкалиемия | ✅ enriched |
| `hyperkalemia_critical` | hyperkalemia_critical | basic |
| `hypermagnesemia` | hypermagnesemia | basic |
| `hypernatremia` | Гипернатриемия | ✅ enriched |
| `hypernatremia_severe` | hypernatremia_severe | basic |
| `hyperphosphatemia` | hyperphosphatemia | basic |
| `hypertensive_nephropathy` | hypertensive_nephropathy | basic |
| `hypocalcemia_severe` | hypocalcemia_severe | basic |
| `hypokalemia` | Гипокалиемия | ✅ enriched |
| `hypokalemia_severe` | hypokalemia_severe | basic |
| `hypomagnesemia` | hypomagnesemia | basic |
| `hyponatremia` | Гипонатриемия | ✅ enriched |
| `hyponatremia_severe` | hyponatremia_severe | basic |
| `hypophosphatemia` | hypophosphatemia | basic |
| `iga_nephropathy` | iga_nephropathy | basic |
| `lithium_nephropathy` | lithium_nephropathy | basic |
| `lupus_nephritis` | lupus_nephritis | basic |
| `membranous_nephropathy` | membranous_nephropathy | basic |
| `minimal_change_disease` | minimal_change_disease | basic |
| `myeloma_kidney` | myeloma_kidney | basic |
| `nsaid_nephropathy` | nsaid_nephropathy | basic |
| `rapidly_progressive_glomerulonephritis` | rapidly_progressive_glomerulonephritis | basic |
| `renal_amyloidosis` | renal_amyloidosis | basic |
| `renal_artery_stenosis` | renal_artery_stenosis | basic |
| `renal_sarcoidosis` | renal_sarcoidosis | basic |
| `renal_vein_thrombosis` | renal_vein_thrombosis | basic |

### Эндокринология (41)

| ID правила | Метка | Уровень |
|---|---|---|
| `acromegaly` | acromegaly | basic |
| `acth_high` | acth_high | basic |
| `adrenal_insufficiency` | adrenal_insufficiency | basic |
| `congenital_adrenal_hyperplasia` | congenital_adrenal_hyperplasia | basic |
| `cortisol_evening_high` | cortisol_evening_high | basic |
| `cushing_disease` | cushing_disease | basic |
| `cushing_syndrome` | cushing_syndrome | basic |
| `diabetes_insipidus` | diabetes_insipidus | basic |
| `endocrine_infertility` | endocrine_infertility | basic |
| `free_androgen_index_high` | free_androgen_index_high | basic |
| `free_androgen_index_low` | free_androgen_index_low | basic |
| `glucagonoma` | glucagonoma | basic |
| `glucose_ranges` | glucose_ranges | basic |
| `graves_disease` | graves_disease | basic |
| `gynecomastia` | gynecomastia | basic |
| `high_dhea_s_male` | high_dhea_s_male | basic |
| `hyperandrogenism_female` | hyperandrogenism_female | basic |
| `hyperestrogenemia_male` | hyperestrogenemia_male | basic |
| `hyperprolactinemia` | hyperprolactinemia | basic |
| `hypogonadism_male` | hypogonadism_male | basic |
| `hypoparathyroidism` | hypoparathyroidism | basic |
| `hypopituitarism` | hypopituitarism | basic |
| `insulinoma` | insulinoma | basic |
| `low_dhea_s_male` | low_dhea_s_male | basic |
| `men1` | men1 | basic |
| `men2` | men2 | basic |
| `pagets_disease` | pagets_disease | basic |
| `pcos` | pcos | basic |
| `pheochromocytoma` | pheochromocytoma | basic |
| `primary_hyperaldosteronism` | primary_hyperaldosteronism | basic |
| `primary_hyperparathyroidism` | primary_hyperparathyroidism | ✅ enriched |
| `primary_hypogonadism_female` | primary_hypogonadism_female | basic |
| `primary_obesity` | primary_obesity | basic |
| `prolactin_very_high` | prolactin_very_high | basic |
| `prolactinoma` | prolactinoma | basic |
| `pseudohypoparathyroidism` | pseudohypoparathyroidism | basic |
| `secondary_hyperparathyroidism` | secondary_hyperparathyroidism | basic |
| `secondary_hypogonadism_female` | secondary_hypogonadism_female | basic |
| `shbg_abnormal` | shbg_abnormal | basic |
| `somatostatinoma` | somatostatinoma | basic |
| `subacute_thyroiditis` | subacute_thyroiditis | basic |

### Кардиология (26)

| ID правила | Метка | Уровень |
|---|---|---|
| `acute_coronary_syndrome` | acute_coronary_syndrome | basic |
| `acute_coronary_syndrome_ckmb` | acute_coronary_syndrome_ckmb | basic |
| `acute_myocardial_infarction_troponin_i` | acute_myocardial_infarction_troponin_i | basic |
| `acute_myocardial_infarction_troponin_t` | acute_myocardial_infarction_troponin_t | basic |
| `atherogenic_index_high` | atherogenic_index_high | basic |
| `bnp_elevated` | bnp_elevated | basic |
| `chronic_heart_failure` | chronic_heart_failure | basic |
| `ck_mb_elevated` | ck_mb_elevated | basic |
| `d_dimer_elevated` | d_dimer_elevated | basic |
| `dilated_cardiomyopathy_marker` | dilated_cardiomyopathy_marker | basic |
| `familial_hypercholesterolemia` | familial_hypercholesterolemia | basic |
| `heart_failure_decompensation` | heart_failure_decompensation | basic |
| `heart_failure_nyha_2` | heart_failure_nyha_2 | basic |
| `heart_failure_nyha_3` | heart_failure_nyha_3 | basic |
| `heart_failure_nyha_4` | heart_failure_nyha_4 | basic |
| `infective_endocarditis_risk` | infective_endocarditis_risk | basic |
| `isolated_hypertriglyceridemia` | isolated_hypertriglyceridemia | basic |
| `low_hdl_severe` | low_hdl_severe | basic |
| `myocardial_infarction_severe` | myocardial_infarction_severe | basic |
| `myocarditis_suspected` | myocarditis_suspected | basic |
| `myoglobin_elevated` | myoglobin_elevated | basic |
| `nt_probnp_elevated` | nt_probnp_elevated | basic |
| `pericarditis_markers` | pericarditis_markers | basic |
| `pulmonary_embolism_high_risk` | pulmonary_embolism_high_risk | basic |
| `troponin_i_high` | troponin_i_high | basic |
| `troponin_t_high` | troponin_t_high | basic |

### Гематология (25)

| ID правила | Метка | Уровень |
|---|---|---|
| `anemia_chronic_disease` | Анемия хронического воспаления | ✅ enriched |
| `b12_deficiency` | Дефицит витамина B12 | ✅ enriched |
| `basophilia` | basophilia | basic |
| `eosinophilia` | eosinophilia | basic |
| `folate_deficiency` | Дефицит фолиевой кислоты | ✅ enriched |
| `hemolytic_anemia` | hemolytic_anemia | basic |
| `ldh_elevated_severe` | ldh_elevated_severe | basic |
| `leukemoid_reaction` | leukemoid_reaction | basic |
| `leukocytosis_extreme` | leukocytosis_extreme | basic |
| `leukocytosis_moderate` | leukocytosis_moderate | basic |
| `leukopenia` | leukopenia | basic |
| `lymphocytosis_extreme` | lymphocytosis_extreme | basic |
| `lymphopenia` | lymphopenia | basic |
| `macrocytic_anemia` | macrocytic_anemia | basic |
| `monocytosis` | monocytosis | basic |
| `neutropenia` | neutropenia | basic |
| `neutrophilia` | neutrophilia | basic |
| `pancytopenia` | pancytopenia | basic |
| `polycythemia` | polycythemia | basic |
| `thrombocytopenia_critical` | thrombocytopenia_critical | basic |
| `thrombocytopenia_moderate` | thrombocytopenia_moderate | basic |
| `thrombocytopenia_severe` | thrombocytopenia_severe | basic |
| `thrombocytosis` | thrombocytosis | basic |
| `thrombocytosis_extreme` | thrombocytosis_extreme | basic |
| `venous_thromboembolism` | venous_thromboembolism | basic |

### Общие показатели (22)

| ID правила | Метка | Уровень |
|---|---|---|
| `alt_ranges` | alt_ranges | basic |
| `ast_ranges` | ast_ranges | basic |
| `blood_pressure_ranges` | blood_pressure_ranges | basic |
| `bmi_ranges` | bmi_ranges | basic |
| `calcium_ranges` | calcium_ranges | basic |
| `creatinine_ranges` | creatinine_ranges | basic |
| `egfr_ranges` | egfr_ranges | basic |
| `esr_ranges` | esr_ranges | basic |
| `ferritin_ranges` | ferritin_ranges | basic |
| `ggt_ranges` | ggt_ranges | basic |
| `hdl_ranges` | hdl_ranges | basic |
| `hematocrit_ranges` | hematocrit_ranges | basic |
| `hemoglobin_ranges` | hemoglobin_ranges | basic |
| `ldl_ranges` | ldl_ranges | basic |
| `potassium_ranges` | potassium_ranges | basic |
| `rbc_ranges` | rbc_ranges | basic |
| `serum_iron_ranges` | serum_iron_ranges | basic |
| `sodium_ranges` | sodium_ranges | basic |
| `triglycerides_ranges` | triglycerides_ranges | basic |
| `tsh_ranges` | tsh_ranges | basic |
| `uric_acid_ranges` | uric_acid_ranges | basic |
| `vitamin_d_ranges` | vitamin_d_ranges | basic |

### Онкомаркеры (18)

| ID правила | Метка | Уровень |
|---|---|---|
| `afp_elevated` | afp_elevated | basic |
| `beta_hcg_tumor_marker_elevated` | beta_hcg_tumor_marker_elevated | basic |
| `ca125_elevated` | ca125_elevated | basic |
| `ca15_3_elevated` | ca15_3_elevated | basic |
| `ca19_9_elevated` | ca19_9_elevated | basic |
| `ca50_elevated` | ca50_elevated | basic |
| `ca72_4_elevated` | ca72_4_elevated | basic |
| `cea_elevated_non_smoker` | cea_elevated_non_smoker | basic |
| `cea_elevated_smoker` | cea_elevated_smoker | basic |
| `chromogranin_a_elevated` | chromogranin_a_elevated | basic |
| `cyfra_21_1_elevated` | cyfra_21_1_elevated | basic |
| `he4_elevated` | he4_elevated | basic |
| `nse_elevated` | nse_elevated | basic |
| `psa_elevated_age_50` | psa_elevated_age_50 | basic |
| `psa_elevated_age_60` | psa_elevated_age_60 | basic |
| `psa_elevated_age_70` | psa_elevated_age_70 | basic |
| `psa_ratio_low` | psa_ratio_low | basic |
| `scc_elevated` | scc_elevated | basic |

### Инфекционные болезни (15)

| ID правила | Метка | Уровень |
|---|---|---|
| `bacterial_infection_risk` | bacterial_infection_risk | basic |
| `hepatitis_b_active` | hepatitis_b_active | basic |
| `hepatitis_c_active` | hepatitis_c_active | basic |
| `hiv_infection` | hiv_infection | basic |
| `infectious_mononucleosis` | infectious_mononucleosis | basic |
| `lower_respiratory_infection` | Нижняя респираторная инфекция | ✅ enriched |
| `postoperative_inflammation` | postoperative_inflammation | basic |
| `procalcitonin_bacterial` | procalcitonin_bacterial | basic |
| `sepsis` | sepsis | basic |
| `sepsis_high_risk_combined` | sepsis_high_risk_combined | basic |
| `syphilis_active` | syphilis_active | basic |
| `systemic_inflammation` | Системное воспаление | ✅ enriched |
| `systemic_inflammatory_response` | systemic_inflammatory_response | basic |
| `urinary_tract_infection` | Инфекция мочевыводящих путей | ✅ enriched |
| `viral_infection_suspect` | viral_infection_suspect | basic |

### Педиатрия (14)

| ID правила | Метка | Уровень |
|---|---|---|
| `albumin_low_children` | albumin_low_children | basic |
| `anemia_children` | anemia_children | basic |
| `ferritin_elevated_children` | ferritin_elevated_children | basic |
| `hypercalcemia_children` | hypercalcemia_children | basic |
| `hypernatremia_children` | hypernatremia_children | basic |
| `hypocalcemia_children` | hypocalcemia_children | basic |
| `hypokalemia_children` | hypokalemia_children | basic |
| `hyponatremia_children` | hyponatremia_children | basic |
| `iron_deficiency_children` | iron_deficiency_children | basic |
| `leukocytosis_children` | leukocytosis_children | basic |
| `lymphocytosis_children` | lymphocytosis_children | basic |
| `rickets_risk` | rickets_risk | basic |
| `uti_children` | uti_children | basic |
| `vitamin_d_deficiency_children` | vitamin_d_deficiency_children | basic |

### Витамины/микроэлементы (13)

| ID правила | Метка | Уровень |
|---|---|---|
| `copper_deficiency` | copper_deficiency | basic |
| `copper_elevated` | copper_elevated | basic |
| `folate_deficiency_severe` | folate_deficiency_severe | basic |
| `iodine_deficiency` | iodine_deficiency | basic |
| `iodine_excess` | iodine_excess | basic |
| `selenium_deficiency` | selenium_deficiency | basic |
| `vitamin_a_deficiency` | vitamin_a_deficiency | basic |
| `vitamin_b12_deficiency_moderate` | vitamin_b12_deficiency_moderate | basic |
| `vitamin_b12_deficiency_severe` | vitamin_b12_deficiency_severe | basic |
| `vitamin_d_deficiency_moderate` | vitamin_d_deficiency_moderate | basic |
| `vitamin_d_deficiency_severe` | vitamin_d_deficiency_severe | basic |
| `vitamin_e_deficiency` | vitamin_e_deficiency | basic |
| `zinc_deficiency` | zinc_deficiency | basic |

### Гастроэнтерология (8)

| ID правила | Метка | Уровень |
|---|---|---|
| `acute_pancreatitis` | acute_pancreatitis | basic |
| `alcoholic_liver_disease` | alcoholic_liver_disease | basic |
| `celiac_disease` | Целиакия | ✅ enriched |
| `cholelithiasis` | cholelithiasis | basic |
| `chronic_pancreatitis` | chronic_pancreatitis | basic |
| `crohns_disease` | crohns_disease | basic |
| `inflammatory_bowel_disease` | inflammatory_bowel_disease | basic |
| `ulcerative_colitis` | ulcerative_colitis | basic |

### Ревматология (4)

| ID правила | Метка | Уровень |
|---|---|---|
| `ankylosing_spondylitis` | ankylosing_spondylitis | basic |
| `rheumatoid_arthritis` | rheumatoid_arthritis | basic |
| `systemic_lupus` | systemic_lupus | basic |
| `vasculitis` | vasculitis | basic |

### Остеология (3)

| ID правила | Метка | Уровень |
|---|---|---|
| `osteomalacia` | osteomalacia | basic |
| `osteoporosis` | osteoporosis | basic |
| `paget_disease` | paget_disease | basic |

### Гепатология (3)

| ID правила | Метка | Уровень |
|---|---|---|
| `acute_hepatitis` | acute_hepatitis | basic |
| `cholestasis` | cholestasis | basic |
| `hypoalbuminemia` | hypoalbuminemia | basic |

### (общие) (1)

| ID правила | Метка | Уровень |
|---|---|---|
| `diabetes` | diabetes | basic |

---

## Комбинированные диагнозы

Синдромы, требующие одновременного срабатывания нескольких находок — задаются в `knowledge/configs/clinical_logic.yaml`, секция `combinations`:

| ID | Название | Условия |
|----|----------|---------|
| `primary_hyperparathyroidism` | Первичный гиперпаратиреоз (предположительно) | `hypercalcemia` + `vitamin_d_deficiency` |
| `septic_syndrome` | Септический синдром | `sepsis` + `systemic_inflammation` |
| `hepatorenal_syndrome` | Гепаторенальный синдром (предположительно) | `acute_kidney_injury` + `acute_hepatitis` |
| `metabolic_bone_disease` | Метаболическое заболевание костей | `vitamin_d_deficiency` + `hypercalcemia` |

Список условий — это id конкретных условий (не обязательно id файла целиком), должен матчиться с тем, что реально производит `InferenceEngine`.

---

## Как добавить новое правило

**Актуальный формат** — `conditions:`, именно его понимает `RuleVersion.from_yaml()` напрямую (старый формат `thresholds:`/`scoring:` тоже поддерживается через автоконвертацию для обратной совместимости, но для новых правил используйте `conditions:` — он не требует угадывания риска/веса движком):

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

Шаги:

1. Создайте YAML-файл в `knowledge/guidelines/<специальность>/<id>.yaml` с `conditions:` (см. пример выше).
2. Если правило комбинирует несколько параметров через логику "И" (не "любой из"), опишите синдром отдельно в `clinical_logic.yaml` → `combinations`, а не пытайтесь выразить это одним `condition` — движок проверяет каждое условие независимо (логика "ИЛИ" между условиями одного файла).
3. Добавьте метку в `diagnosis_labels` в `clinical_logic.yaml`.
4. При необходимости добавьте диагноз в `system_groups` и `allowed_primary` в `clinical_logic.yaml`.
5. Для enriched-уровня — добавьте запись в `clinical_interpretations.yaml` (критерии, дифдиагноз, красные флаги, тактика, референсы). Без этого правило останется basic — это нормально, не все правила обязаны быть enriched.
6. Перезагрузите конфигурацию через `POST /reload_config` (роль admin) или кнопку в админ-панели — перезапуск контейнера не требуется.

## Калибровка порогов

Пороги для параметров, участвующих в текстовых интерпретациях (`{interpretation}`/`{additional}` в `comment_template`), берутся из `knowledge/configs/clinical_thresholds.yaml` и `knowledge/configs/medical_data.json` — эти два файла должны оставаться согласованными между собой, чтобы не создавать два расходящихся источника истины по одному параметру.

## Как перегенерировать таблицу выше

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from application.services.version_manager import VersionManager
from domain.interfaces import RuleRepository
from domain.rule_version import RuleTier

class R(RuleRepository):
    def __init__(self): self.store={}
    def save(self,v): self.store[v.rule_id]=v; return v
    def get_active_versions(self): return list(self.store.values())
    def get_by_id(self,r,v=None): return self.store.get(r)
    def activate_version(self,r,v): pass
    def get_version_history(self,r): return []

repo=R(); vm=VersionManager(repo,'knowledge/guidelines'); versions=vm.hot_reload()
print(f'{len(versions)} правил, {sum(1 for v in versions if v.tier == RuleTier.ENRICHED)} enriched')
"
```
