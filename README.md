# SoloClassScheduler

**SoloClassScheduler** is a full-stack university scheduling system that generates conflict-aware class timetables based on lecturer availability, room capacity, and module requirements.

It features secure authentication, robust backend APIs, a responsive React frontend, and a powerful scheduling engine with conflict detection.

---

## Features

### ✅ Scheduling Engine (v1.2+)
- Generates non-conflicting schedules
- Checks:
  - Lecturer availability
  - Room capacity vs. expected students
  - Timeslot overlaps
- Logs structured conflict reasons in the response

### ✅ Backend API
- Built with Flask + SQLAlchemy
- Full CRUD:
  - Lecturers
  - Modules
  - Timeslots
  - Rooms
  - Program Levels
- JWT authentication (admin-only access for sensitive routes)
- Data validation with Pydantic v2 models
- Auto-generated database schema with Alembic
- PostgreSQL integration

### ✅ Frontend (v1.3 work in progress)
- Built with React + Vite
- React Router for navigation
- Components:
  - ScheduleTable
  - ConflictList
  - GenerateButton
  - LoadingIndicator / ErrorMessage
- Responsive design and Tailwind styling (planned)

---

## Tech Stack

| Layer     | Stack                        |
|-----------|------------------------------|
| Frontend  | React, Vite, React Router    |
| Backend   | Python, Flask, SQLAlchemy    |
| Database  | PostgreSQL                   |
| Auth      | JWT (Flask-JWT-Extended)     |
| ORM       | SQLAlchemy + Alembic         |
| Validation| Pydantic v2                  |
| Testing   | Pytest                       |

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL is running and a database is created
createdb class_scheduler

# Apply DB migrations
alembic upgrade head

# Run Flask server
flask run
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit: [http://localhost:5173](http://localhost:5173)

---

## Environment Variables

Create a `.env` file in the backend with:

```
FLASK_ENV=development
DATABASE_URL=postgresql://localhost/class_scheduler
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

---

## Admin User Setup

To create your first admin:

```bash
flask --app run:create_app create-admin
```

---

## API Overview

| Method | Endpoint                      | Description                |
|--------|-------------------------------|----------------------------|
| POST   | `/api/schedule/generate`      | Generate a schedule        |
| GET    | `/api/lecturers`              | List lecturers             |
| POST   | `/api/lecturers`              | Create a lecturer (admin)  |
| ...    | *(more for modules, rooms...)*|                            |

---

## Testing

```bash
PYTHONPATH=./backend pytest backend/tests/
```

Tests include full schedule generation + schema validation.

---

## Current Milestone

**v1.3 – UI Upgrade**  
Frontend will support:
- Schedule viewing
- Lecturer/module filters
- Calendar-style layout

---

## License

MIT License
