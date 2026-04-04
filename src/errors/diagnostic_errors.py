"""Diagnostic error definitions."""


class DiagnosticError(Exception):
    """Base error for diagnostic operations."""
    code = "DIAGNOSTIC_ERROR"


class DiagnosticNotFoundError(DiagnosticError):
    code = "DIAGNOSTIC_NOT_FOUND"


class DiagnosticValidationError(DiagnosticError):
    code = "DIAGNOSTIC_VALIDATION"


class DiagnosticTimeoutError(DiagnosticError):
    code = "DIAGNOSTIC_TIMEOUT"


ERROR_CODES = {
    DiagnosticError.code: "General diagnostic error",
    DiagnosticNotFoundError.code: "Diagnostic resource not found",
    DiagnosticValidationError.code: "Diagnostic validation failed",
    DiagnosticTimeoutError.code: "Diagnostic operation timed out",
}
