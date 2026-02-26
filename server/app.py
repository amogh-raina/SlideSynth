"""SlideSynth FastAPI server.

Starts with: uvicorn server.app:app --reload --port 8000

WebSocket protocol (ws://localhost:8000/ws/{thread_id}):
  Client → Server:
    {"type": "chat",   "message": "<user text>"}
    {"type": "resume", "decision": "approve"|"reject"|"edit", "message": "<optional>", "args": {}}

  Server → Client:
    {"type": "thinking",    "agent": "<name>", "content": "<token chunk>"}
    {"type": "tool_call",   "agent": "<name>", "tool": "<name>", "input": {...}}
    {"type": "tool_result", "agent": "<name>", "tool": "<name>", "output": "<summary>"}
    {"type": "agent_start", "agent": "<name>"}
    {"type": "agent_done",  "agent": "<name>"}
    {"type": "todo_update", "todos": [...]}
    {"type": "interrupt",   "action": "<tool>", "data": {...}}
    {"type": "error",       "message": "<text>"}
    {"type": "complete",    "message": "<final assistant message>"}
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent lifecycle
# ---------------------------------------------------------------------------


import os as _os
from tools import set_project_root as _set_project_root

_PROJECTS_DIR = Path(
    _os.environ.get("SLIDESYNTH_PROJECT_ROOT", "")
) if _os.environ.get("SLIDESYNTH_PROJECT_ROOT") else Path(__file__).parent.parent / "data" / "projects"


def _get_agent(thread_id: str):
    """Return a per-project agent cached by thread_id.

    Each thread maps to data/projects/{thread_id}/ on disk.
    The agent's FilesystemBackend is rooted there so virtual paths
    like /docs/document.md resolve to the correct project directory.
    """
    from agent import get_agent  # noqa: PLC0415

    project_root = str(_PROJECTS_DIR / thread_id)
    return get_agent(project_root=project_root)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Per-project agents are created on first WS connect — no warmup needed.
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SlideSynth",
    description="Multi-agent PDF → Reveal.js presentation system",
    version="0.1.0",
    lifespan=lifespan,
)

# Serve the web UI and any generated project files
_WEB_DIR = Path(__file__).parent.parent / "web"
if _WEB_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(_WEB_DIR), html=True), name="web")

# ---------------------------------------------------------------------------
# REST routes (import after app is created to avoid circular refs)
# ---------------------------------------------------------------------------

from server.routes import router  # noqa: E402

app.include_router(router, prefix="/api")

# ---------------------------------------------------------------------------
# WebSocket streaming endpoint
# ---------------------------------------------------------------------------

# Active WebSocket connections keyed by thread_id
_connections: Dict[str, WebSocket] = {}


def _unwrap(value: Any) -> Any:
    """Unwrap LangGraph Overwrite/Send wrappers to get the underlying value."""
    if hasattr(value, "value"):
        return value.value
    return value


async def _send(ws: WebSocket, payload: Dict[str, Any]) -> None:
    """Send a JSON message to the client; ignore closed sockets."""
    try:
        await ws.send_json(payload)
    except Exception:
        pass


async def _send_stream_content(ws: WebSocket, agent_name: str, content: Any) -> None:
    """Extract text from a chat model stream chunk and forward as thinking events.

    Handles:
    - Plain string content (OpenAI-style models)
    - List-of-blocks content (Anthropic-style):  {"type": "text"} and
      {"type": "thinking"} blocks from extended thinking.
    """
    if isinstance(content, str) and content:
        await _send(ws, {"type": "thinking", "agent": agent_name, "content": content})
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            text = ""
            if btype == "text":
                text = block.get("text", "")
            elif btype == "thinking":
                text = block.get("thinking", "")
            if text:
                await _send(ws, {"type": "thinking", "agent": agent_name, "content": text})


async def _stream_agent(ws: WebSocket, thread_id: str, messages: list) -> None:
    """Stream astream_events to the WebSocket client.

    Translates LangGraph event types into typed WebSocket messages.  Handles
    interrupt detection and sends a ``{"type": "interrupt"}`` when the agent
    pauses for human approval.
    """
    from langgraph.types import Command  # noqa: PLC0415

    project_root = str(_PROJECTS_DIR / thread_id)
    _set_project_root(project_root)

    agent = _get_agent(thread_id)
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 250}

    last_message: str = ""
    current_agent: str = "SlideSynth"

    try:
        async for event in agent.astream_events(
            {"messages": messages},
            config=config,
            version="v2",
        ):
            event_type: str = event.get("event", "")
            meta: Dict[str, Any] = event.get("metadata", {})
            agent_name: str = meta.get("lc_agent_name", current_agent)

            # --- agent boundary events ----------------------------------
            if event_type == "on_chain_start":
                if agent_name != current_agent:
                    current_agent = agent_name
                    await _send(ws, {"type": "agent_start", "agent": agent_name})

            elif event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                # Capture final text from orchestrator
                if isinstance(output, dict):
                    msgs = _unwrap(output.get("messages", []))
                    if isinstance(msgs, list) and msgs:
                        last = msgs[-1]
                        if hasattr(last, "content") and isinstance(last.content, str):
                            last_message = last.content
                    # Check for todo state update
                    todos = _unwrap(output.get("todos"))
                    if isinstance(todos, list) and todos:
                        await _send(ws, {"type": "todo_update", "todos": todos})

            # --- LLM token streaming ------------------------------------
            elif event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content"):
                    await _send_stream_content(ws, agent_name, chunk.content)

            # --- tool lifecycle -----------------------------------------
            elif event_type == "on_tool_start":
                tool_input = event.get("data", {}).get("input", {})
                tool_name = event.get("name", "unknown_tool")
                await _send(
                    ws,
                    {
                        "type": "tool_call",
                        "agent": agent_name,
                        "tool": tool_name,
                        "input": _safe_truncate(tool_input, max_chars=300),
                    },
                )

            elif event_type == "on_tool_end":
                tool_name = event.get("name", "unknown_tool")
                output = event.get("data", {}).get("output", "")
                await _send(
                    ws,
                    {
                        "type": "tool_result",
                        "agent": agent_name,
                        "tool": tool_name,
                        "output": _safe_truncate(str(output), max_chars=200),
                    },
                )

    except Exception as exc:
        await _send(ws, {"type": "error", "message": str(exc)})
        logger.exception("Error during agent stream for thread %s", thread_id)
        return

    # After stream finishes, check for pending interrupts
    try:
        state = agent.get_state(config)
        if state.next:
            # There are pending nodes — indicates an interrupt
            interrupts = _extract_interrupts(state)
            await _send(
                ws,
                {
                    "type": "interrupt",
                    "action": interrupts.get("tool", "unknown"),
                    "data": interrupts,
                },
            )
        else:
            await _send(ws, {"type": "complete", "message": last_message})
    except Exception as exc:
        logger.warning("Could not check state after stream: %s", exc)
        await _send(ws, {"type": "complete", "message": last_message})


async def _resume_agent(ws: WebSocket, thread_id: str, decision: Dict[str, Any]) -> None:
    """Resume agent after an interrupt with the user's decision."""
    from langchain_core.messages import AIMessage  # noqa: PLC0415

    project_root = str(_PROJECTS_DIR / thread_id)
    _set_project_root(project_root)

    agent = _get_agent(thread_id)
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 250}

    decision_type = decision.get("decision", "approve")
    msg = decision.get("message", "")
    args = decision.get("args", {})

    resume_payload: Dict[str, Any] = {"type": decision_type}
    if msg:
        resume_payload["message"] = msg
    if args:
        resume_payload["args"] = args

    from langchain_core.messages import HumanMessage  # noqa: PLC0415

    try:
        from langgraph.types import Command  # noqa: PLC0415

        # Resume by invoking with None input and the Command
        last_message = ""
        current_agent = "SlideSynth"
        async for event in agent.astream_events(
            Command(resume={"decisions": [resume_payload]}),
            config=config,
            version="v2",
        ):
            event_type = event.get("event", "")
            meta = event.get("metadata", {})
            agent_name = meta.get("lc_agent_name", current_agent)

            if event_type == "on_chain_start":
                if agent_name != current_agent:
                    current_agent = agent_name
                    await _send(ws, {"type": "agent_start", "agent": agent_name})

            elif event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content"):
                    await _send_stream_content(ws, agent_name, chunk.content)

            elif event_type == "on_tool_start":
                await _send(ws, {
                    "type": "tool_call",
                    "agent": agent_name,
                    "tool": event.get("name", ""),
                    "input": _safe_truncate(event.get("data", {}).get("input", {}), 200),
                })

            elif event_type == "on_tool_end":
                await _send(ws, {
                    "type": "tool_result",
                    "agent": agent_name,
                    "tool": event.get("name", ""),
                    "output": _safe_truncate(str(event.get("data", {}).get("output", "")), 200),
                })

            elif event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict):
                    msgs = _unwrap(output.get("messages", []))
                    if isinstance(msgs, list) and msgs:
                        last = msgs[-1]
                        if hasattr(last, "content") and isinstance(last.content, str):
                            last_message = last.content
                    todos = _unwrap(output.get("todos"))
                    if isinstance(todos, list) and todos:
                        await _send(ws, {"type": "todo_update", "todos": todos})

        # Check for another interrupt after resume
        state = agent.get_state(config)
        if state.next:
            interrupts = _extract_interrupts(state)
            await _send(ws, {"type": "interrupt", "action": interrupts.get("tool", ""), "data": interrupts})
        else:
            await _send(ws, {"type": "complete", "message": last_message})

    except Exception as exc:
        await _send(ws, {"type": "error", "message": str(exc)})
        logger.exception("Error during agent resume for thread %s", thread_id)


def _safe_truncate(value: Any, max_chars: int = 300) -> Any:
    """Truncate string or dict repr to keep WebSocket messages small."""
    if isinstance(value, str):
        return value[:max_chars] + ("…" if len(value) > max_chars else "")
    if isinstance(value, dict):
        s = json.dumps(value)
        if len(s) > max_chars:
            return s[:max_chars] + "…"
        return value
    return str(value)[:max_chars]


def _extract_interrupts(state: Any) -> Dict[str, Any]:
    """Extract interrupt metadata from a LangGraph state snapshot."""
    try:
        tasks = getattr(state, "tasks", [])
        for task in tasks:
            interrupts_list = getattr(task, "interrupts", [])
            if interrupts_list:
                first = interrupts_list[0]
                value = getattr(first, "value", {})
                tool = value.get("tool_name", "") if isinstance(value, dict) else ""
                return {"tool": tool, "raw": value}
    except Exception:
        pass
    return {"tool": "export_to_pdf", "raw": {}}


@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    """Bidirectional WebSocket for streaming agent events.

    Protocol:
      Client sends: {"type": "chat",   "message": "<user text>"}
                    {"type": "resume", "decision": "approve|reject|edit", ...}
      Server sends: see module docstring
    """
    await websocket.accept()
    _connections[thread_id] = websocket
    logger.info("WS connected: thread=%s", thread_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await _send(websocket, {"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                message = data.get("message", "").strip()
                if not message:
                    await _send(websocket, {"type": "error", "message": "Empty message"})
                    continue
                await _stream_agent(
                    websocket,
                    thread_id,
                    [{"role": "user", "content": message}],
                )

            elif msg_type == "resume":
                await _resume_agent(websocket, thread_id, data)

            else:
                await _send(websocket, {"type": "error", "message": f"Unknown type: {msg_type}"})

    except WebSocketDisconnect:
        logger.info("WS disconnected: thread=%s", thread_id)
    finally:
        _connections.pop(thread_id, None)
