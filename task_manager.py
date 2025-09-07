"""
Task Manager for handling task CRUD operations and scheduling with APScheduler
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import pytz
from db import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskManager:
    """Manages tasks, scheduling, and reminders"""
    
    def __init__(self):
        """Initialize the task manager"""
        self.db_manager = get_db_manager()
        self.scheduler = None
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Setup APScheduler for task scheduling"""
        try:
            jobstores = {
                'default': MemoryJobStore()
            }
            executors = {
                'default': ThreadPoolExecutor(20)
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone=pytz.UTC
            )
            
            self.scheduler.start()
            logger.info("Task scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to setup scheduler: {e}")
            raise
    
    def create_task(self, task_data: Dict, meeting_id: str = None) -> str:
        """
        Create a new task
        
        Args:
            task_data: Dictionary containing task information
            meeting_id: Optional meeting ID this task belongs to
            
        Returns:
            str: Task ID
        """
        try:
            # Prepare task document
            task_doc = {
                'task': task_data.get('task', '').strip(),
                'assignee': task_data.get('assignee', 'TBD').strip(),
                'priority': task_data.get('priority', 'medium').lower(),
                'context': task_data.get('context', '').strip(),
                'status': 'pending',
                'meeting_id': meeting_id,
                'transcript_id': task_data.get('transcript_id'),
                'suggested_deadline': task_data.get('suggested_deadline'),
                'actual_deadline': task_data.get('actual_deadline'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Validate required fields
            if not task_doc['task']:
                raise ValueError("Task description is required")
            
            # Set actual deadline if not provided
            if not task_doc['actual_deadline'] and task_doc['suggested_deadline']:
                task_doc['actual_deadline'] = task_doc['suggested_deadline']
            elif not task_doc['actual_deadline']:
                # Default to 7 days from now
                default_deadline = datetime.utcnow() + timedelta(days=7)
                task_doc['actual_deadline'] = default_deadline.strftime('%Y-%m-%d')
            
            # Save to database
            task_id = self.db_manager.save_task(task_doc)
            
            # Schedule reminders
            self._schedule_task_reminders(task_id, task_doc)
            
            logger.info(f"Created task: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    def create_tasks_from_action_items(self, action_items: List[Dict], meeting_id: str = None, transcript_id: str = None) -> List[str]:
        """
        Create multiple tasks from action items
        
        Args:
            action_items: List of action item dictionaries
            meeting_id: Optional meeting ID
            transcript_id: Optional transcript ID
            
        Returns:
            List of created task IDs
        """
        task_ids = []
        
        for item in action_items:
            try:
                task_data = {
                    'task': item.get('task', ''),
                    'assignee': item.get('assignee', 'TBD'),
                    'priority': item.get('priority', 'medium'),
                    'context': item.get('context', ''),
                    'suggested_deadline': item.get('suggested_deadline'),
                    'transcript_id': transcript_id
                }
                
                task_id = self.create_task(task_data, meeting_id)
                task_ids.append(task_id)
                
            except Exception as e:
                logger.error(f"Error creating task from action item: {e}")
                continue
        
        logger.info(f"Created {len(task_ids)} tasks from action items")
        return task_ids
    
    def update_task(self, task_id: str, updates: Dict) -> bool:
        """
        Update a task
        
        Args:
            task_id: ID of the task to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if update was successful
        """
        try:
            updates['updated_at'] = datetime.utcnow()
            
            # Update in database
            collection = self.db_manager.get_collection('tasks')
            result = collection.update_one(
                {'_id': task_id},
                {'$set': updates}
            )
            
            if result.modified_count > 0:
                # Reschedule reminders if deadline changed
                if 'actual_deadline' in updates:
                    self._reschedule_task_reminders(task_id)
                
                logger.info(f"Updated task: {task_id}")
                return True
            else:
                logger.warning(f"Task not found or not updated: {task_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False
    
    def mark_task_completed(self, task_id: str) -> bool:
        """Mark a task as completed"""
        return self.update_task(task_id, {'status': 'completed'})
    
    def mark_task_in_progress(self, task_id: str) -> bool:
        """Mark a task as in progress"""
        return self.update_task(task_id, {'status': 'in_progress'})
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task and cancel its scheduled reminders
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Cancel scheduled reminders
            self._cancel_task_reminders(task_id)
            
            # Delete from database
            collection = self.db_manager.get_collection('tasks')
            result = collection.delete_one({'_id': task_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted task: {task_id}")
                return True
            else:
                logger.warning(f"Task not found: {task_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a task by ID"""
        collection = self.db_manager.get_collection('tasks')
        return collection.find_one({'_id': task_id})
    
    def get_tasks(self, filters: Dict = None) -> List[Dict]:
        """
        Get tasks with optional filters
        
        Args:
            filters: Optional filters (status, assignee, priority, etc.)
            
        Returns:
            List of task documents
        """
        collection = self.db_manager.get_collection('tasks')
        query = filters or {}
        return list(collection.find(query).sort('created_at', -1))
    
    def get_overdue_tasks(self) -> List[Dict]:
        """Get all overdue tasks"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        collection = self.db_manager.get_collection('tasks')
        
        return list(collection.find({
            'status': {'$in': ['pending', 'in_progress']},
            'actual_deadline': {'$lt': today}
        }).sort('actual_deadline', 1))
    
    def get_upcoming_tasks(self, days_ahead: int = 7) -> List[Dict]:
        """Get tasks due within specified days"""
        today = datetime.utcnow()
        future_date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        collection = self.db_manager.get_collection('tasks')
        
        return list(collection.find({
            'status': {'$in': ['pending', 'in_progress']},
            'actual_deadline': {'$gte': today.strftime('%Y-%m-%d'), '$lte': future_date}
        }).sort('actual_deadline', 1))
    
    def _schedule_task_reminders(self, task_id: str, task_data: Dict):
        """Schedule reminders for a task"""
        try:
            if not task_data.get('actual_deadline'):
                return
            
            deadline = datetime.strptime(task_data['actual_deadline'], '%Y-%m-%d')
            
            # Schedule reminder 1 day before deadline
            reminder_date = deadline - timedelta(days=1)
            if reminder_date > datetime.utcnow():
                self.scheduler.add_job(
                    func=self._send_task_reminder,
                    trigger=DateTrigger(run_date=reminder_date),
                    args=[task_id, '1 day before deadline'],
                    id=f"reminder_1day_{task_id}",
                    replace_existing=True
                )
            
            # Schedule reminder on deadline day
            if deadline.date() >= datetime.utcnow().date():
                self.scheduler.add_job(
                    func=self._send_task_reminder,
                    trigger=DateTrigger(run_date=deadline),
                    args=[task_id, 'deadline today'],
                    id=f"reminder_deadline_{task_id}",
                    replace_existing=True
                )
            
            # Schedule overdue check (daily)
            self.scheduler.add_job(
                func=self._check_overdue_tasks,
                trigger=IntervalTrigger(days=1),
                id=f"overdue_check_{task_id}",
                replace_existing=True
            )
            
        except Exception as e:
            logger.error(f"Error scheduling reminders for task {task_id}: {e}")
    
    def _reschedule_task_reminders(self, task_id: str):
        """Reschedule reminders when task deadline changes"""
        # Cancel existing reminders
        self._cancel_task_reminders(task_id)
        
        # Get updated task data
        task = self.get_task(task_id)
        if task:
            self._schedule_task_reminders(task_id, task)
    
    def _cancel_task_reminders(self, task_id: str):
        """Cancel all reminders for a task"""
        try:
            job_ids = [
                f"reminder_1day_{task_id}",
                f"reminder_deadline_{task_id}",
                f"overdue_check_{task_id}"
            ]
            
            for job_id in job_ids:
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass  # Job might not exist
                    
        except Exception as e:
            logger.error(f"Error canceling reminders for task {task_id}: {e}")
    
    def _send_task_reminder(self, task_id: str, reminder_type: str):
        """Send a task reminder (currently logs to console)"""
        try:
            task = self.get_task(task_id)
            if task and task['status'] in ['pending', 'in_progress']:
                logger.info(f"REMINDER: Task '{task['task']}' is {reminder_type}")
                logger.info(f"Assignee: {task['assignee']}, Priority: {task['priority']}")
                
                # TODO: Implement email/notification sending here
                # For now, just log the reminder
                
        except Exception as e:
            logger.error(f"Error sending reminder for task {task_id}: {e}")
    
    def _check_overdue_tasks(self):
        """Check for overdue tasks and send reminders"""
        try:
            overdue_tasks = self.get_overdue_tasks()
            for task in overdue_tasks:
                logger.info(f"OVERDUE TASK: '{task['task']}' (Assignee: {task['assignee']})")
                
        except Exception as e:
            logger.error(f"Error checking overdue tasks: {e}")
    
    def get_task_statistics(self) -> Dict:
        """Get task statistics"""
        collection = self.db_manager.get_collection('tasks')
        
        stats = {
            'total_tasks': collection.count_documents({}),
            'pending_tasks': collection.count_documents({'status': 'pending'}),
            'in_progress_tasks': collection.count_documents({'status': 'in_progress'}),
            'completed_tasks': collection.count_documents({'status': 'completed'}),
            'overdue_tasks': len(self.get_overdue_tasks()),
            'upcoming_tasks': len(self.get_upcoming_tasks())
        }
        
        return stats
    
    def shutdown(self):
        """Shutdown the task manager and scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Task scheduler shutdown")

# Global task manager instance
task_manager = TaskManager()

def get_task_manager() -> TaskManager:
    """Get the global task manager instance"""
    return task_manager
