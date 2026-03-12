"""
Seed script to populate the database with realistic test data.

This script creates:
- 1 admin user: admin@kanbanflow.com / Admin@123
- 5 employee users: alice@, bob@, carol@, dave@, eve@ @kanbanflow.com / Pass@123
- 2 boards: "Website Redesign" and "Marketing Campaign Q4"
- 3 columns per board (To-Do, In Progress, Done)
- 25 tasks with varied priorities, due dates (some overdue), assignees, and Markdown descriptions
- All users as members of both boards

Usage:
    python -m scripts.seed
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models import User, UserRole, Board, BoardMember, Column, Task, TaskPriority, Company


def create_companies(db: Session) -> dict:
    """Create sample companies."""
    print("Creating companies...")
    
    companies_data = [
        ("TechCorp Solutions", "techcorp", "Leading technology solutions provider"),
        ("Creative Agency", "creative-agency", "Full-service digital marketing agency"),
        ("StartupHub", "startup-hub", "Innovation and startup incubator"),
    ]
    
    companies = {}
    for name, company_id, description in companies_data:
        company = Company(
            name=name,
            company_id=company_id,
            description=description
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        companies[company_id] = company
    
    print(f"✓ Created {len(companies)} companies")
    return companies


def create_users(db: Session, companies: dict) -> dict:
    """Create admin and employee users for different companies."""
    print("Creating users...")
    
    # TechCorp users
    techcorp_admin = User(
        name="Admin User",
        email="admin@kanbanflow.com",
        password=get_password_hash("Admin@123"),
        role=UserRole.ADMIN,
        company_id=companies["techcorp"].id,
        avatar=None
    )
    db.add(techcorp_admin)
    
    techcorp_employees = []
    techcorp_employee_data = [
        ("Alice Johnson", "alice@kanbanflow.com"),
        ("Bob Smith", "bob@kanbanflow.com"),
        ("Carol Williams", "carol@kanbanflow.com"),
    ]
    
    for name, email in techcorp_employee_data:
        employee = User(
            name=name,
            email=email,
            password=get_password_hash("Pass@123"),
            role=UserRole.EMPLOYEE,
            company_id=companies["techcorp"].id,
            avatar=None
        )
        db.add(employee)
        techcorp_employees.append(employee)
    
    # Creative Agency users
    creative_admin = User(
        name="Creative Admin",
        email="admin@creative.com",
        password=get_password_hash("Admin@123"),
        role=UserRole.ADMIN,
        company_id=companies["creative-agency"].id,
        avatar=None
    )
    db.add(creative_admin)
    
    creative_employees = []
    creative_employee_data = [
        ("Dave Brown", "dave@creative.com"),
        ("Eve Davis", "eve@creative.com"),
    ]
    
    for name, email in creative_employee_data:
        employee = User(
            name=name,
            email=email,
            password=get_password_hash("Pass@123"),
            role=UserRole.EMPLOYEE,
            company_id=companies["creative-agency"].id,
            avatar=None
        )
        db.add(employee)
        creative_employees.append(employee)
    
    db.commit()
    
    # Refresh to get IDs
    db.refresh(techcorp_admin)
    for emp in techcorp_employees:
        db.refresh(emp)
    db.refresh(creative_admin)
    for emp in creative_employees:
        db.refresh(emp)
    
    print(f"✓ Created users for {len(companies)} companies")
    
    return {
        "techcorp": {
            "admin": techcorp_admin,
            "employees": techcorp_employees,
            "all_users": [techcorp_admin] + techcorp_employees
        },
        "creative": {
            "admin": creative_admin,
            "employees": creative_employees,
            "all_users": [creative_admin] + creative_employees
        }
    }


def create_boards(db: Session, users_dict: dict) -> dict:
    """Create boards with columns for each company."""
    print("Creating boards...")
    
    # TechCorp boards
    techcorp_boards_data = [
        ("Website Redesign", "Complete redesign of company website with modern UI/UX"),
        ("Mobile App Development", "Native mobile app for iOS and Android")
    ]
    
    techcorp_boards = []
    for name, description in techcorp_boards_data:
        board = Board(
            name=name,
            description=description,
            created_by=users_dict["techcorp"]["admin"].id
        )
        db.add(board)
        db.commit()
        db.refresh(board)
        
        # Create default columns for each board
        columns_data = [
            ("To-Do", 0),
            ("In Progress", 1),
            ("Done", 2)
        ]
        
        for col_name, order in columns_data:
            column = Column(
                name=col_name,
                order=order,
                board_id=board.id
            )
            db.add(column)
        
        db.commit()
        techcorp_boards.append(board)
    
    # Creative Agency boards
    creative_boards_data = [
        ("Marketing Campaign Q4", "Q4 marketing initiatives and campaign planning"),
    ]
    
    creative_boards = []
    for name, description in creative_boards_data:
        board = Board(
            name=name,
            description=description,
            created_by=users_dict["creative"]["admin"].id
        )
        db.add(board)
        db.commit()
        db.refresh(board)
        
        # Create default columns for each board
        columns_data = [
            ("To-Do", 0),
            ("In Progress", 1),
            ("Done", 2)
        ]
        
        for col_name, order in columns_data:
            column = Column(
                name=col_name,
                order=order,
                board_id=board.id
            )
            db.add(column)
        
        db.commit()
        creative_boards.append(board)
    
    print(f"✓ Created boards for different companies")
    return {
        "techcorp": techcorp_boards,
        "creative": creative_boards
    }


def add_board_members(db: Session, boards_dict: dict, users_dict: dict):
    """Add users as members to their company boards."""
    print("Adding board members...")
    
    member_count = 0
    
    # Add TechCorp users to TechCorp boards
    for board in boards_dict["techcorp"]:
        for user in users_dict["techcorp"]["all_users"]:
            member = BoardMember(
                user_id=user.id,
                board_id=board.id
            )
            db.add(member)
            member_count += 1
    
    # Add Creative Agency users to Creative Agency boards
    for board in boards_dict["creative"]:
        for user in users_dict["creative"]["all_users"]:
            member = BoardMember(
                user_id=user.id,
                board_id=board.id
            )
            db.add(member)
            member_count += 1
    
    db.commit()
    print(f"✓ Added {member_count} board memberships")


def create_tasks(db: Session, boards_dict: dict, users_dict: dict):
    """Create tasks for each company's boards."""
    print("Creating tasks...")
    
    # Get columns for TechCorp boards
    techcorp_board1_columns = db.query(Column).filter(Column.board_id == boards_dict["techcorp"][0].id).order_by(Column.order).all()
    techcorp_board2_columns = db.query(Column).filter(Column.board_id == boards_dict["techcorp"][1].id).order_by(Column.order).all()
    
    # Get columns for Creative Agency boards
    creative_board1_columns = db.query(Column).filter(Column.board_id == boards_dict["creative"][0].id).order_by(Column.order).all()
    
    # Helper to create dates
    today = datetime.utcnow()
    
    # Tasks for TechCorp - Website Redesign
    techcorp_tasks = [
        {
            "title": "Design new homepage mockup",
            "description": "## Objective\nCreate modern homepage design\n\n**Requirements:**\n- Hero section with CTA\n- Feature highlights\n- Testimonials section",
            "priority": TaskPriority.HIGH,
            "due_date": today + timedelta(days=5),
            "column": techcorp_board1_columns[0],
            "assignee": users_dict["techcorp"]["employees"][0],  # Alice
            "order": 0
        },
        {
            "title": "Implement responsive navigation",
            "description": "## Tasks\n- [x] Desktop navigation\n- [ ] Mobile hamburger menu\n- [ ] Tablet breakpoint",
            "priority": TaskPriority.HIGH,
            "due_date": today + timedelta(days=1),
            "column": techcorp_board1_columns[1],
            "assignee": users_dict["techcorp"]["employees"][1],  # Bob
            "order": 0
        },
        {
            "title": "Set up CI/CD pipeline",
            "description": "Configured GitHub Actions for:\n- Automated testing\n- Build process\n- Deployment to staging",
            "priority": TaskPriority.HIGH,
            "due_date": today - timedelta(days=5),
            "column": techcorp_board1_columns[2],
            "assignee": users_dict["techcorp"]["employees"][2],  # Carol
            "order": 0
        },
    ]
    
    # Tasks for Creative Agency - Marketing Campaign
    creative_tasks = [
        {
            "title": "Plan social media content calendar",
            "description": "## Q4 Content Strategy\n\n**Platforms:**\n- Twitter: 3x daily\n- LinkedIn: 2x daily\n- Instagram: 1x daily",
            "priority": TaskPriority.HIGH,
            "due_date": today + timedelta(days=7),
            "column": creative_board1_columns[0],
            "assignee": users_dict["creative"]["employees"][0],  # Dave
            "order": 0
        },
        {
            "title": "Launch LinkedIn ad campaign",
            "description": "## Campaign Details\n- Budget: $5,000\n- Duration: 30 days\n- Target: B2B decision makers",
            "priority": TaskPriority.HIGH,
            "due_date": today + timedelta(days=2),
            "column": creative_board1_columns[1],
            "assignee": users_dict["creative"]["employees"][1],  # Eve
            "order": 0
        },
        {
            "title": "Q3 performance analysis",
            "description": "## Key Metrics\n- Website traffic: ↑ 45%\n- Conversion rate: ↑ 12%\n- Email open rate: 28%",
            "priority": TaskPriority.HIGH,
            "due_date": today - timedelta(days=7),
            "column": creative_board1_columns[2],
            "assignee": users_dict["creative"]["admin"],
            "order": 0
        },
    ]
    
    # Combine all tasks
    all_tasks = techcorp_tasks + creative_tasks
    
    # Create tasks in database
    for task_data in all_tasks:
        task = Task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            due_date=task_data["due_date"],
            column_id=task_data["column"].id,
            assignee_id=task_data["assignee"].id,
            order=task_data["order"]
        )
        db.add(task)
    
    db.commit()
    print(f"✓ Created {len(all_tasks)} tasks across all boards")


def seed_database():
    """Main function to seed the database."""
    print("\n" + "="*60)
    print("KanbanFlow Database Seeding")
    print("="*60 + "\n")
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data!")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return
            
            # Drop and recreate tables
            print("\nDropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            print("Recreating tables...")
            Base.metadata.create_all(bind=engine)
            print("✓ Tables reset\n")
        
        # Create seed data
        companies = create_companies(db)
        users_dict = create_users(db, companies)
        boards_dict = create_boards(db, users_dict)
        add_board_members(db, boards_dict, users_dict)
        create_tasks(db, boards_dict, users_dict)
        
        print("\n" + "="*60)
        print("✅ Database seeding completed successfully!")
        print("="*60)
        print("\nTest Accounts:")
        print("-" * 60)
        print("TechCorp Solutions:")
        print("  Admin: admin@kanbanflow.com / Admin@123")
        print("  Employees:")
        print("    alice@kanbanflow.com / Pass@123")
        print("    bob@kanbanflow.com / Pass@123")
        print("    carol@kanbanflow.com / Pass@123")
        print("\nCreative Agency:")
        print("  Admin: admin@creative.com / Admin@123")
        print("  Employees:")
        print("    dave@creative.com / Pass@123")
        print("    eve@creative.com / Pass@123")
        print("\nCompanies:")
        print("  1. TechCorp Solutions (techcorp)")
        print("  2. Creative Agency (creative-agency)")
        print("  3. StartupHub (startup-hub)")
        print("\nBoards:")
        print("  TechCorp: Website Redesign, Mobile App Development")
        print("  Creative: Marketing Campaign Q4")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
