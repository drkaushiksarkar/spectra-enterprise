"""Transmission error definitions."""


class TransmissionError(Exception):
    """Base error for transmission operations."""
    code = "TRANSMISSION_ERROR"


class TransmissionNotFoundError(TransmissionError):
    code = "TRANSMISSION_NOT_FOUND"


class TransmissionValidationError(TransmissionError):
    code = "TRANSMISSION_VALIDATION"


class TransmissionTimeoutError(TransmissionError):
    code = "TRANSMISSION_TIMEOUT"


ERROR_CODES = {
    TransmissionError.code: "General transmission error",
    TransmissionNotFoundError.code: "Transmission resource not found",
    TransmissionValidationError.code: "Transmission validation failed",
    TransmissionTimeoutError.code: "Transmission operation timed out",
}
