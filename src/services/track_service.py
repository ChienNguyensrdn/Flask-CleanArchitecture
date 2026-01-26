from typing import List, Optional, Dict, Any
from infrastructure.repositories.track_repository import TrackRepository
from infrastructure.models.track_model import TrackModel
from datetime import datetime


class TrackService:
    """Service for managing track/topic business logic"""
    
    def __init__(self, repository: TrackRepository):
        self.repository = repository
    
    def create_track(self, track_data: Dict[str, Any]) -> TrackModel:
        """Create a new track"""
        # Validate required fields
        required_fields = ['conference_id', 'name']
        for field in required_fields:
            if field not in track_data or not track_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if track name already exists for this conference
        existing = self.repository.get_by_name(
            track_data['name'],
            track_data['conference_id']
        )
        if existing:
            raise ValueError(f"Track '{track_data['name']}' already exists for this conference")
        
        # Add timestamps
        track_data['created_at'] = datetime.utcnow()
        track_data['updated_at'] = datetime.utcnow()
        
        return self.repository.create(track_data)
    
    def get_track(self, track_id: int) -> Optional[TrackModel]:
        """Get track by ID"""
        return self.repository.get_by_id(track_id)
    
    def list_conference_tracks(self, conference_id: int) -> List[TrackModel]:
        """List all active tracks for a conference"""
        return self.repository.get_by_conference(conference_id)
    
    def list_all_conference_tracks(self, conference_id: int, include_inactive: bool = False) -> List[TrackModel]:
        """List all tracks for a conference"""
        return self.repository.get_all_by_conference(conference_id, include_inactive)
    
    def list_all_tracks(self) -> List[TrackModel]:
        """List all tracks"""
        return self.repository.list_all()
    
    def update_track(self, track_id: int, track_data: Dict[str, Any]) -> Optional[TrackModel]:
        """Update a track"""
        track = self.repository.get_by_id(track_id)
        if not track:
            return None
        
        # Prevent updating conference_id
        if 'conference_id' in track_data:
            del track_data['conference_id']
        
        # Update timestamps
        track_data['updated_at'] = datetime.utcnow()
        
        return self.repository.update(track_id, track_data)
    
    def delete_track(self, track_id: int) -> bool:
        """Delete (deactivate) a track"""
        return self.repository.delete(track_id)
    
    def activate_track(self, track_id: int) -> Optional[TrackModel]:
        """Activate a track"""
        return self.repository.update(track_id, {'is_active': True})
    
    def deactivate_track(self, track_id: int) -> Optional[TrackModel]:
        """Deactivate a track"""
        return self.repository.update(track_id, {'is_active': False})
    
    def reorder_tracks(self, conference_id: int, track_order: List[Dict[str, Any]]) -> bool:
        """Reorder tracks within a conference"""
        return self.repository.reorder_tracks(conference_id, track_order)
    
    def set_track_chair(self, track_id: int, user_id: int) -> Optional[TrackModel]:
        """Assign a track chair to a track"""
        return self.repository.update(track_id, {'track_chair_id': user_id})
    
    def get_track_submission_deadline(self, track_id: int) -> Optional[datetime]:
        """Get submission deadline for a track"""
        track = self.repository.get_by_id(track_id)
        if track and track.submission_deadline:
            return track.submission_deadline
        return None
    
    def is_track_submission_open(self, track_id: int) -> bool:
        """Check if submission is open for a track"""
        track = self.repository.get_by_id(track_id)
        if not track or not track.is_active:
            return False
        
        if track.submission_deadline and track.submission_deadline < datetime.utcnow():
            return False
        
        return True
