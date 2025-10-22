#!/usr/bin/env python3
"""
Database Migration Management Script
Similar to Flyway for Python/Flask applications

Usage:
    python migrate.py init          # Initialize migration repository
    python migrate.py create "msg"   # Create new migration
    python migrate.py upgrade        # Apply all pending migrations
    python migrate.py downgrade      # Rollback last migration
    python migrate.py current        # Show current migration
    python migrate.py history        # Show migration history
    python migrate.py populate       # Populate with default data
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def init_migrations():
    """Initialize migration repository"""
    print("Initializing Flask-Migrate repository...")
    return run_command("flask db init")

def create_migration(message):
    """Create a new migration"""
    print(f"Creating migration: {message}")
    return run_command(f'flask db migrate -m "{message}"')

def upgrade_database():
    """Apply all pending migrations"""
    print("Applying database migrations...")
    return run_command("flask db upgrade")

def downgrade_database():
    """Rollback last migration"""
    print("Rolling back last migration...")
    return run_command("flask db downgrade")

def show_current():
    """Show current migration"""
    print("Current migration status:")
    return run_command("flask db current")

def show_history():
    """Show migration history"""
    print("Migration history:")
    return run_command("flask db history")

def populate_data():
    """Populate database with default data"""
    print("Populating database with default data...")
    return run_command("python populate_db.py")

def main():
    """Main migration management function"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'run.py'
    
    if command == 'init':
        init_migrations()
    elif command == 'create':
        if len(sys.argv) < 3:
            print("Error: Migration message required")
            print("Usage: python migrate.py create 'Your migration message'")
            return
        message = sys.argv[2]
        create_migration(message)
    elif command == 'upgrade':
        upgrade_database()
    elif command == 'downgrade':
        downgrade_database()
    elif command == 'current':
        show_current()
    elif command == 'history':
        show_history()
    elif command == 'populate':
        populate_data()
    elif command == 'reset':
        print("Resetting database (WARNING: This will delete all data!)")
        confirm = input("Are you sure? Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            # Delete database and recreate
            db_path = Path("instance/ticketbroker.db")
            if db_path.exists():
                db_path.unlink()
                print("✓ Database deleted")
            upgrade_database()
            populate_data()
        else:
            print("Operation cancelled")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()
