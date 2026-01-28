"""Paper controller for managing paper submission endpoints."""
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.utils import secure_filename
from services.paper_service import PaperService, PaperAuthorService
from infrastructure.repositories.paper_repository import PaperRepository, PaperAuthorRepository
from infrastructure.databases.mssql import get_session
from api.schemas.paper import (
    PaperSubmissionRequestSchema, PaperUpdateRequestSchema,
    PaperResponseSchema, PaperAuthorRequestSchema, PaperAuthorResponseSchema
)
from api.middleware import require_auth
import logging
import os

logger = logging.getLogger(__name__)

bp = Blueprint('paper', __name__, url_prefix='/papers')

paper_submission_schema = PaperSubmissionRequestSchema()
paper_update_schema = PaperUpdateRequestSchema()
paper_response_schema = PaperResponseSchema()
author_request_schema = PaperAuthorRequestSchema()
author_response_schema = PaperAuthorResponseSchema()

# File upload configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_paper_service():
    """Factory to create paper service with fresh session."""
    session = get_session()
    paper_repo = PaperRepository(session)
    author_repo = PaperAuthorRepository(session)
    return PaperService(paper_repo, author_repo), PaperAuthorService(author_repo), session


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE


# ========== PAPER SUBMISSION ENDPOINTS ==========

@bp.route('/', methods=['POST'])
def submit_paper():
    """
    Submit a new paper (draft)
    ---
    post:
      summary: Create new paper submission
      tags:
        - Papers
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conference_id:
                  type: integer
                track_id:
                  type: integer
                title:
                  type: string
                abstract:
                  type: string
                keywords:
                  type: string
                authors:
                  type: array
                  items:
                    type: object
      responses:
        201:
          description: Paper created
        400:
          description: Bad request
    """
    paper_service, _, session = get_paper_service()
    try:
        data = request.get_json()
        
        # Validate request
        errors = paper_submission_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Get current user ID from auth context or request data
        submitter_id = g.get('current_user_id') or data.get('submitter_id')
        if not submitter_id:
            return jsonify({'error': 'Authentication required or submitter_id must be provided'}), 401
        
        paper = paper_service.submit_paper(data, submitter_id)
        return jsonify(paper_response_schema.dump(paper)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Error submitting paper: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit paper'}), 500
    finally:
        session.close()


@bp.route('/', methods=['GET'])
def list_papers():
    """
    Get all papers
    ---
    get:
      summary: List all papers
      tags:
        - Papers
      parameters:
        - name: conference_id
          in: query
          schema:
            type: integer
        - name: submitter_id
          in: query
          schema:
            type: integer
      responses:
        200:
          description: List of papers
    """
    paper_service, _, session = get_paper_service()
    try:
        conference_id = request.args.get('conference_id', type=int)
        # Use authenticated user's ID if available, otherwise from query param
        submitter_id = g.get('current_user_id') or request.args.get('submitter_id', type=int)
        
        if conference_id and submitter_id:
            papers = paper_service.list_user_conference_papers(conference_id, submitter_id)
        elif conference_id:
            papers = paper_service.list_conference_papers(conference_id)
        elif submitter_id:
            papers = paper_service.list_user_papers(submitter_id)
        else:
            papers = []
        
        return jsonify([paper_response_schema.dump(p) for p in papers]), 200
    except Exception as e:
        logger.error(f"Error listing papers: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve papers'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    """
    Get paper details
    ---
    get:
      summary: Get paper by ID
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      responses:
        200:
          description: Paper details
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        paper = paper_service.get_paper(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify(paper_response_schema.dump(paper)), 200
    except Exception as e:
        logger.error(f"Error getting paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve paper'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>', methods=['PUT'])
def update_paper(paper_id):
    """
    Update paper (only draft)
    ---
    put:
      summary: Update paper details
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Paper updated
        400:
          description: Cannot update submitted paper
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        data = request.get_json()
        
        # Validate request
        errors = paper_update_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        paper = paper_service.update_paper(paper_id, data)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify(paper_response_schema.dump(paper)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update paper'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """
    Delete paper (only draft)
    ---
    delete:
      summary: Delete a paper
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      responses:
        204:
          description: Paper deleted
        400:
          description: Cannot delete submitted paper
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        success = paper_service.delete_paper(paper_id)
        if not success:
            return jsonify({'error': 'Paper not found'}), 404
        
        return '', 204
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete paper'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>/submit', methods=['POST'])
def finalize_submission(paper_id):
    """
    Finalize paper submission
    ---
    post:
      summary: Submit paper for review
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      responses:
        200:
          description: Paper submitted
        400:
          description: Cannot submit (missing data/file)
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        paper = paper_service.mark_paper_submitted(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify({
            'message': 'Paper submitted successfully',
            'paper': paper_response_schema.dump(paper)
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        session.rollback()
        logger.error(f"Error finalizing submission {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit paper'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>/withdraw', methods=['POST'])
def withdraw_paper(paper_id):
    """
    Withdraw paper
    ---
    post:
      summary: Withdraw a submitted paper
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      responses:
        200:
          description: Paper withdrawn
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        paper = paper_service.withdraw_paper(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify(paper_response_schema.dump(paper)), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error withdrawing paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to withdraw paper'}), 500
    finally:
        session.close()


# ========== FILE UPLOAD ENDPOINTS ==========

@bp.route('/<int:paper_id>/upload-pdf', methods=['POST'])
def upload_paper_pdf(paper_id):
    """
    Upload paper PDF
    ---
    post:
      summary: Upload paper PDF file
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        200:
          description: File uploaded
        400:
          description: Invalid file
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        paper = paper_service.get_paper(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files allowed'}), 400
        
        if not validate_file_size(file):
            return jsonify({'error': f'File too large (max {MAX_FILE_SIZE/1024/1024}MB)'}), 400
        
        # Save file
        filename = secure_filename(f"paper_{paper_id}.pdf")
        upload_path = paper_service.get_upload_path(paper_id, filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        
        # Update paper
        paper = paper_service.upload_pdf(paper_id, upload_path)
        
        return jsonify({
            'message': 'PDF uploaded successfully',
            'file_path': upload_path
        }), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error uploading PDF for paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to upload file'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>/upload-supplementary', methods=['POST'])
def upload_supplementary(paper_id):
    """
    Upload supplementary materials
    ---
    post:
      summary: Upload supplementary materials
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        200:
          description: File uploaded
        400:
          description: Invalid file
        404:
          description: Paper not found
    """
    paper_service, _, session = get_paper_service()
    try:
        paper = paper_service.get_paper(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not validate_file_size(file):
            return jsonify({'error': f'File too large (max {MAX_FILE_SIZE/1024/1024}MB)'}), 400
        
        # Save file
        filename = secure_filename(f"supplementary_{paper_id}_{file.filename}")
        upload_path = paper_service.get_upload_path(paper_id, filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        
        # Update paper
        paper = paper_service.upload_supplementary(paper_id, upload_path)
        
        return jsonify({
            'message': 'Supplementary file uploaded successfully',
            'file_path': upload_path
        }), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error uploading supplementary for paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to upload file'}), 500
    finally:
        session.close()


# ========== AUTHOR MANAGEMENT ENDPOINTS ==========

@bp.route('/<int:paper_id>/authors', methods=['GET'])
def get_paper_authors(paper_id):
    """
    Get all authors for a paper
    ---
    get:
      summary: List paper authors
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      responses:
        200:
          description: List of authors
    """
    _, author_service, session = get_paper_service()
    try:
        authors = author_service.get_paper_authors(paper_id)
        return jsonify([author_response_schema.dump(a) for a in authors]), 200
    except Exception as e:
        logger.error(f"Error getting authors for paper {paper_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve authors'}), 500
    finally:
        session.close()


@bp.route('/<int:paper_id>/authors', methods=['POST'])
def add_paper_author(paper_id):
    """
    Add author to paper
    ---
    post:
      summary: Add author to paper
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
                email:
                  type: string
                affiliation:
                  type: string
      responses:
        201:
          description: Author added
        400:
          description: Bad request
    """
    try:
        data = request.get_json()
        
        # Validate request
        errors = author_request_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        data['paper_id'] = paper_id
        author = author_service.add_author(data)
        
        return jsonify(author_response_schema.dump(author)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """
    Get author details
    ---
    get:
      summary: Get author by ID
      parameters:
        - name: author_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      responses:
        200:
          description: Author details
        404:
          description: Author not found
    """
    try:
        author = author_service.get_author(author_id)
        if not author:
            return jsonify({'error': 'Author not found'}), 404
        
        return jsonify(author_response_schema.dump(author)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """
    Update author information
    ---
    put:
      summary: Update author details
      parameters:
        - name: author_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Author updated
        404:
          description: Author not found
    """
    try:
        data = request.get_json()
        author = author_service.update_author(author_id, data)
        
        if not author:
            return jsonify({'error': 'Author not found'}), 404
        
        return jsonify(author_response_schema.dump(author)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/authors/<int:author_id>', methods=['DELETE'])
def remove_author(author_id):
    """
    Remove author from paper
    ---
    delete:
      summary: Remove an author
      parameters:
        - name: author_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      responses:
        204:
          description: Author removed
        404:
          description: Author not found
    """
    try:
        success = author_service.remove_author(author_id)
        if not success:
            return jsonify({'error': 'Author not found'}), 404
        
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:paper_id>/corresponding-author/<int:author_id>', methods=['POST'])
def set_corresponding_author(paper_id, author_id):
    """
    Set corresponding author
    ---
    post:
      summary: Set corresponding author for paper
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
        - name: author_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      responses:
        200:
          description: Corresponding author set
        400:
          description: Invalid author
    """
    try:
        success = author_service.set_corresponding_author(paper_id, author_id)
        if not success:
            return jsonify({'error': 'Author not found or does not belong to paper'}), 400
        
        return jsonify({'message': 'Corresponding author set'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:paper_id>/reorder-authors', methods=['POST'])
def reorder_authors(paper_id):
    """
    Reorder paper authors
    ---
    post:
      summary: Reorder authors
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Paper Authors
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                authors:
                  type: array
                  items:
                    type: object
                    properties:
                      author_id:
                        type: integer
                      order:
                        type: integer
      responses:
        200:
          description: Authors reordered
    """
    try:
        data = request.get_json()
        author_order = data.get('authors', [])
        
        success = author_service.reorder_authors(paper_id, author_order)
        if not success:
            return jsonify({'error': 'Failed to reorder authors'}), 400
        
        return jsonify({'message': 'Authors reordered successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== STATUS & REVISION ENDPOINTS ==========

@bp.route('/<int:paper_id>/status', methods=['PUT'])
def update_paper_status(paper_id):
    """
    Update paper status
    ---
    put:
      summary: Change paper status
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
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
        
        paper = paper_service.update_paper_status(paper_id, status)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify(paper_response_schema.dump(paper)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:paper_id>/request-revision', methods=['POST'])
def request_revision(paper_id):
    """
    Request revision for paper
    ---
    post:
      summary: Request paper revision
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                revision_notes:
                  type: string
      responses:
        200:
          description: Revision requested
    """
    try:
        data = request.get_json()
        revision_notes = data.get('revision_notes', '')
        
        paper = paper_service.request_revision(paper_id, revision_notes)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        # TODO: Send email to corresponding author
        
        return jsonify({
            'message': 'Revision requested',
            'paper': paper_response_schema.dump(paper)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:paper_id>/resubmit', methods=['POST'])
def resubmit_paper(paper_id):
    """
    Resubmit paper after revision
    ---
    post:
      summary: Resubmit revised paper
      parameters:
        - name: paper_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Papers
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      responses:
        200:
          description: Paper resubmitted
        400:
          description: Cannot resubmit
    """
    try:
        data = request.get_json()
        
        # Validate
        errors = paper_update_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        paper = paper_service.resubmit_after_revision(paper_id, data)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        return jsonify({
            'message': 'Paper resubmitted successfully',
            'paper': paper_response_schema.dump(paper)
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
