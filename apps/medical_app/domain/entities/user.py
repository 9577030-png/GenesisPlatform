from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    id: int
    username: str
    hashed_password: str
    role: str
    created_at: datetime