import uuid

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models import Booking, Zone
from app.notifications import notify_new_booking
from app.schemas import BookingCreate, BookingOut, BookingStatusUpdate, ZoneOut

app = FastAPI(title="BagMech Bengaluru API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------- ZONES ----------------------



@app.get("/api/config")
async def public_config():
    return {"whatsapp_number": settings.whatsapp_business_number}




    
@app.get("/api/zones", response_model=list[ZoneOut])
async def list_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone).order_by(Zone.name))
    return result.scalars().all()


# ---------------------- BOOKINGS ----------------------

@app.post("/api/bookings", response_model=BookingOut, status_code=201)
async def create_booking(
    payload: BookingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    zone: Zone | None = None
    if payload.zone_id is not None:
        zone = await db.get(Zone, payload.zone_id)
        if zone is None:
            raise HTTPException(status_code=404, detail="Zone not found")

    booking = Booking(
        name=payload.name,
        phone=payload.phone,
        zone_id=payload.zone_id,
        address=payload.address,
        issue=", ".join(payload.issues),
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_shared=payload.location_shared,
    )
    db.add(booking)
    await db.commit()

    # reload with zone relationship for the response
    result = await db.execute(
        select(Booking).options(selectinload(Booking.zone)).where(Booking.id == booking.id)
    )
    saved_booking = result.scalar_one()

    # Fires after the response is sent back to the browser — the person
    # booking doesn't wait on email/WhatsApp round-trips.
    background_tasks.add_task(notify_new_booking, saved_booking, zone)

    return saved_booking


@app.get("/api/bookings", response_model=list[BookingOut])
async def list_bookings(status: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Booking).options(selectinload(Booking.zone)).order_by(Booking.created_at.desc())
    if status:
        query = query.where(Booking.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@app.get("/api/bookings/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Booking).options(selectinload(Booking.zone)).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@app.patch("/api/bookings/{booking_id}/status", response_model=BookingOut)
async def update_booking_status(
    booking_id: uuid.UUID, payload: BookingStatusUpdate, db: AsyncSession = Depends(get_db)
):
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = payload.status
    await db.commit()

    result = await db.execute(
        select(Booking).options(selectinload(Booking.zone)).where(Booking.id == booking_id)
    )
    return result.scalar_one()