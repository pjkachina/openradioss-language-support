# DeckLens Semantic Diff for CAE

Semantic diff tool for CAE input files, starting with OpenRadioss.

## Project layout

```
decklens/
  __init__.py
  cli.py                  # Click CLI: `decklens diff before.rad after.rad`
  parsers/
    base.py               # Deck dataclasses (Material, ShellProperty, Part, etc.)
    openradioss.py        # OpenRadioss parser → Card list → Deck
  diff/
    engine.py             # DiffEngine: Deck × Deck → list[Change]
  explainer/
    claude.py             # ClaudeExplainer: changes → AI narrative (claude-opus-4-8)
tests/
  fixtures/
    sample_v1.rad         # Baseline OpenRadioss deck
    sample_v2.rad         # Modified deck (thickness +33%, force ×2, BCS updated)
  test_parser.py
  test_diff.py
```

## Quick start

```bash
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

decklens diff tests/fixtures/sample_v1.rad tests/fixtures/sample_v2.rad
decklens diff before.rad after.rad --no-ai          # skip Claude analysis
decklens diff before.rad after.rad --format json    # machine-readable output
decklens diff before.rad after.rad --min-severity WARNING
```

## Running tests

```bash
pytest -v
```

## Severity thresholds

| Severity | Condition |
|----------|-----------|
| CRITICAL | ≥20% change (or removal of BC / part) |
| WARNING  | 5–20% change (or addition of BC) |
| INFO     | <5% change |

Thickness changes additionally annotate bending stiffness impact (EI ∝ t³).

## Adding a new solver

1. Add a parser in `decklens/parsers/<solver>.py` that returns a `Deck`
2. Auto-detect format in `cli.py` by file extension or header
3. Extend `DiffEngine` if solver-specific fields need special treatment

## Claude API usage

- Model: `claude-opus-4-8`
- Thinking: adaptive (`thinking={"type": "adaptive"}`)
- Effort: high (`output_config={"effort": "high"}`)
- API key: `ANTHROPIC_API_KEY` env var (or `.env` file)
