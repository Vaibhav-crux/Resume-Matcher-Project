# resume_analyzer/common/errors.py
from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError, NotFound, APIException
from responses import Response

# Standard error responses as dictionaries
ERROR_RESPONSES = {
    "INTERNAL_SERVER_ERROR": {
        "error": "Internal server error",
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR
    },
    "NOT_FOUND": {
        "error": "Resource not found",
        "status": status.HTTP_404_NOT_FOUND
    },
    "BAD_REQUEST": {
        "error": "Bad request",
        "status": status.HTTP_400_BAD_REQUEST
    },
    "UNAUTHORIZED": {
        "error": "Authentication credentials were not provided or are invalid",
        "status": status.HTTP_401_UNAUTHORIZED
    },
    "FORBIDDEN": {
        "error": "You do not have permission to perform this action",
        "status": status.HTTP_403_FORBIDDEN
    },
    "METHOD_NOT_ALLOWED": {
        "error": "Method not allowed",
        "status": status.HTTP_405_METHOD_NOT_ALLOWED
    },
    "CONFLICT": {
        "error": "Resource already exists or conflict occurred",
        "status": status.HTTP_409_CONFLICT
    },
    "VALIDATION_ERROR": {
        "error": "Invalid input data",
        "status": status.HTTP_400_BAD_REQUEST
    }
}

# Helper function to get error response
def get_error_response(error_key, detail=None):
    """
    Returns a standardized error response.
    :param error_key: Key from ERROR_RESPONSES dictionary
    :param detail: Optional additional details to include in the response
    :return: Tuple of (response_dict, status_code)
    """
    if error_key not in ERROR_RESPONSES:
        error = ERROR_RESPONSES["INTERNAL_SERVER_ERROR"]
    else:
        error = ERROR_RESPONSES[error_key]
    
    response = {"error": error["error"]}
    if detail:
        response["detail"] = detail
    
    return response, error["status"]

# Custom exception handler for DRF
def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize error responses across the API.
    :param exc: The exception raised
    :param context: Context of the exception (view, request, etc.)
    :return: Response object with standardized error format
    """
    # Call DRF's default exception handler first to get the standard response
    response = drf_exception_handler(exc, context)

    # If DRF couldn't handle it, or we want to customize it
    if response is None:
        # Handle uncaught exceptions as Internal Server Error
        response_data, status_code = get_error_response("INTERNAL_SERVER_ERROR")
        return Response(response_data, status=status_code)

    # Customize specific exceptions
    if isinstance(exc, ValidationError):
        response_data, status_code = get_error_response("VALIDATION_ERROR", detail=exc.detail)
        return Response(response_data, status=status_code)
    elif isinstance(exc, NotFound):
        response_data, status_code = get_error_response("NOT_FOUND", detail=str(exc))
        return Response(response_data, status=status_code)
    elif isinstance(exc, APIException):
        # Handle other API exceptions generically
        response_data, status_code = get_error_response("BAD_REQUEST", detail=str(exc))
        return Response(response_data, status=status_code)

    # If response exists but wasn't customized, return it as-is
    return response