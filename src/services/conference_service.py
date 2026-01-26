from typing import List, Optional, Dict, Any
from infrastructure.repositories.conference_repository import ConferenceRepository
from infrastructure.models.conference_model import ConferenceModel
from domain.exceptions import Exception as DomainException
from datetime import datetime


class ConferenceService:
    """Service for managing conference business logic"""
    
    def __init__(self, repository: ConferenceRepository):
        self.repository = repository
    
    def create_conference(self, conference_data: Dict[str, Any]) -> ConferenceModel:
        """Create a new conference"""
        # Validate required fields
        required_fields = ['tenant_id', 'name', 'short_name']
        for field in required_fields:
            if field not in conference_data or not conference_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if short_name already exists for this tenant
        existing = self.repository.get_by_short_name(
            conference_data['short_name'],
            conference_data['tenant_id']
        )
        if existing:
            raise ValueError(f"Short name '{conference_data['short_name']}' already exists for this tenant")
        
        # Set default status
        if 'status' not in conference_data:
            conference_data['status'] = 'draft'
        
        # Add timestamps
        conference_data['created_at'] = datetime.utcnow()
        conference_data['updated_at'] = datetime.utcnow()
        
        return self.repository.create(conference_data)
    
    def get_conference(self, conference_id: int) -> Optional[ConferenceModel]:
        """Get conference by ID"""
        return self.repository.get_by_id(conference_id)
    
    def get_conference_by_short_name(self, short_name: str, tenant_id: int) -> Optional[ConferenceModel]:
        """Get conference by short name"""
        return self.repository.get_by_short_name(short_name, tenant_id)
    
    def list_tenant_conferences(self, tenant_id: int) -> List[ConferenceModel]:
        """List all conferences for a tenant"""
        return self.repository.get_by_tenant(tenant_id)
    
    def list_all_conferences(self) -> List[ConferenceModel]:
        """List all conferences"""
        return self.repository.list_all()
    
    def get_public_cfp_conferences(self) -> List[ConferenceModel]:
        """Get all conferences with public CFP"""
        return self.repository.list_public_cfp()
    
    def update_conference(self, conference_id: int, conference_data: Dict[str, Any]) -> Optional[ConferenceModel]:
        """Update a conference"""
        conference = self.repository.get_by_id(conference_id)
        if not conference:
            return None
        
        # Prevent updating tenant_id
        if 'tenant_id' in conference_data:
            del conference_data['tenant_id']
        
        # Update timestamps
        conference_data['updated_at'] = datetime.utcnow()
        
        return self.repository.update(conference_id, conference_data)
    
    def delete_conference(self, conference_id: int) -> bool:
        """Delete a conference"""
        return self.repository.delete(conference_id)
    
    def publish_cfp(self, conference_id: int, cfp_content: str) -> Optional[ConferenceModel]:
        """Publish CFP for a conference"""
        conference = self.repository.get_by_id(conference_id)
        if not conference:
            return None
        
        # Update CFP content and make it public
        return self.repository.update_cfp_content(conference_id, cfp_content, True)
    
    def unpublish_cfp(self, conference_id: int) -> Optional[ConferenceModel]:
        """Unpublish CFP for a conference"""
        conference = self.repository.get_by_id(conference_id)
        if not conference:
            return None
        
        return self.repository.update(conference_id, {'cfp_is_public': False})
    
    def change_conference_status(self, conference_id: int, status: str) -> Optional[ConferenceModel]:
        """Change conference status"""
        valid_statuses = ['draft', 'open', 'reviewing', 'decided', 'published']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return self.repository.update_status(conference_id, status)
    
    def get_submission_deadline(self, conference_id: int) -> Optional[datetime]:
        """Get submission deadline for a conference"""
        conference = self.repository.get_by_id(conference_id)
        if conference:
            return conference.submission_deadline
        return None
    
    def is_cfp_open(self, conference_id: int) -> bool:
        """Check if CFP is open for a conference"""
        conference = self.repository.get_by_id(conference_id)
        if not conference:
            return False
        
        if not conference.cfp_is_public or conference.status not in ['open', 'reviewing']:
            return False
        
        if conference.submission_deadline and conference.submission_deadline < datetime.utcnow():
            return False
        
        return True
