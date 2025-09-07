"""
Ollama NLP module for meeting summarization and action item extraction using gemma:2b
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
import requests
import ollama
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaNLPProcessor:
    """Handles AI processing using Ollama gemma:2b model"""
    
    def __init__(self):
        """Initialize the Ollama NLP processor"""
        self.model_name = "gemma:2b"
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.client = ollama.Client(host=self.base_url)
        self._ensure_model_available()
    
    def _ensure_model_available(self):
        """Ensure the gemma:2b model is available"""
        try:
            # Check if model is available
            models = self.client.list()
            model_names = [model['name'] for model in models['models']]
            
            if self.model_name not in model_names:
                logger.info(f"Pulling {self.model_name} model...")
                self.client.pull(self.model_name)
                logger.info(f"Successfully pulled {self.model_name}")
            else:
                logger.info(f"Model {self.model_name} is available")
        except Exception as e:
            logger.error(f"Error ensuring model availability: {e}")
            raise
    
    def summarize_meeting(self, transcript_text: str, meeting_title: str = None) -> Dict:
        """
        Generate a meeting summary using gemma:2b
        
        Args:
            transcript_text: The meeting transcript text
            meeting_title: Optional meeting title
            
        Returns:
            Dictionary containing the summary and metadata
        """
        try:
            # Truncate transcript if too long (gemma:2b has context limits)
            max_length = 4000  # Conservative limit for gemma:2b
            if len(transcript_text) > max_length:
                transcript_text = transcript_text[:max_length] + "..."
                logger.warning(f"Transcript truncated to {max_length} characters")
            
            prompt = self._create_summary_prompt(transcript_text, meeting_title)
            
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.3,  # Lower temperature for more focused summaries
                    'top_p': 0.9
                }
            )
            
            summary_text = response['message']['content'].strip()
            
            return {
                'summary': summary_text,
                'meeting_title': meeting_title or "Untitled Meeting",
                'transcript_length': len(transcript_text),
                'model_used': self.model_name,
                'created_at': datetime.utcnow(),
                'processing_method': 'ollama_gemma2b'
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def extract_action_items(self, transcript_text: str, summary_text: str = None) -> List[Dict]:
        """
        Extract action items from meeting transcript
        
        Args:
            transcript_text: The meeting transcript text
            summary_text: Optional summary text for context
            
        Returns:
            List of action item dictionaries
        """
        try:
            # Truncate transcript if too long
            max_length = 3000
            if len(transcript_text) > max_length:
                transcript_text = transcript_text[:max_length] + "..."
            
            prompt = self._create_action_items_prompt(transcript_text, summary_text)
            
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.2,  # Very low temperature for structured extraction
                    'top_p': 0.8
                }
            )
            
            action_items_text = response['message']['content'].strip()
            action_items = self._parse_action_items(action_items_text)
            
            # Enhance action items with suggested deadlines
            enhanced_items = []
            for item in action_items:
                item['suggested_deadline'] = self._suggest_deadline(item.get('task', ''))
                item['created_at'] = datetime.utcnow()
                enhanced_items.append(item)
            
            return enhanced_items
        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            raise
    
    def _create_summary_prompt(self, transcript_text: str, meeting_title: str = None) -> str:
        """Create prompt for meeting summarization"""
        title_context = f"Meeting: {meeting_title}\n\n" if meeting_title else ""
        
        prompt = f"""Please provide a concise summary of the following meeting transcript. 
Focus on key decisions, important discussions, and main outcomes.

{title_context}Meeting Transcript:
{transcript_text}

Please provide a summary that:
1. Captures the main topics discussed
2. Highlights key decisions made
3. Notes important outcomes or conclusions
4. Is approximately 200-300 words
5. Is clear and professional

Summary:"""
        
        return prompt
    
    def _create_action_items_prompt(self, transcript_text: str, summary_text: str = None) -> str:
        """Create prompt for action item extraction"""
        summary_context = f"Meeting Summary: {summary_text}\n\n" if summary_text else ""
        
        prompt = f"""Please extract action items from the following meeting transcript. 
For each action item, identify the task, assignee (if mentioned), and priority level.

{summary_context}Meeting Transcript:
{transcript_text}

Please extract action items in the following JSON format:
[
    {{
        "task": "Description of the task",
        "assignee": "Person responsible (or 'TBD' if not specified)",
        "priority": "high/medium/low",
        "context": "Brief context or additional notes"
    }}
]

If no action items are found, return an empty array: []

Focus on:
- Specific tasks that need to be completed
- Who is responsible for each task
- Priority level based on urgency and importance
- Clear, actionable task descriptions

Action Items:"""
        
        return prompt
    
    def _parse_action_items(self, action_items_text: str) -> List[Dict]:
        """Parse action items from the model response"""
        try:
            # Try to extract JSON from the response
            if '[' in action_items_text and ']' in action_items_text:
                # Find JSON array in the response
                start_idx = action_items_text.find('[')
                end_idx = action_items_text.rfind(']') + 1
                json_text = action_items_text[start_idx:end_idx]
                
                action_items = json.loads(json_text)
                
                # Validate and clean the action items
                cleaned_items = []
                for item in action_items:
                    if isinstance(item, dict) and 'task' in item:
                        cleaned_item = {
                            'task': item.get('task', '').strip(),
                            'assignee': item.get('assignee', 'TBD').strip(),
                            'priority': item.get('priority', 'medium').lower(),
                            'context': item.get('context', '').strip()
                        }
                        # Validate priority
                        if cleaned_item['priority'] not in ['high', 'medium', 'low']:
                            cleaned_item['priority'] = 'medium'
                        cleaned_items.append(cleaned_item)
                
                return cleaned_items
            else:
                # Fallback: try to extract action items from text
                return self._extract_action_items_from_text(action_items_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, trying text extraction")
            return self._extract_action_items_from_text(action_items_text)
        except Exception as e:
            logger.error(f"Error parsing action items: {e}")
            return []
    
    def _extract_action_items_from_text(self, text: str) -> List[Dict]:
        """Fallback method to extract action items from unstructured text"""
        lines = text.split('\n')
        action_items = []
        
        for line in lines:
            line = line.strip()
            if line and ('task' in line.lower() or 'action' in line.lower() or 'todo' in line.lower()):
                # Simple extraction - look for patterns
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        task = parts[1].strip()
                        if task:
                            action_items.append({
                                'task': task,
                                'assignee': 'TBD',
                                'priority': 'medium',
                                'context': ''
                            })
        
        return action_items
    
    def _suggest_deadline(self, task_text: str) -> str:
        """Suggest a deadline based on task content"""
        task_lower = task_text.lower()
        
        # Keywords that suggest urgency
        urgent_keywords = ['urgent', 'asap', 'immediately', 'today', 'tomorrow', 'deadline', 'critical']
        medium_keywords = ['next week', 'soon', 'priority', 'important']
        
        if any(keyword in task_lower for keyword in urgent_keywords):
            days_ahead = 1
        elif any(keyword in task_lower for keyword in medium_keywords):
            days_ahead = 3
        else:
            days_ahead = 7  # Default: 1 week
        
        deadline = datetime.utcnow() + timedelta(days=days_ahead)
        return deadline.strftime('%Y-%m-%d')
    
    def process_meeting(self, transcript_text: str, meeting_title: str = None) -> Dict:
        """
        Process a complete meeting: generate summary and extract action items
        
        Args:
            transcript_text: The meeting transcript text
            meeting_title: Optional meeting title
            
        Returns:
            Dictionary containing summary and action items
        """
        try:
            logger.info("Starting meeting processing...")
            
            # Generate summary
            summary_result = self.summarize_meeting(transcript_text, meeting_title)
            
            # Extract action items
            action_items = self.extract_action_items(transcript_text, summary_result['summary'])
            
            result = {
                'summary': summary_result,
                'action_items': action_items,
                'processing_completed_at': datetime.utcnow(),
                'total_action_items': len(action_items)
            }
            
            logger.info(f"Meeting processing completed. Found {len(action_items)} action items.")
            return result
            
        except Exception as e:
            logger.error(f"Error processing meeting: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to Ollama service"""
        try:
            models = self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False

# Global Ollama NLP processor instance
ollama_processor = OllamaNLPProcessor()

def get_ollama_processor() -> OllamaNLPProcessor:
    """Get the global Ollama NLP processor instance"""
    return ollama_processor
