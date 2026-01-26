from flask import Blueprint, request, jsonify
from services.track_service import TrackService
from infrastructure.repositories.track_repository import TrackRepository
from infrastructure.databases.mssql import session
from api.schemas.track import TrackRequestSchema, TrackResponseSchema

bp = Blueprint('track', __name__, url_prefix='/tracks')
track_service = TrackService(TrackRepository(session))
track_request_schema = TrackRequestSchema()
track_response_schema = TrackResponseSchema()


@bp.route('/', methods=['GET'])
def list_tracks():
    """
    Get all tracks
    ---
    get:
      summary: Get all tracks
      tags:
        - Tracks
      responses:
        200:
          description: List of all tracks
    """
    try:
        tracks = track_service.list_all_tracks()
        return jsonify([track_response_schema.dump(t) for t in tracks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/conference/<int:conference_id>', methods=['GET'])
def list_conference_tracks(conference_id):
    """
    Get all active tracks for a conference
    ---
    get:
      summary: Get tracks for a conference
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
        - name: include_inactive
          in: query
          schema:
            type: boolean
          description: Include inactive tracks
      tags:
        - Tracks
      responses:
        200:
          description: List of tracks for conference
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        if include_inactive:
            tracks = track_service.list_all_conference_tracks(conference_id, True)
        else:
            tracks = track_service.list_conference_tracks(conference_id)
        
        return jsonify([track_response_schema.dump(t) for t in tracks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>', methods=['GET'])
def get_track(track_id):
    """
    Get track by ID
    ---
    get:
      summary: Get track details
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      responses:
        200:
          description: Track details
        404:
          description: Track not found
    """
    try:
        track = track_service.get_track(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        return jsonify(track_response_schema.dump(track)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def create_track():
    """
    Create a new track
    ---
    post:
      summary: Create a new track
      tags:
        - Tracks
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conference_id:
                  type: integer
                name:
                  type: string
                short_name:
                  type: string
                description:
                  type: string
                keywords:
                  type: string
      responses:
        201:
          description: Track created
        400:
          description: Bad request
    """
    try:
        data = request.get_json()
        
        # Validate request
        errors = track_request_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        track = track_service.create_track(data)
        return jsonify(track_response_schema.dump(track)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>', methods=['PUT'])
def update_track(track_id):
    """
    Update track
    ---
    put:
      summary: Update track details
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Track updated
        404:
          description: Track not found
    """
    try:
        data = request.get_json()
        track = track_service.update_track(track_id, data)
        
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        return jsonify(track_response_schema.dump(track)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    """
    Delete track (soft delete)
    ---
    delete:
      summary: Delete a track
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      responses:
        204:
          description: Track deleted
        404:
          description: Track not found
    """
    try:
        success = track_service.delete_track(track_id)
        if not success:
            return jsonify({'error': 'Track not found'}), 404
        
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>/activate', methods=['POST'])
def activate_track(track_id):
    """
    Activate a track
    ---
    post:
      summary: Activate a track
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      responses:
        200:
          description: Track activated
        404:
          description: Track not found
    """
    try:
        track = track_service.activate_track(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        return jsonify(track_response_schema.dump(track)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>/deactivate', methods=['POST'])
def deactivate_track(track_id):
    """
    Deactivate a track
    ---
    post:
      summary: Deactivate a track
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      responses:
        200:
          description: Track deactivated
        404:
          description: Track not found
    """
    try:
        track = track_service.deactivate_track(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        return jsonify(track_response_schema.dump(track)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/conference/<int:conference_id>/reorder', methods=['POST'])
def reorder_conference_tracks(conference_id):
    """
    Reorder tracks in a conference
    ---
    post:
      summary: Reorder tracks
      parameters:
        - name: conference_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                track_order:
                  type: array
                  items:
                    type: object
                    properties:
                      track_id:
                        type: integer
                      display_order:
                        type: integer
      responses:
        200:
          description: Tracks reordered
        400:
          description: Bad request
    """
    try:
        data = request.get_json()
        track_order = data.get('track_order', [])
        
        if not track_order:
            return jsonify({'error': 'track_order is required'}), 400
        
        success = track_service.reorder_tracks(conference_id, track_order)
        if not success:
            return jsonify({'error': 'Failed to reorder tracks'}), 400
        
        return jsonify({'message': 'Tracks reordered successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>/chair/<int:user_id>', methods=['POST'])
def set_track_chair(track_id, user_id):
    """
    Set track chair
    ---
    post:
      summary: Assign track chair
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      responses:
        200:
          description: Track chair assigned
        404:
          description: Track not found
    """
    try:
        track = track_service.set_track_chair(track_id, user_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        return jsonify(track_response_schema.dump(track)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:track_id>/submission-status', methods=['GET'])
def get_track_submission_status(track_id):
    """
    Get track submission status
    ---
    get:
      summary: Check if submissions are open for track
      parameters:
        - name: track_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tracks
      responses:
        200:
          description: Submission status
        404:
          description: Track not found
    """
    try:
        track = track_service.get_track(track_id)
        if not track:
            return jsonify({'error': 'Track not found'}), 404
        
        is_open = track_service.is_track_submission_open(track_id)
        return jsonify({
            'track_id': track_id,
            'name': track.name,
            'is_open': is_open,
            'is_active': track.is_active,
            'submission_deadline': track.submission_deadline.isoformat() if track.submission_deadline else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
