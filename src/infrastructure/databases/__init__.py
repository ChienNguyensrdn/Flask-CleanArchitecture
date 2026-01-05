from infrastructure.databases.mssql import init_mssql
from infrastructure.models import course_register_model, todo_model, user_model, course_model, consultant_model, appointment_model, program_model, feedback_model,survey_model
from infrastructure.models.auth import auth_user_model, auth_role_model,auth_funtion_model

def init_db(app):
    init_mssql(app)
    
# Migration Entities -> tables
from infrastructure.databases.mssql import Base