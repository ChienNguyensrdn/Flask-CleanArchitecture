"""Domain-level exceptions for the application."""


class DomainException(Exception):
    """Base class for all domain exceptions in the application."""
    
    def __init__(self, message="A domain error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundException(DomainException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message="Resource not found", resource_type=None, resource_id=None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_type and resource_id:
            message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message)


class ValidationException(DomainException):
    """Exception raised for validation errors."""
    
    def __init__(self, message="Validation error", errors=None):
        self.errors = errors or []
        super().__init__(message)


class UnauthorizedException(DomainException):
    """Exception raised for unauthorized access."""
    
    def __init__(self, message="Unauthorized access"):
        super().__init__(message)


class ForbiddenException(DomainException):
    """Exception raised when access is forbidden."""
    
    def __init__(self, message="Access forbidden"):
        super().__init__(message)


class ConflictException(DomainException):
    """Exception raised for conflicts in the application."""
    
    def __init__(self, message="Conflict occurred", conflicting_field=None):
        self.conflicting_field = conflicting_field
        super().__init__(message)


class BusinessRuleViolationException(DomainException):
    """Exception raised when a business rule is violated."""
    
    def __init__(self, message="Business rule violation", rule_code=None):
        self.rule_code = rule_code
        super().__init__(message)


# Backward compatibility aliases
CustomException = DomainException