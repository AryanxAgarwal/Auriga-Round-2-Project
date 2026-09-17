from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel

from app.database import engine, Base, get_db
from app.models.all_models import Spot, ActiveParking, AuditLog, RateCard, VehicleType
from app.services.parking_service import parse_messy_rate, calculate_fee

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Parking Lot Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RateImportSchema(BaseModel):
    rates: Dict[str, Any]

class CheckInSchema(BaseModel):
    license_plate: str
    vehicle_type: VehicleType

class CheckOutSchema(BaseModel):
    license_plate: str

class TransferSchema(BaseModel):
    old_license_plate: str
    new_license_plate: str

class ClockSchema(BaseModel):
    hours_passed: float = 24.0

DEFAULT_RATES = {
    VehicleType.COMPACT: 10.0,
    VehicleType.STANDARD: 15.0,
    VehicleType.EV: 20.0
}

@app.on_event("startup")
def startup_db_seed():
    db = next(get_db())
    if not db.query(RateCard).first():
        for v_type, rate in DEFAULT_RATES.items():
            db.add(RateCard(spot_type=v_type, hourly_rate=rate))
        db.commit()

@app.post("/rates/import")
def import_rate_card(payload: RateImportSchema, db: Session = Depends(get_db)):
    updated_rates = {}
    for spot_type_str, messy_val in payload.rates.items():
        try:
            v_type = VehicleType(spot_type_str.lower())
            clean_rate = parse_messy_rate(messy_val)
            
            rate_obj = db.query(RateCard).filter(RateCard.spot_type == v_type).first()
            if rate_obj:
                rate_obj.hourly_rate = clean_rate
            else:
                rate_obj = RateCard(spot_type=v_type, hourly_rate=clean_rate)
                db.add(rate_obj)
            
            updated_rates[v_type.value] = clean_rate
        except ValueError:
            continue
            
    db.commit()
    return {"message": "Rate card imported and cleaned successfully", "cleaned_rates": updated_rates}

@app.get("/rates")
def get_rates(db: Session = Depends(get_db)):
    rates = db.query(RateCard).all()
    return {r.spot_type.value: r.hourly_rate for r in rates}

@app.post("/spots/seed")
def seed_spots(db: Session = Depends(get_db)):
    if db.query(Spot).first():
        return {"message": "Spots already initialized"}
    
    sample_spots = [
        Spot(spot_id="L1-CMP-01", spot_type=VehicleType.COMPACT),
        Spot(spot_id="L1-CMP-02", spot_type=VehicleType.COMPACT),
        Spot(spot_id="L1-STD-01", spot_type=VehicleType.STANDARD),
        Spot(spot_id="L1-STD-02", spot_type=VehicleType.STANDARD),
        Spot(spot_id="L1-EV-01", spot_type=VehicleType.EV),
        Spot(spot_id="L1-EV-02", spot_type=VehicleType.EV),
    ]
    db.add_all(sample_spots)
    db.commit()
    return {"message": "Garages seeded with sample spots", "total": len(sample_spots)}

@app.get("/spots")
def list_spots(db: Session = Depends(get_db)):
    return db.query(Spot).all()

@app.post("/parkings/checkin")
def check_in(payload: CheckInSchema, db: Session = Depends(get_db)):
    plate = payload.license_plate.strip().upper()
    
    existing = db.query(ActiveParking).filter(ActiveParking.license_plate == plate).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Vehicle {plate} is already parked in spot {existing.spot_id}")
    
    free_spot = db.query(Spot).filter(
        Spot.spot_type == payload.vehicle_type,
        Spot.is_occupied == False
    ).first()
    
    if not free_spot:
        raise HTTPException(
            status_code=400, 
            detail=f"No available {payload.vehicle_type.value.upper()} spots right now."
        )
    
    free_spot.is_occupied = True
    new_parking = ActiveParking(
        license_plate=plate,
        spot_id=free_spot.spot_id,
        vehicle_type=payload.vehicle_type,
        entry_time=datetime.utcnow()
    )
    db.add(new_parking)
    db.commit()
    
    return {
        "message": "Check-in successful",
        "license_plate": plate,
        "spot_id": free_spot.spot_id,
        "entry_time": new_parking.entry_time
    }

@app.post("/parkings/checkout")
def check_out(payload: CheckOutSchema, db: Session = Depends(get_db)):
    plate = payload.license_plate.strip().upper()
    active = db.query(ActiveParking).filter(ActiveParking.license_plate == plate).first()
    
    if not active:
        raise HTTPException(status_code=404, detail=f"No active parking found for plate {plate}")
    
    exit_time = datetime.utcnow()
    
    rate_card = db.query(RateCard).filter(RateCard.spot_type == active.vehicle_type).first()
    hourly_rate = rate_card.hourly_rate if rate_card else 10.0
    
    fee = calculate_fee(active.entry_time, exit_time, hourly_rate)
    
    spot = db.query(Spot).filter(Spot.spot_id == active.spot_id).first()
    if spot:
        spot.is_occupied = False
        
    audit = AuditLog(
        license_plate=plate,
        spot_id=active.spot_id,
        entry_time=active.entry_time,
        exit_time=exit_time,
        fee_charged=fee,
        note="Normal Check-out"
    )
    db.add(audit)
    db.delete(active)
    db.commit()
    
    return {
        "message": "Check-out successful",
        "license_plate": plate,
        "spot_id": audit.spot_id,
        "duration_hours": round((exit_time - active.entry_time).total_seconds() / 3600, 2),
        "fee_charged": fee
    }

@app.post("/parkings/transfer")
def transfer_parking(payload: TransferSchema, db: Session = Depends(get_db)):
    old_plate = payload.old_license_plate.strip().upper()
    new_plate = payload.new_license_plate.strip().upper()
    
    active = db.query(ActiveParking).filter(ActiveParking.license_plate == old_plate).first()
    if not active:
        raise HTTPException(status_code=404, detail=f"No active session found for plate {old_plate}")
    
    target_existing = db.query(ActiveParking).filter(ActiveParking.license_plate == new_plate).first()
    if target_existing:
        raise HTTPException(status_code=400, detail=f"Target plate {new_plate} already has an active session")
    
    new_active = ActiveParking(
        license_plate=new_plate,
        spot_id=active.spot_id,
        vehicle_type=active.vehicle_type,
        entry_time=active.entry_time
    )
    db.delete(active)
    db.add(new_active)
    db.commit()
    
    return {
        "message": "Valet session transfer successful",
        "old_license_plate": old_plate,
        "new_license_plate": new_plate,
        "spot_id": new_active.spot_id,
        "entry_time": new_active.entry_time
    }

@app.post("/clock")
def trigger_clock_job(payload: ClockSchema, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    active_sessions = db.query(ActiveParking).all()
    auto_closed_count = 0
    closed_details = []

    for active in active_sessions:
        elapsed_hours = (now - active.entry_time).total_seconds() / 3600
        
        if elapsed_hours >= 24.0:
            rate_card = db.query(RateCard).filter(RateCard.spot_type == active.vehicle_type).first()
            hourly_rate = rate_card.hourly_rate if rate_card else 10.0
            
            fee = calculate_fee(active.entry_time, now, hourly_rate)
            
            spot = db.query(Spot).filter(Spot.spot_id == active.spot_id).first()
            if spot:
                spot.is_occupied = False
                
            audit = AuditLog(
                license_plate=active.license_plate,
                spot_id=active.spot_id,
                entry_time=active.entry_time,
                exit_time=now,
                fee_charged=fee,
                note="Auto-closed via 24h clock job"
            )
            db.add(audit)
            db.delete(active)
            
            auto_closed_count += 1
            closed_details.append({
                "license_plate": active.license_plate,
                "spot_id": active.spot_id,
                "fee_charged": fee
            })

    db.commit()
    return {
        "message": f"Clock job processed. Auto-closed {auto_closed_count} session(s).",
        "auto_closed_count": auto_closed_count,
        "closed_details": closed_details
    }

@app.get("/parkings/active")
def list_active_parkings(db: Session = Depends(get_db)):
    return db.query(ActiveParking).all()

@app.get("/audit/logs")
def list_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()
