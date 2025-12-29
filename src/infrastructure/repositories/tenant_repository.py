from domain.models.tenant import Tenant
from infrastructure.models.tenant_model import TenantModel
from infrastructure.databases import Base
from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from config import Config
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from infrastructure.databases.mssql import session

load_dotenv()

class TenantRepository:
    def __init__(self, session: Session = session):
        self._tenants = []
        self._id_counter = 1
        self.session = session

    def add(self, tenant: Tenant) -> TenantModel:
        try:
            # Manual mapping from Tenant to TenantModel
            db_tenant = TenantModel(
                Name=tenant.name,
                Email=tenant.email,
                Active=tenant.active,
                Created_at=tenant.created_at,
                Updated_at=tenant.updated_at
            )
            self.session.add(db_tenant)
            self.session.commit()
            return db_tenant
        except Exception as e:
            self.session.rollback()
            raise e

    def get_by_id(self, tenant_id: int) -> Optional[TenantModel]:
        return self.session.query(TenantModel).filter(TenantModel.Tenant_ID == tenant_id).first()

    def list(self) -> List[TenantModel]:
        return self.session.query(TenantModel).all()

    def update(self, tenant_id: int, tenant: Tenant) -> Optional[TenantModel]:
        db_tenant = self.get_by_id(tenant_id)
        if db_tenant:
            db_tenant.Name = tenant.name
            db_tenant.Email = tenant.email
            db_tenant.Active = tenant.active
            db_tenant.Updated_at = tenant.updated_at
            self.session.commit()
        return db_tenant

    def delete(self, tenant_id: int) -> None:
        db_tenant = self.get_by_id(tenant_id)
        if db_tenant:
            self.session.delete(db_tenant)
            self.session.commit()
