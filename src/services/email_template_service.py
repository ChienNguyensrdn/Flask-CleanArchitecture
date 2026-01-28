from typing import List, Optional, Dict, Any
from infrastructure.repositories.email_template_repository import EmailTemplateRepository, EmailLogRepository
from infrastructure.models.email_template_model import EmailTemplateModel, EmailLogModel
from datetime import datetime, timezone
import re


class EmailTemplateService:
    """Service for managing email templates"""
    
    def __init__(self, template_repository: EmailTemplateRepository, log_repository: EmailLogRepository):
        self.template_repository = template_repository
        self.log_repository = log_repository
    
    def create_template(self, template_data: Dict[str, Any]) -> EmailTemplateModel:
        """Create a new email template"""
        # Validate required fields
        required_fields = ['template_type', 'name', 'subject']
        for field in required_fields:
            if field not in template_data or not template_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Add timestamps
        template_data['created_at'] = datetime.now(timezone.utc)
        template_data['updated_at'] = datetime.now(timezone.utc)
        
        return self.template_repository.create(template_data)
    
    def get_template(self, template_id: int) -> Optional[EmailTemplateModel]:
        """Get email template by ID"""
        return self.template_repository.get_by_id(template_id)
    
    def get_template_by_type(self, template_type: str, conference_id: Optional[int] = None) -> Optional[EmailTemplateModel]:
        """Get email template by type"""
        return self.template_repository.get_by_type(template_type, conference_id)
    
    def list_conference_templates(self, conference_id: int) -> List[EmailTemplateModel]:
        """List all email templates for a conference"""
        return self.template_repository.get_by_conference(conference_id)
    
    def list_all_templates(self) -> List[EmailTemplateModel]:
        """List all email templates"""
        return self.template_repository.list_all()
    
    def update_template(self, template_id: int, template_data: Dict[str, Any]) -> Optional[EmailTemplateModel]:
        """Update an email template"""
        template = self.template_repository.get_by_id(template_id)
        if not template:
            return None
        
        # Update timestamps
        template_data['updated_at'] = datetime.now(timezone.utc)
        
        return self.template_repository.update(template_id, template_data)
    
    def delete_template(self, template_id: int) -> bool:
        """Delete (deactivate) an email template"""
        return self.template_repository.delete(template_id)
    
    def render_template(self, template_id: int, placeholders: Dict[str, str]) -> tuple[str, str]:
        """Render email template with placeholders"""
        template = self.template_repository.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
        
        subject = self._replace_placeholders(template.subject, placeholders)
        body_html = self._replace_placeholders(template.body_html or "", placeholders)
        
        return subject, body_html
    
    def _replace_placeholders(self, text: str, placeholders: Dict[str, str]) -> str:
        """Replace placeholders in text with actual values"""
        result = text
        for key, value in placeholders.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value) if value else "")
        return result
    
    def get_available_placeholders(self, template_type: str) -> List[str]:
        """Get available placeholders for a template type"""
        placeholders_map = {
            'submission_confirmation': [
                'author_name', 'paper_title', 'paper_id', 'conference_name', 
                'submission_date', 'submission_deadline'
            ],
            'pc_invitation': [
                'reviewer_name', 'conference_name', 'review_deadline', 
                'number_of_papers', 'review_platform_url'
            ],
            'review_assigned': [
                'reviewer_name', 'paper_title', 'paper_id', 'conference_name', 
                'review_deadline', 'review_platform_url'
            ],
            'review_reminder': [
                'reviewer_name', 'conference_name', 'pending_reviews_count', 
                'review_deadline'
            ],
            'decision_accept': [
                'author_name', 'paper_title', 'paper_id', 'conference_name', 
                'camera_ready_deadline', 'notification_date'
            ],
            'decision_reject': [
                'author_name', 'paper_title', 'paper_id', 'conference_name'
            ],
            'camera_ready_reminder': [
                'author_name', 'paper_title', 'paper_id', 'conference_name', 
                'camera_ready_deadline'
            ],
            'rebuttal_open': [
                'author_name', 'paper_title', 'paper_id', 'conference_name', 
                'rebuttal_deadline'
            ]
        }
        return placeholders_map.get(template_type, [])


class EmailLogService:
    """Service for managing email logs"""
    
    def __init__(self, repository: EmailLogRepository):
        self.repository = repository
    
    def log_email(self, log_data: Dict[str, Any]) -> EmailLogModel:
        """Log an email"""
        # Validate required fields
        required_fields = ['recipient_email', 'subject']
        for field in required_fields:
            if field not in log_data or not log_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Set default status
        if 'status' not in log_data:
            log_data['status'] = 'pending'
        
        # Add timestamp
        log_data['created_at'] = datetime.now(timezone.utc)
        
        return self.repository.create(log_data)
    
    def get_log(self, log_id: int) -> Optional[EmailLogModel]:
        """Get email log by ID"""
        return self.repository.get_by_id(log_id)
    
    def list_conference_logs(self, conference_id: int) -> List[EmailLogModel]:
        """List all email logs for a conference"""
        return self.repository.get_by_conference(conference_id)
    
    def list_recipient_logs(self, recipient_email: str) -> List[EmailLogModel]:
        """List all emails sent to a recipient"""
        return self.repository.get_by_recipient(recipient_email)
    
    def list_paper_logs(self, paper_id: int) -> List[EmailLogModel]:
        """List all emails related to a paper"""
        return self.repository.get_by_paper(paper_id)
    
    def list_logs_by_status(self, status: str) -> List[EmailLogModel]:
        """List emails by status"""
        return self.repository.list_by_status(status)
    
    def list_all_logs(self) -> List[EmailLogModel]:
        """List all email logs"""
        return self.repository.list_all()
    
    def mark_as_sent(self, log_id: int) -> Optional[EmailLogModel]:
        """Mark email as sent"""
        return self.repository.update_status(log_id, 'sent', datetime.now(timezone.utc))
    
    def mark_as_failed(self, log_id: int, error_message: str) -> Optional[EmailLogModel]:
        """Mark email as failed"""
        return self.repository.update_status(log_id, 'failed', None, error_message)
    
    def mark_as_bounced(self, log_id: int, error_message: str) -> Optional[EmailLogModel]:
        """Mark email as bounced"""
        return self.repository.update_status(log_id, 'bounced', None, error_message)
    
    def get_failed_emails(self) -> List[EmailLogModel]:
        """Get all failed emails"""
        return self.repository.list_by_status('failed')
    
    def get_pending_emails(self) -> List[EmailLogModel]:
        """Get all pending emails"""
        return self.repository.list_by_status('pending')
