# ClassScheduler

ClassScheduler is an automated class scheduling system designed to manage academic timetables efficiently. It features secure user authentication, full CRUD operations for lecturers, modules, timeslots, rooms, and program levels, with advanced filtering, sorting, and pagination.

---

## 🚀 Features Implemented

### ✅ User Authentication
- JWT-based login system
- Admin-restricted endpoints
- Secure password hashing

### ✅ CRUD APIs (All Protected)
- Lecturers
- Modules
- Timeslots
- Rooms
- Program Levels
- Input validation, pagination, search, sorting
- Structured error handling

### ✅ Dev Features
- Flask + SQLAlchemy backend
- Environment variable support (`.env`)
- Auto-detected weekend slots
- CLI command to create admin users

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Database**: SQLite (dev) / PostgreSQL (recommended for production)
- **Auth**: JWT Tokens
- **Testing**: Postman + cURL examples

---

## 📦 Installation

```bash
git clone https://github.com/your-username/ClassScheduler.git
cd ClassScheduler/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///solo_scheduler.db
```

---

## 🔑 First Admin User

```bash
flask --app run:create_app create-admin
```

---

## 🧪 API Testing

Use included cURL examples or import the Postman collection.  
All endpoints require JWT authentication.  
Admin access is required for POST, PUT, and DELETE routes.

---

## 🧭 Next Milestone

**Scheduling Engine:**
- Constraint-based timetable generation
- Conflict detection
- Output per lecturer, program, and room

---

## 📁 Folder Structure

```
SoloClassScheduler/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   ├── scheduler_engine/ (next phase)
│   ├── .env
│   ├── run.py
│   └── requirements.txt
```

---

## 📄 License

MIT License
