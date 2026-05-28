# Changelog

## v2.1.0 — GitHub Release Packaging

### Added
- Bilingual README for public repository publishing.
- MIT license file.
- `pyproject.toml` project metadata.
- `.gitignore` suitable for Python, Streamlit, PyQt, build artifacts, and local datasets.
- `desktop.bat` / `desktop.sh` for the optional PyQt6 desktop shell.
- Friendly `python launcher.py info` metadata command.

### Changed
- Replaced protected/encoded wrappers with readable Python source files.
- `python launcher.py` now defaults to browser mode instead of requiring a subcommand.
- `launcher.py run` starts the Streamlit application directly.
- `launcher.py desktop` starts the optional PyQt6 shell.

### Removed
- Removed `__pycache__` and `.pyc` files from the distributable package.
- Removed local `license.key` and the runtime license gate from the GitHub release build.
- Removed packaging-only authorization runtime files that are not needed for open GitHub distribution.

## v2.0.0 — Original v2 Feature Set

- Streamlit + Plotly visual exploration interface.
- Single Horn, Dual Horn, ΔHORN, Starfield, Chessboard, Cao Analysis, Keyword Terrain, Wrinkle Cloud, Postal-Möbius, and Oreo modes.
- Chinese / English UI toggle.
- PDF, DOCX, TXT, and MD ingestion.
- Keyword extraction, sensitivity calculation, and deterministic visual positioning.
