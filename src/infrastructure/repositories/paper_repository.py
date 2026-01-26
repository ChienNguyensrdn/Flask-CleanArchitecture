from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.models.paper_model import PaperModel
from infrastructure.models.paper_author_model import PaperAuthorModel
from datetime import datetime


class PaperRepository:
    """Repository for managing Paper database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, paper_data: dict) -> PaperModel:
        """Create a new paper"""
        try:
            db_paper = PaperModel(**paper_data)
            self.session.add(db_paper)
            self.session.commit()
            self.session.refresh(db_paper)
            return db_paper
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, paper_id: int) -> Optional[PaperModel]:
        """Get paper by ID"""
        return self.session.query(PaperModel).filter(
            PaperModel.id == paper_id
        ).first()
    
    def get_by_conference(self, conference_id: int) -> List[PaperModel]:
        """Get all papers for a conference"""
        return self.session.query(PaperModel).filter(
            PaperModel.conference_id == conference_id,
            PaperModel.is_withdrawn == False
        ).all()
    
    def get_by_submitter(self, submitter_id: int) -> List[PaperModel]:
        """Get all papers submitted by a user"""
        return self.session.query(PaperModel).filter(
            PaperModel.submitter_id == submitter_id,
            PaperModel.is_withdrawn == False
        ).all()
    
    def get_by_conference_and_submitter(self, conference_id: int, submitter_id: int) -> List[PaperModel]:
        """Get papers for a specific conference and submitter"""
        return self.session.query(PaperModel).filter(
            PaperModel.conference_id == conference_id,
            PaperModel.submitter_id == submitter_id,
            PaperModel.is_withdrawn == False
        ).all()
    
    def get_by_track(self, track_id: int) -> List[PaperModel]:
        """Get all papers in a track"""
        return self.session.query(PaperModel).filter(
            PaperModel.track_id == track_id,
            PaperModel.is_withdrawn == False
        ).all()
    
    def get_by_status(self, conference_id: int, status: str) -> List[PaperModel]:
        """Get papers by status in a conference"""
        return self.session.query(PaperModel).filter(
            PaperModel.conference_id == conference_id,
            PaperModel.status == status,
            PaperModel.is_withdrawn == False
        ).all()
    
    def get_submitted_papers(self, conference_id: int) -> List[PaperModel]:
        """Get all submitted papers (exclude draft) in a conference"""
        return self.session.query(PaperModel).filter(
            PaperModel.conference_id == conference_id,
            PaperModel.status != 'draft',
            PaperModel.is_withdrawn == False
        ).all()
    
    def list_all(self) -> List[PaperModel]:
        """Get all papers"""
        return self.session.query(PaperModel).all()
    
    def update(self, paper_id: int, paper_data: dict) -> Optional[PaperModel]:
        """Update an existing paper"""
        try:
            db_paper = self.get_by_id(paper_id)
            if not db_paper:
                return None
            
            for key, value in paper_data.items():
                if hasattr(db_paper, key):
                    setattr(db_paper, key, value)
            
            db_paper.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_paper)
            return db_paper
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, paper_id: int) -> bool:
        """Delete a paper (hard delete)"""
        try:
            db_paper = self.get_by_id(paper_id)
            if not db_paper:
                return False
            
            self.session.delete(db_paper)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def withdraw(self, paper_id: int) -> Optional[PaperModel]:
        """Withdraw a paper (soft delete)"""
        return self.update(paper_id, {
            'is_withdrawn': True,
            'withdrawn_at': datetime.utcnow(),
            'status': 'withdrawn'
        })
    
    def update_status(self, paper_id: int, status: str) -> Optional[PaperModel]:
        """Update paper status"""
        return self.update(paper_id, {'status': status})
    
    def mark_submitted(self, paper_id: int) -> Optional[PaperModel]:
        """Mark paper as submitted"""
        return self.update(paper_id, {
            'status': 'submitted',
            'submitted_at': datetime.utcnow()
        })
    
    def update_pdf_path(self, paper_id: int, pdf_path: str) -> Optional[PaperModel]:
        """Update PDF file path"""
        return self.update(paper_id, {'pdf_path': pdf_path})
    
    def update_supplementary_path(self, paper_id: int, supplementary_path: str) -> Optional[PaperModel]:
        """Update supplementary file path"""
        return self.update(paper_id, {'supplementary_path': supplementary_path})
    
    def mark_revision_required(self, paper_id: int) -> Optional[PaperModel]:
        """Mark paper as requires revision"""
        return self.update(paper_id, {
            'requires_revision': True,
            'status': 'revision_requested'
        })
    
    def assign_paper_number(self, paper_id: int, paper_number: str) -> Optional[PaperModel]:
        """Assign a paper number to paper"""
        return self.update(paper_id, {'paper_number': paper_number})


class PaperAuthorRepository:
    """Repository for managing Paper Author database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, author_data: dict) -> PaperAuthorModel:
        """Create a new paper author"""
        try:
            db_author = PaperAuthorModel(**author_data)
            self.session.add(db_author)
            self.session.commit()
            self.session.refresh(db_author)
            return db_author
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_by_id(self, author_id: int) -> Optional[PaperAuthorModel]:
        """Get paper author by ID"""
        return self.session.query(PaperAuthorModel).filter(
            PaperAuthorModel.id == author_id
        ).first()
    
    def get_by_paper(self, paper_id: int) -> List[PaperAuthorModel]:
        """Get all authors for a paper"""
        return self.session.query(PaperAuthorModel).filter(
            PaperAuthorModel.paper_id == paper_id
        ).order_by(PaperAuthorModel.author_order).all()
    
    def get_corresponding_author(self, paper_id: int) -> Optional[PaperAuthorModel]:
        """Get corresponding author for a paper"""
        return self.session.query(PaperAuthorModel).filter(
            PaperAuthorModel.paper_id == paper_id,
            PaperAuthorModel.is_corresponding == True
        ).first()
    
    def get_by_paper_and_user(self, paper_id: int, user_id: int) -> Optional[PaperAuthorModel]:
        """Get author by paper and user"""
        return self.session.query(PaperAuthorModel).filter(
            PaperAuthorModel.paper_id == paper_id,
            PaperAuthorModel.user_id == user_id
        ).first()
    
    def list_all(self) -> List[PaperAuthorModel]:
        """Get all paper authors"""
        return self.session.query(PaperAuthorModel).all()
    
    def update(self, author_id: int, author_data: dict) -> Optional[PaperAuthorModel]:
        """Update a paper author"""
        try:
            db_author = self.get_by_id(author_id)
            if not db_author:
                return None
            
            for key, value in author_data.items():
                if hasattr(db_author, key):
                    setattr(db_author, key, value)
            
            db_author.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_author)
            return db_author
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, author_id: int) -> bool:
        """Delete a paper author"""
        try:
            db_author = self.get_by_id(author_id)
            if not db_author:
                return False
            
            self.session.delete(db_author)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def set_corresponding_author(self, paper_id: int, author_id: int) -> bool:
        """Set corresponding author for a paper"""
        try:
            # Unset previous corresponding author
            self.session.query(PaperAuthorModel).filter(
                PaperAuthorModel.paper_id == paper_id,
                PaperAuthorModel.is_corresponding == True
            ).update({'is_corresponding': False})
            
            # Set new corresponding author
            db_author = self.get_by_id(author_id)
            if db_author and db_author.paper_id == paper_id:
                db_author.is_corresponding = True
                self.session.commit()
                return True
            
            return False
        except Exception as e:
            self.session.rollback()
            raise e
    
    def reorder_authors(self, paper_id: int, author_order: List[dict]) -> bool:
        """Reorder authors for a paper"""
        try:
            for item in author_order:
                author = self.get_by_id(item['author_id'])
                if author and author.paper_id == paper_id:
                    author.author_order = item['order']
            
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
