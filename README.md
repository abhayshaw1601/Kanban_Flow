# KanbanFlow - AI-Powered Project Management Platform

A modern, intelligent Kanban-style project management application with advanced AI capabilities, autonomous task management, and comprehensive team collaboration features.

## 🌟 Key Features

###  Core Kanban Functionality
- **Interactive Kanban Boards**: Drag-and-drop task management with customizable columns
- **Multi-Board Support**: Create and manage multiple project boards
- **Team Collaboration**: Add team members to boards with role-based permissions
- **Task Management**: Create, edit, assign, and track tasks with priorities and due dates
- **Real-time Updates**: Live synchronization across all team members

###  AI-Powered Features

#### 1. **AI Task Analyzer**
- **Intelligent Task Breakdown**: Analyze vague prompts and generate structured sub-tasks
- **Acceptance Criteria Generation**: Automatically create detailed acceptance criteria
- **Blocker Identification**: Predict potential blockers with mitigation strategies
- **Confidence Scoring**: AI confidence levels for all generated content
- **Context-Aware Analysis**: Considers board structure and project context

#### 2. **AI Diagram Analyzer**
- **Architecture Analysis**: Upload diagrams and extract system components
- **Automatic Task Generation**: Convert diagrams into actionable development tasks
- **Component Mapping**: Identify services, databases, APIs, and dependencies
- **Project Planning**: Generate development phases and task priorities
- **Effort Estimation**: AI-powered time estimates for each task

#### 3. **Board Diagram Integration**
- **Direct Upload**: Upload diagrams directly to any board
- **Instant Task Creation**: AI-generated tasks appear immediately on the board
- **Rich Task Descriptions**: Detailed descriptions with component context
- **Smart Prioritization**: AI assigns priorities based on architectural importance
- **Ready for Assignment**: Tasks created unassigned, ready for team allocation

###  Autonomous Project Management

#### 4. **The Autonomous Project Manager**
- **Automatic Monitoring**: Continuously monitors task progress and deadlines
- **Smart Reassignment**: Automatically reassigns overdue tasks to high performers
- **AI Nagging System**: Generates passive-aggressive comments for stuck tasks
- **Blocker Detection**: Automatically flags tasks due within 3 days as blockers
- **Performance-Based Logic**: Uses team member performance metrics for decisions

#### 5. **Advanced Analytics & Reporting**
- **Member Performance Tracking**: Color-coded performance indicators (Green >50%, Yellow 30-50%, Red <30%)
- **Detailed Statistics**: Comprehensive analytics on task completion rates
- **Audit Dashboard**: Admin tools for project oversight and management
- **Blocker Management**: Track and manage blocked tasks across all projects
- **Team Insights**: Performance metrics and workload distribution

###  Team Management

#### 6. **Role-Based Access Control**
- **Admin Features**: Full system access, audit tools, AI features, team management
- **Employee Features**: Task management, board access, personal analytics
- **Company Isolation**: Multi-tenant architecture with company-based separation
- **Board Permissions**: Granular access control per board

#### 7. **Notification System**
- **Blocker Notifications**: Aggressive nagging for overdue tasks
- **Reassignment Alerts**: Notifications when tasks are reassigned
- **Performance Feedback**: Encouraging messages for high performers
- **Real-time Updates**: Instant notifications for task changes

###  Advanced Task Features

#### 8. **Smart Task Management**
- **AI Enhancement**: Enhance existing tasks with AI analysis
- **Comment System**: AI-generated and human comments on tasks
- **Blocker Tracking**: Visual indicators and reasons for blocked tasks
- **Due Date Management**: Automatic deadline monitoring and alerts
- **Priority Intelligence**: AI-suggested task priorities

#### 9. **Interactive Dashboards**
- **Personal Dashboard**: Individual task overview and statistics
- **Team Dashboard**: Team performance and workload visualization
- **Admin Dashboard**: System-wide analytics and management tools
- **Board Overview**: Quick access to all boards and recent activity

## 🛠 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping
- **SQLite**: Lightweight database for development
- **Pydantic**: Data validation using Python type annotations
- **Google Gemini AI**: Advanced AI integration for analysis and generation
- **JWT Authentication**: Secure token-based authentication
- **Bcrypt**: Password hashing and security

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **React Query**: Data fetching and state management
- **React DnD**: Drag and drop functionality
- **Lucide Icons**: Beautiful icon library

### AI Integration
- **Gemini AI API**: Google's advanced language model
- **Vision Analysis**: Image processing for diagram analysis
- **Natural Language Processing**: Task analysis and generation
- **Structured Output**: JSON-formatted AI responses
- **Context-Aware Prompting**: Intelligent prompt engineering

##  Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kanbanflow
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Copy environment file and add your Gemini API key
   cp .env.example .env
   # Edit .env and add: GEMINI_API_KEY=your_api_key_here
   
   # Create database and admin user
   python create_companies_tables.py
   python create_admin.py
   
   # Start the backend server
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Copy environment file
   cp .env.example .env.local
   # Edit .env.local if needed
   
   # Start the frontend server
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Credentials
- **Admin**: admin@company.com / admin123
- **Employee**: employee@company.com / employee123

##  Feature Documentation

### AI Features
- [AI Task Analyzer](./AI_TASK_ANALYZER_README.md) - Intelligent task breakdown and analysis
- [Gemini Integration](./GEMINI_AI_TASK_ANALYZER_README.md) - Google Gemini AI integration details
- [Diagram Analyzer](./DIAGRAM_ANALYZER_README.md) - Architecture diagram analysis
- [Board Integration](./BOARD_DIAGRAM_INTEGRATION_README.md) - Diagram-to-tasks workflow

### System Features
- [Integrated AI](./INTEGRATED_AI_README.md) - Complete AI system overview
- [Setup Guide](./SETUP.md) - Detailed installation and configuration
- [Dependencies](./frontend/DEPENDENCIES.md) - Frontend dependencies and versions

##  Usage Examples

### 1. AI Task Analysis
```
Input: "Build a user authentication system"

AI Output:
- Create user registration endpoint
- Implement login functionality  
- Add password hashing
- Set up JWT token management
- Create user profile management
```

### 2. Diagram Analysis
```
Upload: Architecture diagram (PNG/JPEG)

AI Generates:
- 8 system components identified
- 12 connections mapped
- 5 development tasks created
- Priority assignments (High/Medium/Low)
- Effort estimates (1-3 weeks each)
```

### 3. Autonomous Management
```
Scenario: Task overdue by 2 days

AI Actions:
- Generates passive-aggressive comment
- Marks task as blocker
- Reassigns to high-performing team member
- Sends notifications to relevant parties
```

##  API Endpoints

### Core APIs
- `POST /api/auth/login` - User authentication
- `GET /api/boards` - List user boards
- `POST /api/boards` - Create new board
- `GET /api/boards/{id}` - Get board details
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task

### AI APIs
- `POST /ai/analyze` - Analyze task with AI
- `POST /ai/enhance-task/{id}` - Enhance existing task
- `POST /ai/analyze-diagram` - Analyze architecture diagram
- `POST /ai/create-tasks-from-diagram/{board_id}` - Create tasks from diagram
- `GET /ai/health` - Check AI service status

### Admin APIs
- `POST /api/audit/run` - Run project audit
- `GET /api/audit/pending` - Get pending projects
- `POST /api/audit/clear-blockers` - Clear all blockers
- `GET /api/analytics/member/{id}` - Get member statistics

##  Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Feature Tests
```bash
# Test AI integration
python test_ai_auth.py

# Test autonomous manager
python test_autonomous_manager.py

# Test diagram analyzer
python demo_diagram_analyzer.py

# Test complete workflow
python test_diagram_to_tasks.py
```

### Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```

##  Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Admin and employee role separation
- **Company Isolation**: Multi-tenant data separation
- **Input Validation**: Comprehensive input sanitization
- **File Upload Security**: Image type and size validation
- **API Rate Limiting**: Protection against abuse
- **Password Security**: Bcrypt hashing with salt

##  Performance Features

- **Real-time Updates**: WebSocket-like real-time synchronization
- **Optimistic Updates**: Immediate UI feedback
- **Caching Strategy**: React Query for efficient data management
- **Lazy Loading**: Component and route-based code splitting
- **Database Optimization**: Efficient queries and indexing
- **AI Response Caching**: Reduced API calls for similar requests

##  Deployment

### Production Setup
1. **Environment Configuration**
   - Set production environment variables
   - Configure database connection
   - Set up SSL certificates

2. **Backend Deployment**
   ```bash
   # Using Docker
   docker build -t kanbanflow-backend ./backend
   docker run -p 8000:8000 kanbanflow-backend
   ```

3. **Frontend Deployment**
   ```bash
   # Build for production
   npm run build
   npm start
   ```

### Environment Variables
```env
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./kanban.db
SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:3000

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices
- Write comprehensive tests
- Document new features
- Follow existing code style
- Update README for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google Gemini AI** - Advanced AI capabilities
- **Radix UI** - Accessible component primitives
- **Tailwind CSS** - Utility-first CSS framework
- **FastAPI** - Modern Python web framework
- **Next.js** - React production framework


### Recent Updates
- ✅ AI Diagram Analyzer
- ✅ Board Diagram Integration  
- ✅ Autonomous Project Manager
- ✅ Advanced Analytics Dashboard
- ✅ Performance Tracking System
- ✅ Notification System
- ✅ Comment System with AI Integration

---

**KanbanFlow** - Transforming project management with AI-powered intelligence and autonomous task management.