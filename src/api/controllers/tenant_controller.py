from flask import Blueprint, request, jsonify
from services.tenant_service import TenantService
from infrastructure.repositories.tenant_repository import TenantRepository
from datetime import datetime
from infrastructure.databases.mssql import session

bp = Blueprint('tenant', __name__, url_prefix='/tenants')

tenant_service = TenantService(TenantRepository(session))

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
    tenants = tenant_service.list_tenants()
    return jsonify([{
        'Tenant_ID': t.Tenant_ID,
        'Name': t.Name,
        'Email': t.Email,
        'Active': t.Active,
        'Created_at': t.Created_at,
        'Updated_at': t.Updated_at
    } for t in tenants]), 200

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
    tenant = tenant_service.get_tenant(tenant_id)
    if not tenant:
        return jsonify({'message': 'Tenant not found'}), 404
    return jsonify({
        'Tenant_ID': tenant.Tenant_ID,
        'Name': tenant.Name,
        'Email': tenant.Email,
        'Active': tenant.Active,
        'Created_at': tenant.Created_at,
        'Updated_at': tenant.Updated_at
    }), 200

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
    data = request.get_json()
    
    if not data or 'Name' not in data:
        return jsonify({'message': 'Name is required'}), 400
    
    tenant = tenant_service.create_tenant(
        name=data.get('Name'),
        email=data.get('Email'),
        active=data.get('Active', True),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return jsonify({
        'Tenant_ID': tenant.Tenant_ID,
        'Name': tenant.Name,
        'Email': tenant.Email,
        'Active': tenant.Active,
        'Created_at': tenant.Created_at,
        'Updated_at': tenant.Updated_at
    }), 201

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
    data = request.get_json()
    tenant = tenant_service.get_tenant(tenant_id)
    
    if not tenant:
        return jsonify({'message': 'Tenant not found'}), 404
    
    updated_tenant = tenant_service.update_tenant(
        tenant_id=tenant_id,
        name=data.get('Name', tenant.Name),
        email=data.get('Email', tenant.Email),
        active=data.get('Active', tenant.Active),
        created_at=tenant.Created_at,
        updated_at=datetime.utcnow()
    )
    
    return jsonify({
        'Tenant_ID': updated_tenant.Tenant_ID,
        'Name': updated_tenant.Name,
        'Email': updated_tenant.Email,
        'Active': updated_tenant.Active,
        'Created_at': updated_tenant.Created_at,
        'Updated_at': updated_tenant.Updated_at
    }), 200

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
    tenant = tenant_service.get_tenant(tenant_id)
    
    if not tenant:
        return jsonify({'message': 'Tenant not found'}), 404
    
    tenant_service.delete_tenant(tenant_id)
    return '', 204
