"""
Test script for the AI-Driven Meeting Summarizer
Run this to test the complete workflow
"""
import os
import sys
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from db import get_db_manager
from transcript_loader import get_transcript_loader
from ollama_nlp import get_ollama_processor
from task_manager import get_task_manager
from exports import get_export_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        db_manager = get_db_manager()
        stats = db_manager.get_database_stats()
        print(f"✅ Database connected successfully!")
        print(f"   - Transcripts: {stats['transcripts']}")
        print(f"   - Summaries: {stats['summaries']}")
        print(f"   - Tasks: {stats['tasks']}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🔍 Testing Ollama connection...")
    try:
        ollama_processor = get_ollama_processor()
        if ollama_processor.test_connection():
            print("✅ Ollama connected successfully!")
            return True
        else:
            print("❌ Ollama connection failed")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_transcript_processing():
    """Test transcript processing"""
    print("\n🔍 Testing transcript processing...")
    try:
        transcript_loader = get_transcript_loader()
        
        # Test with sample text
        sample_text = """
        Meeting: Test Meeting
        Attendees: Alice, Bob
        
        Alice: Let's discuss the project timeline.
        Bob: We need to complete the design by Friday.
        Alice: I'll prepare the mockups by Wednesday.
        Bob: Perfect, I'll review them on Thursday.
        """
        
        result = transcript_loader.process_file('sample_meeting.txt')
        print(f"✅ Transcript processing successful!")
        print(f"   - File type: {result['file_type']}")
        print(f"   - Text length: {len(result['text'])} characters")
        print(f"   - Processing method: {result['processing_method']}")
        return True
    except Exception as e:
        print(f"❌ Transcript processing failed: {e}")
        return False

def test_ai_processing():
    """Test AI processing with Ollama"""
    print("\n🔍 Testing AI processing...")
    try:
        ollama_processor = get_ollama_processor()
        
        # Test with short sample
        sample_text = """
        Meeting: Quick Standup
        Alice: I completed the user authentication feature yesterday.
        Bob: I'm working on the payment integration, should be done by Friday.
        Carol: I'll prepare the UI mockups for the dashboard redesign.
        Alice: Great work everyone. Let's meet again tomorrow.
        """
        
        result = ollama_processor.process_meeting(sample_text, "Test Meeting")
        
        print(f"✅ AI processing successful!")
        print(f"   - Summary length: {len(result['summary']['summary'])} characters")
        print(f"   - Action items found: {len(result['action_items'])}")
        
        # Print action items
        for i, item in enumerate(result['action_items'], 1):
            print(f"   - {i}. {item['task']} (Assignee: {item['assignee']})")
        
        return True
    except Exception as e:
        print(f"❌ AI processing failed: {e}")
        return False

def test_task_management():
    """Test task management"""
    print("\n🔍 Testing task management...")
    try:
        task_manager = get_task_manager()
        
        # Create a test task
        test_task = {
            'task': 'Test task for demonstration',
            'assignee': 'Test User',
            'priority': 'medium',
            'context': 'This is a test task',
            'suggested_deadline': '2024-01-20'
        }
        
        task_id = task_manager.create_task(test_task)
        print(f"✅ Task created successfully! ID: {task_id}")
        
        # Get task
        task = task_manager.get_task(task_id)
        print(f"   - Task: {task['task']}")
        print(f"   - Assignee: {task['assignee']}")
        print(f"   - Status: {task['status']}")
        
        # Update task
        task_manager.mark_task_in_progress(task_id)
        print("   - Task marked as in progress")
        
        # Get task statistics
        stats = task_manager.get_task_statistics()
        print(f"   - Total tasks: {stats['total_tasks']}")
        
        return True
    except Exception as e:
        print(f"❌ Task management failed: {e}")
        return False

def test_export_functionality():
    """Test export functionality"""
    print("\n🔍 Testing export functionality...")
    try:
        export_manager = get_export_manager()
        
        # Test CSV export
        csv_data = export_manager.export_tasks_to_csv()
        print(f"✅ CSV export successful! Size: {len(csv_data)} bytes")
        
        # Test PDF export (if we have a summary)
        try:
            # Get a summary from database
            db_manager = get_db_manager()
            summaries = db_manager.get_recent_meetings(1)
            if summaries:
                pdf_data = export_manager.export_summary_to_pdf(summaries[0]['_id'])
                print(f"✅ PDF export successful! Size: {len(pdf_data)} bytes")
            else:
                print("⚠️ No summaries found for PDF export test")
        except Exception as e:
            print(f"⚠️ PDF export test skipped: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Export functionality failed: {e}")
        return False

def run_complete_workflow_test():
    """Run a complete workflow test"""
    print("\n🚀 Running complete workflow test...")
    
    try:
        # Load sample transcript
        transcript_loader = get_transcript_loader()
        transcript_data = transcript_loader.process_file('sample_meeting.txt')
        
        # Save transcript to database
        db_manager = get_db_manager()
        transcript_id = db_manager.save_transcript({
            'file_name': 'sample_meeting.txt',
            'file_type': transcript_data['file_type'],
            'processing_method': transcript_data['processing_method'],
            'text': transcript_data['text'],
            'meeting_title': 'Sample Meeting Test'
        })
        
        print(f"✅ Transcript saved with ID: {transcript_id}")
        
        # Process with AI
        ollama_processor = get_ollama_processor()
        result = ollama_processor.process_meeting(transcript_data['text'], 'Sample Meeting Test')
        
        # Save summary
        summary_data = result['summary']
        summary_data['transcript_id'] = transcript_id
        summary_data['meeting_id'] = transcript_id
        
        summary_id = db_manager.save_summary(summary_data)
        print(f"✅ Summary saved with ID: {summary_id}")
        
        # Create tasks
        task_manager = get_task_manager()
        task_ids = task_manager.create_tasks_from_action_items(
            result['action_items'],
            meeting_id=transcript_id,
            transcript_id=transcript_id
        )
        
        print(f"✅ Created {len(task_ids)} tasks")
        
        # Export results
        export_manager = get_export_manager()
        csv_data = export_manager.export_meeting_report_to_csv(summary_id)
        print(f"✅ Exported complete report ({len(csv_data)} bytes)")
        
        print("\n🎉 Complete workflow test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 AI-Driven Meeting Summarizer - Test Suite")
    print("=" * 50)
    
    # Create sample files first
    try:
        from sample_data import create_sample_files
        create_sample_files()
        print("✅ Sample files created")
    except Exception as e:
        print(f"⚠️ Could not create sample files: {e}")
    
    # Run tests
    tests = [
        test_database_connection,
        test_ollama_connection,
        test_transcript_processing,
        test_ai_processing,
        test_task_management,
        test_export_functionality,
        run_complete_workflow_test
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")
    
    print("\n💡 To run the Streamlit app:")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main()
