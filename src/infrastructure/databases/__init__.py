from infrastructure.databases.mssql import init_mssql
from infrastructure.databases.base import Base


def init_db(app):
    # Import models here to avoid circular imports
    # This ensures all models are registered with Base before creating tables
    from infrastructure.models import user_model
    from infrastructure.models import tenant_model
    from infrastructure.models import conference_model
    from infrastructure.models import track_model
    from infrastructure.models import paper_model
    from infrastructure.models import paper_author_model
    from infrastructure.models import pc_member_model
    from infrastructure.models import coi_model
    from infrastructure.models import paper_assignment_model
    from infrastructure.models import review_model
    from infrastructure.models import decision_model
    from infrastructure.models import camera_ready_model
    from infrastructure.models import email_template_model
    from infrastructure.models import audit_log_model
    
    init_mssql(app)