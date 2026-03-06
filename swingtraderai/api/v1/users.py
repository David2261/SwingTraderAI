from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.api.deps import get_current_user
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db
from swingtraderai.schemas.auth import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)) -> UserOut:
	return UserOut.from_orm(current_user)


@router.get("/{user_id}", response_model=UserOut)
async def read_user(
	user_id: int,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_user),
) -> UserOut:
	user = await db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return UserOut.from_orm(current_user)
