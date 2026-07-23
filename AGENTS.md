# AGENTS.md

## Project overview

OCR system that extracts structured data (prices, leverage levels, exchange info) from CoinGlass liquidation heatmap screenshots. Early-stage — single source file (`src/main.py`), with tests in `tests/test_main.py`.

**Language: all code, comments, docs, and variable names are in English.**

## Quick start

```bash
# Install dependencies
uv venv --python 3.12
uv pip install .

# Run on all images in data/input/
uv run python src/main.py

# Run on a single image
uv run python src/main.py "data/input/imagen.png"

# Dev dependencies (pytest, ruff)
uv pip install ".[dev]"
```

## Key facts

- **Package manager**: uv (not pip, not poetry). Lockfile `uv.lock` exists but is gitignored.
- **Python**: >=3.12 required.
- **OCR library**: EasyOCR is the chosen library. PaddleOCR is broken on Windows (shm.dll/PyTorch issue). Tesseract was tested and discarded (too inaccurate on dark dashboards).
- **EasyOCR config**: Languages `['es', 'en']`, `gpu=False`. Model files auto-downloaded on first run to user home dir, not in repo.
- **Entrypoint**: `src/main.py` — the only source file.
- **Data flow**: Image -> EasyOCR `readtext()` -> classify detections (exchange, pair, timeframe, price, other) -> sort prices by X coordinate -> save as Markdown with YAML frontmatter.

## Output format

Files saved to `data/output/` with naming: `ocr_{exchange}_{pair}_{timeframe}_{date}_{time}.md`

Each file has YAML frontmatter (metadata) + Markdown tables (prices with bounding box coords and confidence, plus other detected texts).

## Code conventions

- Commit messages: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`)
- No linter config file — ruff runs with defaults
- No CI/CD, no pre-commit hooks
- `tests/test_main.py` — 14 tests (unit + integration)
- pytest configured in `pyproject.toml` with marker `slow` for EasyOCR tests

## Common pitfalls

- **README is outdated**: references `requirements.txt` which doesn't exist. Trust `pyproject.toml` as source of truth.
- **Data files are gitignored but currently tracked** — `.gitignore` excludes `data/input/*` and `data/output/*`, but files were committed before gitignore rules were added.
- **EasyOCR misreads some text**: "Apalancamiento" -> "Apalancamicnto", "BTC/USDT" -> "BTCIUSDT". Exchange and price detection are reliable; text labels less so.
- **Price regex**: `^\d+([.,]\d+)?$` — matches any number including decimals. Originally BTC-specific but generalized.

## Roadmap

See `docs/tasks.md` for the full 7-phase plan. Currently: Phase 5 (OCR extraction) partially implemented via `src/main.py`. Phases 1-4, 6-7 are pending.
