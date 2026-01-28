from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime


class ReviewResponseSchema(Schema):
    """Schema for review response"""
    id = fields.Int()
    paper_id = fields.Int()
    reviewer_pc_id = fields.Int()
    overall_score = fields.Int()
    confidence_score = fields.Int()
    recommendation = fields.Str()
    originality_score = fields.Int()
    significance_score = fields.Int()
    technical_quality_score = fields.Int()
    clarity_score = fields.Int()
    relevance_score = fields.Int()
    summary = fields.Str()
    strengths = fields.Str()
    weaknesses = fields.Str()
    detailed_comments = fields.Str()
    confidential_comments = fields.Str()
    questions_for_authors = fields.Str()


class DecisionRequestSchema(Schema):
    """Schema for creating a decision"""
    paper_id = fields.Int(required=True)
    decision = fields.Str(
        required=True,
        validate=validate.OneOf(['accept', 'conditional_accept', 'reject', 'desk_reject'])
    )
    decision_type = fields.Str(
        validate=validate.OneOf(['full_paper', 'short_paper', 'poster', 'workshop']),
        allow_none=True
    )
    decided_by = fields.Int(required=True)
    avg_score = fields.Int(allow_none=True)
    review_count = fields.Int(allow_none=True)
    internal_notes = fields.Str(allow_none=True)
    meta_review = fields.Str(allow_none=True)
    feedback_to_authors = fields.Str(allow_none=True)
    conditions = fields.Str(allow_none=True)


class DecisionUpdateSchema(Schema):
    """Schema for updating a decision"""
    decision = fields.Str(
        validate=validate.OneOf(['accept', 'conditional_accept', 'reject', 'desk_reject']),
        allow_none=True
    )
    decision_type = fields.Str(
        validate=validate.OneOf(['full_paper', 'short_paper', 'poster', 'workshop']),
        allow_none=True
    )
    meta_review = fields.Str(allow_none=True)
    feedback_to_authors = fields.Str(allow_none=True)
    conditions = fields.Str(allow_none=True)
    internal_notes = fields.Str(allow_none=True)


class DecisionResponseSchema(Schema):
    """Schema for decision response"""
    id = fields.Int()
    paper_id = fields.Int()
    decision = fields.Str()
    decision_type = fields.Str()
    decided_by = fields.Int()
    decided_at = fields.DateTime()
    avg_score = fields.Int()
    review_count = fields.Int()
    internal_notes = fields.Str()
    meta_review = fields.Str()
    feedback_to_authors = fields.Str()
    conditions = fields.Str()
    conditions_met = fields.Bool()


class BulkNotificationRequestSchema(Schema):
    """Schema for bulk notifications"""
    decision_ids = fields.List(fields.Int(), required=True)
    include_feedback = fields.Bool(missing=True)
    include_reviews = fields.Bool(missing=False)
    send_immediately = fields.Bool(missing=False)
    custom_message = fields.Str(allow_none=True)


class ReviewAggregationSchema(Schema):
    """Schema for review aggregation results"""
    paper_id = fields.Int()
    total_reviews = fields.Int()
    avg_overall_score = fields.Float()
    avg_confidence = fields.Float()
    recommendation_summary = fields.Dict()
    avg_originality = fields.Float()
    avg_significance = fields.Float()
    avg_technical_quality = fields.Float()
    avg_clarity = fields.Float()
    avg_relevance = fields.Float()
    consensus_level = fields.Str()  # strong, moderate, weak
    recommended_decision = fields.Str()


class ConditionalAcceptSchema(Schema):
    """Schema for conditional accept requirements"""
    decision_id = fields.Int(required=True)
    conditions = fields.Str(required=True)
    deadline = fields.DateTime(allow_none=True)


class NotificationStatusSchema(Schema):
    """Schema for notification status"""
    id = fields.Int()
    decision_id = fields.Int()
    recipient_email = fields.Str()
    notification_type = fields.Str()  # acceptance, rejection, conditional_accept
    status = fields.Str()  # sent, failed, pending
    sent_at = fields.DateTime(allow_none=True)
    error_message = fields.Str(allow_none=True)


class DeskRejectRequestSchema(Schema):
    """Schema for desk reject"""
    paper_id = fields.Int(required=True)
    reason = fields.Str(required=True)
    decided_by = fields.Int(required=True)


class FinalDecisionReportSchema(Schema):
    """Schema for final decision report"""
    conference_id = fields.Int()
    total_papers = fields.Int()
    accepted = fields.Int()
    rejected = fields.Int()
    conditional_accept = fields.Int()
    desk_rejected = fields.Int()
    acceptance_rate = fields.Float()
    decision_timeline = fields.Dict()
