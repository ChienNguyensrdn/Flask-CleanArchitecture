from flask import Blueprint, request, jsonify
from services.conference_service import ConferenceService
from infrastructure.repositories.conference_repository import ConferenceRepository
from infrastructure.databases.mssql import session
from api.schemas.conference import ConferenceRequestSchema, ConferenceResponseSchema
from marshmallow import ValidationError
from datetime import datetime

bp = Blueprint('conference', __name__, url_prefix='/conferences')
conference_service = ConferenceService(ConferenceRepository(session))
conference_request_schema = ConferenceRequestSchema()
conference_response_schema = ConferenceResponseSchema()


@bp.route('/', methods=['GET'])
def list_conferences():
    """
    Get all conferences
    ---
    get:
      summary: Get all conferences
      tags:
        - Conferences
      responses:
        200:
          description: List of conferences
    """
    try:
        conferences = conference_service.list_all_conferences()
        return jsonify([conference_response_schema.dump(c) for c in conferences]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tenant/<int:tenant_id>', methods=['GET'])
def list_tenant_conferences(tenant_id):
    """
    Get all conferences for a tenant
    ---
    get:
      summary: Get conferences for a tenant
      parameters:
        - name: tenant_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      responses:
        200:
          description: List of conferences for tenant
    """
    try:
        conferences = conference_service.list_tenant_conferences(tenant_id)
        return jsonify([conference_response_schema.dump(c) for c in conferences]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/public-cfp', methods=['GET'])
def list_public_cfp():
    """
    Get all conferences with public CFP
    ---
    get:
      summary: Get conferences with public CFP
      tags:
        - Conferences
      responses:
        200:
          description: List of conferences with public CFP
    """
    try:
        conferences = conference_service.get_public_cfp_conferences()
        return jsonify([conference_response_schema.dump(c) for c in conferences]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>', methods=['GET'])
def get_conference(conference_id):
    """
    Get conference by ID
    ---
    get:
      summary: Get conference details
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      responses:
        200:
          description: Conference details
        404:
          description: Conference not found
    """
    try:
        conference = conference_service.get_conference(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        return jsonify(conference_response_schema.dump(conference)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def create_conference():
    """
    Create a new conference
    ---
    post:
      summary: Create a new conference
      tags:
        - Conferences
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                tenant_id:
                  type: integer
                name:
                  type: string
                short_name:
                  type: string
                description:
                  type: string
                venue:
                  type: string
                cfp_is_public:
                  type: boolean
      responses:
        201:
          description: Conference created
        400:
          description: Bad request
    """
    try:
        data = request.get_json()
        
        # Validate request
        errors = conference_request_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        conference = conference_service.create_conference(data)
        return jsonify(conference_response_schema.dump(conference)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>', methods=['PUT'])
def update_conference(conference_id):
    """
    Update conference
    ---
    put:
      summary: Update conference details
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Conference updated
        404:
          description: Conference not found
    """
    try:
        data = request.get_json()
        conference = conference_service.update_conference(conference_id, data)
        
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        return jsonify(conference_response_schema.dump(conference)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>', methods=['DELETE'])
def delete_conference(conference_id):
    """
    Delete conference
    ---
    delete:
      summary: Delete a conference
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      responses:
        204:
          description: Conference deleted
        404:
          description: Conference not found
    """
    try:
        success = conference_service.delete_conference(conference_id)
        if not success:
            return jsonify({'error': 'Conference not found'}), 404
        
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>/cfp/publish', methods=['POST'])
def publish_cfp(conference_id):
    """
    Publish CFP for a conference
    ---
    post:
      summary: Publish Call for Papers
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                cfp_content:
                  type: string
      responses:
        200:
          description: CFP published
        404:
          description: Conference not found
    """
    try:
        data = request.get_json()
        cfp_content = data.get('cfp_content', '')
        
        conference = conference_service.publish_cfp(conference_id, cfp_content)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        return jsonify(conference_response_schema.dump(conference)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>/cfp/unpublish', methods=['POST'])
def unpublish_cfp(conference_id):
    """
    Unpublish CFP for a conference
    ---
    post:
      summary: Unpublish Call for Papers
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      responses:
        200:
          description: CFP unpublished
        404:
          description: Conference not found
    """
    try:
        conference = conference_service.unpublish_cfp(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        return jsonify(conference_response_schema.dump(conference)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>/status', methods=['PUT'])
def update_conference_status(conference_id):
    """
    Update conference status
    ---
    put:
      summary: Change conference status
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: ['draft', 'open', 'reviewing', 'decided', 'published']
      responses:
        200:
          description: Status updated
        400:
          description: Invalid status
    """
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        conference = conference_service.change_conference_status(conference_id, status)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        return jsonify(conference_response_schema.dump(conference)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:conference_id>/cfp-status', methods=['GET'])
def get_cfp_status(conference_id):
    """
    Get CFP status for a conference
    ---
    get:
      summary: Check if CFP is open
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Conferences
      responses:
        200:
          description: CFP status
        404:
          description: Conference not found
    """
    try:
        conference = conference_service.get_conference(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        
        is_open = conference_service.is_cfp_open(conference_id)
        return jsonify({
            'conference_id': conference_id,
            'cfp_is_public': conference.cfp_is_public,
            'is_cfp_open': is_open,
            'submission_deadline': conference.submission_deadline.isoformat() if conference.submission_deadline else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
