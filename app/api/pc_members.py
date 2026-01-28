"""PC Member management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user, require_chair
from app.models.user import User
from app.models.pc_member import PCMember, PCRole, InvitationStatus
from app.models.paper_assignment import PaperAssignment, AssignmentStatus
from app.models.paper import Paper
from pydantic import BaseModel, EmailStr


router = APIRouter(prefix="/pc-members", tags=["PC Members"])


class PCMemberInvite(BaseModel):
    """Schema for inviting a PC member."""
    user_id: int
    conference_id: int
    track_id: Optional[int] = None
    role: PCRole = PCRole.REVIEWER
    expertise_keywords: Optional[str] = None
    max_papers: int = 10


class PCMemberResponse(BaseModel):
    """Schema for PC member response."""
    id: int
    conference_id: int
    user_id: int
    track_id: Optional[int]
    role: PCRole
    invitation_status: InvitationStatus
    expertise_keywords: Optional[str]
    max_papers: int
    assigned_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    """Schema for creating a paper assignment."""
    paper_id: int
    reviewer_id: int  # PC member ID
    is_primary: bool = False


class AssignmentResponse(BaseModel):
    """Schema for assignment response."""
    id: int
    paper_id: int
    reviewer_id: int
    status: AssignmentStatus
    is_primary: bool
    assigned_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[PCMemberResponse])
async def list_pc_members(
    conference_id: int,
    track_id: Optional[int] = None,
    role: Optional[PCRole] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """List PC members for a conference."""
    query = db.query(PCMember).filter(PCMember.conference_id == conference_id)
    
    if track_id:
        query = query.filter(PCMember.track_id == track_id)
    if role:
        query = query.filter(PCMember.role == role)
    
    return query.all()


@router.post("/invite", response_model=PCMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_pc_member(
    data: PCMemberInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Invite a user to be a PC member."""
    # Check if already a PC member
    existing = db.query(PCMember).filter(
        PCMember.conference_id == data.conference_id,
        PCMember.user_id == data.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a PC member")
    
    pc_member = PCMember(
        conference_id=data.conference_id,
        user_id=data.user_id,
        track_id=data.track_id,
        role=data.role,
        expertise_keywords=data.expertise_keywords,
        max_papers=data.max_papers,
        invitation_sent_at=datetime.utcnow()
    )
    db.add(pc_member)
    db.commit()
    db.refresh(pc_member)
    
    # TODO: Send invitation email
    
    return pc_member


@router.post("/{pc_member_id}/respond")
async def respond_to_invitation(
    pc_member_id: int,
    accept: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Respond to PC membership invitation."""
    pc_member = db.query(PCMember).filter(PCMember.id == pc_member_id).first()
    if not pc_member:
        raise HTTPException(status_code=404, detail="PC membership not found")
    
    if pc_member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your invitation")
    
    if pc_member.invitation_status != InvitationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invitation already responded")
    
    pc_member.invitation_status = InvitationStatus.ACCEPTED if accept else InvitationStatus.DECLINED
    pc_member.invitation_responded_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Invitation accepted" if accept else "Invitation declined"}


# Assignment endpoints
@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Assign a paper to a reviewer."""
    # Validate paper
    paper = db.query(Paper).filter(Paper.id == data.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Validate reviewer
    reviewer = db.query(PCMember).filter(PCMember.id == data.reviewer_id).first()
    if not reviewer:
        raise HTTPException(status_code=404, detail="Reviewer not found")
    
    if reviewer.invitation_status != InvitationStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Reviewer has not accepted invitation")
    
    # Check if already assigned
    existing = db.query(PaperAssignment).filter(
        PaperAssignment.paper_id == data.paper_id,
        PaperAssignment.reviewer_id == data.reviewer_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Paper already assigned to this reviewer")
    
    # Check reviewer quota
    if reviewer.assigned_count >= reviewer.max_papers:
        raise HTTPException(status_code=400, detail="Reviewer has reached maximum papers")
    
    assignment = PaperAssignment(
        paper_id=data.paper_id,
        reviewer_id=data.reviewer_id,
        is_primary=data.is_primary
    )
    db.add(assignment)
    
    # Update reviewer count
    reviewer.assigned_count += 1
    
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/assignments", response_model=List[AssignmentResponse])
async def list_assignments(
    paper_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    conference_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """List paper assignments."""
    query = db.query(PaperAssignment)
    
    if paper_id:
        query = query.filter(PaperAssignment.paper_id == paper_id)
    if reviewer_id:
        query = query.filter(PaperAssignment.reviewer_id == reviewer_id)
    if conference_id:
        query = query.join(Paper).filter(Paper.conference_id == conference_id)
    
    return query.all()


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Remove a paper assignment."""
    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.review and assignment.review.is_submitted:
        raise HTTPException(status_code=400, detail="Cannot remove assignment with submitted review")
    
    # Update reviewer count
    reviewer = assignment.reviewer
    reviewer.assigned_count = max(0, reviewer.assigned_count - 1)
    
    db.delete(assignment)
    db.commit()
