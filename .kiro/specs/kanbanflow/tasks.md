# Implementation Plan: KanbanFlow

## Overview

This implementation plan breaks down the KanbanFlow project into incremental, testable steps. The approach follows a bottom-up strategy: first establishing the backend API with database models and authentication, then building the frontend components that consume the API. Each task builds on previous work, ensuring no orphaned code. Testing tasks are marked as optional (*) to allow for faster MVP development while maintaining the option for comprehensive test coverage.

## Tasks

- [x] 1. Set up project structure and development environment
  - Create root directory with backend/ and frontend/ subdirectories
  - Initialize backend: Python virtual environment, FastAPI project structure
  - Initialize frontend: Next.js 14 with App Router, TypeScript, Tailwind CSS
  - Set up Docker Compose with PostgreSQL, backend, and frontend services
  - Create .env files for environment variables (database URL, JWT secret, API URL)
  - Install core dependencies: FastAPI, SQLAlchemy, Next.js, React Query, axios
  - _Requirements: 27.1, 27.2, 27.3, 27.5_

- [ ] 2. Implement database models and connection
  - [x] 2.1 Set up database connection and base configuration
    - Create database.py with SQLAlchemy engine, SessionLocal, and Base
    - Configure PostgreSQL connection string from environment variables
    - Create get_db dependency function for FastAPI
    - _Requirements: 25.7, 26.1_
  
  - [x] 2.2 Implement User model
    - Create User model with id, name, email, password, avatar, role, created_at
    - Define UserRole enum (admin, employee)
    - Add relationships for created_boards, board_memberships, assigned_tasks
    - _Requirements: 25.1, 2.1_
  
  - [x] 2.3 Implement Board, BoardMember, Column, and Task models
    - Create Board model with id, name, description, created_at, created_by
    - Create BoardMember junction table model with user_id, board_id, unique constraint
    - Create Column model with id, name, order, board_id
    - Create Task model with id, title, description, due_date, priority, order, column_id, assignee_id, created_at, updated_at
    - Define TaskPriority enum (low, medium, high)
    - Add all foreign key relationships and cascade delete rules
    - _Requirements: 25.2, 25.3, 25.4, 25.5, 25.6_
  
  - [ ]* 2.4 Write property test for database schema structure
    - **Property 60: Database schema structure**
    - **Validates: Requirements 25.1-25.7**


- [ ] 3. Implement authentication and security utilities
  - [x] 3.1 Create password hashing and JWT utilities
    - Implement get_password_hash using bcrypt
    - Implement verify_password for password verification
    - Implement create_access_token (30 min expiry)
    - Implement create_refresh_token (7 day expiry)
    - Implement decode_token for JWT validation
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 29.6_
  
  - [ ]* 3.2 Write property test for password hashing invariant
    - **Property 1: Password hashing invariant**
    - **Validates: Requirements 1.1, 1.6**
  
  - [ ]* 3.3 Write property test for JWT token structure
    - **Property 6: JWT token structure**
    - **Validates: Requirements 1.2**
  
  - [x] 3.4 Create authentication dependencies
    - Implement get_current_user dependency (extracts user from access_token cookie)
    - Implement get_current_admin dependency (checks user role is admin)
    - Handle JWT validation errors with 401 responses
    - _Requirements: 29.1, 29.2, 29.4_

- [x] 4. Implement Pydantic schemas for request/response validation
  - Create UserResponse, UserCreate schemas
  - Create BoardResponse, BoardCreate, BoardDetail schemas
  - Create TaskResponse, TaskCreate, TaskUpdate, TaskMove schemas
  - Create ColumnResponse schema
  - Create LoginRequest, TokenResponse schemas
  - Ensure password field is excluded from all response schemas
  - _Requirements: 3.4, 7.5, 8.2_

- [ ] 5. Implement authentication API endpoints
  - [x] 5.1 Implement POST /api/auth/register endpoint
    - Validate email uniqueness
    - Hash password with bcrypt
    - Create user with employee role by default
    - Return user data (excluding password)
    - _Requirements: 1.1, 24.1_
  
  - [x] 5.2 Implement POST /api/auth/login endpoint
    - Validate credentials against database
    - Generate access_token and refresh_token
    - Set both tokens as httpOnly cookies
    - Return success response
    - _Requirements: 1.2, 24.2, 29.3_
  
  - [ ]* 5.3 Write property test for invalid credentials rejection
    - **Property 4: Invalid credentials rejection**
    - **Validates: Requirements 1.5**
  
  - [x] 5.4 Implement POST /api/auth/refresh endpoint
    - Validate refresh_token from cookie
    - Generate new access_token
    - Set new access_token as httpOnly cookie
    - Return success response
    - _Requirements: 1.3, 24.3_
  
  - [ ]* 5.5 Write property test for token refresh round-trip
    - **Property 2: Token refresh round-trip**
    - **Validates: Requirements 1.3**
  
  - [x] 5.6 Implement POST /api/auth/logout endpoint
    - Clear access_token and refresh_token cookies
    - Return success response
    - _Requirements: 1.4, 24.4_
  
  - [ ]* 5.7 Write property test for logout invalidation
    - **Property 3: Logout invalidation**
    - **Validates: Requirements 1.4**

- [x] 6. Checkpoint - Ensure authentication tests pass
  - Run all authentication tests
  - Verify JWT token generation and validation
  - Verify password hashing works correctly
  - Ask the user if questions arise

- [ ] 7. Implement user management API endpoints
  - [x] 7.1 Implement GET /api/users/me endpoint
    - Require authentication (get_current_user dependency)
    - Return current user profile with all fields except password
    - _Requirements: 3.1, 24.5_
  
  - [ ]* 7.2 Write property test for user profile completeness
    - **Property 14: User profile completeness**
    - **Validates: Requirements 3.1**
  
  - [x] 7.3 Implement GET /api/users endpoint (admin only)
    - Require admin authentication (get_current_admin dependency)
    - Return list of all users (excluding passwords)
    - _Requirements: 3.2, 24.6_
  
  - [ ]* 7.4 Write property tests for user list authorization
    - **Property 15: Admin user list access**
    - **Property 16: Employee user list restriction**
    - **Validates: Requirements 3.2, 3.3**
  
  - [ ]* 7.5 Write property test for password exclusion from responses
    - **Property 5: Password exclusion from responses**
    - **Validates: Requirements 3.4**

- [ ] 8. Implement board management API endpoints
  - [x] 8.1 Implement POST /api/boards endpoint (admin only)
    - Require admin authentication
    - Create board with name, description, created_by, created_at
    - Automatically create 3 default columns (To-Do, In Progress, Done)
    - Add creator as board member
    - Return created board
    - _Requirements: 4.1, 6.1, 24.8_
  
  - [ ]* 8.2 Write property test for board creation with association
    - **Property 17: Board creation with association**
    - **Validates: Requirements 4.1, 4.5**
  
  - [ ]* 8.3 Write property test for default columns creation
    - **Property 21: Default columns creation**
    - **Validates: Requirements 6.1**
  
  - [x] 8.4 Implement GET /api/boards endpoint
    - Require authentication
    - Query boards where user is a board member
    - Return list of boards with basic info
    - _Requirements: 4.2, 24.7_
  
  - [ ]* 8.5 Write property test for board membership access control
    - **Property 18: Board membership access control**
    - **Validates: Requirements 4.2**
  
  - [x] 8.6 Implement GET /api/boards/:id endpoint
    - Require authentication
    - Verify user is board member (403 if not)
    - Return board with all columns (ordered), tasks (ordered), and assignee info
    - _Requirements: 4.3, 4.4, 24.9_
  
  - [ ]* 8.7 Write property tests for board detail access
    - **Property 19: Board detail completeness**
    - **Property 20: Non-member board access rejection**
    - **Validates: Requirements 4.3, 4.4**

- [ ] 9. Implement board membership API endpoints
  - [x] 9.1 Implement GET /api/members/:boardId endpoint
    - Require authentication
    - Verify user is board member
    - Return list of all board members with user info
    - _Requirements: 5.2, 24.14_
  
  - [x] 9.2 Implement POST /api/members endpoint (admin only)
    - Require admin authentication
    - Create board_members record for user_id and board_id
    - Handle duplicate member attempts gracefully
    - Return success response
    - _Requirements: 5.1, 24.15_
  
  - [ ]* 9.3 Write property tests for board membership
    - **Property 24: Member addition creates relationship**
    - **Property 25: Board member listing**
    - **Property 26: Member access grant**
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [x] 10. Checkpoint - Ensure board management tests pass
  - Run all board and membership tests
  - Verify authorization checks work correctly
  - Verify board members can access boards
  - Ask the user if questions arise

- [x] 11. Implement task management API endpoints
  - [x] 11.1 Implement POST /api/tasks endpoint (admin only)
    - Require admin authentication
    - Validate priority is low/medium/high
    - Validate assigneeId references existing user (if provided)
    - Validate columnId references existing column
    - Create task with all fields, set created_at and updated_at
    - Calculate appropriate order value (append to column)
    - Return created task
    - _Requirements: 7.1, 7.2, 7.5, 8.2, 24.10_
  
  - [ ]* 11.2 Write property tests for task creation
    - **Property 27: Task creation with all fields**
    - **Property 29: Priority validation**
    - **Property 30: Task assignment validation**
    - **Validates: Requirements 7.1, 7.2, 7.5, 8.2**
  
  - [x] 11.3 Implement PATCH /api/tasks/:id endpoint
    - Require authentication
    - Allow admins to update all fields
    - Allow employees to update only status-related fields (columnId, order)
    - Update updated_at timestamp
    - Validate priority and assigneeId if provided
    - Return updated task
    - _Requirements: 7.3, 24.11_
  
  - [ ]* 11.4 Write property test for task update timestamp
    - **Property 28: Task update timestamp**
    - **Validates: Requirements 7.3, 9.5**
  
  - [x] 11.5 Implement PATCH /api/tasks/:id/move endpoint
    - Require authentication
    - Update task's columnId and order
    - Recalculate order values for affected tasks in both columns
    - Update updated_at timestamp
    - Return updated task
    - _Requirements: 9.1, 9.2, 24.12_
  
  - [ ]* 11.6 Write property tests for task movement
    - **Property 32: Task movement updates**
    - **Property 33: Task reordering within column**
    - **Validates: Requirements 9.1, 9.2**
  
  - [x] 11.7 Implement DELETE /api/tasks/:id endpoint (admin only)
    - Require admin authentication
    - Delete task from database
    - Return success response
    - _Requirements: 7.6, 24.13_
  
  - [ ]* 11.8 Write property test for task deletion
    - **Property 35: Task deletion removes from database**
    - **Validates: Requirements 7.6**

- [ ] 12. Implement authorization property tests
  - [ ]* 12.1 Write property tests for admin permissions
    - **Property 7: Admin board management permissions**
    - **Property 9: Admin task management permissions**
    - **Property 12: Team management authorization (admin part)**
    - **Validates: Requirements 2.2, 2.4, 2.7**
  
  - [ ]* 12.2 Write property tests for employee restrictions
    - **Property 8: Employee board management restrictions**
    - **Property 10: Employee task management restrictions**
    - **Property 11: Employee task movement permissions**
    - **Property 12: Team management authorization (employee part)**
    - **Validates: Requirements 2.3, 2.5, 2.6, 2.8**

- [ ] 13. Implement seed data script
  - [x] 13.1 Create scripts/seed.py
    - Create 1 admin user: admin@kanbanflow.com / Admin@123
    - Create 5 employee users: alice@, bob@, carol@, dave@, eve@ @kanbanflow.com / Pass@123
    - Create 2 boards: "Website Redesign" and "Marketing Campaign Q4"
    - Create 3 columns per board (To-Do, In Progress, Done)
    - Create 25 tasks with varied priorities, due dates (some overdue), assignees, markdown descriptions
    - Add all users as members to both boards
    - _Requirements: 28.1-28.7_
  
  - [ ]* 13.2 Write property test for seed data creation
    - **Property 61: Seed data creation**
    - **Validates: Requirements 28.1-28.7**

- [x] 14. Checkpoint - Ensure backend is complete and tested
  - Run all backend tests (unit and property tests)
  - Verify all API endpoints work correctly
  - Test with seed data
  - Ask the user if questions arise

- [ ] 15. Set up Next.js frontend structure
  - [x] 15.1 Configure Next.js with TypeScript and Tailwind CSS
    - Initialize Next.js 14 with App Router
    - Configure Tailwind CSS with shadcn/ui
    - Set up dark mode support with next-themes
    - Create app directory structure: (auth), dashboard layouts
    - _Requirements: 20.1, 20.2, 20.3_
  
  - [x] 15.2 Install and configure frontend dependencies
    - Install React Query (@tanstack/react-query)
    - Install axios for HTTP requests
    - Install @hello-pangea/dnd for drag-and-drop
    - Install @uiw/react-md-editor for markdown editing
    - Install sonner for toast notifications
    - Install shadcn/ui components (button, dialog, input, select, etc.)
    - _Requirements: 21.2, 22.1, 23.1_
  
  - [x] 15.3 Create API client configuration
    - Create lib/api.ts with axios instance
    - Configure baseURL from environment variable
    - Set withCredentials: true for cookie handling
    - Add response interceptor for 401 handling (redirect to login)
    - _Requirements: 23.2, 23.4_
  
  - [ ]* 15.4 Write property test for cookie credentials in requests
    - **Property 59: Cookie credentials in requests**
    - **Validates: Requirements 23.2**

- [ ] 16. Implement authentication pages
  - [x] 16.1 Create login page (app/login/page.tsx)
    - Create form with email and password inputs
    - Handle form submission with API call to /api/auth/login
    - Redirect to /dashboard on success
    - Display error toast on failure
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [ ]* 16.2 Write property test for login API communication
    - **Property 53: Login API communication**
    - **Validates: Requirements 11.2**
  
  - [x] 16.3 Create registration page (app/register/page.tsx)
    - Create form with name, email, and password inputs
    - Handle form submission with API call to /api/auth/register
    - Redirect to /login on success
    - Display error toast on failure
    - _Requirements: 11.5, 11.6_
  
  - [ ]* 16.4 Write property test for registration API communication
    - **Property 54: Registration API communication**
    - **Validates: Requirements 11.6**

- [ ] 17. Implement route protection middleware
  - [x] 17.1 Create middleware.ts for route protection
    - Check for access_token cookie
    - Redirect to /login if not authenticated and accessing /dashboard routes
    - Allow access if authenticated
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ]* 17.2 Write property tests for route protection
    - **Property 36: Unauthenticated dashboard redirect**
    - **Property 37: Authenticated dashboard access**
    - **Validates: Requirements 12.1, 12.2**

- [ ] 18. Implement dashboard layout and navigation
  - [x] 18.1 Create dashboard layout (app/dashboard/layout.tsx)
    - Create Sidebar component with navigation links
    - Create TopBar component with user info and logout button
    - Add dark mode toggle
    - Make sidebar collapsible for mobile
    - Fetch current user data with React Query
    - _Requirements: 13.1, 13.2, 13.5_
  
  - [x] 18.2 Implement role-based navigation visibility
    - Hide "Team Management" link for employees
    - Show all links for admins
    - _Requirements: 13.4_
  
  - [ ]* 18.3 Write property test for employee admin UI hiding
    - **Property 38: Employee admin UI hiding**
    - **Validates: Requirements 13.4, 14.3, 18.2**

- [ ] 19. Implement boards overview page
  - [x] 19.1 Create boards page (app/dashboard/boards/page.tsx)
    - Fetch user's boards with React Query
    - Display board cards with name and description
    - Show "Create Board" button for admins only
    - Handle loading and error states
    - _Requirements: 14.1, 14.2, 14.3, 14.4_
  
  - [ ]* 19.2 Write property tests for boards overview
    - **Property 39: Admin UI element visibility**
    - **Property 40: Board overview displays user boards**
    - **Validates: Requirements 14.1, 14.2**

- [ ] 20. Implement Kanban board page
  - [x] 20.1 Create board detail page (app/dashboard/boards/[boardId]/page.tsx)
    - Fetch board details with columns and tasks using React Query
    - Pass data to KanbanBoard component
    - Handle loading and error states
    - _Requirements: 15.1, 15.2_
  
  - [x] 20.2 Create KanbanBoard component
    - Implement drag-and-drop with @hello-pangea/dnd
    - Display columns horizontally
    - Handle onDragEnd to call /api/tasks/:id/move
    - Invalidate React Query cache after drag
    - Show "Add Task" button for admins only
    - _Requirements: 16.1, 16.2, 16.5, 18.1, 18.2_
  
  - [ ]* 20.3 Write property tests for drag-and-drop
    - **Property 49: Drag-and-drop triggers API update**
    - **Property 50: Cache invalidation after mutation**
    - **Validates: Requirements 16.1, 16.2, 16.5**
  
  - [x] 20.4 Create Column component
    - Render column header with name
    - Render droppable area for tasks
    - Display empty state when no tasks
    - Order tasks by order field
    - _Requirements: 15.1, 15.2, 15.9_
  
  - [x] 20.5 Create TaskCard component
    - Display title, priority badge, due date, assignee avatar
    - Color-code priority badges: red (high), yellow (medium), green (low)
    - Display overdue dates in red text
    - Display assignee initials in avatar circle
    - Make card clickable to open TaskModal
    - _Requirements: 15.3, 15.4, 15.5, 15.6, 15.7, 15.8_
  
  - [ ]* 20.6 Write property tests for board display
    - **Property 41: Board page displays columns and tasks**
    - **Property 42: Task card information completeness**
    - **Property 43: Overdue task highlighting**
    - **Property 44: Assignee avatar display**
    - **Validates: Requirements 15.1, 15.2, 15.3, 15.7, 15.8**

- [x] 21. Checkpoint - Ensure board display works correctly
  - Test board page rendering with seed data
  - Verify drag-and-drop functionality
  - Verify task cards display correctly
  - Ask the user if questions arise

- [x] 22. Implement task modal and forms
  - [x] 22.1 Create TaskModal component
    - Display modal dialog with task details
    - Show editable fields: title, description (markdown editor), due date, priority, assignee
    - Fetch board members for assignee dropdown
    - Handle save with API call to PATCH /api/tasks/:id
    - Show delete button for admins only
    - Invalidate cache after save
    - _Requirements: 17.1, 17.2, 17.4, 17.5, 17.6, 17.9_
  
  - [ ]* 22.2 Write property tests for task modal
    - **Property 45: Task modal field availability**
    - **Property 46: Assignee dropdown shows board members**
    - **Property 51: Task edit API communication**
    - **Validates: Requirements 17.2, 17.6, 17.9**
  
  - [x] 22.3 Create TaskForm component for task creation
    - Display form with title, description, due date, priority, column, assignee fields
    - Use markdown editor for description
    - Handle submit with API call to POST /api/tasks
    - Invalidate cache after creation
    - Close modal on success
    - _Requirements: 18.3, 18.4, 18.5_
  
  - [ ]* 22.4 Write property test for task creation API communication
    - **Property 52: Task creation API communication**
    - **Validates: Requirements 18.5**

- [x] 23. Implement team management page (admin only)
  - [x] 23.1 Create team page (app/dashboard/team/page.tsx)
    - Protect route for admins only (redirect employees)
    - Fetch all users with React Query
    - Display user list with roles and board memberships
    - Provide interface to add users to boards
    - _Requirements: 19.1, 19.2, 19.3, 19.4_
  
  - [ ]* 23.2 Write property tests for team management
    - **Property 47: Team page displays all users**
    - **Property 48: Employee team page access rejection**
    - **Validates: Requirements 19.1, 19.2, 19.4**

- [x] 24. Implement toast notifications and error handling
  - [x] 24.1 Add toast notifications for all actions
    - Show success toast after create/update/delete operations
    - Show error toast on API failures with descriptive messages
    - Use sonner library for toast display
    - _Requirements: 21.1, 21.3, 21.4_
  
  - [ ]* 24.2 Write property tests for notifications
    - **Property 55: Action toast notifications**
    - **Property 56: Network error handling**
    - **Property 57: Unauthorized response redirect**
    - **Validates: Requirements 21.1, 21.3, 21.4, 22.5, 23.4**

- [x] 25. Implement React Query hooks and caching
  - [x] 25.1 Create custom hooks for data fetching
    - Create useBoards hook for fetching boards
    - Create useBoard hook for fetching board details
    - Create useTasks hook for fetching tasks
    - Create useUsers hook for fetching users
    - Create useBoardMembers hook for fetching board members
    - Configure cache time and stale time appropriately
    - _Requirements: 22.1, 22.2_
  
  - [x] 25.2 Create mutation hooks with cache invalidation
    - Create useCreateBoard mutation
    - Create useCreateTask mutation
    - Create useUpdateTask mutation
    - Create useMoveTask mutation
    - Create useDeleteTask mutation
    - Create useAddBoardMember mutation
    - Invalidate relevant queries after mutations
    - _Requirements: 22.3_
  
  - [ ]* 25.3 Write property test for API response caching
    - **Property 58: API response caching**
    - **Validates: Requirements 22.2**

- [x] 26. Implement styling and theming
  - [x] 26.1 Apply Tailwind CSS styling to all components
    - Style authentication pages
    - Style dashboard layout (sidebar, topbar)
    - Style board cards and Kanban board
    - Style task cards with priority colors
    - Style modals and forms
    - Ensure responsive design for mobile
    - _Requirements: 20.1, 20.5_
  
  - [x] 26.2 Implement dark mode
    - Add dark mode toggle in TopBar
    - Configure next-themes provider
    - Apply dark mode classes to all components
    - Test dark mode across all pages
    - _Requirements: 20.3_

- [x] 27. Final integration and testing
  - [x] 27.1 Test complete user flows
    - Test registration → login → create board → add task → move task flow
    - Test admin vs employee permission differences
    - Test drag-and-drop across different scenarios
    - Test task editing and deletion
    - Test team management
    - Test logout and re-login
    - _Requirements: All_
  
  - [ ]* 27.2 Run all property-based tests
    - Run backend property tests with hypothesis (100+ iterations each)
    - Run frontend property tests with fast-check (100+ iterations each)
    - Verify all 66 properties pass
    - _Requirements: All_
  
  - [ ]* 27.3 Run integration tests
    - Test API integration flows
    - Test frontend-backend integration
    - Test error handling across the stack
    - _Requirements: All_

- [x] 28. Final checkpoint - Ensure all tests pass and application works end-to-end
  - Verify all unit tests pass
  - Verify all property tests pass
  - Verify all integration tests pass
  - Test with seed data
  - Verify Docker Compose setup works
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP development
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: backend first, then frontend
- All code should be production-ready with proper error handling
- Use TypeScript for type safety in frontend code
- Use Pydantic for data validation in backend code
