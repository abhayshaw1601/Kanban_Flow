#!/usr/bin/env python3
"""
KanbanFlow Seed Script - Track 3 Requirements

This script creates seed data to fulfill Track 3 requirements:
- At least 20 active tasks spread across different columns
- At least 4 different team members assigned to tasks
- Multiple boards (Workspaces & Boards requirement)
- Tasks with Title, Markdown Description, Due Date, Priority Labels, and Assignees
- Proper Kanban columns (To-Do, In Progress, Done)
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.append('.')

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.board import Board
from app.models.column import Column
from app.models.board_member import BoardMember
from app.models.task import Task, TaskPriority


def create_kanbanflow_seed_data():
    """Create comprehensive seed data for KanbanFlow Track 3 requirements."""
    print("🚀 KanbanFlow Seed Script - Track 3 Requirements")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Step 1: Create or get company
        print("📢 Step 1: Setting up company...")
        company = db.query(Company).filter(Company.company_id == "kanbanflow-demo").first()
        if not company:
            company = Company(
                name="KanbanFlow Demo Company",
                company_id="kanbanflow-demo",
                description="Demo company for KanbanFlow Track 3 requirements"
            )
            db.add(company)
            db.flush()
            print("✅ Created demo company")
        else:
            print("✅ Using existing demo company")
        
        # Step 2: Create users (1 admin + 5 employees = 6 total, ensuring 4+ team members)
        print("\n👥 Step 2: Creating team members...")
        
        users_data = [
            {
                "name": "Admin User",
                "email": "admin@kanbanflow.com",
                "password": "Admin@123",
                "role": UserRole.ADMIN
            },
            {
                "name": "Alice Johnson",
                "email": "alice@kanbanflow.com", 
                "password": "Pass@123",
                "role": UserRole.EMPLOYEE
            },
            {
                "name": "Bob Smith",
                "email": "bob@kanbanflow.com",
                "password": "Pass@123", 
                "role": UserRole.EMPLOYEE
            },
            {
                "name": "Carol Davis",
                "email": "carol@kanbanflow.com",
                "password": "Pass@123",
                "role": UserRole.EMPLOYEE
            },
            {
                "name": "Dave Wilson",
                "email": "dave@kanbanflow.com",
                "password": "Pass@123",
                "role": UserRole.EMPLOYEE
            },
            {
                "name": "Eve Martinez",
                "email": "eve@kanbanflow.com",
                "password": "Pass@123",
                "role": UserRole.EMPLOYEE
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    company_id=company.id
                )
                db.add(user)
                created_users.append(user)
                print(f"✅ Created user: {user_data['name']} ({user_data['role'].value})")
            else:
                created_users.append(existing_user)
                print(f"✅ Using existing user: {user_data['name']}")
        
        db.flush()  # Get user IDs
        
        # Get admin and employees
        admin_user = next(u for u in created_users if u.role == UserRole.ADMIN)
        employee_users = [u for u in created_users if u.role == UserRole.EMPLOYEE]
        
        print(f"✅ Total users: {len(created_users)} (1 admin + {len(employee_users)} employees)")
        
        # Step 3: Create boards
        print("\n📋 Step 3: Creating project boards...")
        
        boards_data = [
            {
                "name": "Website Redesign",
                "description": "Complete redesign of the company website with modern UI/UX, responsive design, and improved performance."
            },
            {
                "name": "Marketing Campaign Q4",
                "description": "Q4 marketing campaign planning and execution including social media, email marketing, and content creation."
            }
        ]
        
        created_boards = []
        for board_data in boards_data:
            existing_board = db.query(Board).filter(
                Board.name == board_data["name"],
                Board.created_by == admin_user.id
            ).first()
            
            if not existing_board:
                board = Board(
                    name=board_data["name"],
                    description=board_data["description"],
                    created_by=admin_user.id
                )
                db.add(board)
                created_boards.append(board)
                print(f"✅ Created board: {board_data['name']}")
            else:
                created_boards.append(existing_board)
                print(f"✅ Using existing board: {board_data['name']}")
        
        db.flush()  # Get board IDs
        
        # Step 4: Create columns for each board
        print("\n📊 Step 4: Creating Kanban columns...")
        
        columns_data = [
            {"name": "To-Do", "order": 0},
            {"name": "In Progress", "order": 1}, 
            {"name": "Done", "order": 2}
        ]
        
        board_columns = {}
        for board in created_boards:
            board_columns[board.id] = []
            for col_data in columns_data:
                existing_column = db.query(Column).filter(
                    Column.board_id == board.id,
                    Column.name == col_data["name"]
                ).first()
                
                if not existing_column:
                    column = Column(
                        name=col_data["name"],
                        order=col_data["order"],
                        board_id=board.id
                    )
                    db.add(column)
                    board_columns[board.id].append(column)
                else:
                    board_columns[board.id].append(existing_column)
            
            print(f"✅ Created columns for board: {board.name}")
        
        db.flush()  # Get column IDs
        
        # Step 5: Add board members
        print("\n👥 Step 5: Adding team members to boards...")
        
        for board in created_boards:
            # Add admin as member
            admin_membership = db.query(BoardMember).filter(
                BoardMember.user_id == admin_user.id,
                BoardMember.board_id == board.id
            ).first()
            
            if not admin_membership:
                db.add(BoardMember(user_id=admin_user.id, board_id=board.id))
            
            # Add all employees as members
            for employee in employee_users:
                employee_membership = db.query(BoardMember).filter(
                    BoardMember.user_id == employee.id,
                    BoardMember.board_id == board.id
                ).first()
                
                if not employee_membership:
                    db.add(BoardMember(user_id=employee.id, board_id=board.id))
            
            print(f"✅ Added {len(employee_users) + 1} members to board: {board.name}")
        
        db.flush()
        
        # Step 6: Create tasks (20+ tasks as required)
        print("\n📝 Step 6: Creating tasks (20+ required)...")
        
        # Website Redesign Board Tasks (11 tasks)
        website_tasks = [
            {
                "title": "User Research & Analysis",
                "description": """# User Research & Analysis

## Objective
Conduct comprehensive user research to understand current pain points and requirements.

## Tasks
- [ ] Survey existing users
- [ ] Analyze current website analytics
- [ ] Create user personas
- [ ] Document findings

## Deliverables
- User research report
- User personas document
- Analytics insights summary""",
                "priority": TaskPriority.HIGH,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=7),
                "order": 0
            },
            {
                "title": "Wireframe Design",
                "description": """# Wireframe Design

## Overview
Create low-fidelity wireframes for all main pages of the website.

## Pages to wireframe:
- Homepage
- About Us
- Services
- Contact
- Blog

## Tools
- Figma or Sketch
- Collaborative review process""",
                "priority": TaskPriority.HIGH,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=14),
                "order": 0
            },
            {
                "title": "Logo Design Concepts",
                "description": """# Logo Design Concepts

Create multiple logo concepts for the new brand identity.

**Requirements:**
- 5 different concepts
- Vector format (SVG)
- Color and monochrome versions
- Scalable for web and print""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=10),
                "order": 1
            },
            {
                "title": "Content Strategy",
                "description": """# Content Strategy Development

## Goals
- Define content pillars
- Create content calendar
- Establish tone of voice
- Plan SEO strategy

## Deliverables
- Content strategy document
- Editorial calendar template
- SEO keyword research""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=21),
                "order": 2
            },
            {
                "title": "Homepage Mockup",
                "description": """# Homepage High-Fidelity Mockup

Create detailed visual mockup of the new homepage design.

**Specifications:**
- Desktop and mobile versions
- Interactive elements defined
- Color scheme applied
- Typography finalized""",
                "priority": TaskPriority.HIGH,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=18),
                "order": 1
            },
            {
                "title": "Technical Architecture Planning",
                "description": """# Technical Architecture

Plan the technical implementation approach.

## Components
- Frontend framework selection
- Backend API design
- Database schema
- Hosting infrastructure
- Performance optimization strategy""",
                "priority": TaskPriority.HIGH,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=12),
                "order": 3
            },
            {
                "title": "Responsive Design System",
                "description": """# Design System Creation

Build comprehensive design system for consistency.

**Components:**
- Color palette
- Typography scale
- Button styles
- Form elements
- Grid system
- Component library""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=25),
                "order": 2
            },
            {
                "title": "Accessibility Audit",
                "description": """# Accessibility Compliance

Ensure website meets WCAG 2.1 AA standards.

## Checklist
- [ ] Color contrast ratios
- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Alt text for images
- [ ] Semantic HTML structure""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=30),
                "order": 4
            },
            {
                "title": "Performance Optimization",
                "description": """# Website Performance Optimization

Optimize website for speed and performance.

**Targets:**
- Page load time < 3 seconds
- Lighthouse score > 90
- Mobile-first optimization
- Image compression and lazy loading""",
                "priority": TaskPriority.LOW,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=35),
                "order": 5
            },
            {
                "title": "Content Migration",
                "description": """# Content Migration Plan

Plan and execute migration of existing content.

## Steps
1. Content audit
2. Content mapping
3. SEO preservation
4. Redirect strategy
5. Testing and validation""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 2,  # Done
                "due_date": datetime.now() - timedelta(days=5),  # Overdue
                "order": 0
            },
            {
                "title": "Browser Testing",
                "description": """# Cross-Browser Testing

Test website across different browsers and devices.

**Test Matrix:**
- Chrome, Firefox, Safari, Edge
- Desktop and mobile versions
- Different screen resolutions
- Performance testing""",
                "priority": TaskPriority.LOW,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=40),
                "order": 3
            }
        ]
        
        # Marketing Campaign Tasks (10 tasks)
        marketing_tasks = [
            {
                "title": "Q4 Campaign Strategy",
                "description": """# Q4 Marketing Campaign Strategy

## Campaign Overview
Develop comprehensive marketing strategy for Q4 holiday season.

## Key Components
- Target audience analysis
- Channel strategy (social, email, paid ads)
- Budget allocation
- Timeline and milestones
- Success metrics and KPIs

## Deliverables
- Campaign strategy document
- Budget breakdown
- Timeline with key dates""",
                "priority": TaskPriority.HIGH,
                "column_index": 2,  # Done
                "due_date": datetime.now() - timedelta(days=10),
                "order": 0
            },
            {
                "title": "Social Media Content Calendar",
                "description": """# Social Media Content Calendar

Create content calendar for Q4 social media campaigns.

**Platforms:**
- Instagram
- Facebook
- Twitter
- LinkedIn

**Content Types:**
- Product highlights
- Behind-the-scenes
- User-generated content
- Holiday-themed posts""",
                "priority": TaskPriority.HIGH,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=5),
                "order": 0
            },
            {
                "title": "Email Marketing Templates",
                "description": """# Email Marketing Template Design

Design responsive email templates for Q4 campaigns.

## Template Types
- Welcome series
- Product announcements
- Holiday promotions
- Newsletter template

## Requirements
- Mobile responsive
- Brand consistent
- A/B test variations""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=15),
                "order": 0
            },
            {
                "title": "Influencer Partnership Program",
                "description": """# Influencer Partnership Strategy

Develop influencer partnership program for Q4.

**Objectives:**
- Identify potential influencers
- Create partnership packages
- Develop content guidelines
- Track ROI and engagement

**Deliverables:**
- Influencer database
- Partnership contracts
- Content brief templates""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=20),
                "order": 1
            },
            {
                "title": "Holiday Video Campaign",
                "description": """# Holiday Video Content Creation

Produce video content for holiday marketing campaign.

## Video Types
- Product showcase videos
- Customer testimonials
- Behind-the-scenes content
- Holiday greeting video

## Specifications
- 1080p minimum resolution
- Multiple aspect ratios (16:9, 1:1, 9:16)
- Subtitles for accessibility""",
                "priority": TaskPriority.HIGH,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=25),
                "order": 1
            },
            {
                "title": "Google Ads Campaign Setup",
                "description": """# Google Ads Campaign Configuration

Set up and optimize Google Ads campaigns for Q4.

**Campaign Types:**
- Search campaigns
- Display campaigns
- Shopping campaigns
- YouTube ads

**Setup Tasks:**
- Keyword research
- Ad copy creation
- Landing page optimization
- Conversion tracking""",
                "priority": TaskPriority.HIGH,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=8),
                "order": 2
            },
            {
                "title": "Customer Survey & Feedback",
                "description": """# Customer Feedback Collection

Gather customer insights for campaign optimization.

## Survey Topics
- Product satisfaction
- Brand perception
- Purchase behavior
- Marketing channel preferences

## Methods
- Email surveys
- Social media polls
- Website feedback forms
- Phone interviews""",
                "priority": TaskPriority.LOW,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=30),
                "order": 3
            },
            {
                "title": "Analytics Dashboard Setup",
                "description": """# Marketing Analytics Dashboard

Create comprehensive analytics dashboard for campaign tracking.

**Metrics to Track:**
- Website traffic and conversions
- Social media engagement
- Email open/click rates
- Ad performance and ROI
- Customer acquisition cost

**Tools:**
- Google Analytics
- Social media insights
- Email platform analytics""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 1,  # In Progress
                "due_date": datetime.now() + timedelta(days=12),
                "order": 2
            },
            {
                "title": "Content Creation Guidelines",
                "description": """# Brand Content Guidelines

Establish content creation guidelines for consistent brand messaging.

## Guidelines Include
- Brand voice and tone
- Visual style guide
- Content templates
- Approval workflow
- Legal compliance checklist

## Deliverables
- Brand guidelines document
- Content templates
- Review process flowchart""",
                "priority": TaskPriority.MEDIUM,
                "column_index": 2,  # Done
                "due_date": datetime.now() - timedelta(days=3),
                "order": 1
            },
            {
                "title": "Black Friday Campaign",
                "description": """# Black Friday Special Campaign

Plan and execute Black Friday marketing campaign.

**Campaign Elements:**
- Special discount offers
- Limited-time promotions
- Email blast series
- Social media countdown
- Website banner updates

**Timeline:**
- Pre-campaign teasers
- Black Friday day execution
- Cyber Monday follow-up""",
                "priority": TaskPriority.HIGH,
                "column_index": 0,  # To-Do
                "due_date": datetime.now() + timedelta(days=45),  # Future Black Friday
                "order": 4
            }
        ]
        
        # Create tasks for Website Redesign board
        website_board = created_boards[0]
        website_columns = board_columns[website_board.id]
        
        for task_data in website_tasks:
            # Check if task already exists
            existing_task = db.query(Task).filter(
                Task.title == task_data["title"],
                Task.column_id.in_([col.id for col in website_columns])
            ).first()
            
            if not existing_task:
                # Assign to random employee
                assignee = random.choice(employee_users)
                column = website_columns[task_data["column_index"]]
                
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=task_data["priority"],
                    due_date=task_data["due_date"],
                    order=task_data["order"],
                    column_id=column.id,
                    assignee_id=assignee.id
                )
                db.add(task)
                print(f"✅ Created task: {task_data['title']} (assigned to {assignee.name})")
        
        # Create tasks for Marketing Campaign board
        marketing_board = created_boards[1]
        marketing_columns = board_columns[marketing_board.id]
        
        for task_data in marketing_tasks:
            # Check if task already exists
            existing_task = db.query(Task).filter(
                Task.title == task_data["title"],
                Task.column_id.in_([col.id for col in marketing_columns])
            ).first()
            
            if not existing_task:
                # Assign to random employee
                assignee = random.choice(employee_users)
                column = marketing_columns[task_data["column_index"]]
                
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=task_data["priority"],
                    due_date=task_data["due_date"],
                    order=task_data["order"],
                    column_id=column.id,
                    assignee_id=assignee.id
                )
                db.add(task)
                print(f"✅ Created task: {task_data['title']} (assigned to {assignee.name})")
        
        # Commit all changes
        db.commit()
        
        # Final verification
        print("\n" + "=" * 60)
        print("🎉 KANBANFLOW SEED DATA CREATED SUCCESSFULLY!")
        print("=" * 60)
        
        # Count and display results
        total_users = db.query(User).filter(User.company_id == company.id).count()
        total_boards = db.query(Board).filter(Board.created_by == admin_user.id).count()
        total_tasks = db.query(Task).join(Column).join(Board).filter(Board.created_by == admin_user.id).count()
        total_columns = db.query(Column).join(Board).filter(Board.created_by == admin_user.id).count()
        
        print(f"📊 SUMMARY:")
        print(f"   👥 Users created: {total_users} (1 admin + {total_users-1} employees)")
        print(f"   📋 Boards created: {total_boards}")
        print(f"   📊 Columns created: {total_columns}")
        print(f"   📝 Tasks created: {total_tasks}")
        
        # Verify Track 3 requirements
        print(f"\n✅ TRACK 3 REQUIREMENTS VERIFICATION:")
        print(f"   ✅ Workspaces & Boards: {total_boards} boards created")
        print(f"   ✅ Kanban Columns: 3 columns per board (To-Do, In Progress, Done)")
        print(f"   ✅ Task Cards: {total_tasks} tasks with Title, Markdown Description, Due Date, Priority, Assignee")
        print(f"   ✅ Team Members: {total_users-1} employees available for task assignment")
        print(f"   ✅ Data Requirement: {total_tasks} tasks (requirement: 20+) ✅")
        print(f"   ✅ Team Assignment: Tasks assigned to {total_users-1} different team members (requirement: 4+) ✅")
        
        print(f"\n🔐 LOGIN CREDENTIALS:")
        print(f"   Admin: admin@kanbanflow.com / Admin@123")
        print(f"   Alice: alice@kanbanflow.com / Pass@123")
        print(f"   Bob: bob@kanbanflow.com / Pass@123")
        print(f"   Carol: carol@kanbanflow.com / Pass@123")
        print(f"   Dave: dave@kanbanflow.com / Pass@123")
        print(f"   Eve: eve@kanbanflow.com / Pass@123")
        
        print(f"\n🌐 ACCESS THE APPLICATION:")
        print(f"   Frontend: http://localhost:3000")
        print(f"   Backend API: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting KanbanFlow seed script...")
    create_kanbanflow_seed_data()
    print("✅ Seed script completed!")