from typing import List, Optional, Dict, Any
from infrastructure.models.decision_model import DecisionModel
from infrastructure.models.review_model import ReviewModel
from infrastructure.models.paper_model import PaperModel
from datetime import datetime
from sqlalchemy import func, and_, or_


class ReviewRepository:
    """Repository for managing reviews"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create(self, review_data: Dict[str, Any]) -> ReviewModel:
        """Create a new review"""
        review = ReviewModel(**review_data)
        self.db.add(review)
        self.db.commit()
        return review
    
    def get_by_id(self, review_id: int) -> Optional[ReviewModel]:
        """Get review by ID"""
        return self.db.query(ReviewModel).filter(ReviewModel.id == review_id).first()
    
    def get_by_paper(self, paper_id: int) -> List[ReviewModel]:
        """Get all reviews for a paper"""
        return self.db.query(ReviewModel).filter(ReviewModel.paper_id == paper_id).all()
    
    def get_by_reviewer(self, reviewer_id: int) -> List[ReviewModel]:
        """Get all reviews by a reviewer"""
        return self.db.query(ReviewModel).filter(ReviewModel.reviewer_pc_id == reviewer_id).all()
    
    def get_by_paper_and_reviewer(self, paper_id: int, reviewer_id: int) -> Optional[ReviewModel]:
        """Get review by paper and reviewer"""
        return self.db.query(ReviewModel).filter(
            and_(ReviewModel.paper_id == paper_id, ReviewModel.reviewer_pc_id == reviewer_id)
        ).first()
    
    def update(self, review_id: int, review_data: Dict[str, Any]) -> Optional[ReviewModel]:
        """Update review"""
        review = self.get_by_id(review_id)
        if not review:
            return None
        
        for key, value in review_data.items():
            setattr(review, key, value)
        
        self.db.commit()
        return review
    
    def delete(self, review_id: int) -> bool:
        """Delete review"""
        review = self.get_by_id(review_id)
        if not review:
            return False
        
        self.db.delete(review)
        self.db.commit()
        return True
    
    def get_completed_reviews(self, paper_id: int) -> List[ReviewModel]:
        """Get completed reviews for a paper"""
        return self.db.query(ReviewModel).filter(
            and_(
                ReviewModel.paper_id == paper_id,
                ReviewModel.overall_score.isnot(None)
            )
        ).all()
    
    def get_pending_reviews(self, paper_id: int) -> List[ReviewModel]:
        """Get pending reviews for a paper"""
        return self.db.query(ReviewModel).filter(
            and_(
                ReviewModel.paper_id == paper_id,
                ReviewModel.overall_score.is_(None)
            )
        ).all()
    
    def count_reviews_by_paper(self, paper_id: int) -> int:
        """Count reviews for a paper"""
        return self.db.query(func.count(ReviewModel.id)).filter(
            ReviewModel.paper_id == paper_id
        ).scalar() or 0
    
    def get_conference_reviews(self, conference_id: int) -> List[ReviewModel]:
        """Get all reviews for a conference"""
        return self.db.query(ReviewModel).join(PaperModel).filter(
            PaperModel.conference_id == conference_id
        ).all()
    
    def get_average_score_for_paper(self, paper_id: int) -> float:
        """Calculate average overall score for a paper"""
        result = self.db.query(func.avg(ReviewModel.overall_score)).filter(
            ReviewModel.paper_id == paper_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_average_confidence_for_paper(self, paper_id: int) -> float:
        """Calculate average confidence for a paper"""
        result = self.db.query(func.avg(ReviewModel.confidence_score)).filter(
            ReviewModel.paper_id == paper_id
        ).scalar()
        return float(result) if result else 0.0


class DecisionRepository:
    """Repository for managing decisions"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create(self, decision_data: Dict[str, Any]) -> DecisionModel:
        """Create a new decision"""
        decision = DecisionModel(**decision_data)
        self.db.add(decision)
        self.db.commit()
        return decision
    
    def get_by_id(self, decision_id: int) -> Optional[DecisionModel]:
        """Get decision by ID"""
        return self.db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    
    def get_by_paper(self, paper_id: int) -> Optional[DecisionModel]:
        """Get decision by paper"""
        return self.db.query(DecisionModel).filter(DecisionModel.paper_id == paper_id).first()
    
    def get_by_conference(self, conference_id: int) -> List[DecisionModel]:
        """Get all decisions for a conference"""
        return self.db.query(DecisionModel).join(PaperModel).filter(
            PaperModel.conference_id == conference_id
        ).all()
    
    def get_by_decision_type(self, conference_id: int, decision: str) -> List[DecisionModel]:
        """Get decisions by type for a conference"""
        return self.db.query(DecisionModel).join(PaperModel).filter(
            and_(
                PaperModel.conference_id == conference_id,
                DecisionModel.decision == decision
            )
        ).all()
    
    def update(self, decision_id: int, decision_data: Dict[str, Any]) -> Optional[DecisionModel]:
        """Update decision"""
        decision = self.get_by_id(decision_id)
        if not decision:
            return None
        
        for key, value in decision_data.items():
            setattr(decision, key, value)
        
        self.db.commit()
        return decision
    
    def delete(self, decision_id: int) -> bool:
        """Delete decision"""
        decision = self.get_by_id(decision_id)
        if not decision:
            return False
        
        self.db.delete(decision)
        self.db.commit()
        return True
    
    def verify_conditions(self, decision_id: int, verified_by: int) -> Optional[DecisionModel]:
        """Mark conditional accept conditions as verified"""
        decision = self.get_by_id(decision_id)
        if not decision:
            return None
        
        decision.conditions_met = True
        decision.conditions_verified_by = verified_by
        decision.conditions_verified_at = datetime.utcnow()
        self.db.commit()
        
        return decision
    
    def count_decisions_by_type(self, conference_id: int) -> Dict[str, int]:
        """Count decisions by type for a conference"""
        results = self.db.query(
            DecisionModel.decision,
            func.count(DecisionModel.id)
        ).join(PaperModel).filter(
            PaperModel.conference_id == conference_id
        ).group_by(DecisionModel.decision).all()
        
        return {decision: count for decision, count in results}
    
    def get_acceptance_rate(self, conference_id: int) -> float:
        """Calculate acceptance rate for a conference"""
        total = self.db.query(func.count(DecisionModel.id)).join(PaperModel).filter(
            PaperModel.conference_id == conference_id
        ).scalar() or 0
        
        if total == 0:
            return 0.0
        
        accepted = self.db.query(func.count(DecisionModel.id)).join(PaperModel).filter(
            and_(
                PaperModel.conference_id == conference_id,
                DecisionModel.decision.in_(['accept', 'conditional_accept'])
            )
        ).scalar() or 0
        
        return (accepted / total) * 100
    
    def get_decisions_by_decided_by(self, decided_by: int) -> List[DecisionModel]:
        """Get all decisions made by a user"""
        return self.db.query(DecisionModel).filter(DecisionModel.decided_by == decided_by).all()
    
    def get_recent_decisions(self, conference_id: int, limit: int = 10) -> List[DecisionModel]:
        """Get recent decisions for a conference"""
        return self.db.query(DecisionModel).join(PaperModel).filter(
            PaperModel.conference_id == conference_id
        ).order_by(DecisionModel.decided_at.desc()).limit(limit).all()
