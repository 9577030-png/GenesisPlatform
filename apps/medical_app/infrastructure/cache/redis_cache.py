import json
import hashlib
import redis
from typing import Optional, Any
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter

class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.client = redis.from_url(redis_url)
        self.ttl = 3600  # 1 С‡Р°СЃ

    def _make_key(self, patient: PatientProfile, parameters: list, rules_version: str) -> str:
        data = {
            "patient_id": patient.id,
            "gender": patient.gender.value,
            "age": patient.age,
            "parameters": sorted([(p.name, p.value, p.unit.name) for p in parameters]),
            "rules_version": rules_version
        }
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def get(self, patient: PatientProfile, parameters: list, rules_version: str) -> Optional[dict]:
        key = self._make_key(patient, parameters, rules_version)
        cached = self.client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, patient: PatientProfile, parameters: list, rules_version: str, result: dict) -> None:
        key = self._make_key(patient, parameters, rules_version)
        self.client.setex(key, self.ttl, json.dumps(result, default=str))

    def invalidate_all(self) -> None:
        self.client.flushdb()
