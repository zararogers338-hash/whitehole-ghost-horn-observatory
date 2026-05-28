# -*- coding: utf-8 -*-
"""Command-line launcher for White Hole Ghost Horn Observatory."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

APP_NAME = "White Hole Ghost Horn Observatory"
REPOSITORY_NAME = "whitehole-ghost-horn-observatory"
VERSION = "2.1.0"
ROOT = Path(__file__).resolve().parent


def _call(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd, cwd=str(ROOT))
    except KeyboardInterrupt:
        return 130


def cmd_run(args: argparse.Namespace) -> int:
    """Run the Streamlit browser UI."""
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "streamlit_app.py"),
        "--server.address",
        args.address,
        "--server.port",
        str(args.port),
    ]
    if args.headless:
        cmd.extend(["--server.headless", "true"])
    return _call(cmd)


def cmd_desktop(_args: argparse.Namespace) -> int:
    """Run the optional PyQt6 desktop shell."""
    return _call([sys.executable, str(ROOT / "main.py")])


def cmd_info(_args: argparse.Namespace) -> int:
    print(json.dumps({
        "app_name": APP_NAME,
        "repository_name": REPOSITORY_NAME,
        "version": VERSION,
        "entrypoints": {
            "browser": "python launcher.py run",
            "desktop": "python launcher.py desktop",
            "streamlit": "streamlit run streamlit_app.py",
        },
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="whitehole",
        description=f"{APP_NAME} v{VERSION} launcher",
    )
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="launch the Streamlit browser UI")
    run.add_argument("--address", default="127.0.0.1", help="server bind address")
    run.add_argument("--port", type=int, default=8501, help="server port")
    run.add_argument("--headless", action="store_true", help="disable browser auto-open")
    run.set_defaults(func=cmd_run)

    desktop = sub.add_parser("desktop", help="launch the optional PyQt6 desktop shell")
    desktop.set_defaults(func=cmd_desktop)

    info = sub.add_parser("info", help="print project metadata")
    info.set_defaults(func=cmd_info)
    return parser


def main(argv: list[str] | None = None) -> int:
    # Friendly default: `python launcher.py` now runs the app instead of erroring.
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        argv = ["run"]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
