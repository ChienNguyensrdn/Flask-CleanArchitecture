"""Tenant controller for managing tenant endpoints."""
from flask import Blueprint, request, jsonify
from services.tenant_service import TenantService
from infrastructure.repositories.tenant_repository import TenantRepository
from datetime import datetime, timezone
from infrastructure.databases.mssql import get_session
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('tenant', __name__, url_prefix='/tenants')


def get_tenant_service():
    """Factory to create tenant service with fresh session."""
    session = get_session()
    return TenantService(TenantRepository(session)), session


@bp.route('/', methods=['GET'])
def list_tenants():
    """
    Get all tenants
    ---
    get:
      summary: Get all tenants
      tags:
        - Tenants
      responses:
        200:
          description: List of tenants
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    Tenant_ID:
                      type: integer
                    Name:
                      type: string
                    Email:
                      type: string
                    Active:
                      type: boolean
                    Created_at:
                      type: string
                    Updated_at:
                      type: string
    """
    service, session = get_tenant_service()
    try:
        tenants = service.list_tenants()
        return jsonify([{
            'Tenant_ID': t.Tenant_ID,
            'Name': t.Name,
            'Email': t.Email,
            'Active': t.Active,
            'Created_at': t.Created_at,
            'Updated_at': t.Updated_at
        } for t in tenants]), 200
    except Exception as e:
        logger.error(f"Error listing tenants: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve tenants'}), 500
    finally:
        session.close()


@bp.route('/<int:tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    """
    Get tenant by id
    ---
    get:
      summary: Get tenant by id
      parameters:
        - name: tenant_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of tenant to retrieve
      tags:
        - Tenants
      responses:
        200:
          description: Tenant object
        404:
          description: Tenant not found
    """
    service, session = get_tenant_service()
    try:
        tenant = service.get_tenant(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        return jsonify({
            'Tenant_ID': tenant.Tenant_ID,
            'Name': tenant.Name,
            'Email': tenant.Email,
            'Active': tenant.Active,
            'Created_at': tenant.Created_at,
            'Updated_at': tenant.Updated_at
        }), 200
    except Exception as e:
        logger.error(f"Error getting tenant {tenant_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve tenant'}), 500
    finally:
        session.close()


@bp.route('/', methods=['POST'])
def create_tenant():
    """
    Create a new tenant
    ---
    post:
      summary: Create a new tenant
      tags:
        - Tenants
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                Name:
                  type: string
                Email:
                  type: string
                Active:
                  type: boolean
      responses:
        201:
          description: Tenant created successfully
        400:
          description: Invalid request body
    """
    service, session = get_tenant_service()
    try:
        data = request.get_json()
        
        if not data or 'Name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        tenant = service.create_tenant(
            name=data.get('Name'),
            email=data.get('Email'),
            active=data.get('Active', True),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return jsonify({
            'Tenant_ID': tenant.Tenant_ID,
            'Name': tenant.Name,
            'Email': tenant.Email,
            'Active': tenant.Active,
            'Created_at': tenant.Created_at,
            'Updated_at': tenant.Updated_at
        }), 201
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating tenant: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create tenant'}), 500
    finally:
        session.close()


@bp.route('/<int:tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    """
    Update a tenant
    ---
    put:
      summary: Update a tenant
      parameters:
        - name: tenant_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tenants
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                Name:
                  type: string
                Email:
                  type: string
                Active:
                  type: boolean
      responses:
        200:
          description: Tenant updated successfully
        404:
          description: Tenant not found
    """
    service, session = get_tenant_service()
    try:
        data = request.get_json()
        tenant = service.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        updated_tenant = service.update_tenant(
            tenant_id=tenant_id,
            name=data.get('Name', tenant.Name),
            email=data.get('Email', tenant.Email),
            active=data.get('Active', tenant.Active),
            created_at=tenant.Created_at,
            updated_at=datetime.now(timezone.utc)
        )
        
        return jsonify({
            'Tenant_ID': updated_tenant.Tenant_ID,
            'Name': updated_tenant.Name,
            'Email': updated_tenant.Email,
            'Active': updated_tenant.Active,
            'Created_at': updated_tenant.Created_at,
            'Updated_at': updated_tenant.Updated_at
        }), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating tenant {tenant_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update tenant'}), 500
    finally:
        session.close()


@bp.route('/<int:tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    """
    Delete a tenant
    ---
    delete:
      summary: Delete a tenant
      parameters:
        - name: tenant_id
          in: path
          required: true
          schema:
            type: integer
      tags:
        - Tenants
      responses:
        204:
          description: Tenant deleted successfully
        404:
          description: Tenant not found
    """
    service, session = get_tenant_service()
    try:
        tenant = service.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        service.delete_tenant(tenant_id)
        return '', 204
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting tenant {tenant_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete tenant'}), 500
    finally:
        session.close()
