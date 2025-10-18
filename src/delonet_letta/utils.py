"""Utility functions for error handling and retries."""

import time
from typing import TypeVar, Callable, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LettaError(Exception):
    """Base exception for Letta operations."""
    pass


class MCPServerError(LettaError):
    """Exception raised when MCP server operations fail."""
    pass


class ToolRegistrationError(LettaError):
    """Exception raised when tool registration fails."""
    pass


class AgentError(LettaError):
    """Exception raised when agent operations fail."""
    pass


def handle_already_exists(error_message: str) -> bool:
    """
    Check if an error is due to a resource already existing.

    Args:
        error_message: The error message to check

    Returns:
        True if the error is an "already exists" error
    """
    already_exists_patterns = [
        "already exists",
        "already registered",
        "duplicate",
        "conflict",
    ]

    error_lower = str(error_message).lower()
    return any(pattern in error_lower for pattern in already_exists_patterns)


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for subsequent retries
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")

            raise last_exception

        return wrapper
    return decorator


def safe_execute(
    operation: Callable[..., T],
    error_message: str,
    raise_on_error: bool = False,
    default_return: Optional[T] = None
) -> Optional[T]:
    """
    Safely execute an operation with standardized error handling.

    Args:
        operation: The operation to execute
        error_message: Error message prefix to use
        raise_on_error: Whether to re-raise exceptions
        default_return: Default value to return on error

    Returns:
        Operation result or default_return on error

    Raises:
        Exception: If raise_on_error is True
    """
    try:
        return operation()
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        if raise_on_error:
            raise
        return default_return
