import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.all_models import VehicleType

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_parking.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_seed_spots():
    response = client.post("/spots/seed")
    assert response.status_code == 200
    assert response.json()["total"] == 6

    response_duplicate = client.post("/spots/seed")
    assert response_duplicate.json()["message"] == "Spots already initialized"

def test_import_messy_rates():
    payload = {
        "rates": {
            "compact": "$12.50/hr",
            "standard": "18.0",
            "ev": "Free / 25"
        }
    }
    response = client.post("/rates/import", json=payload)
    assert response.status_code == 200
    cleaned = response.json()["cleaned_rates"]
    assert cleaned["compact"] == 12.5
    assert cleaned["standard"] == 18.0
    assert cleaned["ev"] == 25.0

def test_checkin_checkout_flow():
    client.post("/spots/seed")

    # Check in
    checkin_payload = {"license_plate": "RJ-14-AB-1234", "vehicle_type": "compact"}
    res_in = client.post("/parkings/checkin", json=checkin_payload)
    assert res_in.status_code == 200
    assert res_in.json()["license_plate"] == "RJ-14-AB-1234"

    # Duplicate check-in fails
    res_dup = client.post("/parkings/checkin", json=checkin_payload)
    assert res_dup.status_code == 400

    # Check out
    checkout_payload = {"license_plate": "RJ-14-AB-1234"}
    res_out = client.post("/parkings/checkout", json=checkout_payload)
    assert res_out.status_code == 200
    assert res_out.json()["fee_charged"] >= 0.0

def test_valet_transfer():
    client.post("/spots/seed")
    client.post("/parkings/checkin", json={"license_plate": "OLD-PLATE", "vehicle_type": "standard"})

    transfer_payload = {"old_license_plate": "OLD-PLATE", "new_license_plate": "NEW-PLATE"}
    res_trans = client.post("/parkings/transfer", json=transfer_payload)
    assert res_trans.status_code == 200
    assert res_trans.json()["new_license_plate"] == "NEW-PLATE"

    # Old plate should no longer be active
    res_checkout_old = client.post("/parkings/checkout", json={"license_plate": "OLD-PLATE"})
    assert res_checkout_old.status_code == 404
