import sqlite3
import secrets
import logging
from typing import Optional, List
from datetime import datetime
from medical_app.domain.entities.user import User
from medical_app.application.ports.user_repository import UserRepository
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class SqlUserRepository(UserRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        self._ensure_default_users()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logger.debug("Users table ensured.")

    def _ensure_default_users(self):
        # РќР• РёСЃРїРѕР»СЊР·СѓРµРј С„РёРєСЃРёСЂРѕРІР°РЅРЅС‹Рµ РїР°СЂРѕР»Рё РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ (admin/admin Рё С‚.Рї.) -
        # СЌС‚Рѕ РѕС‚РєСЂС‹С‚Р°СЏ СѓСЏР·РІРёРјРѕСЃС‚СЊ, РµСЃР»Рё РєС‚Рѕ-С‚Рѕ Р·Р°Р±СѓРґРµС‚ СЃРјРµРЅРёС‚СЊ РїР°СЂРѕР»СЊ РїРµСЂРµРґ РїСЂРѕРґС‹.
        # Р“РµРЅРµСЂРёСЂСѓРµРј СЃР»СѓС‡Р°Р№РЅС‹Р№ РїР°СЂРѕР»СЊ РѕРґРёРЅ СЂР°Р· РїСЂРё РїРµСЂРІРѕРј Р·Р°РїСѓСЃРєРµ Рё РѕРґРёРЅ СЂР°Р·
        # РїРѕРєР°Р·С‹РІР°РµРј РµРіРѕ РІ Р»РѕРіРµ - РґР°Р»СЊС€Рµ РѕРЅ РЅРёРіРґРµ РЅРµ С…СЂР°РЅРёС‚СЃСЏ РІ РѕС‚РєСЂС‹С‚РѕРј РІРёРґРµ.
        for username, role in [
            ("admin", "admin"),
            ("doctor", "doctor")
        ]:
            existing = self.get_by_username(username)
            if existing is None:
                password = secrets.token_urlsafe(12)
                hashed = pwd_context.hash(password)
                self.create(username, hashed, role)
                logger.warning(
                    f"РЎРѕР·РґР°РЅ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊ РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ '{username}' (СЂРѕР»СЊ: {role}) "
                    f"СЃРѕ СЃРіРµРЅРµСЂРёСЂРѕРІР°РЅРЅС‹Рј РїР°СЂРѕР»РµРј: {password} - СЃРѕС…СЂР°РЅРёС‚Рµ РµРіРѕ СЃРµР№С‡Р°СЃ, "
                    f"РїРѕРІС‚РѕСЂРЅРѕ РЅРёРіРґРµ РЅРµ РїРѕРєР°Р·С‹РІР°РµС‚СЃСЏ. РЎРјРµРЅРёС‚Рµ РїР°СЂРѕР»СЊ РїРѕСЃР»Рµ РїРµСЂРІРѕРіРѕ РІС…РѕРґР°."
                )

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, hashed_password, role, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(
                id=row[0],
                username=row[1],
                hashed_password=row[2],
                role=row[3],
                created_at=datetime.fromisoformat(row[4])
            )
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, hashed_password, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(
                id=row[0],
                username=row[1],
                hashed_password=row[2],
                role=row[3],
                created_at=datetime.fromisoformat(row[4])
            )
        return None

    def create(self, username: str, hashed_password: str, role: str = "user") -> User:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
            (username, hashed_password, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return self.get_by_id(user_id)

    def list_all(self) -> List[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, hashed_password, role, created_at FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [
            User(
                id=r[0],
                username=r[1],
                hashed_password=r[2],
                role=r[3],
                created_at=datetime.fromisoformat(r[4])
            )
            for r in rows
        ]

    def delete(self, user_id: int) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
