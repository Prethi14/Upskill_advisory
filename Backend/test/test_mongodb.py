#!/usr/bin/env python3
"""
Simple MongoDB connection test without external dependencies
"""

import os
import sys
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test MongoDB connection with your credentials."""
    print("Testing MongoDB Connection...")
    print("=" * 50)
    
    # Connection string with your credentials
    connection_string = os.getenv(
        "MONGODB_CONNECTION_STRING",
    )
    
    print(f"Connection string: {connection_string[:50]}...")
    
    try:
        # Connect to MongoDB
        client = MongoClient(connection_string, server_api=ServerApi('1'))
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Access database and collection
        db = client["upskill_advisor"]
        collection = db["courses"]
        
        # Get current document count
        count = collection.count_documents({})
        print(f"📊 Current documents in courses collection: {count}")
        
        # Insert a test document
        test_doc = {
            "course_id": "test_001",
            "title": "Test Course",
            "description": "This is a test course",
            "skills": ["testing", "mongodb"],
            "difficulty": "beginner",
            "duration_weeks": 2
        }
        
        # Insert (or replace if exists)
        result = collection.replace_one(
            {"course_id": "test_001"}, 
            test_doc, 
            upsert=True
        )
        
        if result.upserted_id or result.modified_count:
            print("✅ Successfully inserted/updated test document")
        
        # Query the test document
        found_doc = collection.find_one({"course_id": "test_001"})
        if found_doc:
            print("✅ Successfully retrieved test document:")
            print(f"   Title: {found_doc['title']}")
            print(f"   Skills: {found_doc['skills']}")
        
        # Get updated count
        new_count = collection.count_documents({})
        print(f"📊 New document count: {new_count}")
        
        # Close connection
        client.close()
        print("✅ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_courses_json():
    """Test loading courses.json file."""
    print("\nTesting courses.json file...")
    print("=" * 30)
    
    courses_file = "courses.json"
    
    if not os.path.exists(courses_file):
        print(f"❌ {courses_file} not found!")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {[f for f in os.listdir('.') if f.endswith('.json')]}")
        return None
    
    try:
        import json
        with open(courses_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            courses = data
        elif isinstance(data, dict) and 'courses' in data:
            courses = data['courses']
        else:
            courses = [data]
        
        print(f"✅ Loaded {len(courses)} courses from {courses_file}")
        
        if courses:
            sample = courses[0]
            print("📋 Sample course structure:")
            for key, value in sample.items():
                if isinstance(value, list):
                    print(f"  {key}: {value[:2]}{'...' if len(value) > 2 else ''}")
                else:
                    value_str = str(value)[:40] + "..." if len(str(value)) > 40 else str(value)
                    print(f"  {key}: {value_str}")
        
        return courses
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading courses: {e}")
        return None

def test_environment():
    """Test environment setup."""
    print("\nTesting Environment...")
    print("=" * 25)
    
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check for required files
    required_files = [".env", "courses.json", "main.py"]
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
    
    # Check environment variables
    env_vars = ["MONGODB_CONNECTION_STRING", "MONGODB_DB", "MONGODB_COLLECTION"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive parts
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")

def main():
    """Run all tests."""
    print("🚀 SIMPLE MONGODB TESTS")
    print("=" * 50)
    
    # Test 1: Environment
    test_environment()
    
    # Test 2: MongoDB connection
    if test_connection():
        print("\n✅ MongoDB connection test PASSED")
    else:
        print("\n❌ MongoDB connection test FAILED")
        return
    
    # Test 3: Courses file
    courses = test_courses_json()
    if courses:
        print("\n✅ Courses loading test PASSED")
    else:
        print("\n❌ Courses loading test FAILED")
    
    print("\n" + "=" * 50)
    print("🎉 TESTS COMPLETED!")
    print("If MongoDB connection works, you can proceed with the main application.")

if __name__ == "__main__":
    main()