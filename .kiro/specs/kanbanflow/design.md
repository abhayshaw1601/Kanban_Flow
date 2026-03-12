# Design Document: KanbanFlow

## Overview

KanbanFlow is a full-stack Kanban-style project management application built with a modern tech stack. The system follows a client-server architecture with a Next.js 14 frontend (using App Router), FastAPI backend, and PostgreSQL database. Authentication is handled via JWT tokens stored in httpOnly cookies, providing secure session management. The application supports two user roles (admin and employee) with distinct permissions, enabling collaborative project management with appropriate access controls.

The frontend provides an intuitive drag-and-drop interface for managing tasks across Kanban boards, while the backend exposes a RESTful API for all data operations. The system emphasizes security, user experience, and maintainability through modern frameworks and best practices.

## Architecture

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        NextJS[Next.js 14 Frontend]
    end
    
    subgraph "Server Layer"
        FastAPI[FastAPI Backend]
        Auth[JWT Auth Middleware]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        SQLAlchemy[SQLAlchemy ORM]
    end
    
    Browser -->|HTTPS| NextJS
    NextJS -->|API Requests + httpOnly Cookies| FastAPI
    FastAPI --> Auth
    Auth --> FastAPI
    FastAPI --> SQLAlchemy
    SQLAlchemy --> PostgreSQL
```

### Technology Stack

**Frontend:**
- Next.js 14 (App Router) - React framework with server-side rendering
- Tailwind CSS - Utility-first CSS framework
- shadcn/ui - Component library built on Radix UI
- React Query (@tanstack/react-query) - Data fetching and caching
- @hello-pangea/dnd - Drag and drop functionality
- @uiw/react-md-editor - Markdown editor for task descriptions
- axios - HTTP client with cookie support
- sonner - Toast notifications
- Zod - Schema validation

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - Python ORM
- Pydantic - Data validation
- python-jose - JWT token handling
- passlib[bcrypt] - Password hashing
- python-multipart - Form data handling
- uvicorn - ASGI server

**Database:**
- PostgreSQL 15+ - Relational database
- psycopg2 - PostgreSQL adapter for Python

**DevOps:**
- Docker & Docker Compose - Containerization
- Environment variables - Configuration management

### Deployment Architecture

```mermaid
graph LR
    subgraph "Docker Compose"
        Frontend[Frontend Container<br/>Next.js:3000]
        Backend[Backend Container<br/>FastAPI:8000]
        DB[(PostgreSQL Container<br/>:5432)]
    end
    
    Frontend -->|API Calls| Backend
    Backend -->|SQL Queries| DB
    DB -->|Persistent Volume| Storage[Volume Storage]
```

## Components and Interfaces

### Frontend Components

#### 1. Authentication Components

**LoginPage** (`app/login/page.tsx`)
- Form with email and password inputs
- Submits credentials to `/api/auth/login`
- Redirects to `/dashboard` on success
- Displays error messages on failure

**RegisterPage** (`app/register/page.tsx`)
- Form with name, email, and password inputs
- Submits data to `/api/auth/register`
- Redirects to login page on success
- Validates password strength

#### 2. Layout Components

**DashboardLayout** (`app/dashboard/layout.tsx`)
- Sidebar with navigation links
- Top bar with user profile and logout
- Dark mode toggle
- Responsive collapsible sidebar for mobile
- Wraps all dashboard pages

**Sidebar** (`components/Sidebar.tsx`)
- Navigation links: Boards, Team (admin only)
- Active route highlighting
- User role-based visibility

**TopBar** (`components/TopBar.tsx`)
- User avatar and name
- Logout button
- Dark mode toggle

#### 3. Board Components

**BoardsPage** (`app/dashboard/boards/page.tsx`)
- Fetches user's boards via React Query
- Displays board cards with name and description
- "Create Board" button (admin only)
- Links to individual board pages

**BoardPage** (`app/dashboard/boards/[boardId]/page.tsx`)
- Fetches board details with columns and tasks
- Renders KanbanBoard component
- Handles loading and error states

**KanbanBoard** (`components/KanbanBoard.tsx`)
- Displays columns horizontally
- Implements drag-and-drop with @hello-pangea/dnd
- Handles onDragEnd to update task position
- "Add Task" button (admin only)

**Column** (`components/Column.tsx`)
- Droppable area for tasks
- Column header with name
- Empty state when no tasks
- Ordered list of TaskCard components

**TaskCard** (`components/TaskCard.tsx`)
- Draggable task card
- Displays: title, priority badge, due date, assignee avatar
- Color-coded priority: red (high), yellow (medium), green (low)
- Red text for overdue dates
- onClick opens TaskModal

#### 4. Task Components

**TaskModal** (`components/TaskModal.tsx`)
- Modal dialog for task details
- Editable fields: title, description (markdown), due date, priority, assignee
- Save button triggers API update
- Delete button (admin only)
- Close button

**TaskForm** (`components/TaskForm.tsx`)
- Form for creating new tasks
- Fields: title, description, due date, priority, column, assignee
- Markdown editor for description
- Date picker for due date
- Dropdowns for priority and assignee

#### 5. Team Components

**TeamPage** (`app/dashboard/team/page.tsx`)
- Admin-only page
- Lists all users
- Shows user roles and board memberships
- "Add Member to Board" functionality

### Frontend Utilities

**API Client** (`lib/api.ts`)
```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  withCredentials: true, // Send httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for handling 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**React Query Hooks** (`hooks/useBoards.ts`, `hooks/useTasks.ts`, etc.)
- Custom hooks for data fetching
- Automatic caching and revalidation
- Mutation hooks with cache invalidation

**Middleware** (`middleware.ts`)
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: '/dashboard/:path*',
};
```

### Backend Components

#### 1. API Routes

**Authentication Routes** (`app/routers/auth.py`)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

**User Routes** (`app/routers/users.py`)
- `GET /api/users/me` - Current user profile
- `GET /api/users` - List all users (admin only)

**Board Routes** (`app/routers/boards.py`)
- `GET /api/boards` - User's boards
- `POST /api/boards` - Create board (admin only)
- `GET /api/boards/{board_id}` - Board details with columns and tasks

**Task Routes** (`app/routers/tasks.py`)
- `POST /api/tasks` - Create task (admin only)
- `PATCH /api/tasks/{task_id}` - Update task
- `PATCH /api/tasks/{task_id}/move` - Move task (drag-and-drop)
- `DELETE /api/tasks/{task_id}` - Delete task (admin only)

**Member Routes** (`app/routers/members.py`)
- `GET /api/members/{board_id}` - Board members
- `POST /api/members` - Add member to board (admin only)

#### 2. Database Models

**User Model** (`app/models/user.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # bcrypt hashed
    avatar = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    created_boards = relationship("Board", back_populates="creator")
    board_memberships = relationship("BoardMember", back_populates="user")
    assigned_tasks = relationship("Task", back_populates="assignee")
```

**Board Model** (`app/models/board.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Board(Base):
    __tablename__ = "boards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="created_boards")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")
    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
```

**BoardMember Model** (`app/models/board_member.py`)
```python
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class BoardMember(Base):
    __tablename__ = "board_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="board_memberships")
    board = relationship("Board", back_populates="members")
    
    __table_args__ = (UniqueConstraint('user_id', 'board_id', name='_user_board_uc'),)
```

**Column Model** (`app/models/column.py`)
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Column(Base):
    __tablename__ = "columns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    
    # Relationships
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
```

**Task Model** (`app/models/task.py`)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # Markdown content
    due_date = Column(DateTime, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    order = Column(Integer, nullable=False)
    column_id = Column(Integer, ForeignKey("columns.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    column = relationship("Column", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
```

#### 3. Pydantic Schemas

**Request/Response Schemas** (`app/schemas/`)
- Define data validation and serialization
- Separate schemas for requests and responses
- Exclude sensitive fields (passwords) from responses

Example:
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    avatar: Optional[str]
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"
    column_id: int
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None

class TaskMove(BaseModel):
    column_id: int
    order: int
```

#### 4. Authentication & Authorization

**JWT Utilities** (`app/core/security.py`)
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key"  # From environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**Dependencies** (`app/core/deps.py`)
```python
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from typing import Optional

async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = decode_token(access_token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

#### 5. Database Connection

**Database Setup** (`app/core/database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@postgres:5432/kanbanflow"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Data Models

### Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ boards : creates
    users ||--o{ board_members : "member of"
    users ||--o{ tasks : "assigned to"
    boards ||--o{ board_members : has
    boards ||--o{ columns : contains
    columns ||--o{ tasks : contains
    
    users {
        int id PK
        string name
        string email UK
        string password
        string avatar
        enum role
        datetime created_at
    }
    
    boards {
        int id PK
        string name
        string description
        datetime created_at
        int created_by FK
    }
    
    board_members {
        int id PK
        int user_id FK
        int board_id FK
    }
    
    columns {
        int id PK
        string name
        int order
        int board_id FK
    }
    
    tasks {
        int id PK
        string title
        text description
        datetime due_date
        enum priority
        int order
        int column_id FK
        int assignee_id FK
        datetime created_at
        datetime updated_at
    }
```

### Data Validation Rules

**User:**
- Email must be unique and valid format
- Password must be at least 8 characters
- Role must be "admin" or "employee"
- Name is required

**Board:**
- Name is required
- Description is optional
- created_by must reference valid user

**Task:**
- Title is required
- Priority must be "low", "medium", or "high"
- column_id must reference valid column
- assignee_id must reference valid user (if provided)
- order must be non-negative integer

**Column:**
- Name is required
- order must be non-negative integer
- board_id must reference valid board

### Data Flow Examples

**Task Movement Flow:**
1. User drags task to new column
2. Frontend calls `PATCH /api/tasks/{id}/move` with new column_id and order
3. Backend validates user has access to board
4. Backend updates task's column_id and order
5. Backend recalculates order for other tasks in affected columns
6. Backend returns updated task
7. Frontend invalidates React Query cache
8. Frontend refetches board data to show updated state

**Authentication Flow:**
1. User submits login credentials
2. Backend validates credentials
3. Backend generates access_token (30min) and refresh_token (7days)
4. Backend sets both tokens as httpOnly cookies
5. Frontend redirects to dashboard
6. All subsequent requests include cookies automatically
7. When access_token expires, frontend calls `/api/auth/refresh`
8. Backend validates refresh_token and issues new access_token

## Correctness Properties


A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, I've identified the following areas of potential redundancy:

**Authorization Properties**: Requirements 2.2-2.8 all test role-based permissions. These can be consolidated into comprehensive properties that test admin vs employee permissions across different operations rather than having separate properties for each operation type.

**Priority Storage Properties**: Requirements 10.1-10.3 test storing each priority value separately. These are redundant and can be combined into a single property that tests all priority values.

**UI Display Properties**: Requirements 15.4-15.6 test priority badge colors separately. These can be combined into one property that tests the priority-to-color mapping.

**Timestamp Properties**: Requirements 3.5, 4.5, 7.2 all test timestamp generation. These can be consolidated into a single property about timestamp invariants.

**API Endpoint Properties**: Requirements 24.1-24.15 list individual endpoints. Rather than testing each endpoint separately, we'll create properties that test endpoint behavior patterns (auth endpoints, CRUD operations, authorization checks).

After reflection, I'll focus on unique, high-value properties that provide comprehensive coverage without redundancy.

### Authentication & Security Properties

**Property 1: Password hashing invariant**
*For any* user account created or password updated, the stored password in the database should be a bcrypt hash and never plaintext.
**Validates: Requirements 1.1, 1.6**

**Property 2: Token refresh round-trip**
*For any* valid refresh token, using it to obtain a new access token should succeed and the new access token should be valid for authentication.
**Validates: Requirements 1.3**

**Property 3: Logout invalidation**
*For any* authenticated user session, after logout, both the access token and refresh token should be invalid and subsequent requests with those tokens should be rejected.
**Validates: Requirements 1.4**

**Property 4: Invalid credentials rejection**
*For any* login attempt with incorrect password or non-existent email, the system should reject authentication and return an appropriate error.
**Validates: Requirements 1.5**

**Property 5: Password exclusion from responses**
*For any* API response containing user data, the response should never include the password hash field.
**Validates: Requirements 3.4**

**Property 6: JWT token structure**
*For any* generated access token or refresh token, decoding it should reveal the correct user ID, expiration time, and token type.
**Validates: Requirements 1.2**

### Authorization Properties

**Property 7: Admin board management permissions**
*For any* admin user, attempts to create, edit, or delete boards should succeed with appropriate data.
**Validates: Requirements 2.2**

**Property 8: Employee board management restrictions**
*For any* employee user, attempts to create, edit, or delete boards should be rejected with 403 Forbidden status.
**Validates: Requirements 2.3**

**Property 9: Admin task management permissions**
*For any* admin user, attempts to create or delete tasks should succeed.
**Validates: Requirements 2.4, 7.6**

**Property 10: Employee task management restrictions**
*For any* employee user, attempts to create or delete tasks should be rejected with 403 Forbidden status.
**Validates: Requirements 2.5, 7.7**

**Property 11: Employee task movement permissions**
*For any* employee user, attempts to move tasks or update task status should succeed.
**Validates: Requirements 2.6**

**Property 12: Team management authorization**
*For any* admin user, managing team members should succeed, and for any employee user, it should be rejected with 403 Forbidden.
**Validates: Requirements 2.7, 2.8, 5.3**

### User Management Properties

**Property 13: User role assignment invariant**
*For any* created user, the user should have exactly one role that is either "admin" or "employee".
**Validates: Requirements 2.1**

**Property 14: User profile completeness**
*For any* authenticated user requesting their profile, the response should include id, name, email, avatar, role, and createdAt fields.
**Validates: Requirements 3.1**

**Property 15: Admin user list access**
*For any* admin user requesting the user list, the response should include all users in the system.
**Validates: Requirements 3.2**

**Property 16: Employee user list restriction**
*For any* employee user requesting the user list, the request should be rejected with 403 Forbidden.
**Validates: Requirements 3.3**

### Board Management Properties

**Property 17: Board creation with association**
*For any* admin user creating a board with valid name and description, the board should be created with createdBy set to the admin's user ID and createdAt timestamp populated.
**Validates: Requirements 4.1, 4.5**

**Property 18: Board membership access control**
*For any* user requesting their boards, the response should include only boards where the user is a board member, and exclude all other boards.
**Validates: Requirements 4.2**

**Property 19: Board detail completeness**
*For any* board member requesting a specific board, the response should include the board with all its columns, tasks, and assignee information.
**Validates: Requirements 4.3**

**Property 20: Non-member board access rejection**
*For any* user requesting a board where they are not a member, the request should be rejected with 403 Forbidden or 404 Not Found.
**Validates: Requirements 4.4**

**Property 21: Default columns creation**
*For any* newly created board, the system should automatically create three default columns named "To-Do", "In Progress", and "Done" with order values 0, 1, and 2 respectively.
**Validates: Requirements 6.1**

**Property 22: Column ordering invariant**
*For any* board, when columns are retrieved, they should be ordered by their order field in ascending order.
**Validates: Requirements 6.2, 6.3**

**Property 23: Column-board association invariant**
*For any* column in the database, it should have exactly one valid boardId that references an existing board.
**Validates: Requirements 6.4**

### Board Membership Properties

**Property 24: Member addition creates relationship**
*For any* admin adding a user to a board, a board_members record should be created linking the user and board.
**Validates: Requirements 5.1**

**Property 25: Board member listing**
*For any* board, requesting its members should return all users who have board_members records for that board.
**Validates: Requirements 5.2**

**Property 26: Member access grant**
*For any* user added to a board, subsequent requests to view or interact with that board should succeed.
**Validates: Requirements 5.4**

### Task Management Properties

**Property 27: Task creation with all fields**
*For any* admin creating a task with valid data, the task should be stored with all provided fields (title, description, dueDate, priority, columnId, assigneeId) and generated timestamps (createdAt, updatedAt).
**Validates: Requirements 7.1, 7.2**

**Property 28: Task update timestamp**
*For any* task being updated, the updatedAt timestamp should be changed to the current time and should be greater than the previous updatedAt value.
**Validates: Requirements 7.3, 9.5**

**Property 29: Priority validation**
*For any* task creation or update with a priority value, if the priority is not "low", "medium", or "high", the request should be rejected with a validation error.
**Validates: Requirements 7.5**

**Property 30: Task assignment validation**
*For any* task being assigned to a user, if the assigneeId does not reference an existing user, the request should be rejected with a validation error.
**Validates: Requirements 8.2**

**Property 31: Task retrieval with assignee data**
*For any* task with an assignee, when the task is retrieved, the response should include the assignee's name and avatar information.
**Validates: Requirements 8.3**

**Property 32: Task movement updates**
*For any* task being moved to a different column, the task's columnId should be updated to the new column and the order should be updated to the specified position.
**Validates: Requirements 9.1**

**Property 33: Task reordering within column**
*For any* task being reordered within its current column, the task's order value should be updated while columnId remains unchanged.
**Validates: Requirements 9.2**

**Property 34: Task ordering invariant**
*For any* column, when tasks are retrieved, they should be ordered by their order field in ascending order.
**Validates: Requirements 9.3, 9.4**

**Property 35: Task deletion removes from database**
*For any* admin deleting a task, subsequent attempts to retrieve that task should return 404 Not Found.
**Validates: Requirements 7.6**

### Frontend Route Protection Properties

**Property 36: Unauthenticated dashboard redirect**
*For any* unauthenticated user attempting to access any route under /dashboard, the frontend should redirect to the login page.
**Validates: Requirements 12.1**

**Property 37: Authenticated dashboard access**
*For any* authenticated user accessing routes under /dashboard, the frontend should display the requested page without redirecting.
**Validates: Requirements 12.2**

### Frontend Role-Based UI Properties

**Property 38: Employee admin UI hiding**
*For any* employee user viewing the dashboard, admin-only UI elements (create board button, add task button, delete buttons, team management link) should not be rendered.
**Validates: Requirements 13.4, 14.3, 18.2**

**Property 39: Admin UI element visibility**
*For any* admin user viewing the dashboard, admin-only UI elements (create board button, add task button, delete buttons, team management link) should be rendered and functional.
**Validates: Requirements 14.2, 18.1**

### Frontend Data Display Properties

**Property 40: Board overview displays user boards**
*For any* user accessing the boards overview page, the frontend should fetch and display only boards where the user is a member.
**Validates: Requirements 14.1**

**Property 41: Board page displays columns and tasks**
*For any* user accessing a board page, the frontend should display all columns for that board and all tasks within each column ordered by the order field.
**Validates: Requirements 15.1, 15.2**

**Property 42: Task card information completeness**
*For any* task card displayed, it should show the title, priority badge, due date (if present), and assignee avatar (if assigned).
**Validates: Requirements 15.3**

**Property 43: Overdue task highlighting**
*For any* task with a dueDate in the past, the frontend should display the due date text in red color.
**Validates: Requirements 15.7**

**Property 44: Assignee avatar display**
*For any* task with an assignee, the frontend should display an avatar circle with the assignee's initials derived from their name.
**Validates: Requirements 15.8, 20.6**

**Property 45: Task modal field availability**
*For any* task modal opened, it should display editable fields for title, description, due date, priority, and assignee.
**Validates: Requirements 17.2**

**Property 46: Assignee dropdown shows board members**
*For any* task modal's assignee dropdown, it should display all users who are members of the current board.
**Validates: Requirements 17.9**

**Property 47: Team page displays all users**
*For any* admin accessing the team management page, the frontend should display all users in the system with their roles and board memberships.
**Validates: Requirements 19.1, 19.4**

**Property 48: Employee team page access rejection**
*For any* employee attempting to access the team management page, the frontend should reject access and redirect or show an error.
**Validates: Requirements 19.2**

### Frontend Interaction Properties

**Property 49: Drag-and-drop triggers API update**
*For any* task dragged to a different column or position, the frontend should send a PATCH request to /api/tasks/{id}/move with the new columnId and order.
**Validates: Requirements 16.1, 16.2**

**Property 50: Cache invalidation after mutation**
*For any* data mutation operation (create, update, delete, move), the frontend should invalidate the relevant React Query cache entries.
**Validates: Requirements 16.5, 22.3**

**Property 51: Task edit API communication**
*For any* user saving task changes in the modal, the frontend should send a PATCH request to /api/tasks/{id} with the updated fields.
**Validates: Requirements 17.6**

**Property 52: Task creation API communication**
*For any* admin submitting the task creation form, the frontend should send a POST request to /api/tasks with all form data.
**Validates: Requirements 18.5**

**Property 53: Login API communication**
*For any* user submitting login credentials, the frontend should send a POST request to /api/auth/login with email and password.
**Validates: Requirements 11.2**

**Property 54: Registration API communication**
*For any* user submitting registration data, the frontend should send a POST request to /api/auth/register with name, email, and password.
**Validates: Requirements 11.6**

### Frontend Feedback Properties

**Property 55: Action toast notifications**
*For any* user action (create, update, delete), the frontend should display a toast notification indicating success or failure.
**Validates: Requirements 21.1, 21.3, 21.4**

**Property 56: Network error handling**
*For any* network error during data fetching, the frontend should handle it gracefully without crashing and display an appropriate error message.
**Validates: Requirements 22.5**

**Property 57: Unauthorized response redirect**
*For any* API response with 401 Unauthorized status, the frontend should redirect the user to the login page.
**Validates: Requirements 23.4**

### Frontend Caching Properties

**Property 58: API response caching**
*For any* data fetching request, if the same request is made again within the cache time window, the frontend should return cached data without making a new network request.
**Validates: Requirements 22.2**

### Frontend Configuration Properties

**Property 59: Cookie credentials in requests**
*For any* API request made by the frontend, the axios client should include withCredentials: true to send httpOnly cookies.
**Validates: Requirements 23.2**

### Database Schema Properties

**Property 60: Database schema structure**
*For any* fresh database initialization, the schema should include tables for users, boards, board_members, columns, and tasks with all specified columns and foreign key constraints.
**Validates: Requirements 25.1-25.7**

### Seed Data Properties

**Property 61: Seed data creation**
*For any* execution of the seed script, it should create 1 admin user (admin@kanbanflow.com), 5 employee users, 2 boards, 3 columns per board, and 25 tasks with varied attributes.
**Validates: Requirements 28.1-28.7**

### Security Properties

**Property 62: JWT validation enforcement**
*For any* authenticated API endpoint, requests without valid JWT tokens should be rejected with 401 Unauthorized.
**Validates: Requirements 29.1, 29.2**

**Property 63: httpOnly cookie security**
*For any* authentication response, tokens should be set as httpOnly cookies that cannot be accessed via JavaScript.
**Validates: Requirements 29.3**

**Property 64: Role validation enforcement**
*For any* admin-only API endpoint, requests from non-admin users should be rejected with 403 Forbidden.
**Validates: Requirements 29.4**

### Error Handling Properties

**Property 65: HTTP status code correctness**
*For any* API error, the response should include the appropriate HTTP status code: 400 for validation errors, 401 for authentication failures, 403 for authorization failures, 404 for not found, and 500 for server errors.
**Validates: Requirements 30.1-30.6**

**Property 66: Error message descriptiveness**
*For any* API error response, it should include a descriptive error message that explains what went wrong.
**Validates: Requirements 30.2, 30.7**

## Error Handling

### Backend Error Handling

**Validation Errors (400 Bad Request)**
- Invalid email format
- Missing required fields
- Invalid enum values (priority, role)
- Invalid data types
- Constraint violations (duplicate email)

**Authentication Errors (401 Unauthorized)**
- Missing or invalid JWT token
- Expired access token
- Invalid credentials during login
- Token signature mismatch

**Authorization Errors (403 Forbidden)**
- Employee attempting admin-only operations
- User accessing board they're not a member of
- Insufficient permissions for operation

**Not Found Errors (404 Not Found)**
- Requested resource doesn't exist
- Invalid ID in URL parameter
- Deleted resource

**Server Errors (500 Internal Server Error)**
- Database connection failures
- Unexpected exceptions
- Third-party service failures

### Frontend Error Handling

**Network Errors**
- Display toast notification with error message
- Show retry button for failed requests
- Maintain UI state during errors

**Authentication Errors**
- Redirect to login page on 401
- Clear local auth state
- Display login required message

**Validation Errors**
- Display inline form validation errors
- Highlight invalid fields
- Show specific error messages from backend

**Loading States**
- Display skeleton loaders during data fetching
- Show spinner for mutations
- Disable buttons during submission

### Error Response Format

All API errors follow this structure:
```json
{
  "detail": "Descriptive error message",
  "status_code": 400,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Specific user scenarios (e.g., admin creates board with specific data)
- Edge cases (e.g., empty task title, null assignee)
- Error conditions (e.g., invalid priority value)
- Integration between components

**Property-Based Tests**: Verify universal properties across all inputs
- Generate random valid inputs (users, boards, tasks)
- Test properties that should hold for all inputs
- Catch edge cases that manual tests might miss
- Validate invariants and business rules

Both approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property-based tests verify general correctness across the input space.

### Property-Based Testing Configuration

**Library Selection**:
- **Backend (Python)**: Use `hypothesis` library for property-based testing
- **Frontend (TypeScript)**: Use `fast-check` library for property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: kanbanflow, Property {number}: {property_text}`

**Example Property Test (Python with hypothesis)**:
```python
from hypothesis import given, strategies as st
import pytest

# Feature: kanbanflow, Property 1: Password hashing invariant
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    password=st.text(min_size=8, max_size=100)
)
def test_password_hashing_invariant(name, email, password):
    """For any user account created, the stored password should be bcrypt hashed."""
    user = create_user(name=name, email=email, password=password)
    
    # Password should not be stored as plaintext
    assert user.password != password
    
    # Password should be a valid bcrypt hash
    assert user.password.startswith('$2b$')
    
    # Should be able to verify the password
    assert verify_password(password, user.password)
```

**Example Property Test (TypeScript with fast-check)**:
```typescript
import fc from 'fast-check';
import { describe, it, expect } from 'vitest';

// Feature: kanbanflow, Property 36: Unauthenticated dashboard redirect
describe('Property 36: Unauthenticated dashboard redirect', () => {
  it('should redirect unauthenticated users from dashboard routes', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('/dashboard', '/dashboard/boards', '/dashboard/team'),
        (route) => {
          // Simulate unauthenticated request
          const response = accessRoute(route, { authenticated: false });
          
          // Should redirect to login
          expect(response.redirect).toBe('/login');
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Unit Testing Strategy

**Backend Unit Tests (pytest)**:
- Test each API endpoint with specific examples
- Test authentication flows (register, login, logout, refresh)
- Test authorization checks for admin vs employee
- Test database models and relationships
- Test error handling for invalid inputs
- Mock external dependencies

**Frontend Unit Tests (Vitest + React Testing Library)**:
- Test component rendering with specific props
- Test user interactions (clicks, form submissions)
- Test conditional rendering based on user role
- Test API client configuration
- Test error boundary behavior
- Mock API responses

### Integration Testing

**API Integration Tests**:
- Test complete user flows (register → login → create board → add task)
- Test data consistency across related endpoints
- Test transaction rollback on errors
- Use test database for isolation

**Frontend Integration Tests**:
- Test page navigation flows
- Test form submission to API
- Test data fetching and display
- Test drag-and-drop interactions
- Use MSW (Mock Service Worker) for API mocking

### Test Organization

**Backend Test Structure**:
```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_boards.py
│   ├── test_tasks.py
│   └── test_members.py
├── property/
│   ├── test_auth_properties.py
│   ├── test_authorization_properties.py
│   ├── test_board_properties.py
│   └── test_task_properties.py
└── integration/
    └── test_user_flows.py
```

**Frontend Test Structure**:
```
tests/
├── unit/
│   ├── components/
│   │   ├── TaskCard.test.tsx
│   │   ├── KanbanBoard.test.tsx
│   │   └── TaskModal.test.tsx
│   └── hooks/
│       ├── useBoards.test.ts
│       └── useTasks.test.ts
├── property/
│   ├── auth.property.test.ts
│   ├── ui-visibility.property.test.ts
│   └── data-display.property.test.ts
└── integration/
    └── board-flow.test.tsx
```

### Test Data Generation

**Property Test Generators**:
- User generator: random name, email, password, role
- Board generator: random name, description
- Task generator: random title, description (markdown), priority, due date
- Column generator: random name, order
- Ensure generated data meets validation rules

**Seed Data for Manual Testing**:
- Use seed script to populate database with realistic data
- Include overdue tasks, tasks with various priorities
- Include boards with different member configurations
- Include both admin and employee users

### Continuous Integration

**CI Pipeline**:
1. Run linters (flake8, eslint)
2. Run type checkers (mypy, TypeScript compiler)
3. Run unit tests with coverage reporting
4. Run property-based tests (100+ iterations)
5. Run integration tests
6. Build Docker images
7. Deploy to staging environment

**Coverage Goals**:
- Backend: 80%+ code coverage
- Frontend: 70%+ code coverage
- All critical paths must be covered
- All properties must have corresponding tests

### Manual Testing Checklist

- [ ] User registration and login flows
- [ ] Admin can create boards and tasks
- [ ] Employee cannot create boards or tasks
- [ ] Drag-and-drop task movement works smoothly
- [ ] Task modal displays and saves correctly
- [ ] Dark mode toggle works
- [ ] Mobile responsive layout works
- [ ] Toast notifications appear for actions
- [ ] Overdue tasks display in red
- [ ] Avatar initials display correctly
- [ ] Team management page (admin only)
- [ ] Logout clears session
- [ ] Token refresh works automatically
- [ ] Error messages are clear and helpful
