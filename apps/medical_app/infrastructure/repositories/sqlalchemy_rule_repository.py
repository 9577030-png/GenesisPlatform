from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from genesis_medical.domain.rule_version import RuleVersion
from medical_app.application.ports.rule_repository import RuleRepository
from medical_app.infrastructure.repositories.sqlalchemy_models import Base, RuleVersionModel

class SQLAlchemyRuleRepository(RuleRepository):
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self._ensure_tier_column()
        self.Session = sessionmaker(bind=self.engine)

    def _ensure_tier_column(self):
        with self.engine.connect() as conn:
            inspector = inspect(self.engine)
            if "rule_versions" in inspector.get_table_names():
                columns = [col["name"] for col in inspector.get_columns("rule_versions")]
                if "tier" not in columns:
                    conn.execute("ALTER TABLE rule_versions ADD COLUMN tier VARCHAR(20) DEFAULT 'basic'")
                    conn.commit()

    def _to_domain(self, model: RuleVersionModel) -> RuleVersion:
        return RuleVersion(
            version_id=model.version_id,
            rule_id=model.rule_id,
            name=model.name,
            conditions=model.conditions,
            actions=model.actions,
            priority=model.priority,
            conflicts_with=model.conflicts_with,
            supports=model.supports,
            created_at=model.created_at,
            created_by=model.created_by,
            is_active=model.is_active,
            comment=model.comment,
            tier=model.tier
        )

    def save(self, rule_version: RuleVersion) -> RuleVersion:
        with self.Session() as session:
            model = RuleVersionModel(
                rule_id=rule_version.rule_id,
                name=rule_version.name,
                conditions=rule_version.conditions,
                actions=rule_version.actions,
                priority=rule_version.priority,
                conflicts_with=rule_version.conflicts_with,
                supports=rule_version.supports,
                created_by=rule_version.created_by,
                is_active=rule_version.is_active,
                comment=rule_version.comment,
                tier=rule_version.tier
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_domain(model)

    def get_active_versions(self) -> List[RuleVersion]:
        with self.Session() as session:
            models = session.query(RuleVersionModel).filter_by(is_active=True).all()
            return [self._to_domain(m) for m in models]

    def get_by_id(self, rule_id: str, version_id: Optional[int] = None) -> Optional[RuleVersion]:
        with self.Session() as session:
            query = session.query(RuleVersionModel).filter_by(rule_id=rule_id)
            if version_id is not None:
                query = query.filter_by(version_id=version_id)
            else:
                query = query.filter_by(is_active=True)
            model = query.first()
            if model:
                return self._to_domain(model)
            return None

    def activate_version(self, rule_id: str, version_id: int) -> None:
        with self.Session() as session:
            session.query(RuleVersionModel).filter_by(rule_id=rule_id).update({"is_active": False})
            session.query(RuleVersionModel).filter_by(version_id=version_id).update({"is_active": True})
            session.commit()

    def get_version_history(self, rule_id: str) -> List[RuleVersion]:
        with self.Session() as session:
            models = session.query(RuleVersionModel).filter_by(rule_id=rule_id).order_by(RuleVersionModel.created_at.desc()).all()
            return [self._to_domain(m) for m in models]
