# Database Seed Script

This directory contains the seed script for populating the KanbanFlow database with test data.

## Usage

### With Docker Compose

1. Start the database and backend services:
```bash
docker-compose up -d postgres backend
```

2. Run the seed script inside the backend container:
```bash
docker-compose exec backend python -m scripts.seed
```

### Local Development

1. Ensure PostgreSQL is running and accessible

2. Update the `DATABASE_URL` in `.env` if needed (e.g., for localhost):
```
DATABASE_URL=postgresql://kanbanflow:kanbanflow123@localhost:5432/kanbanflow
```

3. Run the seed script:
```bash
cd backend
python -m scripts.seed
```

## What Gets Created

The seed script creates:

- **1 Admin User**
  - Email: `admin@kanbanflow.com`
  - Password: `Admin@123`

- **5 Employee Users**
  - `alice@kanbanflow.com` / `Pass@123`
  - `bob@kanbanflow.com` / `Pass@123`
  - `carol@kanbanflow.com` / `Pass@123`
  - `dave@kanbanflow.com` / `Pass@123`
  - `eve@kanbanflow.com` / `Pass@123`

- **2 Boards**
  - Website Redesign (10 tasks)
  - Marketing Campaign Q4 (15 tasks)

- **3 Columns per Board**
  - To-Do
  - In Progress
  - Done

- **25 Tasks Total**
  - Varied priorities (low, medium, high)
  - Mix of due dates (including some overdue tasks)
  - Assigned to different users
  - Rich Markdown descriptions
  - Distributed across both boards and all columns

- **Board Memberships**
  - All 6 users are members of both boards

## Features Demonstrated

The seed data demonstrates all KanbanFlow features:

- ✅ Role-based access control (admin vs employee)
- ✅ Multiple boards with different projects
- ✅ Task priorities with color coding
- ✅ Due dates (including overdue tasks)
- ✅ Task assignments to team members
- ✅ Markdown formatting in task descriptions
- ✅ Task organization across workflow columns
- ✅ Board membership management

## Resetting Data

If you run the script when data already exists, it will prompt you to confirm before clearing and reseeding the database:

```
⚠️  Database already contains data!
Do you want to clear and reseed? (yes/no):
```

Type `yes` to proceed with clearing and reseeding, or `no` to cancel.
