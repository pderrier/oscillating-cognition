"""Tests for api_client module."""
import pytest
from unittest.mock import patch, MagicMock
from openai import APITimeoutError, RateLimitError, APIConnectionError


def test_get_client_raises_without_api_key():
    """get_client should raise if API key is not set."""
    from api_client import get_client, APIClientError

    with patch('api_client.OPENAI_API_KEY', None):
        with pytest.raises(APIClientError) as exc_info:
            get_client()
        assert "OPENAI_API_KEY not set" in str(exc_info.value)


def test_get_client_creates_client():
    """get_client should create OpenAI client."""
    from api_client import get_client

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.OpenAI') as mock_openai:
        client = get_client(timeout=30)
        mock_openai.assert_called_once()
        assert mock_openai.call_args.kwargs['timeout'] == 30


def test_chat_completion_success():
    """chat_completion should return content on success."""
    from api_client import chat_completion

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"result": "success"}'

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client):

        result = chat_completion(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=100
        )

        assert result == '{"result": "success"}'


def test_chat_completion_retries_on_timeout():
    """chat_completion should retry on timeout errors."""
    from api_client import chat_completion, APIClientError

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APITimeoutError(request=MagicMock())

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client), \
         patch('api_client.time.sleep'):  # Skip actual sleep

        with pytest.raises(APIClientError) as exc_info:
            chat_completion(
                messages=[{"role": "user", "content": "test"}],
                temperature=0.5,
                max_tokens=100,
                max_retries=2,
                retry_delay=0.1
            )

        assert "failed after 2 attempts" in str(exc_info.value)
        assert mock_client.chat.completions.create.call_count == 2


def test_chat_completion_retries_on_rate_limit():
    """chat_completion should retry on rate limit errors."""
    from api_client import chat_completion, APIClientError

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}
    mock_client.chat.completions.create.side_effect = RateLimitError(
        "Rate limited",
        response=mock_response,
        body={}
    )

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client), \
         patch('api_client.time.sleep'):

        with pytest.raises(APIClientError):
            chat_completion(
                messages=[{"role": "user", "content": "test"}],
                temperature=0.5,
                max_tokens=100,
                max_retries=2,
                retry_delay=0.1
            )


def test_chat_completion_success_after_retry():
    """chat_completion should succeed after transient failure."""
    from api_client import chat_completion

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"ok": true}'

    mock_client = MagicMock()
    # Fail first time, succeed second time
    mock_client.chat.completions.create.side_effect = [
        APIConnectionError(request=MagicMock()),
        mock_response
    ]

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client), \
         patch('api_client.time.sleep'):

        result = chat_completion(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=100,
            max_retries=3
        )

        assert result == '{"ok": true}'
        assert mock_client.chat.completions.create.call_count == 2


def test_chat_completion_retries_on_empty_content():
    """chat_completion should retry when API returns empty content."""
    from api_client import chat_completion

    mock_response_empty = MagicMock()
    mock_response_empty.choices = [MagicMock()]
    mock_response_empty.choices[0].message.content = ""

    mock_response_ok = MagicMock()
    mock_response_ok.choices = [MagicMock()]
    mock_response_ok.choices[0].message.content = '{"ok": true}'

    mock_client = MagicMock()
    # First call returns empty, second returns valid content
    mock_client.chat.completions.create.side_effect = [
        mock_response_empty,
        mock_response_ok
    ]

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client), \
         patch('api_client.time.sleep'):

        result = chat_completion(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=100,
            max_retries=3
        )

        assert result == '{"ok": true}'
        assert mock_client.chat.completions.create.call_count == 2


def test_chat_completion_retries_on_none_content():
    """chat_completion should retry when API returns None content."""
    from api_client import chat_completion

    mock_response_none = MagicMock()
    mock_response_none.choices = [MagicMock()]
    mock_response_none.choices[0].message.content = None

    mock_response_ok = MagicMock()
    mock_response_ok.choices = [MagicMock()]
    mock_response_ok.choices[0].message.content = '{"ok": true}'

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [
        mock_response_none,
        mock_response_ok
    ]

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client), \
         patch('api_client.time.sleep'):

        result = chat_completion(
            messages=[{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=100,
            max_retries=3
        )

        assert result == '{"ok": true}'
        assert mock_client.chat.completions.create.call_count == 2


def test_chat_completion_fails_after_all_empty_retries():
    """chat_completion should fail if all retries return empty content."""
    from api_client import chat_completion, APIClientError

    mock_response_empty = MagicMock()
    mock_response_empty.choices = [MagicMock()]
    mock_response_empty.choices[0].message.content = ""

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response_empty

    with patch('api_client.OPENAI_API_KEY', 'test-key'), \
         patch('api_client.get_client', return_value=mock_client), \
         patch('api_client.time.sleep'):

        with pytest.raises(APIClientError) as exc_info:
            chat_completion(
                messages=[{"role": "user", "content": "test"}],
                temperature=0.5,
                max_tokens=100,
                max_retries=2
            )

        assert "failed after 2 attempts" in str(exc_info.value)
        assert mock_client.chat.completions.create.call_count == 2
