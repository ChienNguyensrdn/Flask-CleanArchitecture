from domain.models.tenant import Tenant
from infrastructure.repositories.tenant_repository import TenantRepository
from typing import List, Optional

class TenantService:
    def __init__(self, repository: TenantRepository):
        self.repository = repository

    def create_tenant(self, name: str, email: str, active: bool, created_at, updated_at) -> Tenant:
        tenant = Tenant(id=None, name=name, email=email, active=active, created_at=created_at, updated_at=updated_at)
        return self.repository.add(tenant)

    def get_tenant(self, tenant_id: int) -> Optional[Tenant]:
        return self.repository.get_by_id(tenant_id)

    def list_tenants(self) -> List[Tenant]:
        return self.repository.list()

    def update_tenant(self, tenant_id: int, name: str, email: str, active: bool, created_at, updated_at) -> Optional[Tenant]:
        tenant = Tenant(id=tenant_id, name=name, email=email, active=active, created_at=created_at, updated_at=updated_at)
        return self.repository.update(tenant_id, tenant)

    def delete_tenant(self, tenant_id: int) -> None:
        self.repository.delete(tenant_id)
