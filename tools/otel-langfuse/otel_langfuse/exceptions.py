"""
Exceções de domínio para o cliente de observabilidade e tracing.
"""


class DomainException(Exception):
    """Exceção base para o domínio de observabilidade."""


class ValidationException(DomainException):
    """Lançada quando a validação de parâmetros ou schemas falha."""


class IntegrationException(DomainException):
    """Lançada em falhas de integração com serviços externos de telemetria."""


class TracingException(DomainException):
    """Lançada quando ocorre um erro interno durante a criação ou envio de spans."""
