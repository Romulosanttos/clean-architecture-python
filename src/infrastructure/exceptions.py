"""
Exceções customizadas para a aplicação.
"""


class AppException(Exception):
    """Exceção base da aplicação."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exceção para recursos não encontrados."""
    def __init__(self, resource: str, id: int):
        message = f"{resource} with id {id} not found"
        super().__init__(message, status_code=404)


class ValidationException(AppException):
    """Exceção para erros de validação."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class DatabaseException(AppException):
    """Exceção para erros de banco de dados."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class DuplicateException(AppException):
    """Exceção para recursos duplicados."""
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} with {field}='{value}' already exists"
        super().__init__(message, status_code=409)
