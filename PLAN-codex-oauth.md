# Plan: Add Codex OAuth Backend to Oscillating-Cognition

## Problem

The MCP server requires `OPENAI_API_KEY` to make LLM calls. The user wants to use the free Codex OAuth flow instead (no API key needed).

## Constraint

The Codex OAuth token is scoped to `chatgpt.com/backend-api` — it CANNOT be used with `api.openai.com`. So we can't just swap the token into the OpenAI SDK. We need to proxy through the Codex app-server binary.

## Architecture

### Current flow
```
api_client.py → OpenAI SDK → api.openai.com (needs API key)
```

### Target flow (when no API key)
```
api_client.py → codex_client.py → codex app-server subprocess (JSON-RPC stdio) → chatgpt.com/backend-api (OAuth, free)
```

## What exists

- `api_client.py` has a single entry point: `chat_completion(messages, temperature, max_tokens, ...)` returning a string. All 3 consumers (divergent_generator, convergent_critic, grounding) call this one function.
- The Codex app-server binary is installed at:
  - Windows: `C:\Program Files\Alfred Desktop\codex-runtime\codex.exe`
  - macOS: `/Applications/Alfred Desktop.app/Contents/MacOS/codex-runtime/codex`
  - System PATH: `codex` (if installed globally via npm)
- The app-server protocol is JSON-RPC 2.0 over stdio:
  - `initialize` → handshake
  - `thread/start` → create conversation thread
  - `turn/start` → send `{input: [{type: "text", text: prompt}]}`, receive streaming `item/agentMessage/delta` notifications, `turn/completed` when done

## Implementation Plan

### Step 1: Create `codex_client.py` (~100 lines)

```python
class CodexAppServer:
    """Manages a codex app-server subprocess for OAuth-proxied LLM calls."""
    
    def __init__(self):
        self.process = None
        self.thread_id = None
    
    def start(self):
        """Spawn codex app-server, send initialize, create thread."""
        # Find codex binary (check PATH, then known install paths)
        # subprocess.Popen(["codex", "app-server"], stdin=PIPE, stdout=PIPE)
        # Send initialize JSON-RPC, wait for response
        # Send thread/start, store thread_id
    
    def chat(self, messages, temperature=0.7):
        """Send a turn and collect the full response text."""
        # Build prompt from messages (system + user concatenated)
        # Send turn/start with input text
        # Read stdout line-by-line, accumulate agentMessage/delta text
        # Return on turn/completed
    
    def stop(self):
        """Clean shutdown."""
```

### Step 2: Modify `api_client.py` — auto-detect backend

```python
def chat_completion(messages, temperature, max_tokens, ...):
    if OPENAI_API_KEY:
        # Existing path: OpenAI SDK
        return _openai_chat_completion(messages, temperature, max_tokens, ...)
    else:
        # New path: Codex app-server
        return _codex_chat_completion(messages, temperature)
```

### Step 3: Handle lifecycle

- Lazy-start: spawn app-server on first call, reuse across cycles
- Cleanup: `atexit.register(server.stop)` to kill subprocess on exit
- Error handling: if codex binary not found, raise clear error with install instructions

## Files to change

| File | Change |
|------|--------|
| `codex_client.py` | NEW — Codex app-server subprocess manager |
| `api_client.py` | Add auto-detect: API key → OpenAI SDK, no key → codex_client |
| `config.py` | Add `CODEX_BINARY_PATH` config with auto-detection |
| `requirements.txt` | No new deps (uses subprocess + json, both stdlib) |

## Risks

- **App-server must be authenticated**: User needs to have logged into Codex at least once (`codex` CLI login flow). If not authenticated, the app-server will fail on first turn.
- **Text-only responses**: The app-server returns plain text, not structured JSON. Since oscillating-cognition requests `response_format: json_object`, the prompt must explicitly instruct JSON output (the model usually cooperates).
- **No parallel calls**: The app-server is single-threaded per process. Oscillating-cognition runs sequential cycles, so this is fine.
- **Windows vs WSL path**: On WSL, need to call the Windows binary via `/mnt/c/...` or `codex.cmd`. Auto-detection should check both.

## Effort

~2-3 hours for a senior engineer. The `codex_client.py` is ~100 lines, the `api_client.py` change is ~20 lines, config is ~10 lines.

## Alternative considered

Route through Alfred's `chat_wizard_send_local` Tauri command — rejected because it requires the desktop app to be running, creating a circular dependency (MCP server needs desktop app, desktop app uses MCP server).
