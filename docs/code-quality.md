## Code quality standard (notebook-centric data pipelines)

This document defines the **code quality rules and considerations** for projects that use **Jupyter notebooks for orchestration** and **importable Python libraries under `src/`**.

It consolidates and de-duplicates the existing guidance currently split across the repo’s `docs/` files. **Do not treat these rules as optional**: they exist to keep notebook-driven pipelines maintainable, reproducible, and safe.

---

### Scope and intent

- **Applies to**: all Python code under `src/`, all notebooks under `notebooks/`, and all configuration under `config/`.
- **Primary intent**: notebooks orchestrate and document; `src/` contains reusable, testable logic; configuration is validated; secrets remain outside git.
- **Consistency target**: notebooks should run consistently across environments (local, managed notebook platforms, CI) when the same config and secrets are provided.

---

### Non‑negotiable cross-cutting rules (also apply to repo creation)

#### Secrets vs configuration (required)

- **`.env`**: secrets + environment-specific endpoints. Never committed.
- **YAML under `config/`**: non-secret knobs, paths, model IDs, schema/table/column lists, feature flags.
- Always commit **`.env.example`** (variable names + placeholders + short comments; no secrets).

#### Kernel restart rule (required)

- After changing **YAML** or the **config loader / Pydantic models**, **restart the kernel** and re-run from the top. Autoreload is unreliable for config model definitions and cached settings.

#### Notebook structure baseline (required)

- First executable cell: autoreload + exclude the config loader module (`%aimport -config.loader` or equivalent).
- Second cell: all imports + `config, logger = init_notebook(__name__)`.
- Third cell: `###` title + short intro + Mermaid + collapsible I/O block.
- Body: alternating `####` sections and focused code cells.

#### Charts rule (required)

- **Every visualization must be preceded by documentation** explaining:
    - what it shows and how to interpret it
    - ideal values and “bad” values (thresholds, colors, ranges)
    - a simple example understandable by a non-specialist
- **One visualization per cell** (or a dedicated small group of cells). Never combine multiple charts in one cell.
- If chart logic becomes too complex for a notebook cell, move it to `src/charts/<submodule>/`.

---

### 1) Naming & code clarity

- Use descriptive, purpose-driven names for classes, functions, variables, and modules.
    - Avoid generic names like `x`, `y`, `z`, `var`, `temp`, etc.
- Code must remain **generic**:
    - names must never reference a specific attribute, variable name, or section name defined in the config file
    - prefer domain-agnostic naming that remains stable if YAML keys change
- Keep it clean:
    - avoid duplicating variables
    - avoid redundant definitions across the codebase

---

### 2) Type annotations (strict)

- Every class, function, method, and variable definition must be **100% annotated**.
- Never use `Any` as a type annotation.
- At call sites:
    - use **explicit parameter names** (keyword arguments) rather than positional arguments
    - keep calls self-documenting and stable if function signatures evolve
    - keep types explicit end-to-end (avoid `Any` flowing through call chains); when the type is not obvious, bind results to **explicitly annotated variables** instead of relying on implicit inference

---

### 3) Classes, OOP, and data models

- For all class definitions, use **Pydantic**:
    - `BaseModel` when validating/parsing external data or configs
    - `@dataclass` when representing internal structured data with lightweight validation needs
- Never add default values to parameters unless explicitly requested. Only annotate expected types.
- Follow OOP best practices, but **do not force a class** if it does not improve readability or maintainability.
- Add Pydantic validators only when strictly necessary to implement required validations.

---

### 4) Project structure & module placement

- Place every definition in the appropriate module/submodule.
    - If no module fits, create the correct one.
    - If existing code matches the new module’s purpose, migrate it accordingly.
- Match import paths to directory layout so IDEs and type checkers behave consistently (for example, `src/config/...` is imported as `config...` when installed/editable-installed).
- Prompt definitions belong to `src/` unless explicitly specified otherwise.
- Chart/visualization logic that is too complex for a notebook cell must be moved to:
    - `src/charts/<submodule>/` (example: `src/charts/keywords`)
    - and must follow all rules in this document (typing, docs, logging, etc.)

---

### 5) Documentation standards

#### Python modules, classes, and functions

- Every script must include a **module-level docstring** at the top:
    - brief, concise, and summarizing the module’s purpose
- Every class, function, and method must include a **Google-format docstring**, including a brief usage example.

#### Notebooks and notebook sections

- Every notebook section must include a brief markdown summary of the process it covers, including examples of transformations applied in that section.
- For notebook structure, headings, Mermaid, and I/O blocks, follow the “Notebook quality & formatting” section below.

---

### 6) Logging & progress reporting

- Every process must include proper logging.
- Prefer a shared logging configuration so notebook output matches CLI output (standard format: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`).
- For processes that support it, include a progress bar that displays relevant real-time information:
    - succeeded, failed, remaining
    - plus any other counters that materially help operators understand progress

---

### 7) Performance, safety, and complexity constraints

- Every process must be implemented in a **memory-efficient** way.
- **Cyclomatic complexity must never exceed 18.**
- Avoid `for` loops where vectorized, functional, or otherwise time-efficient alternatives exist.
- Use `yield` for all batching definitions.
- Avoid any implementation that could lead to infinite loops or similar non-terminating behavior.
- Prefer **Polars** over pandas for dataframe operations.

---

### 8) External APIs and resource-intensive processes (required)

For any process that relies on an external API, involves paid calls, or is resource-demanding, implement all of the following:

- **Exception handling**:
    - timeouts
    - rate limits (e.g. “Too Many Requests”)
    - threading considerations where applicable
    - exponential backoff
    - credential/session expiry considerations for long jobs (for example, a refresh hook when tokens expire)
- **Retry logic** for failing items.
- **Checkpoints every N batches** to avoid reprocessing from scratch on failure.
- **Real batching** aligned with the upstream tool/package documentation (example: an embeddings API max documents per request).

---

### 9) Notebook quality & formatting (required)

#### 9.1 Notebook purpose and boundaries

- A notebook’s only purpose is to execute complex logic defined in `src/`.
    - The only inline code allowed in notebooks is Charts & Visualizations.
- `src/` must **never** read data directly.
    - All inputs and parameters must be passed from the notebook.
    - Interpreting this rule for practical pipelines:
        - do not hide IO behind implicit globals or hard-coded paths
        - any IO performed by library code must be explicitly triggered and fully parameterized by the notebook (e.g., passing a URI/path/config object), and must not silently reach into local disk state
- Prefer stable, testable library APIs:
    - notebooks should call stable functions/classes (not re-implement logic inline)
    - separate IO from pure transforms when possible (pure transforms are easier to test and reuse)
- Prefer explicit knobs:
    - define user-tunable parameters as **uppercase** variables near the top of the relevant section (or in a dedicated parameters cell)
    - list those knobs in the intro I/O block
- Prefer idempotent stages where possible:
    - write to dated/checkpointed outputs so reruns are safe
    - design checkpointing early when work is expensive
- Never add hardcoded or default values in `src/`. The notebook controls what values the code runs with (ideally by reading YAML and passing values explicitly).
- Cell logic must not be excessively long:
    - a single cell must contain only one complex execution
    - split cells to improve traceability and avoid re-running costly succeeded steps
- Every notebook must include:
    - a cleanup section at the end that frees cache memory
    - a flag to ignore checkpoints and trigger a full recalculation
- Every specific implementation detail must be covered and documented in notebooks, not in `src/`.

#### 9.2 Required cell order

1) **Code**: autoreload and exclude the config loader from autoreload.
2) **Code**: all imports + `config, logger = init_notebook(__name__)`.
3) **Markdown**: intro (title, purpose, Mermaid, collapsible I/O).

4+) alternating markdown `####` sections + code cells.

Do not place a large markdown title before the autoreload cell. The first executable cell must be autoreload so “Run all” behaves consistently.

#### 9.3 Autoreload and config loader exclusion (cell 1)

```python
%load_ext autoreload
%autoreload 2
%aimport -config.loader
```

Exclude the Pydantic config loader from autoreload to avoid subtle cache/model reload issues. Adjust the module path if your project uses a different package name.

#### 9.4 Initialization (cell 2)

Cell 2 should include all notebook imports and end with:

```python
config, logger = init_notebook(__name__)
```

`init_notebook` should `load_dotenv()`, load YAML into a typed config, and return a logger. Do not duplicate dotenv loading across extra cells unless you have a documented exception.

Do not split imports across many cells unless a later cell is clearly optional.

#### 9.5 Headings (required)

- Notebook title uses `###` (not `#`).
- Use `#### Section name` for steps.
- Use sentence-style short names (avoid numbered headings unless the repo is standardized on them).
- Exploratory notebooks may add a final `#### Notes`, `#### Alternatives`, or `#### References` section.

#### 9.6 Intro markdown (cell 3) requirements

- Title line: `### Human-readable notebook title`
- 1–2 short paragraphs: what it does, what it reads, what it writes.
- Mermaid diagram:
    - use `flowchart LR` (or similar)
    - **no spaces in node IDs**
    - quote edge labels containing parentheses, commas, or brackets
    - avoid HTML in labels
- Collapsible I/O block:

```markdown
<details>
<summary>Notebook I/O</summary>

> **Config:** YAML keys/sections this notebook uses.
>
> **Parameters:** uppercase knobs defined in the notebook.
>
> **Input:** … (paths, tables, upstream notebook links)
>
> **Output:** … (artifacts, figures, in-memory objects)

</details>
```

Use relative links to notebooks, config, and docs where applicable.
Reference environment variables by **name only** and point readers to `.env.example` rather than any real `.env` values.

#### 9.7 Config vs secrets (required to state)

- **YAML**: non-secret knobs, paths, model IDs, schema/table/column lists.
- **`.env`**: credentials and environment-specific endpoints.

In the notebook’s `#### Configuration` section, explicitly state:

- which YAML keys apply
- which env vars apply (names only)

#### 9.8 Logging in notebooks

- Use the shared logger from `init_notebook`.
- Avoid `print` for operational messages in pipeline notebooks.
    - `print` is acceptable for quick exploratory tables/summaries when it improves readability.

#### 9.9 Folder-level `README.md`

Each `notebooks/<module>/` directory should contain a README describing:

- execution order
- inputs/outputs
- relevant config keys and env vars

It may also hold pipeline-wide Mermaid diagrams and file naming tables so individual notebooks stay shorter.

#### 9.10 Pre-PR checklist (notebooks)

- [ ] First cell is autoreload + loader excluded.
- [ ] Second cell: imports + `init_notebook`.
- [ ] Third cell: `###` title + Mermaid + `<details>` I/O.
- [ ] Sections use `#### …`; config/secrets split documented.
- [ ] Folder README updated if the module story changed.

#### 9.11 Notebook metadata and kernel expectations

- Prefer an `nbformat` compatible with the team’s JupyterLab version.
- Avoid hand-editing notebook JSON unless necessary.
- Document the expected environment/kernel in the repo README (for example, Python version and the install steps used by the team).

---

### 10) Charts & visualizations (required)

Before each visualization, include a short markdown block covering:

- **What it shows** and how to interpret it
- **Ideal values** (what “good” looks like)
- **Bad values** (what indicates a problem)
- **Simple example** that any profile can understand

Structural rules:

- Each visualization must be defined in its own cell (or dedicated small group of cells).
- Never include more than one visualization calculation or definition in a single cell.
- Use colors/formatting to improve readability and contrast.

Escalation rule:

- If visualization logic is too complex for a notebook cell, move it to `src/charts/<submodule>/` and keep the notebook cell as thin orchestration.

---

### 11) Config file (`config/*.yaml`) quality rules

- The config file must contain **only** the parameters used by notebooks or `src` for execution.
- Never include sensitive information in YAML — secrets belong in `.env`.
- Never use the config file for variable definitions. Add only what is strictly needed.
- Never define long strings like prompts in the config file.
- Section naming must be clear, descriptive, and reflect where those values will be used (examples: `database`, `llm`, `keywords`).
- Add multiple sections only when a single generic section does not cover all required scenarios (example: different LLM temperatures per use case).
- Highly specific or experimental values belong in the notebook, not in the config.

---