"""
Robust API client with retry logic and error handling.

Supports two backends:
  1. OpenAI SDK (when OPENAI_API_KEY is set)
  2. Codex app-server (when no API key — uses OAuth session)
"""
import time
import logging
from typing import Optional

from config import OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_TIMEOUT = 60  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2  # seconds (will be multiplied exponentially)

# Always import OpenAI types — needed for test patching and the OpenAI code path.
# The openai package is a required dependency regardless of backend.
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError

if not OPENAI_API_KEY:
    logger.info("No OPENAI_API_KEY — will route through Codex app-server")


class APIClientError(Exception):
    """Custom exception for API client errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


def get_client(timeout: int = DEFAULT_TIMEOUT) -> "OpenAI":
    """Create OpenAI client with configured settings."""
    if not OPENAI_API_KEY:
        raise APIClientError(
            "OPENAI_API_KEY not set. Set it in environment or .env file.\n"
            "Or install Codex CLI and run 'codex login' to use OAuth instead."
        )

    return OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
        timeout=timeout
    )


def chat_completion(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    model: str = None,
    json_response: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY
) -> str:
    """
    Make a chat completion request with retry logic.

    Args:
        messages: List of message dicts (role, content)
        temperature: Sampling temperature
        max_tokens: Maximum response tokens
        model: Model to use (default from config)
        json_response: Request JSON response format
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        retry_delay: Base delay between retries (exponential backoff)

    Returns:
        Response content string

    Raises:
        APIClientError: If all retries fail
    """
    # Route through Codex app-server when no API key
    if not OPENAI_API_KEY:
        return _codex_chat_completion(
            messages, temperature, max_tokens, model,
            json_response, max_retries, retry_delay
        )

    if model is None:
        model = OPENAI_MODEL

    client = get_client(timeout)

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if json_response:
        kwargs["response_format"] = {"type": "json_object"}

    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            # Validate response is not None/empty - these are retryable
            if content is None:
                logger.warning(f"API returned None content (attempt {attempt + 1}/{max_retries})")
                last_error = APIClientError("API returned None content")
                if attempt < max_retries - 1:
                    sleep_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                continue

            if not content.strip():
                logger.warning(f"API returned empty content (attempt {attempt + 1}/{max_retries})")
                last_error = APIClientError("API returned empty content")
                if attempt < max_retries - 1:
                    sleep_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                continue

            return content

        except APITimeoutError as e:
            last_error = e
            logger.warning(f"API timeout (attempt {attempt + 1}/{max_retries}): {e}")

        except RateLimitError as e:
            last_error = e
            logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries}): {e}")
            # Rate limits need longer wait
            time.sleep(retry_delay * (2 ** attempt) * 2)
            continue

        except APIConnectionError as e:
            last_error = e
            logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries}): {e}")

        except APIError as e:
            last_error = e
            # Don't retry on 4xx errors (client errors)
            if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                raise APIClientError(
                    f"API client error (not retryable): {e}",
                    original_error=e
                )
            logger.warning(f"API error (attempt {attempt + 1}/{max_retries}): {e}")

        except Exception as e:
            last_error = e
            logger.error(f"Unexpected error (attempt {attempt + 1}/{max_retries}): {e}")
            # Don't retry unknown errors
            raise APIClientError(
                f"Unexpected error: {e}",
                original_error=e
            )

        # Exponential backoff
        if attempt < max_retries - 1:
            sleep_time = retry_delay * (2 ** attempt)
            logger.info(f"Retrying in {sleep_time}s...")
            time.sleep(sleep_time)

    # All retries exhausted
    raise APIClientError(
        f"API request failed after {max_retries} attempts. Last error: {last_error}",
        original_error=last_error
    )


def _codex_chat_completion(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    model: str = None,
    json_response: bool = True,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY
) -> str:
    """Route chat completion through Codex app-server."""
    from codex_client import codex_chat_completion, CodexClientError

    # When json_response is requested, add explicit instruction
    # (Codex app-server doesn't support response_format parameter)
    if json_response:
        has_system = any(m.get("role") == "system" for m in messages)
        if has_system:
            messages = [
                {**m, "content": m["content"] + "\n\nIMPORTANT: Output ONLY valid JSON, no other text."}
                if m.get("role") == "system" else m
                for m in messages
            ]
        else:
            messages = [{"role": "system", "content": "Output ONLY valid JSON, no other text."}] + messages

    last_error = None
    for attempt in range(max_retries):
        try:
            content = codex_chat_completion(
                messages=messages,
                temperature=temperature,
                model=model,
            )
            if content and content.strip():
                return content
            last_error = APIClientError("Codex returned empty content")
        except CodexClientError as e:
            last_error = e
            logger.warning(f"Codex error (attempt {attempt + 1}/{max_retries}): {e}")

        if attempt < max_retries - 1:
            sleep_time = retry_delay * (2 ** attempt)
            time.sleep(sleep_time)

    raise APIClientError(
        f"Codex request failed after {max_retries} attempts: {last_error}",
        original_error=last_error
    )
