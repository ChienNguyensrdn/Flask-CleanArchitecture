from typing import List, Optional, Dict, Any
from infrastructure.repositories.pc_member_repository import PCMemberRepository, COIRepository
from infrastructure.models.pc_member_model import PCMemberModel, BidModel, AssignmentModel
from infrastructure.models.paper_model import PaperModel
from datetime import datetime
from sqlalchemy import func, desc
import statistics


class BiddingService:
    """Service for managing paper bidding"""
    
    def __init__(self, pc_member_repository: PCMemberRepository, coi_repository: COIRepository):
        self.pc_member_repository = pc_member_repository
        self.coi_repository = coi_repository
    
    def submit_bid(self, member_id: int, paper_id: int, bid_value: int) -> Optional[BidModel]:
        """Submit a bid for a paper"""
        # Validate bid value
        valid_values = [-2, -1, 0, 1, 2]
        if bid_value not in valid_values:
            raise ValueError(f"Bid value must be one of {valid_values}")
        
        # Check if member has conflict with paper
        has_conflict = self.coi_repository.check_conflict(member_id, paper_id)
        if has_conflict:
            raise ValueError("Cannot bid on paper due to conflict of interest")
        
        # Check if member has available capacity
        member = self.pc_member_repository.get_by_id(member_id)
        if not member:
            raise ValueError("PC member not found")
        
        capacity = self.pc_member_repository.get_available_capacity(member_id)
        if capacity <= 0:
            raise ValueError("PC member has reached maximum review quota")
        
        bid_data = {
            'pc_member_id': member_id,
            'paper_id': paper_id,
            'bid_value': bid_value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        return self.pc_member_repository.create_bid(bid_data)
    
    def update_bid(self, bid_id: int, new_bid_value: int) -> Optional[BidModel]:
        """Update a bid"""
        valid_values = [-2, -1, 0, 1, 2]
        if new_bid_value not in valid_values:
            raise ValueError(f"Bid value must be one of {valid_values}")
        
        return self.pc_member_repository.update_bid(bid_id, {
            'bid_value': new_bid_value,
            'updated_at': datetime.utcnow()
        })
    
    def get_bid(self, bid_id: int) -> Optional[BidModel]:
        """Get bid by ID"""
        return self.pc_member_repository.get_bid(bid_id)
    
    def list_paper_bids(self, paper_id: int) -> List[BidModel]:
        """List all bids for a paper"""
        return self.pc_member_repository.get_paper_bids(paper_id)
    
    def list_member_bids(self, member_id: int) -> List[BidModel]:
        """List all bids for a member"""
        return self.pc_member_repository.get_member_bids(member_id)
    
    def list_conference_bids(self, conference_id: int) -> List[BidModel]:
        """List all bids for a conference"""
        return self.pc_member_repository.get_conference_bids(conference_id)
    
    def remove_bid(self, bid_id: int) -> bool:
        """Remove a bid"""
        return self.pc_member_repository.delete_bid(bid_id)
    
    def calculate_paper_bid_score(self, paper_id: int) -> Dict[str, Any]:
        """Calculate aggregated bid score for a paper"""
        bids = self.list_paper_bids(paper_id)
        
        if not bids:
            return {
                'paper_id': paper_id,
                'total_bids': 0,
                'average_score': 0,
                'median_score': 0,
                'positive_count': 0,
                'neutral_count': 0,
                'negative_count': 0,
                'strong_positive': 0,
                'strong_negative': 0
            }
        
        bid_values = [bid.bid_value for bid in bids]
        positive = sum(1 for b in bid_values if b > 0)
        negative = sum(1 for b in bid_values if b < 0)
        neutral = sum(1 for b in bid_values if b == 0)
        strong_pos = sum(1 for b in bid_values if b == 2)
        strong_neg = sum(1 for b in bid_values if b == -2)
        
        avg_score = sum(bid_values) / len(bid_values)
        median_score = statistics.median(bid_values)
        
        return {
            'paper_id': paper_id,
            'total_bids': len(bids),
            'average_score': round(avg_score, 2),
            'median_score': median_score,
            'positive_count': positive,
            'neutral_count': neutral,
            'negative_count': negative,
            'strong_positive': strong_pos,
            'strong_negative': strong_neg
        }
    
    def get_papers_by_bid_score(self, conference_id: int, min_score: float = -2, max_score: float = 2) -> List[Dict[str, Any]]:
        """Get papers ranked by bid score"""
        papers = self.pc_member_repository.get_conference_papers(conference_id)
        
        results = []
        for paper in papers:
            score = self.calculate_paper_bid_score(paper.id)
            if min_score <= score['average_score'] <= max_score:
                score['paper_id'] = paper.id
                score['paper_title'] = paper.title
                results.append(score)
        
        # Sort by average score descending
        results.sort(key=lambda x: x['average_score'], reverse=True)
        return results
    
    def get_bidding_summary(self, conference_id: int) -> Dict[str, Any]:
        """Get bidding summary for a conference"""
        members = self.pc_member_repository.get_by_conference(conference_id)
        bids = self.pc_member_repository.get_conference_bids(conference_id)
        
        if not bids:
            return {
                'conference_id': conference_id,
                'total_members': len(members),
                'total_bids': 0,
                'average_bids_per_member': 0,
                'bid_coverage': 0
            }
        
        bid_counts = {}
        for bid in bids:
            bid_counts[bid.pc_member_id] = bid_counts.get(bid.pc_member_id, 0) + 1
        
        avg_bids = sum(bid_counts.values()) / len(bid_counts) if bid_counts else 0
        
        return {
            'conference_id': conference_id,
            'total_members': len(members),
            'total_bids': len(bids),
            'members_who_bid': len(bid_counts),
            'average_bids_per_member': round(avg_bids, 2),
            'bid_distribution': bid_counts
        }


class AssignmentService:
    """Service for managing paper assignments to reviewers"""
    
    def __init__(self, pc_member_repository: PCMemberRepository, coi_repository: COIRepository):
        self.pc_member_repository = pc_member_repository
        self.coi_repository = coi_repository
    
    def assign_reviewer(self, paper_id: int, member_id: int, assigned_by: int) -> Optional[AssignmentModel]:
        """Assign a reviewer to a paper"""
        # Check member exists
        member = self.pc_member_repository.get_by_id(member_id)
        if not member:
            raise ValueError("PC member not found")
        
        # Check if member can review more papers
        if not self.pc_member_repository.can_review_more(member_id):
            raise ValueError("Member has reached maximum review quota")
        
        # Check for conflict of interest
        if self.coi_repository.check_conflict(member_id, paper_id):
            raise ValueError("Cannot assign reviewer due to conflict of interest")
        
        # Check if already assigned
        if self.pc_member_repository.is_paper_assigned_to_member(paper_id, member_id):
            raise ValueError("Member is already assigned to review this paper")
        
        assignment_data = {
            'paper_id': paper_id,
            'pc_member_id': member_id,
            'assigned_by': assigned_by,
            'assigned_at': datetime.utcnow(),
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        # Increment assigned count for member
        self.pc_member_repository.increment_assigned_count(member_id)
        
        return self.pc_member_repository.create_assignment(assignment_data)
    
    def unassign_reviewer(self, assignment_id: int) -> bool:
        """Remove reviewer assignment"""
        assignment = self.pc_member_repository.get_assignment(assignment_id)
        if not assignment:
            return False
        
        # Decrement assigned count
        self.pc_member_repository.decrement_assigned_count(assignment.pc_member_id)
        
        return self.pc_member_repository.delete_assignment(assignment_id)
    
    def get_assignment(self, assignment_id: int) -> Optional[AssignmentModel]:
        """Get assignment by ID"""
        return self.pc_member_repository.get_assignment(assignment_id)
    
    def list_paper_assignments(self, paper_id: int) -> List[AssignmentModel]:
        """List all assignments for a paper"""
        return self.pc_member_repository.get_paper_assignments(paper_id)
    
    def list_member_assignments(self, member_id: int) -> List[AssignmentModel]:
        """List all assignments for a member"""
        return self.pc_member_repository.get_member_assignments(member_id)
    
    def get_paper_reviewer_count(self, paper_id: int) -> int:
        """Get number of assigned reviewers for a paper"""
        return self.pc_member_repository.get_paper_reviewer_count(paper_id)
    
    def get_member_review_load(self, member_id: int) -> Dict[str, Any]:
        """Get review workload for a member"""
        member = self.pc_member_repository.get_by_id(member_id)
        if not member:
            return None
        
        assignments = self.list_member_assignments(member_id)
        completed = sum(1 for a in assignments if a.review_completed)
        pending = len(assignments) - completed
        
        return {
            'member_id': member_id,
            'max_papers': member.max_papers,
            'assigned_count': member.assigned_papers_count or 0,
            'available_capacity': self.pc_member_repository.get_available_capacity(member_id),
            'completed_reviews': completed,
            'pending_reviews': pending,
            'review_percentage': round((completed / len(assignments) * 100), 2) if assignments else 0
        }
    
    def auto_assign_reviewers(self, paper_id: int, num_reviewers: int = 3, 
                             prefer_senior: bool = True, assigned_by: int = None) -> List[AssignmentModel]:
        """Automatically assign reviewers to a paper"""
        if num_reviewers < 1 or num_reviewers > 10:
            raise ValueError("Number of reviewers must be between 1 and 10")
        
        # Get available reviewers (no COI, have capacity)
        all_members = self.pc_member_repository.get_active_reviewers(paper_id)  # Gets conference members
        
        # Filter out those with conflicts
        available = []
        for member in all_members:
            if not self.coi_repository.check_conflict(member.id, paper_id):
                if self.pc_member_repository.get_available_capacity(member.id) > 0:
                    available.append(member)
        
        # Sort by preference
        if prefer_senior:
            role_priority = {'senior_pc': 0, 'track_chair': 1, 'program_chair': 2, 'reviewer': 3}
            available.sort(key=lambda m: role_priority.get(m.role, 4))
        
        # Sort by workload (prefer less busy)
        available.sort(key=lambda m: m.assigned_papers_count or 0)
        
        # Select top reviewers
        selected = available[:num_reviewers]
        
        if len(selected) < num_reviewers:
            raise ValueError(f"Not enough available reviewers. Found {len(selected)}, need {num_reviewers}")
        
        assignments = []
        for member in selected:
            assignment = self.assign_reviewer(paper_id, member.id, assigned_by or 1)
            assignments.append(assignment)
        
        return assignments
    
    def check_reviewer_conflict(self, paper_id: int, member_id: int) -> Dict[str, Any]:
        """Check if reviewer has conflict with paper"""
        conflict = self.coi_repository.get_by_pc_member_and_paper(member_id, paper_id)
        
        return {
            'member_id': member_id,
            'paper_id': paper_id,
            'has_conflict': bool(conflict),
            'conflict_type': conflict.conflict_type if conflict else None,
            'conflict_reason': conflict.description if conflict else None
        }
    
    def get_assignment_statistics(self, conference_id: int) -> Dict[str, Any]:
        """Get assignment statistics for a conference"""
        members = self.pc_member_repository.get_by_conference(conference_id)
        assignments = self.pc_member_repository.get_conference_assignments(conference_id)
        
        if not assignments:
            return {
                'conference_id': conference_id,
                'total_assignments': 0,
                'total_reviewers': len(members),
                'average_workload': 0,
                'max_workload': 0,
                'min_workload': 0
            }
        
        workloads = {}
        for assignment in assignments:
            workloads[assignment.pc_member_id] = workloads.get(assignment.pc_member_id, 0) + 1
        
        workload_values = list(workloads.values()) if workloads else [0]
        
        return {
            'conference_id': conference_id,
            'total_assignments': len(assignments),
            'total_reviewers': len(members),
            'reviewers_with_assignments': len(workloads),
            'average_workload': round(sum(workload_values) / len(workload_values), 2),
            'max_workload': max(workload_values),
            'min_workload': min(workload_values),
            'workload_distribution': workloads
        }
