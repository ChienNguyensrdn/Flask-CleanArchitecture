"""Paper submission API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid

from app.core.database import get_db
from app.core.config import get_settings
from app.api.deps import get_current_user, require_chair
from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.models.paper_author import PaperAuthor
from app.models.conference import Conference, ConferenceStatus
from app.schemas.paper import (
    PaperCreate, PaperUpdate, PaperResponse, PaperWithAuthors,
    PaperSubmit, PaperWithdraw
)

router = APIRouter(prefix="/papers", tags=["Papers"])
settings = get_settings()


def generate_paper_number(conference: Conference, db: Session) -> str:
    """Generate unique paper number for a conference."""
    count = db.query(Paper).filter(Paper.conference_id == conference.id).count()
    return f"{conference.short_name}-{count + 1:04d}"


@router.get("/", response_model=List[PaperResponse])
async def list_papers(
    conference_id: Optional[int] = None,
    track_id: Optional[int] = None,
    status: Optional[PaperStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List papers (authors see their own, chairs see all)."""
    query = db.query(Paper)
    
    # Authors can only see their own papers
    if current_user.role.value == "author":
        query = query.filter(Paper.submitter_id == current_user.id)
    
    if conference_id:
        query = query.filter(Paper.conference_id == conference_id)
    if track_id:
        query = query.filter(Paper.track_id == track_id)
    if status:
        query = query.filter(Paper.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=PaperWithAuthors, status_code=status.HTTP_201_CREATED)
async def create_paper(
    data: PaperCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new paper submission."""
    # Check conference exists and accepts submissions
    conference = db.query(Conference).filter(Conference.id == data.conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    if conference.status not in [ConferenceStatus.CFP_OPEN, ConferenceStatus.SUBMISSION_OPEN]:
        raise HTTPException(status_code=400, detail="Submissions are not open for this conference")
    
    # Check deadline
    if conference.submission_deadline and datetime.utcnow() > conference.submission_deadline:
        raise HTTPException(status_code=400, detail="Submission deadline has passed")
    
    # Create paper
    paper = Paper(
        conference_id=data.conference_id,
        track_id=data.track_id,
        submitter_id=current_user.id,
        title=data.title,
        abstract=data.abstract,
        keywords=data.keywords,
        paper_number=generate_paper_number(conference, db)
    )
    db.add(paper)
    db.flush()  # Get paper.id
    
    # Add authors
    for author_data in data.authors:
        author = PaperAuthor(
            paper_id=paper.id,
            user_id=author_data.user_id,
            email=author_data.email,
            first_name=author_data.first_name,
            last_name=author_data.last_name,
            affiliation=author_data.affiliation,
            country=author_data.country,
            order=author_data.order,
            is_corresponding=author_data.is_corresponding
        )
        db.add(author)
    
    db.commit()
    db.refresh(paper)
    return paper


@router.get("/{paper_id}", response_model=PaperWithAuthors)
async def get_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paper details."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Check access (author or PC/chair)
    if current_user.role.value == "author" and paper.submitter_id != current_user.id:
        # Check if user is a co-author
        is_author = any(a.user_id == current_user.id for a in paper.authors)
        if not is_author:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return paper


@router.put("/{paper_id}", response_model=PaperWithAuthors)
async def update_paper(
    paper_id: int,
    data: PaperUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update paper details (only before submission)."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Only submitter can update
    if paper.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only submitter can update")
    
    # Can only update draft papers
    if paper.status != PaperStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Can only update draft papers")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True, exclude={"authors"})
    for field, value in update_data.items():
        setattr(paper, field, value)
    
    # Update authors if provided
    if data.authors:
        # Remove existing authors
        db.query(PaperAuthor).filter(PaperAuthor.paper_id == paper_id).delete()
        # Add new authors
        for author_data in data.authors:
            author = PaperAuthor(
                paper_id=paper_id,
                user_id=author_data.user_id,
                email=author_data.email,
                first_name=author_data.first_name,
                last_name=author_data.last_name,
                affiliation=author_data.affiliation,
                country=author_data.country,
                order=author_data.order,
                is_corresponding=author_data.is_corresponding
            )
            db.add(author)
    
    db.commit()
    db.refresh(paper)
    return paper


@router.post("/{paper_id}/submit", response_model=PaperResponse)
async def submit_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a paper (change status from draft to submitted)."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if paper.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only submitter can submit")
    
    if paper.status != PaperStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Paper is already submitted")
    
    # Validate paper has PDF
    if not paper.pdf_path:
        raise HTTPException(status_code=400, detail="Paper must have a PDF file")
    
    # Validate paper has at least one author
    if not paper.authors:
        raise HTTPException(status_code=400, detail="Paper must have at least one author")
    
    paper.status = PaperStatus.SUBMITTED
    paper.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(paper)
    return paper


@router.post("/{paper_id}/withdraw", response_model=PaperResponse)
async def withdraw_paper(
    paper_id: int,
    data: PaperWithdraw,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Withdraw a submitted paper."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if paper.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only submitter can withdraw")
    
    if paper.status == PaperStatus.WITHDRAWN:
        raise HTTPException(status_code=400, detail="Paper is already withdrawn")
    
    if paper.status in [PaperStatus.ACCEPTED, PaperStatus.CAMERA_READY]:
        raise HTTPException(status_code=400, detail="Cannot withdraw accepted paper")
    
    paper.status = PaperStatus.WITHDRAWN
    paper.is_withdrawn = True
    paper.withdrawn_at = datetime.utcnow()
    db.commit()
    db.refresh(paper)
    return paper


@router.post("/{paper_id}/upload")
async def upload_paper_pdf(
    paper_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload paper PDF file."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if paper.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only submitter can upload")
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Save file
    filename = f"{paper.paper_number}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(settings.UPLOAD_DIR, "papers", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    paper.pdf_path = filepath
    db.commit()
    
    return {"message": "File uploaded successfully", "path": filepath}
