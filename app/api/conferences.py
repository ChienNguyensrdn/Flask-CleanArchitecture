"""Conference API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user, require_chair
from app.models.user import User
from app.models.conference import Conference, ConferenceStatus
from app.models.track import Track
from app.schemas.conference import (
    ConferenceCreate, ConferenceUpdate, ConferenceResponse,
    ConferenceWithTracks, CFPPublic, TrackCreate, TrackResponse
)

router = APIRouter(prefix="/conferences", tags=["Conferences"])


@router.get("/", response_model=List[ConferenceResponse])
async def list_conferences(
    tenant_id: Optional[int] = None,
    status: Optional[ConferenceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List conferences (filtered by tenant and status)."""
    query = db.query(Conference)
    
    if tenant_id:
        query = query.filter(Conference.tenant_id == tenant_id)
    if status:
        query = query.filter(Conference.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=ConferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_conference(
    data: ConferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Create a new conference (chairs only)."""
    conference = Conference(
        **data.model_dump(),
        created_by_id=current_user.id
    )
    db.add(conference)
    db.commit()
    db.refresh(conference)
    return conference


@router.get("/{conference_id}", response_model=ConferenceWithTracks)
async def get_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conference details with tracks."""
    conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conference


@router.put("/{conference_id}", response_model=ConferenceResponse)
async def update_conference(
    conference_id: int,
    data: ConferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Update conference settings (chairs only)."""
    conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conference, field, value)
    
    db.commit()
    db.refresh(conference)
    return conference


@router.delete("/{conference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conference(
    conference_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Delete a conference (chairs only, only draft conferences)."""
    conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    if conference.status != ConferenceStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Can only delete draft conferences"
        )
    
    db.delete(conference)
    db.commit()


# Public CFP endpoint
@router.get("/public/cfp/{conference_id}", response_model=CFPPublic)
async def get_public_cfp(conference_id: int, db: Session = Depends(get_db)):
    """Get public CFP information (no auth required)."""
    conference = db.query(Conference).filter(
        Conference.id == conference_id,
        Conference.cfp_is_public == True
    ).first()
    
    if not conference:
        raise HTTPException(status_code=404, detail="CFP not found or not public")
    
    return conference


# Track endpoints
@router.post("/{conference_id}/tracks", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def create_track(
    conference_id: int,
    data: TrackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_chair)
):
    """Create a new track for a conference."""
    conference = db.query(Conference).filter(Conference.id == conference_id).first()
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    
    track = Track(conference_id=conference_id, **data.model_dump())
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


@router.get("/{conference_id}/tracks", response_model=List[TrackResponse])
async def list_tracks(
    conference_id: int,
    db: Session = Depends(get_db)
):
    """List all tracks for a conference."""
    return db.query(Track).filter(
        Track.conference_id == conference_id,
        Track.is_active == True
    ).order_by(Track.display_order).all()
