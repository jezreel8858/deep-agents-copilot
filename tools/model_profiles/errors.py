"""Excecoes base do gerador de perfis de modelos (codigos estaveis entre colchetes)."""
from __future__ import annotations
class ModelProfilesError(Exception):
    """Erro esperado: a CLI imprime `[CODIGO] mensagem` e retorna exit 1."""
    code = "ERROR"
    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code
class PathTraversalError(ModelProfilesError):
    code = "PATH_TRAVERSAL"
class RefusalError(ModelProfilesError):
    """Recusa de operacao (ex.: DIRTY, IN_PROGRESS, ORPHAN_JOURNAL)."""
