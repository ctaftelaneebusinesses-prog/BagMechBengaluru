import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ZoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    eta_minutes: int
    is_far: bool


class BookingCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=6, max_length=20)
    zone_id: uuid.UUID | None = None
    address: str = Field(min_length=1, max_length=500)
    issues: list[str] = Field(min_length=1)
    latitude: float | None = None
    longitude: float | None = None
    location_shared: bool = False


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    phone: str
    zone_id: uuid.UUID | None
    address: str
    issue: str
    latitude: float | None
    longitude: float | None
    location_shared: bool
    status: str
    created_at: datetime
    zone: ZoneOut | None = None


class BookingStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|in_progress|completed|cancelled)$")