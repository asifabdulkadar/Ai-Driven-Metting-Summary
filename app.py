"""
AI-Driven Meeting Summarizer - Main Streamlit Application
Complete solution for meeting transcription, summarization, and task management
"""
import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Import our modules
from db import get_db_manager
from transcript_loader import get_transcript_loader
from ollama_nlp import get_ollama_processor
from task_manager import get_task_manager
from exports import get_export_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
db_manager = get_db_manager()
try:
    db_manager.connect()
    st.session_state.db_connected = True
except RuntimeError as e:
    st.session_state.db_connected = False
    st.session_state.db_error = str(e)

# Page configuration
st.set_page_config(
    page_title="AI-Driven Meeting Summarizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .task-card {
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .priority-high {
        border-left: 4px solid #dc3545;
    }
    .priority-medium {
        border-left: 4px solid #ffc107;
    }
    .priority-low {
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_summary' not in st.session_state:
        st.session_state.current_summary = None
    if 'current_tasks' not in st.session_state:
        st.session_state.current_tasks = []
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = 'idle'
    if 'uploaded_file_info' not in st.session_state:
        st.session_state.uploaded_file_info = None

def check_system_status():
    """Check if all system components are working"""
    status = {
        'mongodb': False,
        'ollama': False,
        'whisper': False
    }
    
    # Check MongoDB connection status
    if st.session_state.get('db_connected', False):
        try:
            db_manager.get_database_stats()
            status['mongodb'] = True
        except Exception as e:
            st.error(f"MongoDB connection failed: {e}")
    else:
        st.error(f"MongoDB connection failed: {st.session_state.get('db_error', 'Unknown error')}")
    
    try:
        # Check Ollama
        ollama_processor = get_ollama_processor()
        status['ollama'] = ollama_processor.test_connection()
    except Exception as e:
        st.error(f"Ollama connection failed: {e}")
    
    try:
        # Check Whisper (try to load model)
        transcript_loader = get_transcript_loader()
        transcript_loader.load_whisper_model("base")
        status['whisper'] = True
    except Exception as e:
        st.warning(f"Whisper model loading failed: {e}")
    
    return status

def upload_page():
    """Upload page for file processing"""
    st.markdown('<div class="section-header">📁 Upload Meeting Files</div>', unsafe_allow_html=True)
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'json', 'wav', 'mp3', 'mp4', 'mkv'],
        help="Supported formats: TXT, JSON, WAV, MP3, MP4, MKV"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        # Meeting title input
        meeting_title = st.text_input(
            "Meeting Title (Optional)",
            value="",
            placeholder="Enter meeting title..."
        )
        
        # Process button
        if st.button("🚀 Process Meeting", type="primary"):
            if st.session_state.processing_status == 'processing':
                st.warning("Processing already in progress...")
                return
            
            st.session_state.processing_status = 'processing'
            
            try:
                with st.spinner("Processing file..."):
                    # Load transcript
                    transcript_loader = get_transcript_loader()
                    transcript_data = transcript_loader.process_streamlit_upload(uploaded_file)
                    
                    # Save transcript to database
                    db_manager = get_db_manager()
                    transcript_id = db_manager.save_transcript({
                        'file_name': uploaded_file.name,
                        'file_size': uploaded_file.size,
                        'file_type': transcript_data['file_type'],
                        'processing_method': transcript_data['processing_method'],
                        'text': transcript_data['text'],
                        'meeting_title': meeting_title or uploaded_file.name
                    })
                    
                    st.session_state.uploaded_file_info = {
                        'transcript_id': transcript_id,
                        'meeting_title': meeting_title or uploaded_file.name,
                        'text': transcript_data['text']
                    }
                    
                    st.success("✅ File processed successfully!")
                    st.session_state.processing_status = 'completed'
                    
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")
                st.session_state.processing_status = 'error'
    
    # Show processing results
    if st.session_state.uploaded_file_info:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.write("**Processing Complete!**")
        st.write(f"📝 **Meeting:** {st.session_state.uploaded_file_info['meeting_title']}")
        st.write(f"📊 **Text Length:** {len(st.session_state.uploaded_file_info['text']):,} characters")
        st.write(f"🆔 **Transcript ID:** {st.session_state.uploaded_file_info['transcript_id']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show preview of transcript
        with st.expander("📖 Preview Transcript"):
            preview_text = st.session_state.uploaded_file_info['text'][:1000]
            st.text(preview_text)
            if len(st.session_state.uploaded_file_info['text']) > 1000:
                st.write("... (truncated)")

def summary_page():
    """Summary page for AI processing"""
    st.markdown('<div class="section-header">🤖 AI Summarization</div>', unsafe_allow_html=True)
    
    if not st.session_state.uploaded_file_info:
        st.warning("⚠️ Please upload and process a file first.")
        return
    
    # Generate summary button
    if st.button("🧠 Generate Summary & Action Items", type="primary"):
        if st.session_state.processing_status == 'processing':
            st.warning("Processing already in progress...")
            return
        
        st.session_state.processing_status = 'processing'
        
        try:
            with st.spinner("Generating summary and extracting action items..."):
                # Process with Ollama
                ollama_processor = get_ollama_processor()
                result = ollama_processor.process_meeting(
                    st.session_state.uploaded_file_info['text'],
                    st.session_state.uploaded_file_info['meeting_title']
                )
                
                # Save summary to database
                db_manager = get_db_manager()
                summary_data = result['summary']
                summary_data['transcript_id'] = st.session_state.uploaded_file_info['transcript_id']
                summary_data['meeting_id'] = st.session_state.uploaded_file_info['transcript_id']  # Use transcript_id as meeting_id
                
                summary_id = db_manager.save_summary(summary_data)
                
                # Create tasks from action items
                task_manager = get_task_manager()
                task_ids = task_manager.create_tasks_from_action_items(
                    result['action_items'],
                    meeting_id=st.session_state.uploaded_file_info['transcript_id'],
                    transcript_id=st.session_state.uploaded_file_info['transcript_id']
                )
                
                # Store results in session state
                st.session_state.current_summary = {
                    'id': summary_id,
                    'data': summary_data
                }
                st.session_state.current_tasks = result['action_items']
                
                st.success("✅ Summary and action items generated successfully!")
                st.session_state.processing_status = 'completed'
                
        except Exception as e:
            st.error(f"❌ Error generating summary: {e}")
            st.session_state.processing_status = 'error'
    
    # Display summary
    if st.session_state.current_summary:
        st.markdown('<div class="section-header">📋 Meeting Summary</div>', unsafe_allow_html=True)
        
        summary_data = st.session_state.current_summary['data']
        
        # Summary card
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.write(f"**📝 Meeting:** {summary_data['meeting_title']}")
        st.write(f"**🤖 Model:** {summary_data['model_used']}")
        st.write(f"**📊 Length:** {summary_data['transcript_length']:,} characters")
        st.write(f"**⏰ Created:** {summary_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary content
        st.write("**Summary:**")
        st.write(summary_data['summary'])
        
        # Action items
        if st.session_state.current_tasks:
            st.markdown('<div class="section-header">🎯 Action Items</div>', unsafe_allow_html=True)
            
            for i, task in enumerate(st.session_state.current_tasks, 1):
                priority_class = f"priority-{task.get('priority', 'medium')}"
                st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
                st.write(f"**{i}. {task['task']}**")
                st.write(f"👤 **Assignee:** {task['assignee']}")
                st.write(f"⚡ **Priority:** {task['priority'].title()}")
                st.write(f"📅 **Suggested Deadline:** {task['suggested_deadline']}")
                if task.get('context'):
                    st.write(f"📝 **Context:** {task['context']}")
                st.markdown('</div>', unsafe_allow_html=True)

def tasks_page():
    """Tasks management page"""
    st.markdown('<div class="section-header">📋 Task Management</div>', unsafe_allow_html=True)
    
    task_manager = get_task_manager()
    
    # Task filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "in_progress", "completed"]
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "high", "medium", "low"]
        )
    
    with col3:
        assignee_filter = st.selectbox(
            "Filter by Assignee",
            ["All", "TBD"] + list(set([task['assignee'] for task in task_manager.get_tasks() if task['assignee'] != 'TBD']))
        )
    
    # Apply filters
    filters = {}
    if status_filter != "All":
        filters['status'] = status_filter
    if priority_filter != "All":
        filters['priority'] = priority_filter
    if assignee_filter != "All":
        filters['assignee'] = assignee_filter
    
    # Get tasks
    tasks = task_manager.get_tasks(filters)
    
    if not tasks:
        st.info("No tasks found with the current filters.")
        return
    
    # Task statistics
    stats = task_manager.get_task_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tasks", stats['total_tasks'])
    with col2:
        st.metric("Pending", stats['pending_tasks'])
    with col3:
        st.metric("In Progress", stats['in_progress_tasks'])
    with col4:
        st.metric("Completed", stats['completed_tasks'])
    
    # Display tasks
    st.markdown('<div class="section-header">📝 Task List</div>', unsafe_allow_html=True)
    
    for task in tasks:
        priority_class = f"priority-{task.get('priority', 'medium')}"
        status_color = {
            'pending': '🟡',
            'in_progress': '🔵',
            'completed': '🟢'
        }.get(task['status'], '⚪')
        
        st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{task['task']}**")
            st.write(f"👤 {task['assignee']} | ⚡ {task['priority'].title()} | 📅 {task['actual_deadline']}")
            if task.get('context'):
                st.write(f"📝 {task['context']}")
        
        with col2:
            st.write(f"{status_color} {task['status'].title()}")
        
        with col3:
            # Task actions
            if task['status'] == 'pending':
                if st.button("Start", key=f"start_{task['_id']}"):
                    task_manager.mark_task_in_progress(task['_id'])
                    st.rerun()
            elif task['status'] == 'in_progress':
                if st.button("Complete", key=f"complete_{task['_id']}"):
                    task_manager.mark_task_completed(task['_id'])
                    st.rerun()
            
            if st.button("Delete", key=f"delete_{task['_id']}"):
                task_manager.delete_task(task['_id'])
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def export_page():
    """Export page for downloading results"""
    st.markdown('<div class="section-header">📤 Export Results</div>', unsafe_allow_html=True)
    
    export_manager = get_export_manager()
    
    if not st.session_state.current_summary:
        st.warning("⚠️ Please generate a summary first.")
        return
    
    # Export options
    st.write("**Export Options:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 CSV Exports**")
        
        if st.button("📋 Export Summary to CSV"):
            try:
                csv_data = export_manager.export_summary_to_csv(st.session_state.current_summary['id'])
                filename = export_manager.get_export_filename('summary')
                
                st.download_button(
                    label="⬇️ Download Summary CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
                st.success("✅ Summary CSV ready for download!")
            except Exception as e:
                st.error(f"❌ Error exporting summary: {e}")
        
        if st.button("📝 Export Tasks to CSV"):
            try:
                csv_data = export_manager.export_tasks_to_csv()
                filename = export_manager.get_export_filename('tasks')
                
                st.download_button(
                    label="⬇️ Download Tasks CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
                st.success("✅ Tasks CSV ready for download!")
            except Exception as e:
                st.error(f"❌ Error exporting tasks: {e}")
        
        if st.button("📊 Export Complete Report to CSV"):
            try:
                csv_data = export_manager.export_meeting_report_to_csv(st.session_state.current_summary['id'])
                filename = export_manager.get_export_filename('report')
                
                st.download_button(
                    label="⬇️ Download Complete Report CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
                st.success("✅ Complete report CSV ready for download!")
            except Exception as e:
                st.error(f"❌ Error exporting report: {e}")
    
    with col2:
        st.markdown("**📄 PDF Exports**")
        
        if st.button("📋 Export Summary to PDF"):
            try:
                pdf_data = export_manager.export_summary_to_pdf(st.session_state.current_summary['id'])
                filename = export_manager.get_export_filename('summary_pdf')
                
                st.download_button(
                    label="⬇️ Download Summary PDF",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf"
                )
                st.success("✅ Summary PDF ready for download!")
            except Exception as e:
                st.error(f"❌ Error exporting summary PDF: {e}")
        
        if st.button("📊 Export Complete Report to PDF"):
            try:
                pdf_data = export_manager.export_meeting_report_to_pdf(st.session_state.current_summary['id'])
                filename = export_manager.get_export_filename('report_pdf')
                
                st.download_button(
                    label="⬇️ Download Complete Report PDF",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf"
                )
                st.success("✅ Complete report PDF ready for download!")
            except Exception as e:
                st.error(f"❌ Error exporting report PDF: {e}")
    
    # Task statistics export
    st.markdown("**📊 Statistics Export**")
    if st.button("📈 Export Task Statistics to CSV"):
        try:
            csv_data = export_manager.export_task_statistics_to_csv()
            filename = export_manager.get_export_filename('statistics')
            
            st.download_button(
                label="⬇️ Download Statistics CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
            st.success("✅ Statistics CSV ready for download!")
        except Exception as e:
            st.error(f"❌ Error exporting statistics: {e}")

def dashboard_page():
    """Dashboard page with system overview"""
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    # System status
    st.write("**🔧 System Status**")
    status = check_system_status()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("MongoDB", "✅ Connected" if status['mongodb'] else "❌ Disconnected")
    with col2:
        st.metric("Ollama", "✅ Connected" if status['ollama'] else "❌ Disconnected")
    with col3:
        st.metric("Whisper", "✅ Ready" if status['whisper'] else "⚠️ Limited")
    
    # Database statistics
    if status['mongodb']:
        st.write("**📊 Database Statistics**")
        db_manager = get_db_manager()
        db_stats = db_manager.get_database_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Transcripts", db_stats['transcripts'])
        with col2:
            st.metric("Summaries", db_stats['summaries'])
        with col3:
            st.metric("Total Tasks", db_stats['tasks'])
        with col4:
            st.metric("Pending Tasks", db_stats['pending_tasks'])
        with col5:
            st.metric("Completed Tasks", db_stats['completed_tasks'])
    
    # Recent meetings
    if status['mongodb']:
        st.write("**📅 Recent Meetings**")
        recent_meetings = db_manager.get_recent_meetings(5)
        
        if recent_meetings:
            for meeting in recent_meetings:
                st.write(f"📝 **{meeting.get('meeting_title', 'Untitled')}** - {meeting.get('created_at', '').strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No meetings found.")

def main():
    """Main application"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 AI-Driven Meeting Summarizer</div>', unsafe_allow_html=True)
    
    # Database connection status
    if not st.session_state.get('db_connected', False):
        st.error(f"⚠️ **Database Connection Issue**: {st.session_state.get('db_error', 'Unknown error')}")
        st.info("""
        **To fix this issue:**
        1. Set up MongoDB Atlas (free tier available)
        2. Configure your connection string in Streamlit Cloud secrets
        3. Ensure network access allows connections from anywhere (0.0.0.0/0)
        
        **For local development:** Make sure MongoDB is running locally.
        """)
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📁 Upload", "🤖 Summary", "📋 Tasks", "📤 Export", "📊 Dashboard"]
    )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**ℹ️ About**")
    st.sidebar.markdown("""
    This AI-driven meeting summarizer uses:
    - **Ollama gemma:2b** for AI processing
    - **MongoDB** for data storage
    - **Whisper** for speech-to-text
    - **Streamlit** for the interface
    """)
    
    # Sidebar system status
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔧 System Status**")
    status = check_system_status()
    
    if status['mongodb']:
        st.sidebar.success("✅ MongoDB Connected")
    else:
        st.sidebar.error("❌ MongoDB Disconnected")
    
    if status['ollama']:
        st.sidebar.success("✅ Ollama Connected")
    else:
        st.sidebar.error("❌ Ollama Disconnected")
    
    if status['whisper']:
        st.sidebar.success("✅ Whisper Ready")
    else:
        st.sidebar.warning("⚠️ Whisper Limited")
    
    # Page routing
    if page == "📁 Upload":
        upload_page()
    elif page == "🤖 Summary":
        summary_page()
    elif page == "📋 Tasks":
        tasks_page()
    elif page == "📤 Export":
        export_page()
    elif page == "📊 Dashboard":
        dashboard_page()

if __name__ == "__main__":
    main()
