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
from infrastructure.models.rebuttal_model import RebuttalModel

# Decision and publication
from infrastructure.models.decision_model import DecisionModel
from infrastructure.models.camera_ready_model import CameraReadyModel

# Communication
from infrastructure.models.email_template_model import EmailTemplateModel, EmailLogModel

# Audit and logging
from infrastructure.models.audit_log_model import AuditLogModel

# Legacy models (to be migrated)
from infrastructure.models.program_model import ProgramModel
from infrastructure.models.survey_model import SurveyModel
from infrastructure.models.todo_model import TodoModel
from infrastructure.models.course_model import CourseModel

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
    'RebuttalModel',
    
    # Decisions
    'DecisionModel',
    'CameraReadyModel',
    
    # Communication
    'EmailTemplateModel',
    'EmailLogModel',
    
    # Audit
    'AuditLogModel',
    
    # Legacy
    'ProgramModel',
    'SurveyModel',
    'TodoModel',
    'CourseModel',
]
 