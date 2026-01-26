from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.conference_model import ConferenceModel
from datetime import datetime


class ConferenceRepository:
    """Repository for managing Conference database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, conference_data: dict) -> ConferenceModel:
        """Create a new conference"""
        try:
            db_conference = ConferenceModel(**conference_data)
            self.session.add(db_conference)
            self.session.commit()
            self.session.refresh(db_conference)
            return db_conference
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, conference_id: int) -> Optional[ConferenceModel]:
        """Get conference by ID"""
        return self.session.query(ConferenceModel).filter(
            ConferenceModel.id == conference_id
        ).first()
    
    def get_by_tenant(self, tenant_id: int) -> List[ConferenceModel]:
        """Get all conferences for a tenant"""
        return self.session.query(ConferenceModel).filter(
            ConferenceModel.tenant_id == tenant_id
        ).all()
    
    def get_by_short_name(self, short_name: str, tenant_id: int) -> Optional[ConferenceModel]:
        """Get conference by short name within a tenant"""
        return self.session.query(ConferenceModel).filter(
            ConferenceModel.short_name == short_name,
            ConferenceModel.tenant_id == tenant_id
        ).first()
    
    def list_all(self) -> List[ConferenceModel]:
        """Get all conferences"""
        return self.session.query(ConferenceModel).all()
    
    def list_public_cfp(self) -> List[ConferenceModel]:
        """Get all conferences with public CFP"""
        return self.session.query(ConferenceModel).filter(
            ConferenceModel.cfp_is_public == True,
            ConferenceModel.status.in_(['open', 'reviewing'])
        ).all()
    
    def update(self, conference_id: int, conference_data: dict) -> Optional[ConferenceModel]:
        """Update an existing conference"""
        try:
            db_conference = self.get_by_id(conference_id)
            if not db_conference:
                return None
            
            for key, value in conference_data.items():
                if hasattr(db_conference, key):
                    setattr(db_conference, key, value)
            
            db_conference.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_conference)
            return db_conference
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, conference_id: int) -> bool:
        """Delete a conference"""
        try:
            db_conference = self.get_by_id(conference_id)
            if not db_conference:
                return False
            
            self.session.delete(db_conference)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_status(self, conference_id: int, status: str) -> Optional[ConferenceModel]:
        """Update conference status"""
        return self.update(conference_id, {'status': status})
    
    def update_cfp_content(self, conference_id: int, cfp_content: str, is_public: bool) -> Optional[ConferenceModel]:
        """Update CFP content and visibility"""
        return self.update(conference_id, {
            'cfp_content': cfp_content,
            'cfp_is_public': is_public
        })
