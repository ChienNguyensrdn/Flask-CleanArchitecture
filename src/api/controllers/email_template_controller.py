"""Email Template controller for managing email templates and logs."""
from flask import Blueprint, request, jsonify
from services.email_template_service import EmailTemplateService, EmailLogService
from infrastructure.repositories.email_template_repository import EmailTemplateRepository, EmailLogRepository
from infrastructure.databases.mssql import get_session
from api.schemas.email_template import (
    EmailTemplateRequestSchema, EmailTemplateResponseSchema,
    EmailLogRequestSchema, EmailLogResponseSchema
)
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('email_template', __name__, url_prefix='/email-templates')

template_request_schema = EmailTemplateRequestSchema()
template_response_schema = EmailTemplateResponseSchema()
log_request_schema = EmailLogRequestSchema()
log_response_schema = EmailLogResponseSchema()


def get_template_services():
    """Factory to create template services with fresh session."""
    session = get_session()
    template_repo = EmailTemplateRepository(session)
    log_repo = EmailLogRepository(session)
    
    return {
        'template_service': EmailTemplateService(template_repo, log_repo),
        'log_service': EmailLogService(log_repo),
        'session': session
    }


# ========== EMAIL TEMPLATE ENDPOINTS ==========

@bp.route('/', methods=['GET'])
def list_templates():
    """
    Get all email templates
    ---
    get:
      summary: Get all email templates
      tags:
        - Email Templates
      responses:
        200:
          description: List of email templates
    """
    services = get_template_services()
    try:
        templates = services['template_service'].list_all_templates()
        return jsonify([template_response_schema.dump(t) for t in templates]), 200
    except Exception as e:
        logger.error(f"Error listing templates: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve templates'}), 500
    finally:
        services['session'].close()


@bp.route('/conference/<int:conference_id>', methods=['GET'])
def list_conference_templates(conference_id):
    """
    Get email templates for a conference
    ---
    get:
      summary: Get templates for a conference
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Templates
      responses:
        200:
          description: List of conference templates
    """
    services = get_template_services()
    try:
        templates = services['template_service'].list_conference_templates(conference_id)
        return jsonify([template_response_schema.dump(t) for t in templates]), 200
    except Exception as e:
        logger.error(f"Error listing conference templates: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve templates'}), 500
    finally:
        services['session'].close()


@bp.route('/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """
    Get email template by ID
    ---
    get:
      summary: Get template details
      parameters:
        - name: template_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Templates
      responses:
        200:
          description: Template details
        404:
          description: Template not found
    """
    services = get_template_services()
    try:
        template = services['template_service'].get_template(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify(template_response_schema.dump(template)), 200
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve template'}), 500
    finally:
        services['session'].close()


@bp.route('/type/<string:template_type>', methods=['GET'])
def get_template_by_type(template_type):
    """
    Get email template by type
    ---
    get:
      summary: Get template by type
      parameters:
        - name: template_type
          in: path
          required: true
          schema:
            type: string
        - name: conference_id
          in: query
          schema:
            type: integer
          description: Optional conference ID
      tags:
        - Email Templates
      responses:
        200:
          description: Template details
        404:
          description: Template not found
    """
    services = get_template_services()
    try:
        conference_id = request.args.get('conference_id', type=int)
        template = services['template_service'].get_template_by_type(template_type, conference_id)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify(template_response_schema.dump(template)), 200
    except Exception as e:
        logger.error(f"Error getting template by type {template_type}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve template'}), 500
    finally:
        services['session'].close()


@bp.route('/', methods=['POST'])
def create_template():
    """
    Create a new email template
    ---
    post:
      summary: Create a new email template
      tags:
        - Email Templates
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conference_id:
                  type: integer
                template_type:
                  type: string
                name:
                  type: string
                subject:
                  type: string
                body_html:
                  type: string
                body_text:
                  type: string
      responses:
        201:
          description: Template created
        400:
          description: Bad request
    """
    services = get_template_services()
    try:
        data = request.get_json()
        
        # Validate request
        errors = template_request_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        template = services['template_service'].create_template(data)
        return jsonify(template_response_schema.dump(template)), 201
    except ValueError as e:
        logger.warning(f"Validation error creating template: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        services['session'].rollback()
        logger.error(f"Error creating template: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create template'}), 500
    finally:
        services['session'].close()


@bp.route('/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """
    Update email template
    ---
    put:
      summary: Update template details
      parameters:
        - name: template_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Templates
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Template updated
        404:
          description: Template not found
    """
    services = get_template_services()
    try:
        data = request.get_json()
        template = services['template_service'].update_template(template_id, data)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify(template_response_schema.dump(template)), 200
    except Exception as e:
        services['session'].rollback()
        logger.error(f"Error updating template {template_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update template'}), 500
    finally:
        services['session'].close()


@bp.route('/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """
    Delete email template
    ---
    delete:
      summary: Delete a template
      parameters:
        - name: template_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Templates
      responses:
        204:
          description: Template deleted
        404:
          description: Template not found
    """
    services = get_template_services()
    try:
        success = services['template_service'].delete_template(template_id)
        if not success:
            return jsonify({'error': 'Template not found'}), 404
        
        return '', 204
    except Exception as e:
        services['session'].rollback()
        logger.error(f"Error deleting template {template_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete template'}), 500
    finally:
        services['session'].close()


@bp.route('/<int:template_id>/placeholders', methods=['GET'])
def get_template_placeholders(template_id):
    """
    Get available placeholders for a template
    ---
    get:
      summary: Get available placeholders
      parameters:
        - name: template_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Templates
      responses:
        200:
          description: List of placeholders
    """
    services = get_template_services()
    try:
        template = services['template_service'].get_template(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        placeholders = services['template_service'].get_available_placeholders(template.template_type)
        return jsonify({
            'template_id': template_id,
            'template_type': template.template_type,
            'placeholders': placeholders
        }), 200
    except Exception as e:
        logger.error(f"Error getting placeholders for template {template_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve placeholders'}), 500
    finally:
        services['session'].close()


@bp.route('/<int:template_id>/render', methods=['POST'])
def render_template(template_id):
    """
    Render template with placeholders
    ---
    post:
      summary: Render template with values
      parameters:
        - name: template_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Templates
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                placeholders:
                  type: object
      responses:
        200:
          description: Rendered template
        404:
          description: Template not found
    """
    services = get_template_services()
    try:
        data = request.get_json()
        placeholders = data.get('placeholders', {})
        
        subject, body = services['template_service'].render_template(template_id, placeholders)
        return jsonify({
            'subject': subject,
            'body_html': body
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error rendering template {template_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to render template'}), 500
    finally:
        services['session'].close()


# ========== EMAIL LOG ENDPOINTS ==========

@bp.route('/logs', methods=['GET'])
def list_logs():
    """
    Get all email logs
    ---
    get:
      summary: Get all email logs
      tags:
        - Email Logs
      responses:
        200:
          description: List of email logs
    """
    services = get_template_services()
    try:
        logs = services['log_service'].list_all_logs()
        return jsonify([log_response_schema.dump(l) for l in logs]), 200
    except Exception as e:
        logger.error(f"Error listing logs: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve logs'}), 500
    finally:
        services['session'].close()


@bp.route('/logs/conference/<int:conference_id>', methods=['GET'])
def list_conference_logs(conference_id):
    """
    Get email logs for a conference
    ---
    get:
      summary: Get logs for a conference
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Logs
      responses:
        200:
          description: List of conference email logs
    """
    services = get_template_services()
    try:
        logs = services['log_service'].list_conference_logs(conference_id)
        return jsonify([log_response_schema.dump(l) for l in logs]), 200
    except Exception as e:
        logger.error(f"Error listing conference logs: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve logs'}), 500
    finally:
        services['session'].close()


@bp.route('/logs/<int:log_id>', methods=['GET'])
def get_log(log_id):
    """
    Get email log by ID
    ---
    get:
      summary: Get log details
      parameters:
        - name: log_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Logs
      responses:
        200:
          description: Log details
        404:
          description: Log not found
    """
    services = get_template_services()
    try:
        log = services['log_service'].get_log(log_id)
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        return jsonify(log_response_schema.dump(log)), 200
    except Exception as e:
        logger.error(f"Error getting log {log_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve log'}), 500
    finally:
        services['session'].close()


@bp.route('/logs', methods=['POST'])
def create_log():
    """
    Log an email
    ---
    post:
      summary: Create email log entry
      tags:
        - Email Logs
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conference_id:
                  type: integer
                template_id:
                  type: integer
                recipient_email:
                  type: string
                subject:
                  type: string
                body:
                  type: string
      responses:
        201:
          description: Log created
        400:
          description: Bad request
    """
    services = get_template_services()
    try:
        data = request.get_json()
        
        # Validate request
        errors = log_request_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        log = services['log_service'].log_email(data)
        return jsonify(log_response_schema.dump(log)), 201
    except ValueError as e:
        logger.warning(f"Validation error creating log: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        services['session'].rollback()
        logger.error(f"Error creating log: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create log'}), 500
    finally:
        services['session'].close()


@bp.route('/logs/<int:log_id>/mark-sent', methods=['POST'])
def mark_sent(log_id):
    """
    Mark email as sent
    ---
    post:
      summary: Mark email as sent
      parameters:
        - name: log_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Logs
      responses:
        200:
          description: Email marked as sent
        404:
          description: Log not found
    """
    services = get_template_services()
    try:
        log = services['log_service'].mark_as_sent(log_id)
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        return jsonify(log_response_schema.dump(log)), 200
    except Exception as e:
        services['session'].rollback()
        logger.error(f"Error marking log {log_id} as sent: {e}", exc_info=True)
        return jsonify({'error': 'Failed to mark as sent'}), 500
    finally:
        services['session'].close()


@bp.route('/logs/<int:log_id>/mark-failed', methods=['POST'])
def mark_failed(log_id):
    """
    Mark email as failed
    ---
    post:
      summary: Mark email as failed
      parameters:
        - name: log_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Email Logs
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                error_message:
                  type: string
      responses:
        200:
          description: Email marked as failed
        404:
          description: Log not found
    """
    services = get_template_services()
    try:
        data = request.get_json()
        error_message = data.get('error_message', 'Unknown error')
        
        log = services['log_service'].mark_as_failed(log_id, error_message)
        if not log:
            return jsonify({'error': 'Log not found'}), 404
        
        return jsonify(log_response_schema.dump(log)), 200
    except Exception as e:
        services['session'].rollback()
        logger.error(f"Error marking log {log_id} as failed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to mark as failed'}), 500
    finally:
        services['session'].close()


@bp.route('/logs/status/<string:status>', methods=['GET'])
def list_logs_by_status(status):
    """
    Get logs by status
    ---
    get:
      summary: Get logs by status
      parameters:
        - name: status
          in: path
          required: true
          schema:
            type: string
            enum: ['pending', 'sent', 'failed', 'bounced']
      tags:
        - Email Logs
      responses:
        200:
          description: List of logs with status
    """
    services = get_template_services()
    try:
        logs = services['log_service'].list_logs_by_status(status)
        return jsonify([log_response_schema.dump(l) for l in logs]), 200
    except Exception as e:
        logger.error(f"Error listing logs by status {status}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve logs'}), 500
    finally:
        services['session'].close()


@bp.route('/logs/pending', methods=['GET'])
def get_pending_logs():
    """
    Get all pending emails
    ---
    get:
      summary: Get pending emails
      tags:
        - Email Logs
      responses:
        200:
          description: List of pending emails
    """
    services = get_template_services()
    try:
        logs = services['log_service'].get_pending_emails()
        return jsonify([log_response_schema.dump(l) for l in logs]), 200
    except Exception as e:
        logger.error(f"Error getting pending logs: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve pending emails'}), 500
    finally:
        services['session'].close()
