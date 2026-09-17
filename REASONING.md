# Architectural Reasoning & Design Choices

This document outlines the design decisions, trade-offs, database modeling strategies, and edge-case handling implemented in the Parking Management System.

---

## 1. System Architecture & Component Separation

### Decision: FastAPI + SQLAlchemy ORM
- **FastAPI**: Chosen for its fast asynchronous performance, automatic OpenAPI/Swagger documentation generation, and native integration with Pydantic for request payload validation.
- **SQLAlchemy (ORM)**: Chosen to abstract SQL operations into Python classes, ensuring database agnosticism (easily swappable from SQLite to PostgreSQL/MySQL in production) and maintaining type safety.

---

## 2. Database Schema Design & Normalization

### Table Structure
The database is structured into four normalized models:
1. `User`: Manages user credentials for authentication.
2. `Spot`: Represents physical parking slots (`spot_id`, `spot_type`, `is_occupied`).
3. `ActiveParking`: Represents vehicles currently inside the lot (`license_plate`, `spot_id`, `entry_time`).
4. `AuditLog`: Immutable historical record of completed sessions (`entry_time`, `exit_time`, `fee_charged`).

### Trade-off: Separation of Active vs. Historical Parkings
- **Why Split `ActiveParking` and `AuditLog`?**
  - **Performance**: Queries for active parkings (e.g., checking spot availability or active check-ins) target a small, high-frequency table (`ActiveParking`), keeping lookup time near $O(1)$ indexed by `license_plate`.
  - **Data Lifecycle**: Completed sessions move permanently to `AuditLog`. This prevents table bloating in `ActiveParking` as total historical transactions grow over time.

---

## 3. Key Technical Decisions & Workflow Reasoning

### A. Spot Allocation & Auto-Provisioning
- **Decision**: During check-in (`/parkings/checkin`), if a valid `spot_id` does not exist in the database, the system automatically creates the spot entity on the fly.
- **Reasoning**: Reduces manual setup friction for new parking spots while ensuring foreign key relationships (`ActiveParking.spot_id` -> `Spot.spot_id`) remain valid.

### B. Dynamic Fee Calculation
- **Decision**: Check-out fees are computed dynamically upon vehicle exit based on elapsedTime ($\text{hours} = \Delta t$).
- **Reasoning**:
  $$\text{Fee} = \max(1.0, \text{duration in hours}) \times \text{Hourly Rate}$$
  Enforces a minimum 1-hour charge policy and rounds to 2 decimal places for financial accuracy.

### C. Concurrency & Occupancy Protection
- **Decision**: Before checking in, the system verifies both `Spot.is_occupied == False` and that the `license_plate` does not already exist in `ActiveParking`.
- **Reasoning**: Prevents race conditions such as double-booking the same spot or allowing a single vehicle to check into multiple spots simultaneously.

---

## 4. Edge Case Handling

| Scenario | Handled By |
| :--- | :--- |
| **Checking into an occupied spot** | Throws HTTP `400 Bad Request` ("Spot is already occupied"). |
| **Duplicate check-in for active vehicle** | Throws HTTP `400 Bad Request` ("Vehicle is already checked in"). |
| **Checking out a non-existent plate** | Throws HTTP `404 Not Found` ("Active parking session not found"). |
| **Immediate check-outs (< 1 min)** | Enforces a minimum 1-hour charge to cover base processing fees. |

---

## 5. Future Enhancements

1. **JWT Authentication**: Upgrade in-memory session tokens to signed, expiring JSON Web Tokens (JWT) using `passlib` and `python-jose`.
2. **Rate Card Integration**: Calculate fees based on `RateCard.hourly_rate` per `VehicleType` (`COMPACT`, `STANDARD`, `EV`) rather than a flat rate.
3. **Database Migration Pipeline**: Add Alembic for managing schema migrations safely in production environments.