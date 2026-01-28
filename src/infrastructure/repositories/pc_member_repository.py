from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.pc_member_model import PCMemberModel
from infrastructure.models.coi_model import COIModel
from datetime import datetime


class PCMemberRepository:
    """Repository for managing PC Member database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, member_data: dict) -> PCMemberModel:
        """Create a new PC member"""
        try:
            db_member = PCMemberModel(**member_data)
            self.session.add(db_member)
            self.session.commit()
            self.session.refresh(db_member)
            return db_member
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, member_id: int) -> Optional[PCMemberModel]:
        """Get PC member by ID"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.id == member_id
        ).first()
    
    def get_by_conference(self, conference_id: int) -> List[PCMemberModel]:
        """Get all PC members for a conference"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.conference_id == conference_id,
            PCMemberModel.is_active == True
        ).all()
    
    def get_by_conference_and_user(self, conference_id: int, user_id: int) -> Optional[PCMemberModel]:
        """Get PC member by conference and user"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.conference_id == conference_id,
            PCMemberModel.user_id == user_id
        ).first()
    
    def get_by_track(self, track_id: int) -> List[PCMemberModel]:
        """Get all PC members for a track"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.track_id == track_id,
            PCMemberModel.is_active == True
        ).all()
    
    def get_by_role(self, conference_id: int, role: str) -> List[PCMemberModel]:
        """Get PC members by role in a conference"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.conference_id == conference_id,
            PCMemberModel.role == role,
            PCMemberModel.is_active == True
        ).all()
    
    def get_by_invitation_status(self, conference_id: int, status: str) -> List[PCMemberModel]:
        """Get PC members by invitation status"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.conference_id == conference_id,
            PCMemberModel.invitation_status == status
        ).all()
    
    def get_active_reviewers(self, conference_id: int) -> List[PCMemberModel]:
        """Get active reviewers for a conference"""
        return self.session.query(PCMemberModel).filter(
            PCMemberModel.conference_id == conference_id,
            PCMemberModel.invitation_status == 'accepted',
            PCMemberModel.is_active == True
        ).all()
    
    def list_all(self) -> List[PCMemberModel]:
        """Get all PC members"""
        return self.session.query(PCMemberModel).all()
    
    def update(self, member_id: int, member_data: dict) -> Optional[PCMemberModel]:
        """Update a PC member"""
        try:
            db_member = self.get_by_id(member_id)
            if not db_member:
                return None
            
            for key, value in member_data.items():
                if hasattr(db_member, key):
                    setattr(db_member, key, value)
            
            db_member.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_member)
            return db_member
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, member_id: int) -> bool:
        """Delete a PC member (soft delete by deactivating)"""
        try:
            db_member = self.get_by_id(member_id)
            if not db_member:
                return False
            
            db_member.is_active = False
            db_member.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_invitation_status(self, member_id: int, status: str) -> Optional[PCMemberModel]:
        """Update invitation status"""
        return self.update(member_id, {
            'invitation_status': status,
            'invitation_responded_at': datetime.utcnow()
        })
    
    def send_invitation(self, member_id: int) -> Optional[PCMemberModel]:
        """Mark invitation as sent"""
        return self.update(member_id, {
            'invitation_status': 'pending',
            'invitation_sent_at': datetime.utcnow()
        })
    
    def increment_assigned_count(self, member_id: int) -> Optional[PCMemberModel]:
        """Increment assigned paper count"""
        db_member = self.get_by_id(member_id)
        if db_member:
            db_member.assigned_count += 1
            self.session.commit()
            self.session.refresh(db_member)
            return db_member
        return None
    
    def decrement_assigned_count(self, member_id: int) -> Optional[PCMemberModel]:
        """Decrement assigned paper count"""
        db_member = self.get_by_id(member_id)
        if db_member and db_member.assigned_count > 0:
            db_member.assigned_count -= 1
            self.session.commit()
            self.session.refresh(db_member)
            return db_member
        return None
    
    def get_available_capacity(self, member_id: int) -> int:
        """Get available review capacity for a member"""
        db_member = self.get_by_id(member_id)
        if db_member:
            return db_member.max_papers - db_member.assigned_count
        return 0


class COIRepository:
    """Repository for managing Conflict of Interest database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, coi_data: dict) -> COIModel:
        """Create a new COI record"""
        try:
            db_coi = COIModel(**coi_data)
            self.session.add(db_coi)
            self.session.commit()
            self.session.refresh(db_coi)
            return db_coi
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, coi_id: int) -> Optional[COIModel]:
        """Get COI by ID"""
        return self.session.query(COIModel).filter(
            COIModel.id == coi_id
        ).first()
    
    def get_by_pc_member(self, pc_member_id: int) -> List[COIModel]:
        """Get all COIs for a PC member"""
        return self.session.query(COIModel).filter(
            COIModel.pc_member_id == pc_member_id,
            COIModel.is_active == True
        ).all()
    
    def get_by_pc_member_and_paper(self, pc_member_id: int, paper_id: int) -> Optional[COIModel]:
        """Check if PC member has conflict with a paper"""
        return self.session.query(COIModel).filter(
            COIModel.pc_member_id == pc_member_id,
            COIModel.paper_id == paper_id,
            COIModel.is_active == True
        ).first()
    
    def get_by_pc_member_and_author(self, pc_member_id: int, author_user_id: int) -> List[COIModel]:
        """Get COIs between PC member and author"""
        return self.session.query(COIModel).filter(
            COIModel.pc_member_id == pc_member_id,
            COIModel.author_user_id == author_user_id,
            COIModel.is_active == True
        ).all()
    
    def get_by_paper(self, paper_id: int) -> List[COIModel]:
        """Get all COIs for a paper"""
        return self.session.query(COIModel).filter(
            COIModel.paper_id == paper_id,
            COIModel.is_active == True
        ).all()
    
    def get_by_type(self, conflict_type: str) -> List[COIModel]:
        """Get COIs by type"""
        return self.session.query(COIModel).filter(
            COIModel.conflict_type == conflict_type,
            COIModel.is_active == True
        ).all()
    
    def list_all(self) -> List[COIModel]:
        """Get all COIs"""
        return self.session.query(COIModel).all()
    
    def update(self, coi_id: int, coi_data: dict) -> Optional[COIModel]:
        """Update a COI"""
        try:
            db_coi = self.get_by_id(coi_id)
            if not db_coi:
                return None
            
            for key, value in coi_data.items():
                if hasattr(db_coi, key):
                    setattr(db_coi, key, value)
            
            self.session.commit()
            self.session.refresh(db_coi)
            return db_coi
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, coi_id: int) -> bool:
        """Delete a COI (soft delete by marking inactive)"""
        try:
            db_coi = self.get_by_id(coi_id)
            if not db_coi:
                return False
            
            db_coi.is_active = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def verify_coi(self, coi_id: int, verified_by: int) -> Optional[COIModel]:
        """Verify a COI"""
        return self.update(coi_id, {
            'verified_by': verified_by,
            'verified_at': datetime.utcnow()
        })
    
    def check_conflict(self, pc_member_id: int, paper_id: int) -> bool:
        """Check if a PC member has conflict with a paper"""
        conflict = self.get_by_pc_member_and_paper(pc_member_id, paper_id)
        return conflict is not None
