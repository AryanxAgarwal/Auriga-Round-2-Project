import hashlib
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db

# Dynamically resolve the model class to prevent import crashes
import app.models.all_models as models_module

ModelClass = (
    getattr(models_module, "ParkingRecord", None) or
    getattr(models_module, "Parking", None) or
    getattr(models_module, "ParkingLot", None) or
    getattr(models_module, "Ticket", None) or
    getattr(models_module, "Vehicle", None)
)

router = APIRouter()

USERS_DB = {}

class AuthSchema(BaseModel):
    username: str
    password: str

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

@router.get("/parkings/search")
def search_parkings(
    query: str = Query("", description="Search license plate"),
    sort_by: str = Query("id", description="Field to sort"),
    order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    if not ModelClass:
        return {"total": 0, "page": page, "limit": limit, "results": []}

    db_query = db.query(ModelClass)
    
    if query and hasattr(ModelClass, "license_plate"):
        db_query = db_query.filter(ModelClass.license_plate.contains(query))
    
    sort_attr = getattr(ModelClass, sort_by, getattr(ModelClass, "id", None))
    if sort_attr and order == "desc":
        sort_attr = sort_attr.desc()
    if sort_attr is not None:
        db_query = db_query.order_by(sort_attr)
    
    total = db_query.count()
    records = db_query.offset((page - 1) * limit).limit(limit).all()
    
    results = []
    for r in records:
        results.append({
            "id": getattr(r, "id", "N/A"),
            "license_plate": getattr(r, "license_plate", getattr(r, "plate_number", "N/A")),
            "spot_id": getattr(r, "spot_id", getattr(r, "spot_number", 1)),
            "is_active": getattr(r, "is_active", True),
            "fee_charged": getattr(r, "fee_charged", getattr(r, "fee", 0.0)) or 0.0
        })
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "results": results
    }