"""
MongoDB connection and database operations for the Meeting Summarizer
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import logging
import streamlit as st


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all MongoDB operations for the meeting summarizer"""
    
    def __init__(self):
        """Initialize database manager without connecting"""
        self.client = None
        self.db = None
        self.database_name = os.getenv('DATABASE_NAME', 'meeting_summarizer')
        self._connected = False
    
    def connect(self):
        """Establish connection to MongoDB"""
        if self._connected:
            return
            
        try:
            # Get MongoDB URI from Streamlit secrets
            mongo_uri = st.secrets["mongo"]["uri"]
            print(f"🔌 Testing connection to: {mongo_uri}")
            logger.info("Using MongoDB URI from Streamlit secrets")
        except (KeyError, AttributeError):
            # Fallback to environment variable or localhost
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            print(f"🔌 Testing connection to: {mongo_uri}")
            logger.info("Using MongoDB URI from environment variable or localhost")
        
        try:
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, tls=True)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.get_default_database()
            self._connected = True
            print("✅ MongoDB Atlas connection successful!")
            logger.info(f"✅ Successfully connected to MongoDB Atlas: {self.db.name}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            logger.error(f"MongoDB URI being used: {mongo_uri}")
            raise RuntimeError(f"❌ Could not connect to MongoDB: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            raise RuntimeError(f"❌ Could not connect to MongoDB: {e}")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self._connected:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db[collection_name]
    
    def save_transcript(self, transcript_data: Dict) -> str:
        """
        Save raw transcript to MongoDB
        
        Args:
            transcript_data: Dictionary containing transcript information
            
        Returns:
            str: Document ID of the saved transcript
        """
        collection = self.get_collection('transcripts')
        transcript_data['created_at'] = datetime.utcnow()
        result = collection.insert_one(transcript_data)
        logger.info(f"Saved transcript with ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    def save_summary(self, summary_data: Dict) -> str:
        """
        Save meeting summary to MongoDB
        
        Args:
            summary_data: Dictionary containing summary information
            
        Returns:
            str: Document ID of the saved summary
        """
        collection = self.get_collection('summaries')
        summary_data['created_at'] = datetime.utcnow()
        result = collection.insert_one(summary_data)
        logger.info(f"Saved summary with ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    def save_task(self, task_data: Dict) -> str:
        """
        Save a task to MongoDB
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            str: Document ID of the saved task
        """
        collection = self.get_collection('tasks')
        task_data['created_at'] = datetime.utcnow()
        result = collection.insert_one(task_data)
        logger.info(f"Saved task with ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    def get_transcript(self, transcript_id: str) -> Optional[Dict]:
        """Get a transcript by ID"""
        try:
            collection = self.get_collection('transcripts')
            return collection.find_one({'_id': ObjectId(transcript_id)})
        except Exception as e:
            logger.error(f"Error getting transcript {transcript_id}: {e}")
            return None
    
    def get_summary(self, summary_id: str) -> Optional[Dict]:
        """Get a summary by ID"""
        try:
            collection = self.get_collection('summaries')
            return collection.find_one({'_id': ObjectId(summary_id)})
        except Exception as e:
            logger.error(f"Error getting summary {summary_id}: {e}")
            return None
    
    def get_all_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """
        Get all tasks, optionally filtered by status
        
        Args:
            status: Optional status filter ('pending', 'completed', etc.)
            
        Returns:
            List of task documents
        """
        collection = self.get_collection('tasks')
        query = {} if status is None else {'status': status}
        return list(collection.find(query).sort('created_at', -1))
    
    def get_tasks_by_meeting(self, meeting_id: str) -> List[Dict]:
        """Get all tasks for a specific meeting"""
        collection = self.get_collection('tasks')
        return list(collection.find({'meeting_id': meeting_id}).sort('created_at', -1))
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update task status
        
        Args:
            task_id: ID of the task to update
            status: New status ('pending', 'completed', etc.)
            
        Returns:
            bool: True if update was successful
        """
        try:
            collection = self.get_collection('tasks')
            result = collection.update_one(
                {'_id': ObjectId(task_id)},
                {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False
    
    def get_recent_meetings(self, limit: int = 10) -> List[Dict]:
        """Get recent meetings with their summaries"""
        collection = self.get_collection('summaries')
        return list(collection.find().sort('created_at', -1).limit(limit))
    
    def delete_transcript(self, transcript_id: str) -> bool:
        """Delete a transcript and related data"""
        try:
            # Delete transcript
            transcripts_collection = self.get_collection('transcripts')
            transcripts_collection.delete_one({'_id': ObjectId(transcript_id)})
            
            # Delete related summaries
            summaries_collection = self.get_collection('summaries')
            summaries_collection.delete_many({'transcript_id': transcript_id})
            
            # Delete related tasks
            tasks_collection = self.get_collection('tasks')
            tasks_collection.delete_many({'transcript_id': transcript_id})
            
            logger.info(f"Deleted transcript and related data: {transcript_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting transcript {transcript_id}: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        stats = {
            'transcripts': self.get_collection('transcripts').count_documents({}),
            'summaries': self.get_collection('summaries').count_documents({}),
            'tasks': self.get_collection('tasks').count_documents({}),
            'pending_tasks': self.get_collection('tasks').count_documents({'status': 'pending'}),
            'completed_tasks': self.get_collection('tasks').count_documents({'status': 'completed'})
        }
        return stats
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

# Global database instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager