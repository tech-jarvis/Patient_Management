# PatientHub — Clinic Management System

A full-stack clinic management application. Clinics register and log in to manage their **patients**, **clinicians**, and **appointments** — all data is scoped per clinic with JWT authentication.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.0.6, Django REST Framework 3.15, SimpleJWT |
| Database | PostgreSQL 15 |
| Frontend | React 18, TypeScript, Vite, React Router v6, Axios |
| Containerisation | Docker, Docker Compose |
| CI | GitHub Actions (on-demand + push) |

---

## Data Model

```
Clinic (auth user — email + password)
  ├── Patient (name, gender, email)  many-to-one
  ├── Clinician (name, specialization, email)  many-to-one
  └── Appointment (patient, scheduled_at, duration_minutes, status)
        └── AppointmentClinician (bridge table)  many-to-many with Clinician
```

**Business rules enforced:**
- A patient cannot have two overlapping appointments
- A clinician cannot be in two overlapping appointments at the same time
- Patient/clinician emails must be unique within a clinic (blank emails are allowed)
- All data is isolated per clinic — no cross-clinic data leakage

---

## Project Structure

```
Patient Management/
├── .env                        # Shared environment variables
├── docker-compose.yml
├── .github/workflows/ci.yml
├── Backend/
│   ├── Dockerfile
│   ├── entrypoint.sh           # migrate → collectstatic → runserver
│   ├── requirements.txt
│   ├── manage.py
│   ├── core/
│   │   ├── settings.py
│   │   └── urls.py
│   └── patients/
│       ├── models.py           # Clinic, Patient, Clinician, Appointment, AppointmentClinician
│       ├── serializers.py      # Validation, overlap detection, JWT serializers
│       ├── views.py            # ViewSets + auth views
│       ├── urls.py
│       ├── pagination.py
│       ├── admin.py
│       └── migrations/
└── Frontend/
    ├── Dockerfile
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx             # Router + AuthProvider + protected routes
    │   ├── index.css           # CSS variables design system
    │   ├── contexts/
    │   │   └── AuthContext.tsx # JWT login/logout/refresh state
    │   ├── services/
    │   │   └── api.ts          # Axios client with auto token refresh
    │   ├── types/
    │   │   └── index.ts        # Shared TypeScript interfaces + helpers
    │   ├── components/
    │   │   ├── Layout.tsx      # Sidebar navigation
    │   │   ├── Modal.tsx       # Portal modal with Escape/backdrop close
    │   │   ├── Badge.tsx       # StatusBadge, GenderBadge
    │   │   └── Icons.tsx       # SVG icon components
    │   └── pages/
    │       ├── LoginPage.tsx
    │       ├── DashboardPage.tsx
    │       ├── PatientsPage.tsx
    │       ├── CliniciansPage.tsx
    │       ├── AppointmentsPage.tsx
    │       └── SettingsPage.tsx
```

---

## Running with Docker (recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/tech-jarvis/Patient_Management.git
cd Patient_Management

# 2. Start all services (db → backend → frontend)
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api |
| Django Admin | http://localhost:8000/admin |

To stop: `docker compose down`  
To stop and wipe the database: `docker compose down -v`

---

## Running Locally (without Docker)

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 15 running locally

### 1. Environment

Copy `.env` and update `POSTGRES_HOST` to `localhost`:

```bash
cp .env .env.local
# Edit POSTGRES_HOST=localhost in .env.local
```

### 2. Backend

```bash
cd Backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# (Optional) Create a superuser for /admin
python manage.py createsuperuser

# Start development server
python manage.py runserver
# → http://localhost:8000
```

### 3. Frontend

Open a new terminal:

```bash
cd Frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# → http://localhost:5173
```

---

## Environment Variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_DB` | Database name | `patient_mgmt` |
| `POSTGRES_USER` | DB user | `postgres` |
| `POSTGRES_PASSWORD` | DB password | `postgres123` |
| `POSTGRES_HOST` | DB host (`db` in Docker, `localhost` locally) | `db` |
| `POSTGRES_PORT` | DB port | `5432` |
| `DJANGO_SECRET_KEY` | Django secret key — **change in production** | `change-me-…` |
| `DEBUG` | Django debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1,…` |
| `CORS_ALLOWED_ORIGINS` | Frontend origin allowed by CORS | `http://localhost:5173` |
| `VITE_API_URL` | Backend API base URL used by frontend | `http://localhost:8000/api` |

---

## API Reference

All endpoints are prefixed with `/api/`. Authenticated endpoints require the header:

```
Authorization: Bearer <access_token>
```

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | — | Register a new clinic |
| POST | `/api/auth/login/` | — | Login → returns `access`, `refresh`, `clinic` |
| POST | `/api/auth/token/refresh/` | — | Refresh access token |
| GET | `/api/auth/me/` | ✓ | Get current clinic profile |
| PATCH | `/api/auth/me/` | ✓ | Update clinic name/email |
| POST | `/api/auth/change-password/` | ✓ | Change password |

### Patients

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/patients/` | List patients (supports `search`, `page`, `page_size`) |
| POST | `/api/patients/` | Create patient |
| GET | `/api/patients/{id}/` | Retrieve patient |
| PATCH | `/api/patients/{id}/` | Update patient |
| DELETE | `/api/patients/{id}/` | Delete patient |

### Clinicians

Same pattern as Patients — `/api/clinicians/`  
Supports `search` (name, specialization, email), `page`, `page_size`.

### Appointments

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/appointments/` | List appointments |
| POST | `/api/appointments/` | Create appointment |
| GET | `/api/appointments/{id}/` | Retrieve appointment |
| PATCH | `/api/appointments/{id}/` | Update appointment |
| DELETE | `/api/appointments/{id}/` | Delete appointment |

**Query params:** `search` (patient name), `status`, `date_from` (YYYY-MM-DD), `date_to`, `patient` (id), `ordering`, `page`, `page_size`.

**Request body for create/update:**
```json
{
  "patient": 1,
  "scheduled_at": "2025-06-01T10:00:00Z",
  "duration_minutes": 30,
  "status": "scheduled",
  "clinician_ids": [1, 2]
}
```

---

## JWT Tokens

- **Access token** — valid for **60 minutes**
- **Refresh token** — valid for **7 days**
- The frontend automatically refreshes the access token on 401 responses. If the refresh token has also expired, the user is redirected to `/login`.

---
