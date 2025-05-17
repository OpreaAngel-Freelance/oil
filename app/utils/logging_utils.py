"""
Utility functions for logging.
"""

import logging

# Initialize logger
logger = logging.getLogger(__name__)


def log_retry_attempt(operation_name: str):
    """
    Factory function that returns a callback for logging retry attempts.

    This function creates and returns a callback that can be used with
    the tenacity library's retry decorator as the 'before' callback.

    Args:
        operation_name: The name of the operation being retried

    Returns:
        A function that takes a retry_state parameter and logs the retry attempt
    """
    # We need to return a function that takes retry_state as parameter
    # because that's what tenacity expects for its 'before' callback
    return lambda retry_state: logger.warning(
        f"Retrying {operation_name} (attempt {retry_state.attempt_number})"
    )
