"""Review API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user, require_pc, require_chair
from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.models.paper_assignment import PaperAssignment, AssignmentStatus
from app.models.review import Review
from app.models.review_discussion import ReviewDiscussion
from app.models.decision import Decision
from app.models.pc_member import PCMember
from app.schemas.review import (
    ReviewCreate, ReviewSubmit, ReviewResponse, ReviewForAuthor,
    DiscussionMessage, DiscussionResponse, DecisionCreate, DecisionResponse
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/my-assignments", response_model=List[dict])
async def get_my_assignments(
    conference_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pc)
):
    """Get papers assigned to current reviewer."""
    # Get PC membership
    query = db.query(PaperAssignment).join(PCMember).filter(
        PCMember.user_id == current_user.id
    )
    
    if conference_id:
        query = query.join(Paper).filter(Paper.conference_id == conference_id)
    
    assignments = query.all()
    
    result = []
    for assignment in assignments:
        paper = assignment.paper
        result.append({
            "assignment_id": assignment.id,
            "paper_id": paper.id,
            "paper_number": paper.paper_number,
            "title": paper.title,
            "abstract": paper.abstract,
            "status": assignment.status.value,
            "review_submitted": assignment.review is not None and assignment.review.is_submitted
        })
    
    return result


@router.get("/{assignment_id}", response_model=ReviewResponse)
async def get_review(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pc)
):
    """Get review for an assignment."""
    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if user is the reviewer or a chair
    pc_member = assignment.reviewer
    if pc_member.user_id != current_user.id and current_user.role.value not in ["admin", "chair"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not assignment.review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return assignment.review


@router.post("/{assignment_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_review(
    assignment_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pc)
):
    """Create or update a review (save as draft)."""
    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if user is the assigned reviewer
    pc_member = assignment.reviewer
    if pc_member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this paper")
    
    # Create or update review
    if assignment.review:
        review = assignment.review
        if review.is_final:
            raise HTTPException(status_code=400, detail="Review is already finalized")
    else:
        review = Review(
            assignment_id=assignment_id,
            paper_id=assignment.paper_id,
            reviewer_id=current_user.id
        )
        db.add(review)
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    return review


@router.post("/{assignment_id}/submit", response_model=ReviewResponse)
async def submit_review(
    assignment_id: int,
    data: ReviewSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pc)
):
    """Submit a review (mark as final)."""
    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    pc_member = assignment.reviewer
    if pc_member.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this paper")
    
    # Get or create review
    review = assignment.review
    if not review:
        review = Review(
            assignment_id=assignment_id,
            paper_id=assignment.paper_id,
            reviewer_id=current_user.id
        )
        db.add(review)
    
    # Validate required fields
    if data.overall_score is None:
        raise HTTPException(status_code=400, detail="Overall score is required")
    if data.recommendation is None:
        raise HTTPException(status_code=400, detail="Recommendation is required")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    review.is_submitted = True
    review.is_final = True
    review.submitted_at = datetime.utcnow()
    
    # Update assignment status
    assignment.status = AssignmentStatus.COMPLETED
    assignment.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    return review


# Discussion endpoints
@router.post("/{review_id}/discussion", response_model=DiscussionResponse)
async def add_discussion_message(
    review_id: int,
    data: DiscussionMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pc)
):
    """Add a discussion message to a review (PC internal)."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    message = ReviewDiscussion(
        review_id=review_id,
        author_id=current_user.id,
        message=data.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/{review_id}/discussion", response_model=List[DiscussionResponse])
async def get_discussion_messages(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_pc)
):
    """Get discussion messages for a review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return review.discussions


# Decision endpoints
@router.post("/papers/{paper_id}/decision", response_model=DecisionResponse)
async def make_decision(
    paper_id: int,
    data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Make a decision on a paper (chairs only)."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check if decision already exists
    if paper.decision:
        raise HTTPException(status_code=400, detail="Decision already made")
    
    decision = Decision(
        paper_id=paper_id,
        decided_by_id=current_user.id,
        decision=data.decision,
        meta_review=data.meta_review,
        feedback_to_authors=data.feedback_to_authors,
        conditions=data.conditions
    )
    db.add(decision)
    
    # Update paper status
    if data.decision.value == "accepted":
        paper.status = PaperStatus.ACCEPTED
    elif data.decision.value == "rejected":
        paper.status = PaperStatus.REJECTED
    elif data.decision.value == "revision_required":
        paper.status = PaperStatus.REVISION_REQUESTED
    elif data.decision.value == "conditionally_accepted":
        paper.status = PaperStatus.CONDITIONALLY_ACCEPTED
    
    paper.decision_at = datetime.utcnow()
    
    db.commit()
    db.refresh(decision)
    return decision
