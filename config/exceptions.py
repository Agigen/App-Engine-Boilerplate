#!/usr/bin/env python


class APIError(Exception):
    """Base class for all API exceptions."""
    loglevel = 'warning'
    json_message = 'ERROR_INTERNAL_FAILURE'
    http_status = 500
    human_message = "Internal server error"


class InvalidParameterError(APIError):
    loglevel = "info"
    json_message = "ERROR_INVALID_PARAMETER"
    http_status = 400
    human_message = "Invalid parameter"


class NoSuchEntityError(APIError):
    loglevel = "info"
    json_message = "ERROR_NO_SUCH_ENTITY"
    http_status = 404
    human_message = "No such entity"


class BadImageFormatError(APIError):
    loglevel = "info"
    json_message = "ERROR_BAD_IMAGE_FORMAT"
    http_status = 415
    human_message = "Bad image format"


class NoUserError(APIError):
    loglevel = "info"
    json_message = "ERROR_NO_USER"
    http_status = 403
    human_message = "No user"


class ConflictError(APIError):
    loglevel = "info"
    json_message = "ERROR_CONFLICT"
    http_status = 409
    human_message = "Conflict"


class PermissionDeniedError(APIError):
    loglevel = 'info'
    json_message = 'ERROR_PERMISSION_DENIED'
    http_status = 403
    human_message = "Permission denied"
