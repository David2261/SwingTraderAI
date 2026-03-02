from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
	channel: Optional[str] = None
	sent_to: Optional[str] = None
	status: Optional[str] = None


class NotificationOut(NotificationBase):
	id: UUID
	signal_id: UUID
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
