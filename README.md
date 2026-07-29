# Lending Customer Management Service

A production-ready **FastAPI** application for managing loan lending customers. Store customer profiles in **PostgreSQL**, expose REST APIs, and manage everything through a modern web dashboard.

---

## Features

- **Customer registration** — POST API with full validation (email, phone, credit score, income, loan amount)
- **Customer retrieval** — GET APIs with pagination and search by name, email, or phone
- **Web dashboard** — Create, view, edit, and delete customers from the browser
- **PostgreSQL storage** — Persistent data with SQLAlchemy ORM
- **Clean architecture** — Routes → Service → Repository layered design
- **Auto-setup** — Database tables created automatically on first run

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.10+ |
| Database | PostgreSQL, SQLAlchemy 2 |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Frontend | HTML, CSS, Vanilla JavaScript |

---

## Prerequisites

- **Python 3.10+** (with `py` launcher on Windows)
- **PostgreSQL** running locally or on a remote host
- A database created (e.g. `lending_Project`)

---

## Quick Start

### 1. Clone / open the project

```bash
cd Lending
```

### 2. Create a virtual environment (recommended)

```bash
py -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example file and edit your PostgreSQL credentials:

```bash
copy .env.example .env
```

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_NAME=lending_Project
```

> **Note:** Passwords with special characters (`@`, `#`, etc.) are supported.

### 4. Run the application

```bash
py app.py
```

This will:

1. Check the PostgreSQL connection
2. Create database tables if needed
3. Start the server on **http://localhost:8000**
4. Open the dashboard in your default browser

---

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Customer dashboard (UI) |
| http://localhost:8000/docs | Swagger API documentation |
| http://localhost:8000/health | Health check endpoint |

---

## API Endpoints

Base path: `/api/v1/customers`

### Create a customer

```http
POST /api/v1/customers
Content-Type: application/json
```

```json
{
  "first_name": "Rahul",
  "last_name": "Sharma",
  "email": "rahul@example.com",
  "phone": "+919876543210",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "employment_type": "Salaried",
  "annual_income": 850000,
  "loan_amount": 500000,
  "credit_score": 750,
  "address": "42 MG Road",
  "city": "Bengaluru",
  "state": "Karnataka",
  "country": "India",
  "postal_code": "560001"
}
```

**Response:** `201 Created`

### List customers (paginated)

```http
GET /api/v1/customers?page=1&limit=10
GET /api/v1/customers?name=Rahul
GET /api/v1/customers?email=rahul@example.com
GET /api/v1/customers?phone=98765
```

**Response:** `200 OK` with paginated customer list

### Get customer by ID

```http
GET /api/v1/customers/{customer_id}
```

### Update customer

```http
PUT /api/v1/customers/{customer_id}
```

### Delete customer

```http
DELETE /api/v1/customers/{customer_id}
```

---

## Project Structure

```
Lending/
├── app.py                          # Entry point — run with: py app.py
├── requirements.txt
├── .env.example
│
├── app/
│   ├── main.py                     # FastAPI app & routes setup
│   ├── api/v1/routes/customer.py   # REST API endpoints
│   ├── core/
│   │   ├── config.py               # Environment settings
│   │   └── database.py             # DB engine & sessions
│   ├── models/customer.py          # PostgreSQL table (ORM)
│   ├── schemas/customer.py         # Request/response validation
│   ├── services/customer_service.py
│   ├── repositories/customer_repository.py
│   └── utils/
│       ├── exceptions.py           # Error handling
│       └── logging.py
│
└── static/
    ├── index.html                  # Dashboard UI
    ├── styles.css
    └── app.js
```

---

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌────────────┐
│  Dashboard   │────▶│  FastAPI     │────▶│  Service Layer  │────▶│ PostgreSQL │
│  (Browser)   │     │  Routes      │     │  Repository     │     │            │
└──────────────┘     └──────────────┘     └─────────────────┘     └────────────┘
```

| Layer | Role |
|-------|------|
| **Routes** | HTTP handling, request validation |
| **Service** | Business logic orchestration |
| **Repository** | Database queries (SQLAlchemy) |
| **Schemas** | Pydantic models for input/output |
| **Models** | SQLAlchemy ORM table definitions |

---

## Customer Data Fields

| Field | Type | Notes |
|-------|------|-------|
| first_name, last_name | string | Required |
| email | string | Unique |
| phone | string | Unique |
| date_of_birth | date | ISO format |
| gender | enum | Male, Female, Other |
| employment_type | enum | Salaried, Self-Employed, Business, etc. |
| annual_income | float | Must be > 0 |
| loan_amount | float | Must be > 0 |
| credit_score | int | 300–900 |
| address, city, state, country, postal_code | string | Required |

---

## Troubleshooting

### `Cannot connect to PostgreSQL`

- Ensure PostgreSQL is running
- Verify `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, and `DATABASE_NAME` in `.env`
- Confirm the database exists: `CREATE DATABASE "lending_Project";`

### Port 8000 already in use

Stop the existing process or change the port in `app.py`:

```python
uvicorn.run("app.main:app", host="0.0.0.0", port=8001)
```

### `py app.py` uses wrong Python

The app automatically re-launches with the project `venv` if it exists. Activate the venv manually:

```bash
venv\Scripts\activate
py app.py
```

---

## License

This project is for educational and development use.
