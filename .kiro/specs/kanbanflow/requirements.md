# Requirements Document: KanbanFlow

## Introduction

KanbanFlow is a full-stack Kanban-style project management application that enables teams to organize and track work through visual boards. The system provides role-based access control with admin and employee roles, allowing administrators to manage boards and team members while employees can view and update task progress through an intuitive drag-and-drop interface.

## Glossary

- **System**: The KanbanFlow application (frontend + backend)
- **Frontend**: Next.js 14 application with App Router
- **Backend**: FastAPI Python application
- **Database**: PostgreSQL database
- **Admin**: User with administrative privileges
- **Employee**: User with standard privileges
- **Board**: A collection of columns and tasks representing a project
- **Column**: A vertical section of a board (e.g., To-Do, In Progress, Done)
- **Task**: A work item that can be moved between columns
- **JWT**: JSON Web Token used for authentication
- **httpOnly_Cookie**: Secure cookie that cannot be accessed via JavaScript
- **Drag_and_Drop**: UI interaction for moving tasks between columns
- **Priority**: Task urgency level (low, medium, high)
- **Assignee**: User assigned to complete a task
- **Board_Member**: User with access to a specific board
- **Markdown**: Text formatting syntax for task descriptions
- **Access_Token**: Short-lived JWT for API authentication
- **Refresh_Token**: Long-lived JWT for obtaining new access tokens

## Requirements

### Requirement 1: User Authentication

**User Story:** As a user, I want to securely authenticate with the system, so that I can access my project boards and tasks.

#### Acceptance Criteria

1. WHEN a user submits valid registration credentials (name, email, password), THE System SHALL create a new user account with bcrypt-hashed password
2. WHEN a user submits valid login credentials, THE System SHALL generate an Access_Token and Refresh_Token and store them in httpOnly_Cookies
3. WHEN an Access_Token expires, THE System SHALL accept a valid Refresh_Token to issue a new Access_Token
4. WHEN a user logs out, THE System SHALL invalidate both tokens and clear the httpOnly_Cookies
5. WHEN a user submits invalid credentials, THE System SHALL reject the authentication attempt and return a descriptive error
6. THE System SHALL hash all passwords using bcrypt before storing them in the Database

### Requirement 2: Role-Based Authorization

**User Story:** As a system administrator, I want role-based access control, so that admins and employees have appropriate permissions.

#### Acceptance Criteria

1. WHEN a user is created, THE System SHALL assign either admin or employee role
2. WHEN an Admin attempts to create, edit, or delete boards, THE System SHALL allow the operation
3. WHEN an Employee attempts to create, edit, or delete boards, THE System SHALL reject the operation
4. WHEN an Admin attempts to create or delete tasks, THE System SHALL allow the operation
5. WHEN an Employee attempts to create or delete tasks, THE System SHALL reject the operation
6. WHEN an Employee attempts to move tasks or update task status, THE System SHALL allow the operation
7. WHEN an Admin attempts to manage team members, THE System SHALL allow the operation
8. WHEN an Employee attempts to manage team members, THE System SHALL reject the operation

### Requirement 3: User Management

**User Story:** As an admin, I want to view and manage users, so that I can assign tasks and manage board access.

#### Acceptance Criteria

1. WHEN an authenticated user requests their profile, THE System SHALL return their user data (id, name, email, avatar, role, createdAt)
2. WHEN an Admin requests the user list, THE System SHALL return all users in the system
3. WHEN an Employee requests the user list, THE System SHALL reject the request
4. THE System SHALL NOT return password hashes in any API response
5. WHEN a user is created, THE System SHALL generate a timestamp for createdAt

### Requirement 4: Board Management

**User Story:** As an admin, I want to create and manage project boards, so that I can organize work for different projects.

#### Acceptance Criteria

1. WHEN an Admin creates a board with name and description, THE System SHALL create the board and associate it with the creator
2. WHEN a user requests their boards, THE System SHALL return only boards where they are a Board_Member
3. WHEN a user requests a specific board by ID, THE System SHALL return the board with all columns, tasks, and assignees if the user is a Board_Member
4. WHEN a user requests a board they are not a member of, THE System SHALL reject the request
5. WHEN a board is created, THE System SHALL generate a timestamp for createdAt and store the createdBy user ID

### Requirement 5: Board Membership

**User Story:** As an admin, I want to add team members to boards, so that they can collaborate on projects.

#### Acceptance Criteria

1. WHEN an Admin adds a user to a board, THE System SHALL create a Board_Member relationship
2. WHEN a user requests board members for a board, THE System SHALL return all users associated with that board
3. WHEN an Employee attempts to add members to a board, THE System SHALL reject the operation
4. WHEN a user is added to a board, THE System SHALL allow them to view and interact with that board

### Requirement 6: Column Management

**User Story:** As a system user, I want boards to have organized columns, so that I can track task progress through workflow stages.

#### Acceptance Criteria

1. WHEN a board is created, THE System SHALL create default columns (To-Do, In Progress, Done)
2. THE System SHALL maintain column order within each board
3. WHEN columns are displayed, THE System SHALL order them by the order field
4. THE System SHALL associate each column with exactly one board via boardId

### Requirement 7: Task Creation and Management

**User Story:** As an admin, I want to create and manage tasks, so that I can define work items for the team.

#### Acceptance Criteria

1. WHEN an Admin creates a task, THE System SHALL store title, description, dueDate, priority, columnId, and assigneeId
2. WHEN a task is created, THE System SHALL generate timestamps for createdAt and updatedAt
3. WHEN a task is updated, THE System SHALL update the updatedAt timestamp
4. THE System SHALL support Markdown formatting in task descriptions
5. THE System SHALL validate priority values as low, medium, or high
6. WHEN an Admin deletes a task, THE System SHALL remove it from the Database
7. WHEN an Employee attempts to delete a task, THE System SHALL reject the operation

### Requirement 8: Task Assignment

**User Story:** As an admin, I want to assign tasks to team members, so that work is clearly distributed.

#### Acceptance Criteria

1. WHEN a task is created or updated with an assigneeId, THE System SHALL associate the task with that user
2. WHEN a task is assigned to a user, THE System SHALL validate that the user exists
3. WHEN tasks are retrieved, THE System SHALL include assignee information (name, avatar)
4. THE System SHALL allow tasks to have no assignee (null assigneeId)

### Requirement 9: Task Movement and Ordering

**User Story:** As a user, I want to drag and drop tasks between columns, so that I can update task progress visually.

#### Acceptance Criteria

1. WHEN a user moves a task to a different column, THE System SHALL update the task's columnId and order
2. WHEN a user reorders tasks within a column, THE System SHALL update the task's order value
3. THE System SHALL maintain task order within each column
4. WHEN tasks are displayed in a column, THE System SHALL order them by the order field
5. WHEN a task is moved, THE System SHALL update the updatedAt timestamp

### Requirement 10: Task Priority and Due Dates

**User Story:** As a user, I want to see task priorities and due dates, so that I can identify urgent work.

#### Acceptance Criteria

1. WHEN a task has priority set to high, THE System SHALL store it as "high"
2. WHEN a task has priority set to medium, THE System SHALL store it as "medium"
3. WHEN a task has priority set to low, THE System SHALL store it as "low"
4. WHEN a task has a dueDate, THE System SHALL store it as a timestamp
5. THE System SHALL allow tasks to have no due date (null dueDate)

### Requirement 11: Frontend Authentication Flow

**User Story:** As a user, I want to access login and registration pages, so that I can authenticate with the application.

#### Acceptance Criteria

1. WHEN a user visits the login page, THE Frontend SHALL display email and password input fields
2. WHEN a user submits login credentials, THE Frontend SHALL send them to the Backend authentication endpoint
3. WHEN authentication succeeds, THE Frontend SHALL redirect the user to the dashboard
4. WHEN authentication fails, THE Frontend SHALL display an error message
5. WHEN a user visits the registration page, THE Frontend SHALL display name, email, and password input fields
6. WHEN a user submits registration data, THE Frontend SHALL send it to the Backend registration endpoint

### Requirement 12: Frontend Route Protection

**User Story:** As a system administrator, I want protected routes, so that unauthenticated users cannot access the dashboard.

#### Acceptance Criteria

1. WHEN an unauthenticated user attempts to access dashboard routes, THE Frontend SHALL redirect them to the login page
2. WHEN an authenticated user accesses dashboard routes, THE Frontend SHALL display the requested page
3. THE Frontend SHALL use Next.js middleware to protect all routes under /dashboard

### Requirement 13: Dashboard Layout

**User Story:** As a user, I want a consistent dashboard layout, so that I can navigate the application easily.

#### Acceptance Criteria

1. WHEN a user accesses the dashboard, THE Frontend SHALL display a sidebar with navigation links
2. WHEN a user accesses the dashboard, THE Frontend SHALL display a top bar with user information
3. THE Frontend SHALL provide navigation to boards overview, individual boards, and team management pages
4. WHEN a user is an Employee, THE Frontend SHALL hide admin-only navigation items
5. THE Frontend SHALL support a collapsible sidebar for mobile devices

### Requirement 14: Boards Overview Page

**User Story:** As a user, I want to see all my boards, so that I can select which project to work on.

#### Acceptance Criteria

1. WHEN a user accesses the boards overview page, THE Frontend SHALL fetch and display all boards where the user is a Board_Member
2. WHEN an Admin accesses the boards overview page, THE Frontend SHALL display a button to create new boards
3. WHEN an Employee accesses the boards overview page, THE Frontend SHALL NOT display the create board button
4. THE Frontend SHALL display board name and description for each board

### Requirement 15: Kanban Board Display

**User Story:** As a user, I want to view a Kanban board with columns and tasks, so that I can see project status at a glance.

#### Acceptance Criteria

1. WHEN a user accesses a board page, THE Frontend SHALL display all columns for that board
2. WHEN a user accesses a board page, THE Frontend SHALL display all tasks within each column ordered by the order field
3. THE Frontend SHALL display task cards showing title, priority badge, due date, and assignee avatar
4. WHEN a task has priority high, THE Frontend SHALL display a red priority badge
5. WHEN a task has priority medium, THE Frontend SHALL display a yellow priority badge
6. WHEN a task has priority low, THE Frontend SHALL display a green priority badge
7. WHEN a task's dueDate is in the past, THE Frontend SHALL display the due date in red text
8. WHEN a task has an assignee, THE Frontend SHALL display an avatar circle with the assignee's initials
9. WHEN a column has no tasks, THE Frontend SHALL display an empty state message

### Requirement 16: Drag and Drop Functionality

**User Story:** As a user, I want to drag and drop tasks between columns, so that I can update task status efficiently.

#### Acceptance Criteria

1. WHEN a user drags a task to a different column, THE Frontend SHALL update the task's column via the Backend API
2. WHEN a user reorders tasks within a column, THE Frontend SHALL update the task order via the Backend API
3. THE Frontend SHALL use @hello-pangea/dnd library for drag and drop functionality
4. THE Frontend SHALL display smooth animations during drag operations
5. WHEN a drag operation completes, THE Frontend SHALL invalidate the React Query cache to refresh data

### Requirement 17: Task Detail Modal

**User Story:** As a user, I want to view and edit task details, so that I can manage task information.

#### Acceptance Criteria

1. WHEN a user clicks a task card, THE Frontend SHALL open a modal with full task details
2. THE Frontend SHALL display editable fields for title, description, due date, priority, and assignee
3. THE Frontend SHALL use a Markdown editor (@uiw/react-md-editor) for the description field
4. WHEN an Admin edits task details, THE Frontend SHALL allow saving changes
5. WHEN an Employee edits task details, THE Frontend SHALL allow saving changes to status-related fields only
6. WHEN a user saves task changes, THE Frontend SHALL send updates to the Backend API
7. THE Frontend SHALL display a date picker for the due date field
8. THE Frontend SHALL display a dropdown selector for priority
9. THE Frontend SHALL display a dropdown selector for assignee with all board members

### Requirement 18: Task Creation Interface

**User Story:** As an admin, I want to create new tasks, so that I can add work items to the board.

#### Acceptance Criteria

1. WHEN an Admin views a board, THE Frontend SHALL display an "Add Task" button
2. WHEN an Employee views a board, THE Frontend SHALL NOT display the "Add Task" button
3. WHEN an Admin clicks "Add Task", THE Frontend SHALL open a task creation modal
4. THE Frontend SHALL allow the Admin to specify title, description, due date, priority, column, and assignee
5. WHEN an Admin submits the task creation form, THE Frontend SHALL send the data to the Backend API

### Requirement 19: Team Members Management

**User Story:** As an admin, I want to manage team members, so that I can control board access.

#### Acceptance Criteria

1. WHEN an Admin accesses the team management page, THE Frontend SHALL display all users in the system
2. WHEN an Employee attempts to access the team management page, THE Frontend SHALL reject access
3. THE Frontend SHALL allow Admins to add users to boards
4. THE Frontend SHALL display which boards each user has access to

### Requirement 20: UI Styling and Theme

**User Story:** As a user, I want a modern and consistent UI, so that the application is pleasant to use.

#### Acceptance Criteria

1. THE Frontend SHALL use Tailwind CSS for styling
2. THE Frontend SHALL use shadcn/ui components for UI elements
3. THE Frontend SHALL support dark mode with a toggle switch
4. THE Frontend SHALL use a Trello/Linear-inspired aesthetic
5. THE Frontend SHALL be responsive and work on mobile devices
6. THE Frontend SHALL use colored avatar circles with user initials when no avatar image is provided

### Requirement 21: Notifications and Feedback

**User Story:** As a user, I want to receive feedback on my actions, so that I know when operations succeed or fail.

#### Acceptance Criteria

1. WHEN a user performs an action (create, update, delete), THE Frontend SHALL display a toast notification
2. THE Frontend SHALL use the sonner library for toast notifications
3. WHEN an operation succeeds, THE Frontend SHALL display a success toast
4. WHEN an operation fails, THE Frontend SHALL display an error toast with a descriptive message

### Requirement 22: Data Fetching and Caching

**User Story:** As a user, I want fast and responsive data loading, so that the application feels performant.

#### Acceptance Criteria

1. THE Frontend SHALL use React Query for data fetching
2. THE Frontend SHALL cache API responses to minimize network requests
3. WHEN data is mutated, THE Frontend SHALL invalidate relevant cache entries
4. THE Frontend SHALL display loading states while fetching data
5. THE Frontend SHALL handle network errors gracefully

### Requirement 23: API Client Configuration

**User Story:** As a developer, I want secure API communication, so that authentication tokens are properly handled.

#### Acceptance Criteria

1. THE Frontend SHALL use axios for HTTP requests
2. THE Frontend SHALL configure axios with withCredentials: true to send httpOnly_Cookies
3. THE Frontend SHALL send all API requests to the Backend endpoints
4. THE Frontend SHALL handle 401 Unauthorized responses by redirecting to login

### Requirement 24: Backend API Structure

**User Story:** As a developer, I want a well-organized API, so that endpoints are easy to maintain and extend.

#### Acceptance Criteria

1. THE Backend SHALL provide POST /api/auth/register endpoint for user registration
2. THE Backend SHALL provide POST /api/auth/login endpoint for authentication
3. THE Backend SHALL provide POST /api/auth/refresh endpoint for token refresh
4. THE Backend SHALL provide POST /api/auth/logout endpoint for logout
5. THE Backend SHALL provide GET /api/users/me endpoint for current user profile
6. THE Backend SHALL provide GET /api/users endpoint for user list (admin only)
7. THE Backend SHALL provide GET /api/boards endpoint for user's boards
8. THE Backend SHALL provide POST /api/boards endpoint for board creation (admin only)
9. THE Backend SHALL provide GET /api/boards/:id endpoint for board details
10. THE Backend SHALL provide POST /api/tasks endpoint for task creation (admin only)
11. THE Backend SHALL provide PATCH /api/tasks/:id endpoint for task updates
12. THE Backend SHALL provide PATCH /api/tasks/:id/move endpoint for task movement
13. THE Backend SHALL provide DELETE /api/tasks/:id endpoint for task deletion (admin only)
14. THE Backend SHALL provide GET /api/members/:boardId endpoint for board members
15. THE Backend SHALL provide POST /api/members endpoint for adding board members (admin only)

### Requirement 25: Database Schema Implementation

**User Story:** As a developer, I want a properly structured database, so that data is stored efficiently and relationships are maintained.

#### Acceptance Criteria

1. THE Database SHALL have a users table with columns: id, name, email, password, avatar, role, createdAt
2. THE Database SHALL have a boards table with columns: id, name, description, createdAt, createdBy
3. THE Database SHALL have a board_members table with columns: userId, boardId (junction table)
4. THE Database SHALL have a columns table with columns: id, name, order, boardId
5. THE Database SHALL have a tasks table with columns: id, title, description, dueDate, priority, order, columnId, assigneeId, createdAt, updatedAt
6. THE Database SHALL enforce foreign key constraints for relationships
7. THE Database SHALL use PostgreSQL as the database engine

### Requirement 26: ORM Configuration

**User Story:** As a developer, I want ORM tools for database access, so that I can work with type-safe database queries.

#### Acceptance Criteria

1. THE Backend SHALL use SQLAlchemy as the ORM for Python
2. THE Frontend SHALL use Prisma as the ORM for Next.js (if needed for server-side operations)
3. THE Backend SHALL define SQLAlchemy models matching the database schema
4. THE Backend SHALL use SQLAlchemy sessions for database transactions

### Requirement 27: Docker Deployment

**User Story:** As a developer, I want containerized deployment, so that the application can run consistently across environments.

#### Acceptance Criteria

1. THE System SHALL provide a docker-compose.yml file with services for postgres, backend, and frontend
2. THE System SHALL provide a Dockerfile for the Backend service
3. THE System SHALL provide a Dockerfile for the Frontend service
4. THE System SHALL configure PostgreSQL with a persistence volume
5. THE System SHALL use environment variables for configuration
6. WHEN docker-compose is run, THE System SHALL start all services and establish connections

### Requirement 28: Seed Data

**User Story:** As a developer, I want seed data for testing, so that I can quickly populate the database with realistic data.

#### Acceptance Criteria

1. THE System SHALL provide a seed script at scripts/seed.py
2. WHEN the seed script runs, THE System SHALL create 1 admin user with email admin@kanbanflow.com and password Admin@123
3. WHEN the seed script runs, THE System SHALL create 5 employee users: alice@, bob@, carol@, dave@, eve@ @kanbanflow.com with password Pass@123
4. WHEN the seed script runs, THE System SHALL create 2 boards: "Website Redesign" and "Marketing Campaign Q4"
5. WHEN the seed script runs, THE System SHALL create 3 columns per board
6. WHEN the seed script runs, THE System SHALL create 25 tasks with varied priorities, due dates (including overdue), assignees, and Markdown descriptions
7. THE System SHALL ensure seed data is realistic and demonstrates all features

### Requirement 29: Security Implementation

**User Story:** As a security-conscious user, I want my data protected, so that unauthorized access is prevented.

#### Acceptance Criteria

1. THE Backend SHALL validate all JWT tokens before processing authenticated requests
2. THE Backend SHALL reject requests with expired or invalid tokens
3. THE Backend SHALL store tokens only in httpOnly_Cookies to prevent XSS attacks
4. THE Backend SHALL validate user roles before allowing admin-only operations
5. THE Backend SHALL sanitize all user inputs to prevent injection attacks
6. THE Backend SHALL use bcrypt with appropriate salt rounds for password hashing
7. THE Backend SHALL NOT log or expose sensitive information (passwords, tokens)

### Requirement 30: Error Handling

**User Story:** As a user, I want clear error messages, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN an error occurs, THE Backend SHALL return appropriate HTTP status codes
2. WHEN validation fails, THE Backend SHALL return 400 Bad Request with descriptive error messages
3. WHEN authentication fails, THE Backend SHALL return 401 Unauthorized
4. WHEN authorization fails, THE Backend SHALL return 403 Forbidden
5. WHEN a resource is not found, THE Backend SHALL return 404 Not Found
6. WHEN a server error occurs, THE Backend SHALL return 500 Internal Server Error
7. THE Frontend SHALL display user-friendly error messages based on API responses
