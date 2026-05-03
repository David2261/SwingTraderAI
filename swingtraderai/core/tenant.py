from contextvars import ContextVar
from uuid import UUID

from fastapi import Depends, HTTPException, status

from swingtraderai.api.deps import get_current_active_user
from swingtraderai.db.models.user import User

# ContextVar для хранения tenant_id в рамках запроса
current_tenant_id: ContextVar[UUID | None] = ContextVar(
	"current_tenant_id", default=None
)


async def get_current_tenant_id(
	current_user: User = Depends(get_current_active_user),
) -> UUID:
	"""
	Извлекает tenant_id из текущего пользователя.
	В будущем можно расширить (subdomain, header и т.д.)
	"""
	if not current_user or not hasattr(current_user, "tenant_id"):
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail="Could not determine tenant"
		)

	tenant_id = current_user.tenant_id
	current_tenant_id.set(tenant_id)
	return tenant_id


def get_tenant_id_from_context() -> UUID:
	"""Получить tenant_id из контекста (для внутренних вызовов)"""
	tenant_id = current_tenant_id.get()
	if tenant_id is None:
		raise RuntimeError("tenant_id is not set in context")
	return tenant_id
