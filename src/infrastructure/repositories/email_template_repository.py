from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.email_template_model import EmailTemplateModel, EmailLogModel
from datetime import datetime


class EmailTemplateRepository:
    """Repository for managing Email Template database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, template_data: dict) -> EmailTemplateModel:
        """Create a new email template"""
        try:
            db_template = EmailTemplateModel(**template_data)
            self.session.add(db_template)
            self.session.commit()
            self.session.refresh(db_template)
            return db_template
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, template_id: int) -> Optional[EmailTemplateModel]:
        """Get email template by ID"""
        return self.session.query(EmailTemplateModel).filter(
            EmailTemplateModel.id == template_id
        ).first()
    
    def get_by_type(self, template_type: str, conference_id: Optional[int] = None) -> Optional[EmailTemplateModel]:
        """Get email template by type"""
        query = self.session.query(EmailTemplateModel).filter(
            EmailTemplateModel.template_type == template_type,
            EmailTemplateModel.is_active == True
        )
        
        if conference_id:
            # Try to get conference-specific template first, then fall back to system default
            query = query.filter(
                (EmailTemplateModel.conference_id == conference_id) | 
                (EmailTemplateModel.conference_id == None)
            )
        else:
            query = query.filter(EmailTemplateModel.conference_id == None)
        
        return query.first()
    
    def get_by_conference(self, conference_id: int) -> List[EmailTemplateModel]:
        """Get all email templates for a conference"""
        return self.session.query(EmailTemplateModel).filter(
            EmailTemplateModel.conference_id == conference_id,
            EmailTemplateModel.is_active == True
        ).all()
    
    def list_by_type(self, template_type: str) -> List[EmailTemplateModel]:
        """List all templates of a specific type"""
        return self.session.query(EmailTemplateModel).filter(
            EmailTemplateModel.template_type == template_type,
            EmailTemplateModel.is_active == True
        ).all()
    
    def list_all(self) -> List[EmailTemplateModel]:
        """Get all email templates"""
        return self.session.query(EmailTemplateModel).all()
    
    def update(self, template_id: int, template_data: dict) -> Optional[EmailTemplateModel]:
        """Update an existing email template"""
        try:
            db_template = self.get_by_id(template_id)
            if not db_template:
                return None
            
            for key, value in template_data.items():
                if hasattr(db_template, key):
                    setattr(db_template, key, value)
            
            db_template.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_template)
            return db_template
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, template_id: int) -> bool:
        """Delete an email template (soft delete by marking inactive)"""
        try:
            db_template = self.get_by_id(template_id)
            if not db_template:
                return False
            
            db_template.is_active = False
            db_template.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e


class EmailLogRepository:
    """Repository for managing Email Log database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, log_data: dict) -> EmailLogModel:
        """Create a new email log entry"""
        try:
            db_log = EmailLogModel(**log_data)
            self.session.add(db_log)
            self.session.commit()
            self.session.refresh(db_log)
            return db_log
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, log_id: int) -> Optional[EmailLogModel]:
        """Get email log by ID"""
        return self.session.query(EmailLogModel).filter(
            EmailLogModel.id == log_id
        ).first()
    
    def get_by_conference(self, conference_id: int) -> List[EmailLogModel]:
        """Get all email logs for a conference"""
        return self.session.query(EmailLogModel).filter(
            EmailLogModel.conference_id == conference_id
        ).order_by(EmailLogModel.created_at.desc()).all()
    
    def get_by_recipient(self, recipient_email: str) -> List[EmailLogModel]:
        """Get all emails sent to a recipient"""
        return self.session.query(EmailLogModel).filter(
            EmailLogModel.recipient_email == recipient_email
        ).order_by(EmailLogModel.created_at.desc()).all()
    
    def get_by_paper(self, paper_id: int) -> List[EmailLogModel]:
        """Get all emails related to a paper"""
        return self.session.query(EmailLogModel).filter(
            EmailLogModel.paper_id == paper_id
        ).order_by(EmailLogModel.created_at.desc()).all()
    
    def list_by_status(self, status: str) -> List[EmailLogModel]:
        """Get emails by status"""
        return self.session.query(EmailLogModel).filter(
            EmailLogModel.status == status
        ).order_by(EmailLogModel.created_at.desc()).all()
    
    def list_all(self) -> List[EmailLogModel]:
        """Get all email logs"""
        return self.session.query(EmailLogModel).order_by(
            EmailLogModel.created_at.desc()
        ).all()
    
    def update_status(self, log_id: int, status: str, sent_at: Optional[datetime] = None, error_message: Optional[str] = None) -> Optional[EmailLogModel]:
        """Update email log status"""
        try:
            db_log = self.get_by_id(log_id)
            if not db_log:
                return None
            
            db_log.status = status
            if sent_at:
                db_log.sent_at = sent_at
            if error_message:
                db_log.error_message = error_message
            
            self.session.commit()
            self.session.refresh(db_log)
            return db_log
        except Exception as e:
            self.session.rollback()
            raise e
