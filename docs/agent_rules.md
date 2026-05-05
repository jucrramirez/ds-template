# Antigravity Coding Rules & Guidelines

These rules apply to all Python code (`src/`), Jupyter notebooks (`notebooks/`), and configurations (`config/`). Every rule is strictly mandatory.

## 1. Core Principles
- **Thin notebooks, fat libraries:** Notebooks sequence steps and set parameters. All reusable logic must live in `src/`.
- **Single source of truth:** Runtime parameters belong in versioned YAML config (`config/`), never hardcoded.
- **Secrets stay out of git:** Credentials and environment endpoints go in `.env`. Commit only an `.env.example` with placeholder values.
- **Controlled data footprint:** Large outputs belong in `files/datasets/`, `files/tmp/`, or `files/exports/` and must be git-ignored.

## 2. Placement & Structure
- **Code Location:** Place definitions in their appropriate modules/submodules. Create new ones or migrate existing code if necessary.
- **Import Alignment:** Import paths must align with the directory layout (e.g., `src/config/loader.py` is imported as `config.loader`).
- **Prompt Definitions:** Place prompts in `src/` unless explicitly specified otherwise.
- **Chart Logic:** Complex visualization logic that doesn't fit cleanly in a notebook cell must go in `src/charts/<submodule>/`.
- **Data Access:** `src/` must **never** read data directly. All inputs and parameters must be passed from the notebook. Do not hide I/O behind implicit globals or hard-coded paths.

## 3. Code Quality & Standards

### Naming
- Use descriptive, purpose-driven names for classes, functions, variables, and modules.
- **Never** use generic names like `x`, `y`, `z`, `var`, `tmp`, `data`, or `result`.
- Keep code domain-agnostic. Names must never reference a specific attribute or section name defined in the config file.
- Avoid duplicate or redundant definitions.

### Typing & Arguments
- **100% Type Annotation:** Every class, function, method, and variable definition must be explicitly type-annotated.
- **Never use `Any`.**
- Always use **explicit keyword arguments** at call sites instead of positional arguments.
- Bind results to explicitly annotated variables if the return type is not obvious.

### Data Models & OOP
- Use **Pydantic** for classes: `BaseModel` for external data/config validation, and `@dataclass` for lightweight internal structured data.
- **Never add default values** to parameters unless requested; annotate expected types only.
- Do not force OOP/classes if they do not improve readability or maintainability. Add validators only when strictly necessary.

### Documentation
- **Module-level:** Every script needs a docstring at the top summarizing its purpose.
- **Function/Class-level:** Every class, method, and function requires a **Google-format docstring**, including a brief usage example.
- **Notebook-level:** Every notebook section needs a markdown summary explaining the process and transformations. Specific implementation details belong in the notebook, not in `src/`.

## 4. Execution, Performance & Safety

### Logging & Progress
- Every process must include proper logging using the shared logger from `init_notebook`.
- Use the standard format: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`.
- Include progress bars (succeeded, failed, remaining, counters) where supported.
- **Avoid `print`** for operational messages in pipeline notebooks (only acceptable for exploratory summaries).

### Performance Constraints
- Code must be memory-efficient.
- **Cyclomatic complexity must never exceed 18.**
- Use vectorized/functional alternatives instead of `for` loops where possible. Prefer **Polars** over pandas.
- Use `yield` for all batching definitions. Prevent infinite loops.

### APIs & Resource-Intensive Processes
Must implement:
1. **Exception handling** (timeouts, rate limits, threading, backoff, session expiry).
2. **Retry logic** for failing items.
3. **Checkpoints** every N batches to prevent full recalculation on failure.
4. **Real batching** aligned with upstream API limits.

## 5. Configuration & Secrets

### Separation of Concerns
- **`.env`:** Credentials, API keys, endpoints.
- **`config/*.yaml`:** Paths, model IDs, batch sizes, feature flags. Only parameters used by notebooks/code. Use descriptive sections.
- **Notebooks / `src/`:** Long prompt strings, highly specific or experimental values.

### Rule of thumb
- Always restart the kernel and run from the top after changing YAML or config loader/models (autoreload is unreliable for this).

## 6. Notebook Requirements

### Cell Order (Strict)
1. **Autoreload:** `%load_ext autoreload`, `%autoreload 2`, `%aimport -config.loader`.
2. **Imports & Init:** All imports followed by `from config.loader import init_notebook` and `config, logger = init_notebook(__name__)`.
3. **Intro Markdown:** 
   - `### Human-readable title`
   - 1-2 paragraphs of description.
   - Mermaid flowchart (`LR`).
   - `<details>` block specifying Notebook I/O (Config, Parameters, Input, Output).
4. **Sections:** Alternating `#### Section name` markdown cells and focused code cells.

### Notebook Guidelines
- **Logic placement:** Notebooks execute logic from `src/`. Inline code is only allowed for charts/visualizations.
- **Variables:** User-tunable parameters must be **uppercase variables** near the top of relevant sections.
- **Cell Scope:** One complex execution per cell. Split cells to avoid costly re-runs.
- **Resilience:** Prefer idempotent stages. Include a memory cleanup section at the end and a flag to ignore checkpoints (force full recalculation).
- **Configuration Section:** Each notebook needs a `#### Configuration` section detailing which YAML keys and `.env` variable names are used.

### Directory Metadata
- Each `notebooks/<module>/` directory must contain a `README.md` outlining the execution order, I/O, and relevant config/env keys.
- Ensure the expected environment (Python version) is documented in the root `README.md`.

## 7. Charts & Visualizations
- Precede every visualization with a markdown block explaining: 
  - What it shows and how to interpret it.
  - Ideal vs. bad values.
  - A simple, non-technical example.
- Each visualization goes in its **own cell** (or small cell group). Do not bundle multiple charts in one cell.
- Use colors/formatting to improve readability.

## 8. Stack & Tooling Requirements
- **Python:** `requires-python >= 3.12`.
- **Package Manager:** `uv` (`uv sync`).
- **IDE:** JupyterLab for notebooks.
- **Data Manipulation:** Polars.
- **Packaging:** Editable installs from repo root.
