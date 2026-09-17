from sqlalchemy import Column, String, Integer, DateTime, Float, Enum, Boolean, ForeignKey, JSON
import enum
from datetime import datetime
from app.database import Base

class VehicleType(str, enum.Enum):
    COMPACT = "compact"
    STANDARD = "standard"
    EV = "ev"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Spot(Base):
    __tablename__ = "spots"
    spot_id = Column(String, primary_key=True)
    spot_type = Column(Enum(VehicleType), nullable=False)
    is_occupied = Column(Boolean, default=False)
    meta_info = Column(JSON, nullable=True)

class RateCard(Base):
    __tablename__ = "rate_cards"
    spot_type = Column(Enum(VehicleType), primary_key=True)
    hourly_rate = Column(Float, nullable=False)

class ActiveParking(Base):
    __tablename__ = "active_parkings"
    license_plate = Column(String, primary_key=True, index=True)
    spot_id = Column(String, ForeignKey("spots.spot_id"), nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, nullable=False)
    spot_id = Column(String, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False)
    fee_charged = Column(Float, nullable=False)
    note = Column(String, nullable=True)