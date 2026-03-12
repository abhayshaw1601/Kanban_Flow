# KanbanFlow Setup Guide

This guide will help you set up the KanbanFlow development environment.

## Prerequisites

- Docker and Docker Compose (recommended)
- OR: Python 3.11+, Node.js 20+, and PostgreSQL 15+

## Quick Start with Docker Compose

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Stop services:**
   ```bash
   docker-compose down
   ```

## Manual Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   - Create a database named `kanbanflow`
   - Update the `DATABASE_URL` in `.env` file

5. **Run database migrations (after implementing models):**
   ```bash
   # This will be added in later tasks
   ```

6. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   - Copy `.env.example` to `.env.local`
   - Update `NEXT_PUBLIC_API_URL` if needed

4. **Start the development server:**
   ```bash
   npm run dev
   ```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://kanbanflow:kanbanflow123@postgres:5432/kanbanflow
SECRET_KEY=dev-secret-key-change-in-production-32-characters-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Verification

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### Frontend Access

Open http://localhost:3000 in your browser. You should see the KanbanFlow landing page.

## Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :3000  # or :8000, :5432
# Kill the process or change the port in docker-compose.yml
```

**Database connection issues:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres
# View PostgreSQL logs
docker-compose logs postgres
```

**Rebuild containers:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backend Issues

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Database connection errors:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env file
- Ensure database exists

### Frontend Issues

**Module not found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

## Next Steps

After completing this setup:

1. Implement database models (Task 2)
2. Set up authentication utilities (Task 3)
3. Create API endpoints (Tasks 5-11)
4. Build frontend components (Tasks 15-26)
5. Run seed data script (Task 13)

## Development Workflow

1. **Start services:** `docker-compose up -d`
2. **Make changes** to code (hot reload is enabled)
3. **View logs:** `docker-compose logs -f backend` or `docker-compose logs -f frontend`
4. **Test changes** in browser or with API client
5. **Stop services:** `docker-compose down`

## Production Deployment

For production deployment:

1. Change `SECRET_KEY` to a secure random string
2. Update `DATABASE_URL` to production database
3. Set `FRONTEND_URL` to production domain
4. Use `npm run build` for frontend
5. Use production-grade ASGI server (gunicorn + uvicorn workers)
6. Set up HTTPS/SSL certificates
7. Configure proper CORS settings
8. Enable database backups
9. Set up monitoring and logging

## Support

For issues or questions, refer to:
- FastAPI documentation: https://fastapi.tiangolo.com/
- Next.js documentation: https://nextjs.org/docs
- Docker documentation: https://docs.docker.com/
