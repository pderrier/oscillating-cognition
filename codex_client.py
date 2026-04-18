"""
Codex app-server client: proxy LLM calls through the Codex CLI's OAuth session.

When no OPENAI_API_KEY is set, this module spawns a `codex app-server` subprocess
and communicates via JSON-RPC 2.0 over stdio. The Codex CLI handles auth via its
existing OAuth session (no API key needed).

Protocol (v2):
  1. initialize       → handshake
  2. thread/start     → create conversation thread
  3. turn/start       → send input, receive streaming AgentMessageDelta, TurnCompleted
"""
import atexit
import json
import logging
import shutil
import subprocess
import threading
from typing import Optional

logger = logging.getLogger(__name__)

_CODEX_PATHS = [
    "codex",
    "/usr/local/bin/codex",
]


class CodexClientError(Exception):
    """Error communicating with codex app-server."""
    pass


class CodexAppServer:
    """Manages a codex app-server subprocess for OAuth-proxied LLM calls."""

    def __init__(self, model: str = None):
        self.process: Optional[subprocess.Popen] = None
        self.thread_id: Optional[str] = None
        self.model = model
        self._request_id = 0
        self._lock = threading.Lock()
        self._stdout_lines: list[str] = []
        self._reader_thread: Optional[threading.Thread] = None
        self._line_event = threading.Event()

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _find_binary(self) -> str:
        for path in _CODEX_PATHS:
            if shutil.which(path):
                return path
        raise CodexClientError(
            "codex binary not found. Install with: npm install -g @openai/codex\n"
            "Then run: codex login"
        )

    def _stdout_reader(self):
        """Background thread reading stdout lines into a queue."""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace").strip()
                if decoded:
                    with self._lock:
                        self._stdout_lines.append(decoded)
                    self._line_event.set()
            except Exception:
                break

    def _take_line(self, timeout: float = 60.0) -> Optional[str]:
        """Take one line from the buffer, blocking up to timeout."""
        deadline = __import__("time").time() + timeout
        while True:
            with self._lock:
                if self._stdout_lines:
                    return self._stdout_lines.pop(0)
            remaining = deadline - __import__("time").time()
            if remaining <= 0:
                return None
            self._line_event.clear()
            self._line_event.wait(timeout=min(remaining, 1.0))

    def start(self):
        """Spawn codex app-server, send initialize, create thread."""
        if self.process and self.process.poll() is None:
            return

        binary = self._find_binary()
        logger.info(f"[CODEX] Starting app-server: {binary}")

        self.process = subprocess.Popen(
            [binary, "app-server", "--listen", "stdio://"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Start background reader
        self._reader_thread = threading.Thread(target=self._stdout_reader, daemon=True)
        self._reader_thread.start()

        atexit.register(self.stop)

        # Initialize handshake
        resp = self._request("initialize", {
            "clientInfo": {"name": "oscillating-cognition", "version": "1.0.0"}
        })
        logger.info(f"[CODEX] Initialized: {resp.get('result', {}).get('userAgent', '?')}")

        # Create thread
        thread_params = {"ephemeral": True}
        if self.model:
            thread_params["model"] = self.model
        resp = self._request("thread/start", thread_params)
        result = resp.get("result", {})
        self.thread_id = result.get("threadId") or result.get("thread", {}).get("id")
        if not self.thread_id:
            raise CodexClientError(f"No threadId in thread/start response: {resp}")
        logger.info(f"[CODEX] Thread created: {self.thread_id}")

    def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Send a turn and collect the full response text."""
        self.start()

        # Build prompt from messages
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"[System instructions]\n{content}\n")
            else:
                prompt_parts.append(content)
        prompt = "\n".join(prompt_parts)

        # Send turn
        turn_id = self._next_id()
        self._send({
            "id": turn_id,
            "method": "turn/start",
            "params": {
                "threadId": self.thread_id,
                "input": [{"type": "text", "text": prompt}],
            }
        })

        # Collect streaming response
        response_text = []
        while True:
            msg = self._read_message(timeout=120)
            if msg is None:
                raise CodexClientError("app-server timeout waiting for response")

            method = msg.get("method", "")

            if method == "item/agentMessage/delta":
                delta = msg.get("params", {}).get("delta", "")
                if delta:
                    response_text.append(delta)
            elif method == "turn/completed":
                break
            elif "id" in msg and msg.get("id") == turn_id:
                if "error" in msg:
                    err = msg["error"]
                    raise CodexClientError(f"turn/start error: {err.get('message', err)}")

        result = "".join(response_text)
        if not result.strip():
            raise CodexClientError("Codex app-server returned empty response")
        return result

    def stop(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.close()
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()
            logger.info("[CODEX] App-server stopped")
        self.process = None
        self.thread_id = None

    def _request(self, method: str, params: dict) -> dict:
        """Send a JSON-RPC request and wait for the matching response."""
        req_id = self._next_id()
        self._send({"id": req_id, "method": method, "params": params})

        while True:
            msg = self._read_message(timeout=30)
            if msg is None:
                raise CodexClientError(f"Timeout waiting for {method} response")
            if "id" in msg and msg.get("id") == req_id:
                if "error" in msg:
                    err = msg["error"]
                    raise CodexClientError(f"JSON-RPC error in {method}: {err.get('message', err)}")
                return msg
            # Skip notifications while waiting for our response

    def _send(self, msg: dict):
        msg["jsonrpc"] = "2.0"
        data = (json.dumps(msg) + "\n").encode("utf-8")
        try:
            self.process.stdin.write(data)
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            raise CodexClientError(f"Failed to write to app-server: {e}")

    def _read_message(self, timeout: float = 60.0) -> Optional[dict]:
        """Read one JSON-RPC message from the buffer."""
        line = self._take_line(timeout=timeout)
        if line is None:
            return None
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            logger.warning(f"[CODEX] Invalid JSON: {line[:200]}")
            return self._read_message(timeout=timeout)


# Singleton
_server: Optional[CodexAppServer] = None


def get_codex_server(model: str = None) -> CodexAppServer:
    global _server
    if _server is None:
        _server = CodexAppServer(model=model)
    return _server


def codex_chat_completion(
    messages: list[dict],
    temperature: float = 0.7,
    model: str = None,
    **kwargs
) -> str:
    """Drop-in replacement for api_client.chat_completion via Codex OAuth."""
    server = get_codex_server(model=model)
    return server.chat(messages, temperature=temperature)
