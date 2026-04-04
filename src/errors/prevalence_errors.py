"""Prevalence error definitions."""


class PrevalenceError(Exception):
    """Base error for prevalence operations."""
    code = "PREVALENCE_ERROR"


class PrevalenceNotFoundError(PrevalenceError):
    code = "PREVALENCE_NOT_FOUND"


class PrevalenceValidationError(PrevalenceError):
    code = "PREVALENCE_VALIDATION"


class PrevalenceTimeoutError(PrevalenceError):
    code = "PREVALENCE_TIMEOUT"


ERROR_CODES = {
    PrevalenceError.code: "General prevalence error",
    PrevalenceNotFoundError.code: "Prevalence resource not found",
    PrevalenceValidationError.code: "Prevalence validation failed",
    PrevalenceTimeoutError.code: "Prevalence operation timed out",
}
