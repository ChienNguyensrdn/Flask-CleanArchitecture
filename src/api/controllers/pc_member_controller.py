from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.schemas.pc_member import (
    PCMemberRequestSchema, PCMemberResponseSchema,
    PCInvitationRequestSchema,
    COIRequestSchema, COIResponseSchema,
    BidRequestSchema, BidResponseSchema
)
from services.pc_member_service import PCMemberService, COIService
from services.bidding_assignment_service import BiddingService, AssignmentService
from infrastructure.repositories.pc_member_repository import PCMemberRepository, COIRepository
from infrastructure.databases.mssql import session
from datetime import datetime

bp = Blueprint('pc_member', __name__, url_prefix='/pc-members')

# Initialize schemas
pc_member_response_schema = PCMemberResponseSchema()
pc_invitation_request_schema = PCInvitationRequestSchema()
coi_request_schema = COIRequestSchema()
coi_response_schema = COIResponseSchema()
bid_request_schema = BidRequestSchema()
bid_response_schema = BidResponseSchema()

# Initialize repositories and services
def get_pc_services():
    """Get PC services"""
    pc_repo = PCMemberRepository(session)
    coi_repo = COIRepository(session)
    
    return {
        'pc_service': PCMemberService(pc_repo, coi_repo),
        'coi_service': COIService(coi_repo),
        'bidding_service': BiddingService(pc_repo, coi_repo),
        'assignment_service': AssignmentService(pc_repo, coi_repo)
    }


# ==================== PC MEMBER MANAGEMENT ENDPOINTS ====================

@bp.route('/', methods=['GET'])
def list_pc_members():
    """List all PC members for a conference"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        if not conference_id:
            return jsonify({'error': 'conference_id is required'}), 400
        
        services = get_pc_services()
        members = services['pc_service'].list_conference_members(conference_id)
        
        return jsonify(pc_member_response_schema.dump(members, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>', methods=['GET'])
def get_pc_member(member_id):
    """Get PC member details"""
    try:
        services = get_pc_services()
        member = services['pc_service'].get_member(member_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def create_pc_member():
    """Create new PC member (via invitation)"""
    try:
        data = pc_invitation_request_schema.load(request.get_json())
        
        services = get_pc_services()
        member = services['pc_service'].invite_pc_member(data)
        
        return jsonify(pc_member_response_schema.dump(member)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>', methods=['PUT'])
def update_pc_member(member_id):
    """Update PC member details"""
    try:
        data = request.get_json()
        
        services = get_pc_services()
        member = services['pc_service'].update_member(member_id, data)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>', methods=['DELETE'])
def delete_pc_member(member_id):
    """Remove PC member"""
    try:
        services = get_pc_services()
        success = services['pc_service'].remove_member(member_id)
        
        if not success:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify({'message': 'PC member removed successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/by-role', methods=['GET'])
def get_members_by_role():
    """Get PC members by role"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        role = request.args.get('role')
        
        if not conference_id or not role:
            return jsonify({'error': 'conference_id and role are required'}), 400
        
        services = get_pc_services()
        members = services['pc_service'].list_members_by_role(conference_id, role)
        
        return jsonify(pc_member_response_schema.dump(members, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/active-reviewers', methods=['GET'])
def get_active_reviewers():
    """Get active reviewers for a conference"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        if not conference_id:
            return jsonify({'error': 'conference_id is required'}), 400
        
        services = get_pc_services()
        reviewers = services['pc_service'].list_active_reviewers(conference_id)
        
        return jsonify(pc_member_response_schema.dump(reviewers, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bulk-invite', methods=['POST'])
def bulk_invite_members():
    """Bulk invite PC members"""
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'error': 'Expected array of member invitations'}), 400
        
        services = get_pc_services()
        results = []
        errors = []
        
        for i, item in enumerate(data):
            try:
                member = services['pc_service'].invite_pc_member(item)
                results.append(member)
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
        
        response = {
            'invited': len(results),
            'failed': len(errors),
            'members': pc_member_response_schema.dump(results, many=True)
        }
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/role', methods=['PATCH'])
def change_member_role(member_id):
    """Change PC member role"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'role is required'}), 400
        
        services = get_pc_services()
        member = services['pc_service'].change_role(member_id, new_role)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/track', methods=['PATCH'])
def assign_track(member_id):
    """Assign PC member to track"""
    try:
        data = request.get_json()
        track_id = data.get('track_id')
        
        if not track_id:
            return jsonify({'error': 'track_id is required'}), 400
        
        services = get_pc_services()
        member = services['pc_service'].assign_track(member_id, track_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/expertise', methods=['PATCH'])
def set_expertise(member_id):
    """Set PC member expertise"""
    try:
        data = request.get_json()
        keywords = data.get('expertise_keywords')
        
        if not keywords:
            return jsonify({'error': 'expertise_keywords is required'}), 400
        
        services = get_pc_services()
        member = services['pc_service'].update_expertise(member_id, keywords)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/quota', methods=['PATCH'])
def set_review_quota(member_id):
    """Set maximum papers for review"""
    try:
        data = request.get_json()
        max_papers = data.get('max_papers')
        
        if max_papers is None:
            return jsonify({'error': 'max_papers is required'}), 400
        
        services = get_pc_services()
        member = services['pc_service'].set_review_quota(member_id, max_papers)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== INVITATION MANAGEMENT ENDPOINTS ====================

@bp.route('/<int:member_id>/invitation/send', methods=['POST'])
def send_invitation(member_id):
    """Resend invitation to PC member"""
    try:
        services = get_pc_services()
        member = services['pc_service'].resend_invitation(member_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/invitation/accept', methods=['POST'])
def accept_invitation(member_id):
    """Accept PC invitation"""
    try:
        services = get_pc_services()
        member = services['pc_service'].accept_invitation(member_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/invitation/decline', methods=['POST'])
def decline_invitation(member_id):
    """Decline PC invitation"""
    try:
        services = get_pc_services()
        member = services['pc_service'].decline_invitation(member_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify(pc_member_response_schema.dump(member)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/pending-invitations', methods=['GET'])
def get_pending_invitations():
    """Get pending invitations for a conference"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        if not conference_id:
            return jsonify({'error': 'conference_id is required'}), 400
        
        services = get_pc_services()
        members = services['pc_service'].get_pending_invitations(conference_id)
        
        return jsonify(pc_member_response_schema.dump(members, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== COI MANAGEMENT ENDPOINTS ====================

@bp.route('/coi', methods=['POST'])
def declare_coi():
    """Declare conflict of interest"""
    try:
        data = coi_request_schema.load(request.get_json())
        
        services = get_pc_services()
        coi = services['coi_service'].declare_coi(data)
        
        return jsonify(coi_response_schema.dump(coi)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/coi', methods=['GET'])
def get_member_cois(member_id):
    """Get all COIs for a member"""
    try:
        services = get_pc_services()
        cois = services['coi_service'].list_member_cois(member_id)
        
        return jsonify(coi_response_schema.dump(cois, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/coi/paper/<int:paper_id>', methods=['GET'])
def get_paper_cois(paper_id):
    """Get all COIs for a paper"""
    try:
        services = get_pc_services()
        cois = services['coi_service'].list_paper_cois(paper_id)
        
        return jsonify(coi_response_schema.dump(cois, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/check-conflict', methods=['GET'])
def check_conflict():
    """Check if reviewer has conflict with paper"""
    try:
        member_id = request.args.get('member_id', type=int)
        paper_id = request.args.get('paper_id', type=int)
        
        if not member_id or not paper_id:
            return jsonify({'error': 'member_id and paper_id are required'}), 400
        
        services = get_pc_services()
        result = services['assignment_service'].check_reviewer_conflict(paper_id, member_id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/coi/<int:coi_id>', methods=['PUT'])
def update_coi(coi_id):
    """Update COI"""
    try:
        data = request.get_json()
        
        services = get_pc_services()
        coi = services['coi_service'].update_coi(coi_id, data)
        
        if not coi:
            return jsonify({'error': 'COI not found'}), 404
        
        return jsonify(coi_response_schema.dump(coi)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/coi/<int:coi_id>', methods=['DELETE'])
def delete_coi(coi_id):
    """Delete COI"""
    try:
        services = get_pc_services()
        success = services['coi_service'].remove_coi(coi_id)
        
        if not success:
            return jsonify({'error': 'COI not found'}), 404
        
        return jsonify({'message': 'COI removed successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/coi/bulk-declare', methods=['POST'])
def bulk_declare_cois():
    """Bulk declare COIs"""
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'error': 'Expected array of COI declarations'}), 400
        
        services = get_pc_services()
        results = []
        errors = []
        
        for i, item in enumerate(data):
            try:
                coi = services['coi_service'].declare_coi(item)
                results.append(coi)
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
        
        response = {
            'declared': len(results),
            'failed': len(errors),
            'cois': coi_response_schema.dump(results, many=True)
        }
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BIDDING MANAGEMENT ENDPOINTS ====================

@bp.route('/bids', methods=['POST'])
def submit_bid():
    """Submit bid for a paper"""
    try:
        data = bid_request_schema.load(request.get_json())
        
        services = get_pc_services()
        bid = services['bidding_service'].submit_bid(
            data['pc_member_id'],
            data['paper_id'],
            data['bid_value']
        )
        
        return jsonify(bid_response_schema.dump(bid)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bids/paper/<int:paper_id>', methods=['GET'])
def get_paper_bids(paper_id):
    """Get all bids for a paper"""
    try:
        services = get_pc_services()
        bids = services['bidding_service'].list_paper_bids(paper_id)
        
        return jsonify(bid_response_schema.dump(bids, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/bids', methods=['GET'])
def get_member_bids(member_id):
    """Get all bids submitted by a member"""
    try:
        services = get_pc_services()
        bids = services['bidding_service'].list_member_bids(member_id)
        
        return jsonify(bid_response_schema.dump(bids, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bids/conference', methods=['GET'])
def get_conference_bids():
    """Get all bids for a conference"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        if not conference_id:
            return jsonify({'error': 'conference_id is required'}), 400
        
        services = get_pc_services()
        bids = services['bidding_service'].list_conference_bids(conference_id)
        
        return jsonify(bid_response_schema.dump(bids, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bids/score/<int:paper_id>', methods=['GET'])
def get_paper_bid_score(paper_id):
    """Get aggregated bid score for a paper"""
    try:
        services = get_pc_services()
        score = services['bidding_service'].calculate_paper_bid_score(paper_id)
        
        return jsonify(score), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bids/summary', methods=['GET'])
def get_bidding_summary():
    """Get bidding summary for a conference"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        if not conference_id:
            return jsonify({'error': 'conference_id is required'}), 400
        
        services = get_pc_services()
        summary = services['bidding_service'].get_bidding_summary(conference_id)
        
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ASSIGNMENT MANAGEMENT ENDPOINTS ====================

@bp.route('/assignments', methods=['POST'])
def assign_reviewer():
    """Assign reviewer to paper"""
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        member_id = data.get('member_id')
        assigned_by = data.get('assigned_by', 1)
        
        if not paper_id or not member_id:
            return jsonify({'error': 'paper_id and member_id are required'}), 400
        
        services = get_pc_services()
        assignment = services['assignment_service'].assign_reviewer(paper_id, member_id, assigned_by)
        
        if not assignment:
            return jsonify({'error': 'Assignment failed'}), 400
        
        return jsonify({
            'message': 'Reviewer assigned successfully',
            'assignment_id': assignment.id,
            'paper_id': paper_id,
            'member_id': member_id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
def unassign_reviewer(assignment_id):
    """Remove reviewer assignment"""
    try:
        services = get_pc_services()
        success = services['assignment_service'].unassign_reviewer(assignment_id)
        
        if not success:
            return jsonify({'error': 'Assignment not found'}), 404
        
        return jsonify({'message': 'Reviewer unassigned successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/assignments/paper/<int:paper_id>', methods=['GET'])
def get_paper_assignments(paper_id):
    """Get all reviewers assigned to a paper"""
    try:
        services = get_pc_services()
        assignments = services['assignment_service'].list_paper_assignments(paper_id)
        
        return jsonify({
            'paper_id': paper_id,
            'reviewer_count': len(assignments),
            'assignments': [{'id': a.id, 'member_id': a.pc_member_id, 'assigned_at': a.assigned_at.isoformat()} for a in assignments]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/assignments', methods=['GET'])
def get_member_assignments(member_id):
    """Get all papers assigned to a member"""
    try:
        services = get_pc_services()
        assignments = services['assignment_service'].list_member_assignments(member_id)
        workload = services['assignment_service'].get_member_review_load(member_id)
        
        return jsonify({
            'member_id': member_id,
            'assignment_count': len(assignments),
            'workload': workload,
            'assignments': [{'id': a.id, 'paper_id': a.paper_id, 'assigned_at': a.assigned_at.isoformat()} for a in assignments]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/assignments/auto-assign', methods=['POST'])
def auto_assign_reviewers():
    """Auto-assign reviewers to paper"""
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        num_reviewers = data.get('num_reviewers', 3)
        prefer_senior = data.get('prefer_senior', True)
        assigned_by = data.get('assigned_by', 1)
        
        if not paper_id:
            return jsonify({'error': 'paper_id is required'}), 400
        
        services = get_pc_services()
        assignments = services['assignment_service'].auto_assign_reviewers(
            paper_id, num_reviewers, prefer_senior, assigned_by
        )
        
        return jsonify({
            'message': f'{len(assignments)} reviewers assigned',
            'paper_id': paper_id,
            'reviewer_count': len(assignments)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/workload', methods=['GET'])
def get_member_workload(member_id):
    """Get member review workload"""
    try:
        services = get_pc_services()
        workload = services['assignment_service'].get_member_review_load(member_id)
        
        if not workload:
            return jsonify({'error': 'Member not found'}), 404
        
        return jsonify(workload), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/assignments/statistics', methods=['GET'])
def get_assignment_statistics():
    """Get assignment statistics for a conference"""
    try:
        conference_id = request.args.get('conference_id', type=int)
        if not conference_id:
            return jsonify({'error': 'conference_id is required'}), 400
        
        services = get_pc_services()
        stats = services['assignment_service'].get_assignment_statistics(conference_id)
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== PC MEMBER ACCESS CONTROL ====================

@bp.route('/<int:member_id>/author-access/enable', methods=['POST'])
def enable_author_access(member_id):
    """Enable author info access"""
    try:
        services = get_pc_services()
        member = services['pc_service'].enable_author_access(member_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify({'message': 'Author access enabled', 'member_id': member_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:member_id>/author-access/disable', methods=['POST'])
def disable_author_access(member_id):
    """Disable author info access"""
    try:
        services = get_pc_services()
        member = services['pc_service'].disable_author_access(member_id)
        
        if not member:
            return jsonify({'error': 'PC member not found'}), 404
        
        return jsonify({'message': 'Author access disabled', 'member_id': member_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
