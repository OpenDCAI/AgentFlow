# sandbox/server/backends/error_codes.py
"""
Error Code Definitions for Tool Responses

Standard error code ranges:
- 0: Success
- 4xxx: Client/Input errors (invalid parameters, format issues)
- 5xxx: Execution/System errors (business logic failure, dependency failure, internal errors)
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """Standard error codes for tool responses"""

    # Success
    SUCCESS = 0

    # Client/Input Errors (4xxx)
    # Meaning: Input parameter errors (wrong format, wrong type, missing fields).
    # Strategy: Caller's responsibility, usually not retryable.
    INVALID_INPUT = 4000 
    
    # Execution Errors (5xxx)
    # Meaning: Any error that occurs during execution (business rejection, API failure, system crash).
    # Strategy: Executor's responsibility, determine whether to retry based on specific message.
    EXECUTION_ERROR = 5000

    # Legacy Codes (Keep for backward compatibility if needed, otherwise can be removed)
    # Mapping:
    # 4xxx -> INVALID_INPUT
    # 5xxx -> EXECUTION_ERROR
    INVALID_REQUEST_FORMAT = 4002
    MISSING_REQUIRED_FIELD = 4003
    INVALID_PARAMETER_TYPE = 4004
    INVALID_URL_FORMAT = 4005
    NO_RESULTS_FOUND = 4006
    RESOURCE_NOT_INITIALIZED = 4007
    BUSINESS_FAILURE = 4001
    
    API_KEY_NOT_CONFIGURED = 5002
    API_REQUEST_FAILED = 5003
    API_RESPONSE_PARSE_ERROR = 5004
    UNEXPECTED_ERROR = 5005
    TIMEOUT_ERROR = 5006
    CRAWLING_ERROR = 5007
    SUMMARIZATION_ERROR = 5008
    ALL_REQUESTS_FAILED = 5009
    PARTIAL_FAILURE = 5010
    BACKEND_NOT_INITIALIZED = 5011
    DEPENDENCY_FAILURE = 5012
    INTERNAL_ERROR = 5013


def get_error_message(code: ErrorCode, details: str = "") -> str:
    """
    Get a human-readable error message for an error code
    """
    base_messages = {
        ErrorCode.SUCCESS: "success",
        ErrorCode.INVALID_INPUT: "Invalid input provided",
        ErrorCode.EXECUTION_ERROR: "Tool execution failed",
        
        # Legacy mappings
        ErrorCode.INVALID_REQUEST_FORMAT: "Invalid request format",
        ErrorCode.MISSING_REQUIRED_FIELD: "Missing required field",
        ErrorCode.INVALID_PARAMETER_TYPE: "Invalid parameter type",
        ErrorCode.INVALID_URL_FORMAT: "Invalid URL format",
        ErrorCode.NO_RESULTS_FOUND: "No results found",
        ErrorCode.RESOURCE_NOT_INITIALIZED: "Resource not initialized",
        ErrorCode.BUSINESS_FAILURE: "Business logic execution failed",
        
        ErrorCode.API_KEY_NOT_CONFIGURED: "API key not configured",
        ErrorCode.API_REQUEST_FAILED: "API request failed",
        ErrorCode.API_RESPONSE_PARSE_ERROR: "Failed to parse API response",
        ErrorCode.UNEXPECTED_ERROR: "Unexpected error occurred",
        ErrorCode.TIMEOUT_ERROR: "Request timeout",
        ErrorCode.CRAWLING_ERROR: "Crawling error",
        ErrorCode.SUMMARIZATION_ERROR: "Summarization error",
        ErrorCode.ALL_REQUESTS_FAILED: "All requests failed",
        ErrorCode.PARTIAL_FAILURE: "Partial failure",
        ErrorCode.BACKEND_NOT_INITIALIZED: "Backend not initialized",
        ErrorCode.DEPENDENCY_FAILURE: "External dependency failed",
        ErrorCode.INTERNAL_ERROR: "Internal system error",
    }

    base_msg = base_messages.get(code, "Unknown error")

    if details:
        return f"{base_msg}: {details}"
    return base_msg
