# KanbanFlow

A full-stack Kanban-style project management application built with Next.js 14, FastAPI, and PostgreSQL.

## Features

- 🔐 JWT-based authentication with httpOnly cookies
- 👥 Role-based access control (Admin & Employee)
- 📋 Kanban boards with drag-and-drop functionality
- ✅ Task management with priorities and due dates
- 👤 User management and board membership
- 🌙 Dark mode support
- 📱 Responsive design

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query
- @hello-pangea/dnd (drag-and-drop)
- axios

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT authentication
- bcrypt password hashing

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Running with Docker Compose

1. Clone the repository
2. Start all services:
```bash
docker-compose up -d
```

3. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and configure

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy `.env.example` to `.env.local` and configure

4. Run the development server:
```bash
npm run dev
```

## Project Structure

```
kanbanflow/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration and utilities
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   └── main.py        # FastAPI application
│   ├── scripts/           # Utility scripts (seed data, etc.)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── lib/               # Utilities and API client
│   ├── hooks/             # Custom React hooks
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Default Users (After Seeding)

- Admin: admin@kanbanflow.com / Admin@123
- Employees: alice@, bob@, carol@, dave@, eve@ @kanbanflow.com / Pass@123

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## License

MIT
