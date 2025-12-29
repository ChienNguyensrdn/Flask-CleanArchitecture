class Tenant:
    def __init__(self, id: int, name: str, email: str, created_at, updated_at, active: bool):
        self.id = id
        self.name = name
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at
        self.active = active
