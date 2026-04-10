"""
Domain exception hierarchy and FastAPI exception handlers.

Routers/services raise FitLogError subclasses. The handlers here translate
them to a consistent JSON error envelope at the HTTP boundary.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Domain Exception Hierarchy
# ─────────────────────────────────────────────


class FitLogError(Exception):
    """Base class for all FitLog domain errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        self.details = details or {}


class AuthError(FitLogError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "auth_error"


class ForbiddenError(FitLogError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"


class NotFoundError(FitLogError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class DomainValidationError(FitLogError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "validation_error"


class ConflictError(FitLogError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class ExternalServiceError(FitLogError):
    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "external_service_error"


class ConfigurationError(FitLogError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "configuration_error"


class RateLimitError(FitLogError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"

    def __init__(self, message: str = "Too many requests", *, retry_after: int = 60) -> None:
        super().__init__(message)
        self.retry_after = retry_after


# ─────────────────────────────────────────────
#  Response Builder
# ─────────────────────────────────────────────


def _error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    payload: Dict[str, Any] = {
        # Legacy key kept for backward-compat with Streamlit client
        "detail": message,
        "error": {
            "code": error_code,
            "message": message,
        },
    }
    if details:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


# ─────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────


async def fitlog_error_handler(request: Request, exc: FitLogError) -> JSONResponse:
    logger.warning(
        "FitLogError %s %s: [%s] %s",
        request.method,
        request.url.path,
        exc.error_code,
        exc.message,
    )
    payload: Dict[str, Any] = {
        "detail": exc.message,
        "error": {"code": exc.error_code, "message": exc.message},
    }
    if exc.details:
        payload["error"]["details"] = exc.details
    headers: Optional[Dict[str, str]] = None
    if isinstance(exc, RateLimitError):
        headers = {"Retry-After": str(exc.retry_after)}
    return JSONResponse(status_code=exc.status_code, content=payload, headers=headers)


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.info(
        "Validation error %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="request_validation_error",
        message="Request body failed schema validation",
        details={"errors": exc.errors()},
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled exception %s %s", request.method, request.url.path)
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="internal_error",
        message="An unexpected error occurred",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Wire all FitLog exception handlers into the FastAPI app."""
    app.add_exception_handler(FitLogError, fitlog_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
