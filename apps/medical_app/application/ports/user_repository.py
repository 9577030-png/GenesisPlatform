from abc import ABC, abstractmethod
from typing import Optional, List
from medical_app.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def create(self, username: str, hashed_password: str, role: str = "user") -> User:
        pass

    @abstractmethod
    def list_all(self) -> List[User]:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass
