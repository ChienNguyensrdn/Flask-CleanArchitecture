from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.track_model import TrackModel
from datetime import datetime


class TrackRepository:
    """Repository for managing Track database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, track_data: dict) -> TrackModel:
        """Create a new track"""
        try:
            db_track = TrackModel(**track_data)
            self.session.add(db_track)
            self.session.commit()
            self.session.refresh(db_track)
            return db_track
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, track_id: int) -> Optional[TrackModel]:
        """Get track by ID"""
        return self.session.query(TrackModel).filter(
            TrackModel.id == track_id
        ).first()
    
    def get_by_conference(self, conference_id: int) -> List[TrackModel]:
        """Get all tracks for a conference"""
        return self.session.query(TrackModel).filter(
            TrackModel.conference_id == conference_id,
            TrackModel.is_active == True
        ).order_by(TrackModel.display_order).all()
    
    def get_all_by_conference(self, conference_id: int, include_inactive: bool = False) -> List[TrackModel]:
        """Get all tracks for a conference including inactive ones"""
        query = self.session.query(TrackModel).filter(
            TrackModel.conference_id == conference_id
        )
        if not include_inactive:
            query = query.filter(TrackModel.is_active == True)
        return query.order_by(TrackModel.display_order).all()
    
    def get_by_name(self, name: str, conference_id: int) -> Optional[TrackModel]:
        """Get track by name within a conference"""
        return self.session.query(TrackModel).filter(
            TrackModel.name == name,
            TrackModel.conference_id == conference_id
        ).first()
    
    def list_all(self) -> List[TrackModel]:
        """Get all tracks"""
        return self.session.query(TrackModel).all()
    
    def update(self, track_id: int, track_data: dict) -> Optional[TrackModel]:
        """Update an existing track"""
        try:
            db_track = self.get_by_id(track_id)
            if not db_track:
                return None
            
            for key, value in track_data.items():
                if hasattr(db_track, key):
                    setattr(db_track, key, value)
            
            db_track.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_track)
            return db_track
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, track_id: int) -> bool:
        """Delete a track (soft delete by marking inactive)"""
        try:
            db_track = self.get_by_id(track_id)
            if not db_track:
                return False
            
            db_track.is_active = False
            db_track.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def reorder_tracks(self, conference_id: int, track_order: List[dict]) -> bool:
        """Reorder tracks within a conference"""
        try:
            for item in track_order:
                track = self.get_by_id(item['track_id'])
                if track and track.conference_id == conference_id:
                    track.display_order = item['display_order']
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
