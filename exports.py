"""
Export functionality for CSV and PDF formats
"""
import os
import io
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from fpdf import FPDF
from db import get_db_manager
from task_manager import get_task_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExportManager:
    """Handles export functionality for summaries and tasks"""
    
    def __init__(self):
        """Initialize the export manager"""
        self.db_manager = get_db_manager()
        self.task_manager = get_task_manager()
    
    def export_summary_to_csv(self, summary_id: str) -> bytes:
        """
        Export a meeting summary to CSV format
        
        Args:
            summary_id: ID of the summary to export
            
        Returns:
            bytes: CSV content as bytes
        """
        try:
            summary = self.db_manager.get_summary(summary_id)
            if not summary:
                raise ValueError(f"Summary not found: {summary_id}")
            
            # Prepare data for CSV
            data = {
                'Meeting Title': [summary.get('meeting_title', 'Untitled Meeting')],
                'Summary': [summary.get('summary', '')],
                'Created At': [summary.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if summary.get('created_at') else ''],
                'Model Used': [summary.get('model_used', '')],
                'Transcript Length': [summary.get('transcript_length', 0)]
            }
            
            df = pd.DataFrame(data)
            
            # Convert to CSV bytes
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue().encode('utf-8')
            csv_buffer.close()
            
            logger.info(f"Exported summary {summary_id} to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting summary to CSV: {e}")
            raise
    
    def export_tasks_to_csv(self, filters: Dict = None) -> bytes:
        """
        Export tasks to CSV format
        
        Args:
            filters: Optional filters for tasks
            
        Returns:
            bytes: CSV content as bytes
        """
        try:
            tasks = self.task_manager.get_tasks(filters)
            
            if not tasks:
                # Create empty DataFrame with expected columns
                data = {
                    'Task': [],
                    'Assignee': [],
                    'Priority': [],
                    'Status': [],
                    'Deadline': [],
                    'Context': [],
                    'Created At': [],
                    'Updated At': []
                }
            else:
                # Prepare data for CSV
                data = {
                    'Task': [task.get('task', '') for task in tasks],
                    'Assignee': [task.get('assignee', '') for task in tasks],
                    'Priority': [task.get('priority', '') for task in tasks],
                    'Status': [task.get('status', '') for task in tasks],
                    'Deadline': [task.get('actual_deadline', '') for task in tasks],
                    'Context': [task.get('context', '') for task in tasks],
                    'Created At': [task.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if task.get('created_at') else '' for task in tasks],
                    'Updated At': [task.get('updated_at', '').strftime('%Y-%m-%d %H:%M:%S') if task.get('updated_at') else '' for task in tasks]
                }
            
            df = pd.DataFrame(data)
            
            # Convert to CSV bytes
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue().encode('utf-8')
            csv_buffer.close()
            
            logger.info(f"Exported {len(tasks)} tasks to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting tasks to CSV: {e}")
            raise
    
    def export_meeting_report_to_csv(self, summary_id: str) -> bytes:
        """
        Export complete meeting report (summary + tasks) to CSV
        
        Args:
            summary_id: ID of the summary to export
            
        Returns:
            bytes: CSV content as bytes
        """
        try:
            summary = self.db_manager.get_summary(summary_id)
            if not summary:
                raise ValueError(f"Summary not found: {summary_id}")
            
            # Get related tasks
            meeting_id = summary.get('meeting_id')
            tasks = self.task_manager.get_tasks({'meeting_id': meeting_id}) if meeting_id else []
            
            # Prepare summary data
            summary_data = {
                'Type': ['Summary'],
                'Content': [summary.get('summary', '')],
                'Assignee': [''],
                'Priority': [''],
                'Status': [''],
                'Deadline': [''],
                'Context': [''],
                'Created At': [summary.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if summary.get('created_at') else '']
            }
            
            # Prepare tasks data
            tasks_data = {
                'Type': ['Task'] * len(tasks),
                'Content': [task.get('task', '') for task in tasks],
                'Assignee': [task.get('assignee', '') for task in tasks],
                'Priority': [task.get('priority', '') for task in tasks],
                'Status': [task.get('status', '') for task in tasks],
                'Deadline': [task.get('actual_deadline', '') for task in tasks],
                'Context': [task.get('context', '') for task in tasks],
                'Created At': [task.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if task.get('created_at') else '' for task in tasks]
            }
            
            # Combine data
            combined_data = {
                'Type': summary_data['Type'] + tasks_data['Type'],
                'Content': summary_data['Content'] + tasks_data['Content'],
                'Assignee': summary_data['Assignee'] + tasks_data['Assignee'],
                'Priority': summary_data['Priority'] + tasks_data['Priority'],
                'Status': summary_data['Status'] + tasks_data['Status'],
                'Deadline': summary_data['Deadline'] + tasks_data['Deadline'],
                'Context': summary_data['Context'] + tasks_data['Context'],
                'Created At': summary_data['Created At'] + tasks_data['Created At']
            }
            
            df = pd.DataFrame(combined_data)
            
            # Convert to CSV bytes
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue().encode('utf-8')
            csv_buffer.close()
            
            logger.info(f"Exported meeting report {summary_id} to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting meeting report to CSV: {e}")
            raise
    
    def export_summary_to_pdf(self, summary_id: str) -> bytes:
        """
        Export a meeting summary to PDF format
        
        Args:
            summary_id: ID of the summary to export
            
        Returns:
            bytes: PDF content as bytes
        """
        try:
            summary = self.db_manager.get_summary(summary_id)
            if not summary:
                raise ValueError(f"Summary not found: {summary_id}")
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Set font
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, summary.get('meeting_title', 'Untitled Meeting'), 0, 1, 'C')
            pdf.ln(5)
            
            # Add metadata
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"Created: {summary.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if summary.get('created_at') else ''}", 0, 1)
            pdf.cell(0, 5, f"Model: {summary.get('model_used', '')}", 0, 1)
            pdf.cell(0, 5, f"Transcript Length: {summary.get('transcript_length', 0)} characters", 0, 1)
            pdf.ln(5)
            
            # Add summary content
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Meeting Summary', 0, 1)
            pdf.ln(2)
            
            pdf.set_font('Arial', '', 10)
            summary_text = summary.get('summary', '')
            
            # Split text into lines that fit the page
            lines = summary_text.split('\n')
            for line in lines:
                if line.strip():
                    pdf.multi_cell(0, 5, line.strip())
                    pdf.ln(1)
            
            # Convert to bytes
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            logger.info(f"Exported summary {summary_id} to PDF")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error exporting summary to PDF: {e}")
            raise
    
    def export_meeting_report_to_pdf(self, summary_id: str) -> bytes:
        """
        Export complete meeting report (summary + tasks) to PDF
        
        Args:
            summary_id: ID of the summary to export
            
        Returns:
            bytes: PDF content as bytes
        """
        try:
            summary = self.db_manager.get_summary(summary_id)
            if not summary:
                raise ValueError(f"Summary not found: {summary_id}")
            
            # Get related tasks
            meeting_id = summary.get('meeting_id')
            tasks = self.task_manager.get_tasks({'meeting_id': meeting_id}) if meeting_id else []
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Set font
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, summary.get('meeting_title', 'Untitled Meeting'), 0, 1, 'C')
            pdf.ln(5)
            
            # Add metadata
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f"Created: {summary.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if summary.get('created_at') else ''}", 0, 1)
            pdf.cell(0, 5, f"Model: {summary.get('model_used', '')}", 0, 1)
            pdf.cell(0, 5, f"Transcript Length: {summary.get('transcript_length', 0)} characters", 0, 1)
            pdf.ln(5)
            
            # Add summary content
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Meeting Summary', 0, 1)
            pdf.ln(2)
            
            pdf.set_font('Arial', '', 10)
            summary_text = summary.get('summary', '')
            
            # Split text into lines that fit the page
            lines = summary_text.split('\n')
            for line in lines:
                if line.strip():
                    pdf.multi_cell(0, 5, line.strip())
                    pdf.ln(1)
            
            pdf.ln(5)
            
            # Add action items/tasks
            if tasks:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'Action Items', 0, 1)
                pdf.ln(2)
                
                pdf.set_font('Arial', '', 10)
                for i, task in enumerate(tasks, 1):
                    pdf.cell(0, 5, f"{i}. {task.get('task', '')}", 0, 1)
                    pdf.cell(0, 5, f"   Assignee: {task.get('assignee', 'TBD')}", 0, 1)
                    pdf.cell(0, 5, f"   Priority: {task.get('priority', 'medium')}", 0, 1)
                    pdf.cell(0, 5, f"   Deadline: {task.get('actual_deadline', 'TBD')}", 0, 1)
                    pdf.cell(0, 5, f"   Status: {task.get('status', 'pending')}", 0, 1)
                    if task.get('context'):
                        pdf.cell(0, 5, f"   Context: {task.get('context', '')}", 0, 1)
                    pdf.ln(2)
            
            # Convert to bytes
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            logger.info(f"Exported meeting report {summary_id} to PDF")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error exporting meeting report to PDF: {e}")
            raise
    
    def export_task_statistics_to_csv(self) -> bytes:
        """
        Export task statistics to CSV
        
        Returns:
            bytes: CSV content as bytes
        """
        try:
            stats = self.task_manager.get_task_statistics()
            
            # Prepare data for CSV
            data = {
                'Metric': ['Total Tasks', 'Pending Tasks', 'In Progress Tasks', 'Completed Tasks', 'Overdue Tasks', 'Upcoming Tasks'],
                'Count': [
                    stats['total_tasks'],
                    stats['pending_tasks'],
                    stats['in_progress_tasks'],
                    stats['completed_tasks'],
                    stats['overdue_tasks'],
                    stats['upcoming_tasks']
                ]
            }
            
            df = pd.DataFrame(data)
            
            # Convert to CSV bytes
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue().encode('utf-8')
            csv_buffer.close()
            
            logger.info("Exported task statistics to CSV")
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting task statistics to CSV: {e}")
            raise
    
    def get_export_filename(self, export_type: str, summary_id: str = None) -> str:
        """
        Generate appropriate filename for export
        
        Args:
            export_type: Type of export (summary, tasks, report, statistics)
            summary_id: Optional summary ID for context
            
        Returns:
            str: Generated filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_type == 'summary':
            return f"meeting_summary_{timestamp}.csv"
        elif export_type == 'tasks':
            return f"tasks_{timestamp}.csv"
        elif export_type == 'report':
            return f"meeting_report_{timestamp}.csv"
        elif export_type == 'statistics':
            return f"task_statistics_{timestamp}.csv"
        elif export_type == 'summary_pdf':
            return f"meeting_summary_{timestamp}.pdf"
        elif export_type == 'report_pdf':
            return f"meeting_report_{timestamp}.pdf"
        else:
            return f"export_{timestamp}.csv"

# Global export manager instance
export_manager = ExportManager()

def get_export_manager() -> ExportManager:
    """Get the global export manager instance"""
    return export_manager
