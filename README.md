# EDUCLOUD 2.0

A full-stack Learning Management System (LMS) for managing university courses, enrollments, grades, quizzes, attendance, and group workspaces — built with Django REST Framework and Vue 3.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.14, Django 6.0.5, DRF 3.17.1 |
| **Frontend** | Vue 3, TypeScript 6.0, Vite 8, Tailwind CSS 4 |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Database** | SQLite (development) |
| **Icons** | Lucide Vue Next |

## Features

### Role-Based Dashboards
- **Admin** — System overview, user management, course provisioning with instructor assignment
- **Instructor** — Course modules, attendance (QR/GPS), agile boards, mark sheets, quiz builder
- **Student** — Enrolled courses with progress tracking, pending tasks, GPA overview, digital logbook

### Core Modules
- **Course & Enrollment Management** — CRUD for courses, student enrollments
- **Gradebook** — Per-student grade tracking per course
- **Quiz Engine** — Quizzes with questions, timed attempts, automatic scoring
- **Attendance Proctoring** — QR code + GPS location verification per class session
- **Agile Group Workspaces** — Project groups with task boards (todo/in-progress/done)

## Project Structure

```
EDUCLOUD_V2/
├── backend/                          # Django REST API
│   ├── api/                          # Main app (models, views, serializers)
│   │   ├── models.py                 # UserProfile, Course, Enrollment, Grade, Quiz, etc.
│   │   ├── views.py                  # ModelViewSets with role-based filtering
│   │   ├── serializers.py
│   │   ├── urls.py                   # API routes
│   │   └── admin.py                  # Django admin registrations
│   ├── core/                         # Django project config
│   │   ├── settings.py               # DB, CORS, REST Framework, JWT settings
│   │   └── urls.py                   # Root URL config
│   ├── manage.py
│   └── db.sqlite3
│
├── frontend/                         # Vue 3 SPA
│   ├── src/
│   │   ├── components/
│   │   │   └── AdminSidebar.vue
│   │   ├── views/
│   │   │   ├── admin/                # AdminDashboard, ManageUsers, CourseProvisioning
│   │   │   ├── auth/                 # LoginView
│   │   │   ├── instructor/           # InstructorDashboard, CourseDetail
│   │   │   └── student/              # StudentDashboard
│   │   ├── router/index.ts           # Route definitions
│   │   ├── services/api.ts           # Axios instance
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
└── README.md
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API at `http://127.0.0.1:8000/`. Admin panel at `/admin/`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App at `http://localhost:5173/`. Login routing: `admin` → admin panel, `prof_*` → instructor, `student_*` or default → student dashboard.

### Production Build

```bash
cd frontend
npm run build      # outputs to frontend/dist/
npm run preview    # preview the build
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/token/` | POST | Obtain JWT token pair |
| `/api/token/refresh/` | POST | Refresh JWT token |
| `/api/users/` | GET/POST | List/create users |
| `/api/courses/` | GET/POST | List/create courses |
| `/api/enrollments/` | GET/POST | Manage enrollments |
| `/api/grades/` | GET/POST | Manage grades |
| `/api/quizzes/` | GET/POST | Manage quizzes |
| `/api/attempts/` | GET/POST | Quiz attempt tracking |
| `/api/sessions/` | GET/POST | Class sessions (QR/GPS) |
| `/api/attendance/` | GET/POST | Attendance records |
| `/api/groups/` | GET/POST | Project groups |
| `/api/tasks/` | GET/POST | Task board items |

All endpoints (except `/api/token/`) require JWT Bearer authentication.
