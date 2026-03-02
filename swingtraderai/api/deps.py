from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from swingtraderai.core.config import settings
from swingtraderai.db.models.user import User
from swingtraderai.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
	db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	try:
		payload = jwt.decode(
			token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
		)

		user_id_str = payload.get("sub")
		token_type = payload.get("type")

		if user_id_str is None or token_type != "access":
			raise credentials_exception

		if not user_id_str.isdigit():
			raise credentials_exception

		user_id = int(user_id_str)

	except JWTError as exc:
		raise credentials_exception from exc

	user = await db.get(User, user_id)
	if user is None:
		raise credentials_exception

	if not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
		)

	return user


async def get_current_active_superuser(
	current_user: Annotated[User, Depends(get_current_user)],
) -> User:
	if not current_user.is_superuser:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges"
		)
	return current_user
