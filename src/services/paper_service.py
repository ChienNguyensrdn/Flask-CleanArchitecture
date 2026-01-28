from typing import List, Optional, Dict, Any
from infrastructure.repositories.paper_repository import PaperRepository, PaperAuthorRepository
from infrastructure.models.paper_model import PaperModel
from infrastructure.models.paper_author_model import PaperAuthorModel
from datetime import datetime, timezone
import os
from pathlib import Path


class PaperService:
    """Service for managing paper business logic"""
    
    def __init__(self, repository: PaperRepository, author_repository: PaperAuthorRepository):
        self.repository = repository
        self.author_repository = author_repository
        self.upload_base_path = "uploads/papers"  # Configure as needed
    
    def submit_paper(self, paper_data: Dict[str, Any], submitter_id: int) -> PaperModel:
        """Submit a new paper"""
        # Validate required fields
        required_fields = ['conference_id', 'title', 'abstract']
        for field in required_fields:
            if field not in paper_data or not paper_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Add submitter and timestamps
        paper_data['submitter_id'] = submitter_id
        paper_data['status'] = 'draft'
        paper_data['created_at'] = datetime.now(timezone.utc)
        paper_data['updated_at'] = datetime.now(timezone.utc)
        
        # Create paper
        paper = self.repository.create(paper_data)
        
        # Add authors if provided
        authors = paper_data.get('authors', [])
        if authors:
            for author_data in authors:
                author_data['paper_id'] = paper.id
                self.author_repository.create(author_data)
        
        return paper
    
    def get_paper(self, paper_id: int) -> Optional[PaperModel]:
        """Get paper by ID with authors"""
        paper = self.repository.get_by_id(paper_id)
        if paper:
            paper.authors = self.author_repository.get_by_paper(paper_id)
        return paper
    
    def list_user_papers(self, submitter_id: int) -> List[PaperModel]:
        """List all papers submitted by a user"""
        return self.repository.get_by_submitter(submitter_id)
    
    def list_conference_papers(self, conference_id: int) -> List[PaperModel]:
        """List all papers in a conference"""
        return self.repository.get_by_conference(conference_id)
    
    def list_user_conference_papers(self, conference_id: int, submitter_id: int) -> List[PaperModel]:
        """List papers for specific conference and submitter"""
        papers = self.repository.get_by_conference_and_submitter(conference_id, submitter_id)
        for paper in papers:
            paper.authors = self.author_repository.get_by_paper(paper.id)
        return papers
    
    def list_track_papers(self, track_id: int) -> List[PaperModel]:
        """List papers in a track"""
        return self.repository.get_by_track(track_id)
    
    def update_paper(self, paper_id: int, paper_data: Dict[str, Any]) -> Optional[PaperModel]:
        """Update a paper"""
        paper = self.repository.get_by_id(paper_id)
        if not paper:
            return None
        
        # Can only update draft papers
        if paper.status != 'draft':
            raise ValueError("Cannot update submitted papers")
        
        # Prevent updating conference_id and submitter_id
        if 'conference_id' in paper_data:
            del paper_data['conference_id']
        if 'submitter_id' in paper_data:
            del paper_data['submitter_id']
        
        paper_data['updated_at'] = datetime.now(timezone.utc)
        return self.repository.update(paper_id, paper_data)
    
    def mark_paper_submitted(self, paper_id: int) -> Optional[PaperModel]:
        """Mark paper as submitted"""
        paper = self.repository.get_by_id(paper_id)
        if not paper:
            return None
        
        # Validate paper has at least one author
        authors = self.author_repository.get_by_paper(paper_id)
        if not authors:
            raise ValueError("Paper must have at least one author")
        
        # Validate paper has corresponding author
        corresponding = self.author_repository.get_corresponding_author(paper_id)
        if not corresponding:
            raise ValueError("Paper must have a corresponding author")
        
        # Validate PDF is uploaded
        if not paper.pdf_path:
            raise ValueError("Paper PDF must be uploaded before submission")
        
        return self.repository.mark_submitted(paper_id)
    
    def withdraw_paper(self, paper_id: int) -> Optional[PaperModel]:
        """Withdraw a paper"""
        return self.repository.withdraw(paper_id)
    
    def update_paper_status(self, paper_id: int, status: str) -> Optional[PaperModel]:
        """Update paper status"""
        valid_statuses = ['draft', 'submitted', 'under_review', 'revision_requested', 
                         'accepted', 'rejected', 'withdrawn', 'camera_ready']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return self.repository.update_status(paper_id, status)
    
    def get_upload_path(self, paper_id: int, filename: str) -> str:
        """Get upload path for paper file"""
        path = os.path.join(self.upload_base_path, f"paper_{paper_id}")
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, filename)
    
    def upload_pdf(self, paper_id: int, file_path: str) -> Optional[PaperModel]:
        """Update paper PDF path"""
        return self.repository.update_pdf_path(paper_id, file_path)
    
    def upload_supplementary(self, paper_id: int, file_path: str) -> Optional[PaperModel]:
        """Update supplementary file path"""
        return self.repository.update_supplementary_path(paper_id, file_path)
    
    def mark_revision_required(self, paper_id: int) -> Optional[PaperModel]:
        """Mark paper as requiring revision"""
        return self.repository.mark_revision_required(paper_id)
    
    def request_revision(self, paper_id: int, revision_notes: str) -> Optional[PaperModel]:
        """Request revision for a paper"""
        # This would be combined with email service to notify author
        return self.repository.mark_revision_required(paper_id)
    
    def resubmit_after_revision(self, paper_id: int, updated_data: Dict[str, Any]) -> Optional[PaperModel]:
        """Resubmit paper after revision"""
        paper = self.repository.get_by_id(paper_id)
        if not paper:
            return None
        
        if paper.status != 'revision_requested':
            raise ValueError("Paper is not awaiting revision")
        
        # Update paper
        updated_data['status'] = 'submitted'
        return self.repository.update(paper_id, updated_data)
    
    def delete_paper(self, paper_id: int) -> bool:
        """Delete a paper (only draft papers)"""
        paper = self.repository.get_by_id(paper_id)
        if not paper:
            return False
        
        if paper.status != 'draft':
            raise ValueError("Cannot delete submitted papers")
        
        return self.repository.delete(paper_id)
    
    def assign_paper_number(self, paper_id: int, paper_number: str) -> Optional[PaperModel]:
        """Assign paper number to paper"""
        return self.repository.assign_paper_number(paper_id, paper_number)
    
    def get_paper_by_number(self, conference_id: int, paper_number: str) -> Optional[PaperModel]:
        """Get paper by number (within conference)"""
        papers = self.repository.get_by_conference(conference_id)
        for paper in papers:
            if paper.paper_number == paper_number:
                return paper
        return None


class PaperAuthorService:
    """Service for managing paper authors"""
    
    def __init__(self, repository: PaperAuthorRepository):
        self.repository = repository
    
    def add_author(self, author_data: Dict[str, Any]) -> PaperAuthorModel:
        """Add an author to a paper"""
        # Validate required fields
        required_fields = ['paper_id', 'first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in author_data or not author_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        author_data['created_at'] = datetime.now(timezone.utc)
        author_data['updated_at'] = datetime.now(timezone.utc)
        
        return self.repository.create(author_data)
    
    def get_author(self, author_id: int) -> Optional[PaperAuthorModel]:
        """Get author by ID"""
        return self.repository.get_by_id(author_id)
    
    def get_paper_authors(self, paper_id: int) -> List[PaperAuthorModel]:
        """Get all authors for a paper"""
        return self.repository.get_by_paper(paper_id)
    
    def get_corresponding_author(self, paper_id: int) -> Optional[PaperAuthorModel]:
        """Get corresponding author for a paper"""
        return self.repository.get_corresponding_author(paper_id)
    
    def update_author(self, author_id: int, author_data: Dict[str, Any]) -> Optional[PaperAuthorModel]:
        """Update an author"""
        author = self.repository.get_by_id(author_id)
        if not author:
            return None
        
        # Prevent updating paper_id
        if 'paper_id' in author_data:
            del author_data['paper_id']
        
        author_data['updated_at'] = datetime.now(timezone.utc)
        return self.repository.update(author_id, author_data)
    
    def remove_author(self, author_id: int) -> bool:
        """Remove an author from a paper"""
        return self.repository.delete(author_id)
    
    def set_corresponding_author(self, paper_id: int, author_id: int) -> bool:
        """Set corresponding author for a paper"""
        return self.repository.set_corresponding_author(paper_id, author_id)
    
    def reorder_authors(self, paper_id: int, author_order: List[Dict]) -> bool:
        """Reorder authors for a paper"""
        return self.repository.reorder_authors(paper_id, author_order)
    
    def get_author_papers(self, user_id: int) -> List[PaperAuthorModel]:
        """Get all papers where user is an author"""
        # Note: This would require a more complex query
        # For now, returns all author records
        all_authors = self.repository.list_all()
        return [author for author in all_authors if author.user_id == user_id]
