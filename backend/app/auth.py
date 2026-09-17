import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.all_models import Spot, ActiveParking, AuditLog, VehicleType

router = APIRouter()
USERS_DB = {}

# Schemas
class AuthSchema(BaseModel):
    username: str
    password: str

class CheckInSchema(BaseModel):
    license_plate: str
    spot_id: str
    vehicle_type: VehicleType = VehicleType.STANDARD

class CheckOutSchema(BaseModel):
    license_plate: str

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/auth/register")
def register(data: AuthSchema):
    if data.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")
    USERS_DB[data.username] = hash_pw(data.password)
    return {"message": "Account created successfully"}

@router.post("/auth/login")
def login(data: AuthSchema):
    if USERS_DB.get(data.username) != hash_pw(data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": f"session-token-{data.username}", "username": data.username}

@router.post("/parkings/checkin")
def checkin_vehicle(data: CheckInSchema, db: Session = Depends(get_db)):
    spot = db.query(Spot).filter(Spot.spot_id == data.spot_id).first()
    if not spot:
        spot = Spot(spot_id=data.spot_id, spot_type=data.vehicle_type, is_occupied=True)
        db.add(spot)
    elif spot.is_occupied:
        raise HTTPException(status_code=400, detail=f"Spot #{data.spot_id} is already occupied.")
    else:
        spot.is_occupied = True

    existing_parking = db.query(ActiveParking).filter(ActiveParking.license_plate == data.license_plate).first()
    if existing_parking:
        raise HTTPException(status_code=400, detail=f"Vehicle {data.license_plate} is already checked in.")

    new_parking = ActiveParking(
        license_plate=data.license_plate,
        spot_id=data.spot_id,
        vehicle_type=data.vehicle_type,
        entry_time=datetime.utcnow()
    )
    db.add(new_parking)
    db.commit()

    return {
        "message": f"Successfully checked in {data.license_plate} to Spot #{data.spot_id}",
        "license_plate": data.license_plate
    }

@router.post("/parkings/checkout")
def checkout_vehicle(data: CheckOutSchema, db: Session = Depends(get_db)):
    parking = db.query(ActiveParking).filter(ActiveParking.license_plate == data.license_plate).first()
    if not parking:
        raise HTTPException(status_code=404, detail="Active parking session not found for this license plate.")

    exit_time = datetime.utcnow()
    hours = max(1.0, (exit_time - parking.entry_time).total_seconds() / 3600.0)
    fee = round(hours * 10.0, 2)

    audit = AuditLog(
        license_plate=parking.license_plate,
        spot_id=parking.spot_id,
        entry_time=parking.entry_time,
        exit_time=exit_time,
        fee_charged=fee,
        note="Normal Checkout"
    )
    db.add(audit)

    spot = db.query(Spot).filter(Spot.spot_id == parking.spot_id).first()
    if spot:
        spot.is_occupied = False

    db.delete(parking)
    db.commit()

    return {
        "message": f"Vehicle {data.license_plate} checked out successfully.",
        "fee_charged": fee
    }

@router.get("/parkings/search")
def search_parkings(
    query: str = Query("", description="Search license plate"),
    sort_by: str = Query("license_plate", description="Field to sort"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    db_query = db.query(ActiveParking)
    
    if query:
        db_query = db_query.filter(ActiveParking.license_plate.contains(query))
    
    sort_attr = getattr(ActiveParking, sort_by, ActiveParking.license_plate)
    if order == "desc":
        sort_attr = sort_attr.desc()
    db_query = db_query.order_by(sort_attr)
    
    total = db_query.count()
    records = db_query.offset((page - 1) * limit).limit(limit).all()
    
    results = [
        {
            "id": r.spot_id,
            "license_plate": r.license_plate,
            "spot_id": r.spot_id,
            "is_active": True,
            "fee_charged": 0.0
        }
        for r in records
    ]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": results
    }