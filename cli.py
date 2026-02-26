from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from tools.parse_pdf import parse_pdf_core


def _resolve_output_dir(args: argparse.Namespace) -> Path:
    if args.out:
        return Path(args.out)
    if args.project_id:
        return Path("data/projects") / args.project_id
    return Path("data/projects/debug_parse")


def _cmd_parse(args: argparse.Namespace) -> None:
    output_dir = _resolve_output_dir(args)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = parse_pdf_core(args.pdf, str(output_dir), verbose=args.verbose)
    print(json.dumps(result, indent=2))


def _cmd_serve(args: argparse.Namespace) -> None:
    """Start the FastAPI + WebSocket server."""
    import uvicorn  # noqa: PLC0415

    if args.project_root:
        os.environ["SLIDESYNTH_PROJECT_ROOT"] = args.project_root

    print(f"Starting SlideSynth server on http://0.0.0.0:{args.port}")
    print(f"Web UI:  http://localhost:{args.port}/ui")
    print(f"API:     http://localhost:{args.port}/api")
    print(f"WS:      ws://localhost:{args.port}/ws/<thread_id>")
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


def _cmd_convert(args: argparse.Namespace) -> None:
    """Parse a PDF and run the full agent pipeline (blocks until done)."""
    import uuid  # noqa: PLC0415

    from agent import create_agent  # noqa: PLC0415

    thread_id = args.thread_id or str(uuid.uuid4())
    project_root = args.out or f"data/projects/{thread_id}"
    Path(project_root).mkdir(parents=True, exist_ok=True)

    print(f"Project root: {project_root}")
    print(f"Thread ID:    {thread_id}")
    print("Initialising agent…")

    from tools import set_project_root  # noqa: PLC0415
    set_project_root(project_root)

    agent = create_agent(project_root=project_root)
    config = {"configurable": {"thread_id": thread_id}}
    pdf_path = str(Path(args.pdf).resolve())

    message = (
        f"Convert the PDF at '{pdf_path}' into a Reveal.js presentation. "
        f"The project root is '{project_root}'."
    )

    print("Running pipeline (this may take several minutes)…\n")

    # Stream events to stdout
    async def _run() -> None:
        current_agent = "SlideSynth"
        async for event in agent.astream_events(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            version="v2",
        ):
            etype = event.get("event", "")
            meta = event.get("metadata", {})
            agent_name = meta.get("lc_agent_name", current_agent)

            if etype == "on_chain_start" and agent_name != current_agent:
                current_agent = agent_name
                print(f"\n[{agent_name}] started", flush=True)

            elif etype == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content"):
                    c = chunk.content
                    if isinstance(c, str):
                        print(c, end="", flush=True)
                    elif isinstance(c, list):
                        for block in c:
                            if isinstance(block, dict) and block.get("type") == "text":
                                print(block.get("text", ""), end="", flush=True)

            elif etype == "on_tool_start":
                print(
                    f"\n  → [{agent_name}] {event.get('name', '')}(…)",
                    flush=True,
                )

        print("\n\nPipeline complete!")
        state = agent.get_state(config)
        if state.next:
            print("\nAgent is paused at an interrupt (e.g. export approval).")
            print(f"Resume via:  slidesynth resume --thread-id {thread_id} --decision approve")

    asyncio.run(_run())


def _cmd_resume(args: argparse.Namespace) -> None:
    """Resume an interrupted agent thread."""
    import uuid  # noqa: PLC0415
    from langgraph.types import Command  # noqa: PLC0415

    from agent import get_agent  # noqa: PLC0415

    agent = get_agent()
    config = {"configurable": {"thread_id": args.thread_id}}

    resume_payload = {"type": args.decision}
    if args.message:
        resume_payload["message"] = args.message

    print(f"Resuming thread {args.thread_id} with decision: {args.decision}")

    async def _run() -> None:
        async for event in agent.astream_events(
            Command(resume={"decisions": [resume_payload]}),
            config=config,
            version="v2",
        ):
            etype = event.get("event", "")
            if etype == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content"):
                    c = chunk.content
                    if isinstance(c, str):
                        print(c, end="", flush=True)
        print("\nDone.")

    asyncio.run(_run())


def main() -> None:
    parser = argparse.ArgumentParser(prog="slidesynth")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- parse-pdf ---
    parse_cmd = sub.add_parser("parse-pdf", help="Parse a PDF with Docling (no agent)")
    parse_cmd.add_argument("pdf", help="Path to the PDF file")
    parse_cmd.add_argument("--out", help="Output directory for project artifacts")
    parse_cmd.add_argument("--project-id", help="Project id (uses data/projects/{id})")
    parse_cmd.add_argument("--verbose", action="store_true", help="Print step-by-step progress")

    # --- serve ---
    serve_cmd = sub.add_parser("serve", help="Start the web server")
    serve_cmd.add_argument("--port", type=int, default=8000, help="Port to listen on")
    serve_cmd.add_argument("--reload", action="store_true", help="Enable hot-reload (dev)")
    serve_cmd.add_argument("--project-root", help="Default project root directory")

    # --- convert ---
    convert_cmd = sub.add_parser("convert", help="Full pipeline: PDF → presentation (CLI)")
    convert_cmd.add_argument("pdf", help="Path to the PDF file")
    convert_cmd.add_argument("--out", help="Output directory (default: data/projects/<uuid>)")
    convert_cmd.add_argument("--thread-id", help="Reuse an existing thread ID")

    # --- resume ---
    resume_cmd = sub.add_parser("resume", help="Resume an interrupted agent thread")
    resume_cmd.add_argument("--thread-id", required=True, help="Thread ID to resume")
    resume_cmd.add_argument(
        "--decision",
        choices=["approve", "reject", "edit"],
        default="approve",
        help="Decision to pass to the interrupt",
    )
    resume_cmd.add_argument("--message", default="", help="Optional feedback message")

    args = parser.parse_args()

    dispatch = {
        "parse-pdf": _cmd_parse,
        "serve": _cmd_serve,
        "convert": _cmd_convert,
        "resume": _cmd_resume,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

