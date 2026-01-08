# UTH Conference Paper Management System - Database Models
# Based on EasyChair-style workflow: CFP -> Submission -> Review -> Decision -> Camera-ready

# Core entities
from infrastructure.models.tenant_model import TenantModel
from infrastructure.models.user_model import UserModel

# Conference structure
from infrastructure.models.conference_model import ConferenceModel
from infrastructure.models.track_model import TrackModel

# Paper submission
from infrastructure.models.paper_model import PaperModel
from infrastructure.models.paper_author_model import PaperAuthorModel

# Program Committee
from infrastructure.models.pc_member_model import PCMemberModel
from infrastructure.models.coi_model import COIModel

# Review process
from infrastructure.models.paper_assignment_model import PaperAssignmentModel
from infrastructure.models.review_model import ReviewModel, ReviewDiscussionModel

# Decision and publication
from infrastructure.models.decision_model import DecisionModel
from infrastructure.models.camera_ready_model import CameraReadyModel

# Communication
from infrastructure.models.email_template_model import EmailTemplateModel, EmailLogModel

# Audit and logging
from infrastructure.models.audit_log_model import AuditLogModel

__all__ = [
    # Core
    'TenantModel',
    'UserModel',
    
    # Conference
    'ConferenceModel',
    'TrackModel',
    
    # Papers
    'PaperModel',
    'PaperAuthorModel',
    
    # PC
    'PCMemberModel',
    'COIModel',
    
    # Reviews
    'PaperAssignmentModel',
    'ReviewModel',
    'ReviewDiscussionModel',
    
    # Decisions
    'DecisionModel',
    'CameraReadyModel',
    
    # Communication
    'EmailTemplateModel',
    'EmailLogModel',
    
    # Audit
    'AuditLogModel',
]
 