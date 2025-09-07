#!/usr/bin/env python3
"""
MongoDB Atlas Setup Helper Script
This script helps you test your MongoDB Atlas connection string locally
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection(connection_string):
    """Test MongoDB connection"""
    try:
        print(f"Testing connection to: {connection_string[:50]}...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database operations
        db = client['meeting_summarizer']
        collection = db['test']
        
        # Insert test document
        test_doc = {"test": "connection", "timestamp": "2024-01-01"}
        result = collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Find test document
        found_doc = collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Test document retrieved successfully!")
        
        # Clean up test document
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server selection timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🔧 MongoDB Atlas Connection Tester")
    print("=" * 50)
    
    # Get connection string from user
    if len(sys.argv) > 1:
        connection_string = sys.argv[1]
    else:
        print("\nEnter your MongoDB Atlas connection string:")
        print("Example: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/meeting_summarizer?retryWrites=true&w=majority")
        connection_string = input("\nConnection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided")
        return
    
    # Test connection
    success = test_mongodb_connection(connection_string)
    
    if success:
        print("\n🎉 Your MongoDB Atlas connection is working!")
        print("\nNext steps:")
        print("1. Add this connection string to your Streamlit Cloud secrets")
        print("2. Deploy your app to Streamlit Cloud")
        print("3. Configure the secrets in your Streamlit Cloud app settings")
    else:
        print("\n❌ Connection failed. Please check:")
        print("1. Your connection string is correct")
        print("2. Your MongoDB Atlas cluster is running")
        print("3. Network access allows connections from 0.0.0.0/0")
        print("4. Your username and password are correct")

if __name__ == "__main__":
    main()
