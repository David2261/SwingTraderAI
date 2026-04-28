from typing import Any
from uuid import UUID as PythonUUID

from sqlalchemy import Index, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from uuid6 import uuid7

# global naming conventions make Alembic diffs deterministic
convention = {
	"ix": "ix_%(column_0_label)s",
	"uq": "uq_%(table_name)s_%(column_0_name)s",
	"ck": "ck_%(table_name)s_%(constraint_name)s",
	"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
	"pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
	metadata = metadata


class TenantBase(Base):
	__abstract__ = True

	# Основной идентификатор тенанта (рекомендую UUID)
	tenant_id: Mapped[PythonUUID] = mapped_column(
		UUID(as_uuid=True),
		nullable=False,
		default=uuid7,
	)

	@declared_attr
	def __table_args__(cls) -> Any:
		# Добавляем составной индекс tenant_id + часто используемые поля
		return (Index(f"ix_{cls.__tablename__}_tenant_id", "tenant_id"),)
