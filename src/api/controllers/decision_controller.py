from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.schemas.decision import (
    DecisionRequestSchema, DecisionUpdateSchema, DecisionResponseSchema,
    ReviewAggregationSchema, BulkNotificationRequestSchema,
    DeskRejectRequestSchema, FinalDecisionReportSchema
)
from services.decision_service import DecisionService, ReviewAggregationService, NotificationService
from infrastructure.repositories.decision_repository import DecisionRepository, ReviewRepository
from infrastructure.databases.mssql import session
from datetime import datetime

bp = Blueprint('decision', __name__, url_prefix='/decisions')

# Initialize schemas
decision_request_schema = DecisionRequestSchema()
decision_response_schema = DecisionResponseSchema()
decision_update_schema = DecisionUpdateSchema()
bulk_notification_schema = BulkNotificationRequestSchema()
desk_reject_schema = DeskRejectRequestSchema()

# Initialize repositories and services
def get_decision_services():
    """Get decision services"""
    review_repo = ReviewRepository(session)
    decision_repo = DecisionRepository(session)
    
    review_agg_service = ReviewAggregationService(review_repo)
    decision_service = DecisionService(decision_repo, review_agg_service)
    notification_service = NotificationService(decision_repo)
    
    return {
        'review_repo': review_repo,
        'decision_repo': decision_repo,
        'review_agg_service': review_agg_service,
        'decision_service': decision_service,
        'notification_service': notification_service
    }


# ==================== REVIEW AGGREGATION ENDPOINTS ====================

@bp.route('/reviews/aggregate/<int:paper_id>', methods=['GET'])
def aggregate_paper_reviews(paper_id):
    """Aggregate reviews for a paper"""
    try:
        services = get_decision_services()
        aggregation = services['review_agg_service'].aggregate_paper_reviews(paper_id)
        
        return jsonify(aggregation), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reviews/conference/<int:conference_id>', methods=['GET'])
def get_conference_review_status(conference_id):
    """Get review status for all papers in a conference"""
    try:
        services = get_decision_services()
        # Get all reviews for conference
        reviews = services['review_repo'].get_conference_reviews(conference_id)
        
        papers_reviewed = {}
        for review in reviews:
            if review.paper_id not in papers_reviewed:
                papers_reviewed[review.paper_id] = {
                    'completed': 0,
                    'pending': 0,
                    'total': 0
                }
            
            papers_reviewed[review.paper_id]['total'] += 1
            if review.overall_score:
                papers_reviewed[review.paper_id]['completed'] += 1
            else:
                papers_reviewed[review.paper_id]['pending'] += 1
        
        return jsonify({
            'conference_id': conference_id,
            'paper_count': len(papers_reviewed),
            'papers_status': papers_reviewed
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== DECISION MANAGEMENT ENDPOINTS ====================

@bp.route('/', methods=['POST'])
def create_decision():
    """Create a decision for a paper"""
    try:
        data = decision_request_schema.load(request.get_json())
        
        services = get_decision_services()
        decision = services['decision_service'].create_decision(data)
        
        return jsonify(decision_response_schema.dump(decision)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:decision_id>', methods=['GET'])
def get_decision(decision_id):
    """Get decision by ID"""
    try:
        services = get_decision_services()
        decision = services['decision_service'].get_decision(decision_id)
        
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        
        return jsonify(decision_response_schema.dump(decision)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/paper/<int:paper_id>', methods=['GET'])
def get_paper_decision(paper_id):
    """Get decision for a paper"""
    try:
        services = get_decision_services()
        decision = services['decision_service'].get_paper_decision(paper_id)
        
        if not decision:
            return jsonify({'error': 'No decision found for this paper'}), 404
        
        return jsonify(decision_response_schema.dump(decision)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/conference/<int:conference_id>', methods=['GET'])
def list_conference_decisions(conference_id):
    """List all decisions for a conference"""
    try:
        decision_type = request.args.get('type')
        
        services = get_decision_services()
        
        if decision_type:
            decisions = services['decision_service'].list_decisions_by_type(conference_id, decision_type)
        else:
            decisions = services['decision_service'].list_conference_decisions(conference_id)
        
        return jsonify(decision_response_schema.dump(decisions, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:decision_id>', methods=['PUT'])
def update_decision(decision_id):
    """Update a decision"""
    try:
        data = decision_update_schema.load(request.get_json())
        
        services = get_decision_services()
        decision = services['decision_service'].update_decision(decision_id, data)
        
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        
        return jsonify(decision_response_schema.dump(decision)), 200
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:decision_id>', methods=['DELETE'])
def delete_decision(decision_id):
    """Delete a decision"""
    try:
        services = get_decision_services()
        success = services['decision_repo'].delete(decision_id)
        
        if not success:
            return jsonify({'error': 'Decision not found'}), 404
        
        return jsonify({'message': 'Decision deleted successfully'}), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== AUTO-DECISION ENDPOINTS ====================

@bp.route('/auto-decide/<int:paper_id>', methods=['POST'])
def make_auto_decision(paper_id):
    """Make automatic decision based on review aggregation"""
    try:
        data = request.get_json()
        decided_by = data.get('decided_by', 1)
        
        services = get_decision_services()
        decision = services['decision_service'].make_auto_decision(paper_id, decided_by)
        
        return jsonify(decision_response_schema.dump(decision)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bulk-auto-decide', methods=['POST'])
def bulk_auto_decide():
    """Make automatic decisions for multiple papers"""
    try:
        data = request.get_json()
        paper_ids = data.get('paper_ids', [])
        decided_by = data.get('decided_by', 1)
        
        if not paper_ids:
            return jsonify({'error': 'paper_ids is required'}), 400
        
        services = get_decision_services()
        results = []
        errors = []
        
        for paper_id in paper_ids:
            try:
                decision = services['decision_service'].make_auto_decision(paper_id, decided_by)
                results.append(decision)
            except Exception as e:
                errors.append({'paper_id': paper_id, 'error': str(e)})
        
        return jsonify({
            'successful': len(results),
            'failed': len(errors),
            'decisions': decision_response_schema.dump(results, many=True),
            'errors': errors if errors else None
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CONDITIONAL ACCEPT ENDPOINTS ====================

@bp.route('/<int:decision_id>/conditional', methods=['PATCH'])
def set_conditional_accept(decision_id):
    """Set conditional accept with requirements"""
    try:
        data = request.get_json()
        conditions = data.get('conditions')
        
        if not conditions:
            return jsonify({'error': 'conditions is required'}), 400
        
        services = get_decision_services()
        decision = services['decision_service'].set_conditional_accept(decision_id, conditions)
        
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        
        return jsonify(decision_response_schema.dump(decision)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:decision_id>/verify-conditions', methods=['POST'])
def verify_conditions_met(decision_id):
    """Verify that conditional accept requirements are met"""
    try:
        data = request.get_json()
        verified_by = data.get('verified_by', 1)
        
        services = get_decision_services()
        decision = services['decision_service'].verify_conditions_met(decision_id, verified_by)
        
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        
        return jsonify(decision_response_schema.dump(decision)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== DESK REJECT ENDPOINTS ====================

@bp.route('/desk-reject', methods=['POST'])
def desk_reject():
    """Desk reject a paper"""
    try:
        data = desk_reject_schema.load(request.get_json())
        
        services = get_decision_services()
        decision = services['decision_service'].desk_reject_paper(
            data['paper_id'],
            data['reason'],
            data['decided_by']
        )
        
        return jsonify(decision_response_schema.dump(decision)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== REPORTING ENDPOINTS ====================

@bp.route('/report/conference/<int:conference_id>', methods=['GET'])
def get_decision_report(conference_id):
    """Get decision report for a conference"""
    try:
        services = get_decision_services()
        report = services['decision_service'].get_decision_report(conference_id)
        
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/report/summary/<int:conference_id>', methods=['GET'])
def get_conference_summary(conference_id):
    """Get summary statistics for a conference"""
    try:
        services = get_decision_services()
        
        decisions = services['decision_repo'].get_by_conference(conference_id)
        counts = services['decision_repo'].count_decisions_by_type(conference_id)
        acceptance_rate = services['decision_repo'].get_acceptance_rate(conference_id)
        
        return jsonify({
            'conference_id': conference_id,
            'total_decisions': len(decisions),
            'accepted': counts.get('accept', 0),
            'rejected': counts.get('reject', 0),
            'conditional': counts.get('conditional_accept', 0),
            'desk_rejected': counts.get('desk_reject', 0),
            'acceptance_rate': f"{acceptance_rate:.2f}%"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/by-decision-maker/<int:user_id>', methods=['GET'])
def get_decisions_by_maker(user_id):
    """Get all decisions made by a user"""
    try:
        services = get_decision_services()
        decisions = services['decision_repo'].get_decisions_by_decided_by(user_id)
        
        return jsonify(decision_response_schema.dump(decisions, many=True)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== NOTIFICATION ENDPOINTS ====================

@bp.route('/<int:decision_id>/notification-template', methods=['GET'])
def get_notification_template(decision_id):
    """Get notification template for a decision"""
    try:
        services = get_decision_services()
        decision = services['decision_repo'].get_by_id(decision_id)
        
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        
        template = services['notification_service'].get_notification_template(decision)
        
        return jsonify(template), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/bulk-notifications', methods=['POST'])
def bulk_send_notifications():
    """Send bulk notifications for decisions"""
    try:
        data = bulk_notification_schema.load(request.get_json())
        decision_ids = data.get('decision_ids', [])
        include_feedback = data.get('include_feedback', True)
        include_reviews = data.get('include_reviews', False)
        
        if not decision_ids:
            return jsonify({'error': 'decision_ids is required'}), 400
        
        services = get_decision_services()
        notifications = []
        
        for decision_id in decision_ids:
            decision = services['decision_repo'].get_by_id(decision_id)
            if decision:
                template = services['notification_service'].get_notification_template(decision)
                notifications.append({
                    'decision_id': decision_id,
                    'subject': template.get('subject'),
                    'template': template.get('template'),
                    'type': template.get('decision_type')
                })
        
        return jsonify({
            'total_notifications': len(notifications),
            'notifications': notifications,
            'status': 'ready_to_send'
        }), 200
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics/acceptance-rate/<int:conference_id>', methods=['GET'])
def get_acceptance_rate(conference_id):
    """Get acceptance rate for a conference"""
    try:
        services = get_decision_services()
        rate = services['decision_repo'].get_acceptance_rate(conference_id)
        
        return jsonify({
            'conference_id': conference_id,
            'acceptance_rate': f"{rate:.2f}%"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics/decision-timeline/<int:conference_id>', methods=['GET'])
def get_decision_timeline(conference_id):
    """Get decision timeline for a conference"""
    try:
        services = get_decision_services()
        recent = services['decision_repo'].get_recent_decisions(conference_id, limit=20)
        
        timeline = [
            {
                'decision_id': d.id,
                'decision': d.decision,
                'decided_at': d.decided_at.isoformat(),
                'paper_id': d.paper_id
            }
            for d in recent
        ]
        
        return jsonify({
            'conference_id': conference_id,
            'recent_decisions': timeline
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
