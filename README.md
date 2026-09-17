# Parking Management System

A full-stack web application for managing vehicle parking allocations, real-time check-ins/check-outs, and hourly rate auditing built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

---

## Features

- **Auth & Session Management**: Basic authentication endpoints (`/auth/register`, `/auth/login`).
- **Vehicle Check-In**: Allocates parking spots (`COMPACT`, `STANDARD`, `EV`), tracks active occupancy, and prevents double-booking.
- **Vehicle Check-Out**: Automatically calculates fee charges based on parking duration and logs history to an audit trail.
- **Search & Pagination**: Filter active parkings by license plate with sorting and paginated responses.

---

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **Database**: SQLite
- **Frontend**: Plain HTML, CSS, JavaScript (Fetch API)

---

## Database Architecture

The system uses four main SQLAlchemy entities defined in `backend/app/models/all_models.py`:

| Model | Table Name | Key Attributes | Description |
| :--- | :--- | :--- | :--- |
| **`User`** | `users` | `id`, `username`, `hashed_password` | Stores user credentials. |
| **`Spot`** | `spots` | `spot_id`, `spot_type`, `is_occupied` | Tracks physical parking slot availability. |
| **`ActiveParking`** | `active_parkings` | `license_plate`, `spot_id`, `entry_time` | Stores currently parked vehicles. |
| **`AuditLog`** | `audit_logs` | `license_plate`, `fee_charged`, `exit_time` | Permanent log of completed sessions and fees. |

---

## Project Structure

```text
.
├── backend/
│   └── app/
│       ├── main.py             # FastAPI entrypoint
│       ├── auth.py             # API endpoints (auth, checkin, checkout, search)
│       ├── database.py         # SQLAlchemy engine and session setup
│       └── models/
│           └── all_models.py   # Database models & enums
├── frontend/                   # Static UI assets
│   ├── index.html
│   └── app.js
├── parking.db                  # SQLite database file
└── requirements.txt