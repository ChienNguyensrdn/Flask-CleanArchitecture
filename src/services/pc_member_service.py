from typing import List, Optional, Dict, Any
from infrastructure.repositories.pc_member_repository import PCMemberRepository, COIRepository
from infrastructure.models.pc_member_model import PCMemberModel
from infrastructure.models.coi_model import COIModel
from datetime import datetime, timedelta


class PCMemberService:
    """Service for managing PC members"""
    
    def __init__(self, repository: PCMemberRepository, coi_repository: COIRepository):
        self.repository = repository
        self.coi_repository = coi_repository
    
    def invite_pc_member(self, member_data: Dict[str, Any]) -> PCMemberModel:
        """Invite a PC member"""
        # Validate required fields
        required_fields = ['conference_id', 'user_id', 'role']
        for field in required_fields:
            if field not in member_data or not member_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if already a member
        existing = self.repository.get_by_conference_and_user(
            member_data['conference_id'],
            member_data['user_id']
        )
        if existing:
            raise ValueError("User is already a PC member for this conference")
        
        # Add timestamps
        member_data['invitation_sent_at'] = datetime.utcnow()
        member_data['invitation_status'] = 'pending'
        member_data['created_at'] = datetime.utcnow()
        member_data['updated_at'] = datetime.utcnow()
        
        return self.repository.create(member_data)
    
    def get_member(self, member_id: int) -> Optional[PCMemberModel]:
        """Get PC member by ID"""
        return self.repository.get_by_id(member_id)
    
    def list_conference_members(self, conference_id: int) -> List[PCMemberModel]:
        """List all PC members for a conference"""
        return self.repository.get_by_conference(conference_id)
    
    def list_track_members(self, track_id: int) -> List[PCMemberModel]:
        """List all PC members for a track"""
        return self.repository.get_by_track(track_id)
    
    def list_members_by_role(self, conference_id: int, role: str) -> List[PCMemberModel]:
        """List PC members by role"""
        return self.repository.get_by_role(conference_id, role)
    
    def list_active_reviewers(self, conference_id: int) -> List[PCMemberModel]:
        """List active reviewers for a conference"""
        return self.repository.get_active_reviewers(conference_id)
    
    def accept_invitation(self, member_id: int) -> Optional[PCMemberModel]:
        """Accept PC invitation"""
        return self.repository.update_invitation_status(member_id, 'accepted')
    
    def decline_invitation(self, member_id: int) -> Optional[PCMemberModel]:
        """Decline PC invitation"""
        return self.repository.update_invitation_status(member_id, 'declined')
    
    def resend_invitation(self, member_id: int) -> Optional[PCMemberModel]:
        """Resend invitation to PC member"""
        return self.repository.send_invitation(member_id)
    
    def update_member(self, member_id: int, member_data: Dict[str, Any]) -> Optional[PCMemberModel]:
        """Update PC member"""
        member = self.repository.get_by_id(member_id)
        if not member:
            return None
        
        # Prevent updating conference_id and user_id
        if 'conference_id' in member_data:
            del member_data['conference_id']
        if 'user_id' in member_data:
            del member_data['user_id']
        
        member_data['updated_at'] = datetime.utcnow()
        return self.repository.update(member_id, member_data)
    
    def remove_member(self, member_id: int) -> bool:
        """Remove PC member (soft delete)"""
        return self.repository.delete(member_id)
    
    def change_role(self, member_id: int, new_role: str) -> Optional[PCMemberModel]:
        """Change PC member role"""
        valid_roles = ['reviewer', 'senior_pc', 'track_chair', 'program_chair', 'general_chair']
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        return self.repository.update(member_id, {'role': new_role})
    
    def assign_track(self, member_id: int, track_id: int) -> Optional[PCMemberModel]:
        """Assign PC member to track"""
        return self.repository.update(member_id, {'track_id': track_id})
    
    def update_expertise(self, member_id: int, expertise_keywords: str) -> Optional[PCMemberModel]:
        """Update PC member expertise keywords"""
        return self.repository.update(member_id, {'expertise_keywords': expertise_keywords})
    
    def set_review_quota(self, member_id: int, max_papers: int) -> Optional[PCMemberModel]:
        """Set maximum papers for review"""
        if max_papers < 1 or max_papers > 100:
            raise ValueError("Max papers must be between 1 and 100")
        
        return self.repository.update(member_id, {'max_papers': max_papers})
    
    def get_available_capacity(self, member_id: int) -> int:
        """Get available review capacity"""
        return self.repository.get_available_capacity(member_id)
    
    def can_review_paper(self, member_id: int) -> bool:
        """Check if member can review more papers"""
        capacity = self.get_available_capacity(member_id)
        return capacity > 0
    
    def enable_author_access(self, member_id: int) -> Optional[PCMemberModel]:
        """Enable author info access for member"""
        return self.repository.update(member_id, {'can_access_author_info': True})
    
    def disable_author_access(self, member_id: int) -> Optional[PCMemberModel]:
        """Disable author info access for member"""
        return self.repository.update(member_id, {'can_access_author_info': False})
    
    def get_members_by_invitation_status(self, conference_id: int, status: str) -> List[PCMemberModel]:
        """Get members by invitation status"""
        return self.repository.get_by_invitation_status(conference_id, status)
    
    def get_pending_invitations(self, conference_id: int) -> List[PCMemberModel]:
        """Get pending invitations for a conference"""
        return self.get_members_by_invitation_status(conference_id, 'pending')


class COIService:
    """Service for managing conflicts of interest"""
    
    def __init__(self, repository: COIRepository):
        self.repository = repository
    
    def declare_coi(self, coi_data: Dict[str, Any]) -> COIModel:
        """Declare a conflict of interest"""
        # Validate
        if 'pc_member_id' not in coi_data or not coi_data['pc_member_id']:
            raise ValueError("PC member ID is required")
        
        if 'conflict_type' not in coi_data or not coi_data['conflict_type']:
            raise ValueError("Conflict type is required")
        
        # At least one of paper_id or author_user_id should be provided
        if not coi_data.get('paper_id') and not coi_data.get('author_user_id'):
            raise ValueError("Either paper_id or author_user_id must be provided")
        
        # Set defaults
        coi_data['declared_by'] = coi_data.get('declared_by', 'self')
        coi_data['is_active'] = True
        coi_data['created_at'] = datetime.utcnow()
        
        return self.repository.create(coi_data)
    
    def get_coi(self, coi_id: int) -> Optional[COIModel]:
        """Get COI by ID"""
        return self.repository.get_by_id(coi_id)
    
    def list_member_cois(self, pc_member_id: int) -> List[COIModel]:
        """List all COIs for a PC member"""
        return self.repository.get_by_pc_member(pc_member_id)
    
    def list_paper_cois(self, paper_id: int) -> List[COIModel]:
        """List all COIs for a paper"""
        return self.repository.get_by_paper(paper_id)
    
    def check_member_paper_conflict(self, pc_member_id: int, paper_id: int) -> bool:
        """Check if member has conflict with paper"""
        return self.repository.check_conflict(pc_member_id, paper_id)
    
    def get_member_paper_conflict(self, pc_member_id: int, paper_id: int) -> Optional[COIModel]:
        """Get conflict between member and paper"""
        return self.repository.get_by_pc_member_and_paper(pc_member_id, paper_id)
    
    def list_member_author_conflicts(self, pc_member_id: int, author_user_id: int) -> List[COIModel]:
        """Get conflicts between member and author"""
        return self.repository.get_by_pc_member_and_author(pc_member_id, author_user_id)
    
    def update_coi(self, coi_id: int, coi_data: Dict[str, Any]) -> Optional[COIModel]:
        """Update a COI"""
        coi = self.repository.get_by_id(coi_id)
        if not coi:
            return None
        
        # Prevent updating pc_member_id
        if 'pc_member_id' in coi_data:
            del coi_data['pc_member_id']
        
        return self.repository.update(coi_id, coi_data)
    
    def remove_coi(self, coi_id: int) -> bool:
        """Remove a COI (soft delete)"""
        return self.repository.delete(coi_id)
    
    def verify_coi(self, coi_id: int, verified_by: int) -> Optional[COIModel]:
        """Verify a COI"""
        return self.repository.verify_coi(coi_id, verified_by)
    
    def set_conflict_period(self, coi_id: int, start_date: datetime, end_date: datetime) -> Optional[COIModel]:
        """Set validity period for a conflict"""
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        return self.repository.update(coi_id, {
            'conflict_start_date': start_date,
            'conflict_end_date': end_date
        })
    
    def is_conflict_active(self, coi_id: int) -> bool:
        """Check if conflict is currently active"""
        coi = self.repository.get_by_id(coi_id)
        if not coi or not coi.is_active:
            return False
        
        now = datetime.utcnow()
        
        # Check validity period
        if coi.conflict_start_date and now < coi.conflict_start_date:
            return False
        
        if coi.conflict_end_date and now > coi.conflict_end_date:
            return False
        
        return True
    
    def list_cois_by_type(self, conflict_type: str) -> List[COIModel]:
        """List COIs by type"""
        return self.repository.get_by_type(conflict_type)
