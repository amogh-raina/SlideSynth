"""SlideSynth REST API routes.

All routes are mounted under /api by server/app.py.
"""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------------
# Data directory (project files live here, one subdir per thread_id)
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).parent.parent / "data" / "projects"
_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _project_dir(thread_id: str) -> Path:
    return _DATA_DIR / thread_id


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str


class ResumeRequest(BaseModel):
    decision: str  # "approve" | "reject" | "edit"
    message: str = ""
    args: dict = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/projects", summary="Create a new project by uploading a PDF")
async def create_project(file: UploadFile):
    """Upload a PDF and create a new project thread.

    Returns the thread_id to use for all subsequent API/WS calls.
    The PDF is saved to data/projects/{thread_id}/input.pdf.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    thread_id = str(uuid.uuid4())
    project_dir = _project_dir(thread_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = project_dir / "input.pdf"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return JSONResponse(
        content={
            "thread_id": thread_id,
            "pdf_path": str(pdf_path),
            "message": (
                f"Project created. Connect to /ws/{thread_id} and send "
                f'{{"type": "chat", "message": "Convert {file.filename} to a presentation"}}'
            ),
        },
        status_code=201,
    )


@router.get("/projects", summary="List all project thread IDs")
async def list_projects():
    """Return all project directories found in data/projects/."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    threads = [d.name for d in sorted(_DATA_DIR.iterdir()) if d.is_dir()]
    return {"projects": threads}


@router.get("/projects/{thread_id}", summary="Get project metadata")
async def get_project(thread_id: str):
    """Return metadata about a project: PDF path, generated files, todos."""
    project_dir = _project_dir(thread_id)
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project {thread_id} not found")

    files = [str(p.relative_to(project_dir)) for p in project_dir.rglob("*") if p.is_file()]
    has_presentation = (project_dir / "presentation.html").exists()
    slide_count = len(list((project_dir / "slides").glob("slide*.html"))) if (project_dir / "slides").exists() else 0

    return {
        "thread_id": thread_id,
        "files": sorted(files),
        "has_presentation": has_presentation,
        "slide_count": slide_count,
    }


@router.get(
    "/projects/{thread_id}/files/{file_path:path}",
    summary="Serve a file from a project",
)
async def get_project_file(thread_id: str, file_path: str):
    """Return a file generated inside the project directory.

    Used by the web viewer to load slide HTML, images, and the presentation.
    """
    project_dir = _project_dir(thread_id)
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project {thread_id} not found")

    target = (project_dir / file_path).resolve()
    # Security: ensure resolved path stays inside the project dir
    if not str(target).startswith(str(project_dir.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    return FileResponse(str(target))


@router.get(
    "/projects/{thread_id}/presentation",
    summary="Serve the combined Reveal.js presentation",
)
async def get_presentation(thread_id: str):
    """Return presentation.html with a base tag so all relative asset
    paths resolve through the file-serving endpoint."""
    project_dir = _project_dir(thread_id)
    presentation = project_dir / "presentation.html"
    if not presentation.exists():
        raise HTTPException(
            status_code=404,
            detail="Presentation not generated yet. Run the full pipeline first.",
        )
    html = presentation.read_text(encoding="utf-8")
    # Inject <base> so browser resolves relative paths via the files API.
    # presentation.html references images as "slides/assets/..." so the
    # base points one level up: /api/projects/{id}/files/
    base_tag = f'<base href="/api/projects/{thread_id}/files/">'
    html = html.replace("<head>", f"<head>\n  {base_tag}", 1)
    return HTMLResponse(content=html)


@router.delete("/projects/{thread_id}", summary="Delete a project")
async def delete_project(thread_id: str):
    """Delete all files for a project thread."""
    project_dir = _project_dir(thread_id)
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail=f"Project {thread_id} not found")
    shutil.rmtree(project_dir)
    return {"deleted": thread_id}


# ---------------------------------------------------------------------------
# Chat history persistence
# ---------------------------------------------------------------------------

def _chat_history_path(thread_id: str) -> Path:
    return _project_dir(thread_id) / "chat_history.json"


def append_chat_event(thread_id: str, event: dict) -> None:
    """Append a chat event to the project's chat_history.json.

    Called from the WebSocket handler to persist messages.
    """
    path = _chat_history_path(thread_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    history: list = []
    if path.exists():
        try:
            history = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            history = []
    history.append(event)
    path.write_text(json.dumps(history, ensure_ascii=False), encoding="utf-8")


@router.get(
    "/projects/{thread_id}/chat",
    summary="Retrieve persisted chat history",
)
async def get_chat_history(thread_id: str):
    """Return the saved chat events for a project.

    Used by the frontend to restore conversation state when switching projects.
    """
    path = _chat_history_path(thread_id)
    if not path.exists():
        return JSONResponse(content=[])
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        history = []
    return JSONResponse(content=history)


@router.get("/health", summary="Health check")
async def health():
    """Return server health status."""
    return {"status": "ok", "service": "SlideSynth"}
