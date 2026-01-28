from typing import List, Optional, Dict, Any
from infrastructure.repositories.decision_repository import DecisionRepository, ReviewRepository
from infrastructure.models.decision_model import DecisionModel
from infrastructure.models.review_model import ReviewModel
from infrastructure.models.paper_model import PaperModel
from datetime import datetime
import statistics


class ReviewAggregationService:
    """Service for aggregating reviews"""
    
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository
    
    def aggregate_paper_reviews(self, paper_id: int) -> Dict[str, Any]:
        """Aggregate all reviews for a paper"""
        reviews = self.review_repository.get_completed_reviews(paper_id)
        
        if not reviews:
            return {
                'paper_id': paper_id,
                'total_reviews': 0,
                'avg_overall_score': 0,
                'avg_confidence': 0,
                'recommendation_summary': {},
                'consensus_level': 'none'
            }
        
        # Aggregate scores
        overall_scores = [r.overall_score for r in reviews if r.overall_score]
        confidence_scores = [r.confidence_score for r in reviews if r.confidence_score]
        originality_scores = [r.originality_score for r in reviews if r.originality_score]
        significance_scores = [r.significance_score for r in reviews if r.significance_score]
        technical_scores = [r.technical_quality_score for r in reviews if r.technical_quality_score]
        clarity_scores = [r.clarity_score for r in reviews if r.clarity_score]
        relevance_scores = [r.relevance_score for r in reviews if r.relevance_score]
        
        # Recommendation distribution
        recommendations = [r.recommendation for r in reviews if r.recommendation]
        recommendation_count = {}
        for rec in recommendations:
            recommendation_count[rec] = recommendation_count.get(rec, 0) + 1
        
        # Calculate consensus
        consensus = self._calculate_consensus(overall_scores)
        
        # Determine recommended decision
        recommended_decision = self._recommend_decision(overall_scores, recommendations)
        
        return {
            'paper_id': paper_id,
            'total_reviews': len(reviews),
            'avg_overall_score': round(statistics.mean(overall_scores), 2) if overall_scores else 0,
            'avg_confidence': round(statistics.mean(confidence_scores), 2) if confidence_scores else 0,
            'avg_originality': round(statistics.mean(originality_scores), 2) if originality_scores else 0,
            'avg_significance': round(statistics.mean(significance_scores), 2) if significance_scores else 0,
            'avg_technical_quality': round(statistics.mean(technical_scores), 2) if technical_scores else 0,
            'avg_clarity': round(statistics.mean(clarity_scores), 2) if clarity_scores else 0,
            'avg_relevance': round(statistics.mean(relevance_scores), 2) if relevance_scores else 0,
            'recommendation_summary': recommendation_count,
            'consensus_level': consensus,
            'recommended_decision': recommended_decision,
            'min_score': min(overall_scores) if overall_scores else 0,
            'max_score': max(overall_scores) if overall_scores else 0
        }
    
    def _calculate_consensus(self, scores: List[int]) -> str:
        """Calculate consensus level from scores"""
        if not scores or len(scores) < 2:
            return 'weak'
        
        mean_score = statistics.mean(scores)
        stdev = statistics.stdev(scores) if len(scores) > 1 else 0
        
        if stdev < 0.5:
            return 'strong'
        elif stdev < 1.5:
            return 'moderate'
        else:
            return 'weak'
    
    def _recommend_decision(self, scores: List[float], recommendations: List[str]) -> str:
        """Recommend a decision based on scores and recommendations"""
        if not scores:
            return 'reject'
        
        avg_score = statistics.mean(scores)
        
        # Accept recommendations
        accept_count = sum(1 for r in recommendations if 'accept' in r.lower())
        reject_count = sum(1 for r in recommendations if 'reject' in r.lower())
        
        if accept_count > reject_count and avg_score >= 7:
            return 'accept'
        elif accept_count > reject_count and avg_score >= 6:
            return 'conditional_accept'
        else:
            return 'reject'


class DecisionService:
    """Service for managing decisions"""
    
    def __init__(self, decision_repository: DecisionRepository, review_aggregation: ReviewAggregationService):
        self.decision_repository = decision_repository
        self.review_aggregation = review_aggregation
    
    def create_decision(self, decision_data: Dict[str, Any]) -> DecisionModel:
        """Create a decision"""
        paper_id = decision_data.get('paper_id')
        
        # Check if decision already exists
        existing = self.decision_repository.get_by_paper(paper_id)
        if existing:
            raise ValueError(f"Decision already exists for paper {paper_id}")
        
        decision_data['decided_at'] = datetime.utcnow()
        return self.decision_repository.create(decision_data)
    
    def get_decision(self, decision_id: int) -> Optional[DecisionModel]:
        """Get decision by ID"""
        return self.decision_repository.get_by_id(decision_id)
    
    def get_paper_decision(self, paper_id: int) -> Optional[DecisionModel]:
        """Get decision for a paper"""
        return self.decision_repository.get_by_paper(paper_id)
    
    def list_conference_decisions(self, conference_id: int) -> List[DecisionModel]:
        """List all decisions for a conference"""
        return self.decision_repository.get_by_conference(conference_id)
    
    def list_decisions_by_type(self, conference_id: int, decision_type: str) -> List[DecisionModel]:
        """List decisions by type"""
        return self.decision_repository.get_by_decision_type(conference_id, decision_type)
    
    def update_decision(self, decision_id: int, decision_data: Dict[str, Any]) -> Optional[DecisionModel]:
        """Update a decision"""
        decision = self.decision_repository.get_by_id(decision_id)
        if not decision:
            return None
        
        return self.decision_repository.update(decision_id, decision_data)
    
    def make_auto_decision(self, paper_id: int, decided_by: int) -> DecisionModel:
        """Make automatic decision based on review aggregation"""
        aggregation = self.review_aggregation.aggregate_paper_reviews(paper_id)
        
        decision_data = {
            'paper_id': paper_id,
            'decision': aggregation['recommended_decision'],
            'decided_by': decided_by,
            'avg_score': int(aggregation['avg_overall_score']),
            'review_count': aggregation['total_reviews'],
            'decided_at': datetime.utcnow()
        }
        
        return self.create_decision(decision_data)
    
    def set_conditional_accept(self, decision_id: int, conditions: str) -> Optional[DecisionModel]:
        """Set conditions for conditional accept"""
        decision = self.decision_repository.get_by_id(decision_id)
        if not decision:
            return None
        
        return self.decision_repository.update(decision_id, {
            'decision': 'conditional_accept',
            'conditions': conditions
        })
    
    def verify_conditions_met(self, decision_id: int, verified_by: int) -> Optional[DecisionModel]:
        """Verify that conditions for conditional accept are met"""
        return self.decision_repository.verify_conditions(decision_id, verified_by)
    
    def desk_reject_paper(self, paper_id: int, reason: str, decided_by: int) -> DecisionModel:
        """Desk reject a paper"""
        decision_data = {
            'paper_id': paper_id,
            'decision': 'desk_reject',
            'decided_by': decided_by,
            'internal_notes': reason,
            'decided_at': datetime.utcnow()
        }
        
        return self.create_decision(decision_data)
    
    def get_decision_report(self, conference_id: int) -> Dict[str, Any]:
        """Get decision report for a conference"""
        decisions = self.decision_repository.get_by_conference(conference_id)
        counts = self.decision_repository.count_decisions_by_type(conference_id)
        acceptance_rate = self.decision_repository.get_acceptance_rate(conference_id)
        
        total = len(decisions)
        
        return {
            'conference_id': conference_id,
            'total_papers': total,
            'accepted': counts.get('accept', 0),
            'rejected': counts.get('reject', 0),
            'conditional_accept': counts.get('conditional_accept', 0),
            'desk_rejected': counts.get('desk_reject', 0),
            'acceptance_rate': round(acceptance_rate, 2),
            'status_distribution': counts
        }
    
    def get_pending_decisions(self, conference_id: int) -> int:
        """Count papers without decisions"""
        # This would need a join with PaperModel to find papers without decisions
        all_decisions = self.decision_repository.get_by_conference(conference_id)
        # Assuming you have a way to get total papers count
        return 0  # Implementation depends on paper repository


class NotificationService:
    """Service for sending decision notifications"""
    
    def __init__(self, decision_repository: DecisionRepository):
        self.decision_repository = decision_repository
    
    def prepare_acceptance_notification(self, decision: DecisionModel) -> Dict[str, str]:
        """Prepare acceptance notification"""
        return {
            'subject': 'Paper Acceptance Notification',
            'template': 'acceptance_email',
            'body': f"Congratulations! Your paper has been accepted.\n\nFeedback: {decision.feedback_to_authors}",
            'decision_type': 'accepted'
        }
    
    def prepare_rejection_notification(self, decision: DecisionModel) -> Dict[str, str]:
        """Prepare rejection notification"""
        return {
            'subject': 'Paper Decision Notification',
            'template': 'rejection_email',
            'body': f"Thank you for your submission. Unfortunately, your paper was not accepted.\n\nFeedback: {decision.feedback_to_authors}",
            'decision_type': 'rejected'
        }
    
    def prepare_conditional_notification(self, decision: DecisionModel) -> Dict[str, str]:
        """Prepare conditional accept notification"""
        return {
            'subject': 'Conditional Acceptance - Action Required',
            'template': 'conditional_email',
            'body': f"Your paper has been conditionally accepted. Please address the following:\n\n{decision.conditions}",
            'decision_type': 'conditional'
        }
    
    def prepare_desk_reject_notification(self, decision: DecisionModel) -> Dict[str, str]:
        """Prepare desk reject notification"""
        return {
            'subject': 'Desk Rejection Notice',
            'template': 'desk_reject_email',
            'body': f"Your paper has been desk rejected.\n\nReason: {decision.internal_notes}",
            'decision_type': 'desk_rejected'
        }
    
    def get_notification_template(self, decision: DecisionModel) -> Dict[str, str]:
        """Get appropriate notification template"""
        if decision.decision == 'accept':
            return self.prepare_acceptance_notification(decision)
        elif decision.decision == 'reject':
            return self.prepare_rejection_notification(decision)
        elif decision.decision == 'conditional_accept':
            return self.prepare_conditional_notification(decision)
        elif decision.decision == 'desk_reject':
            return self.prepare_desk_reject_notification(decision)
        
        return {}
