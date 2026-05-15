# Notebook Guidelines

Guidelines for generating, refactoring, or editing ONLY notebooks.

## 0. Response Rules (Meta)
- Always follow **all rules** in this document. When in doubt, ask.
- Be concise. Return only what is requested unless an explanation is necessary.
- Use precise language. Avoid vague verbs like "handle", "process", or "manage" — prefer "validate", "parse", "emit", "return".
- If a rule conflicts with a user request, apply the rule and explain why.

## 1. Core Principles
- **Thin notebooks, fat libraries**: Notebooks sequence steps and set parameters; reusable logic lives in `src/`.
- **Single source of truth**: Runtime knobs live in versioned YAML config — not hardcoded.
- **Secrets stay out of git**: Credentials come from `.env`, never from YAML or code.
- **Controlled data footprint**: Large outputs go to `files/datasets/`, `files/tmp/`, or `files/exports/`, and are excluded from version control.

## 2. Notebook Required Structure
### Kernel Restart Rule
After changing YAML or config loader/Pydantic models, always restart the kernel and re-run from the top. Autoreload is unreliable for config models.

### Required Cell Order
Every notebook must follow this exact order:

**Cell 1 — Autoreload:**
```python
%load_ext autoreload
%autoreload 2
%aimport -config.loader
```
*Note: Excluding the config loader prevents cache/model reload bugs.*

**Cell 2 — Imports and Initialization:**
```python
# All notebook imports go here
from config.loader import init_notebook

config, logger = init_notebook(__name__)
```
*Note: `init_notebook` must call `load_dotenv()`, parse YAML config, and return a logger. Do not split imports across many cells unless optional.*
- **[SUGGESTION]** Organize imports strictly into standard library, third-party packages, and local modules (PEP 8).

**Cell 3 — Intro Markdown:**
```markdown
### Human-readable notebook title

1–2 short paragraphs: what it does, what reads, what writes.

flowchart LR
  InputData --> Transform --> Output

<details>
<summary>Notebook I/O</summary>

> **Config:** YAML keys/sections used.
> **Parameters:** uppercase knobs defined in notebook.
> **Input:** tables/files/APIs consumed.
> **Output:** artifacts produced under files/.

</details>
```

**Cells 4+:** Alternating `####` section markdown cells and focused code cells. *Do not place a large markdown title before the autoreload cell.*

## 3. General Notebook Rules
- A notebook's **only purpose** is to execute logic defined in `src/`. The only inline code allowed is charts/visualizations.
- `src/` must **never** read data directly. All inputs/parameters must be passed from the notebook.
- Never add hardcoded/default values in `src/`. Control values via notebook.
- Define user-tunable parameters as **uppercase** variables near the top of the relevant section (e.g., `DATA_SOURCE`). List them in the intro I/O block.
- A single cell must contain only one complex execution to improve traceability.
- Every notebook must include:
  - A **cleanup section** at the end to free cache memory.
  - A **flag to ignore checkpoints** for full recalculation.
- Prefer idempotent stages (write to dated/checkpointed outputs).
- Separate I/O from pure transforms.
- **[SUGGESTION]** Clear cell outputs before committing to reduce file size and avoid merge conflicts (or use `nbstripout`).
- **[SUGGESTION]** Do not suppress warnings without a clear explanatory comment.

## 4. Notebook Headings
- Notebook title uses `###` — not `#`.
- Step sections use `#### Section name` (sentence-style, unnumbered).
- Exploratory notebooks may add `#### Notes`, `#### Alternatives`, or `#### References` sections.

## 5. Configuration Section
In the `#### Configuration` section, explicitly state:
- Applicable YAML keys.
- Applicable env var names (names only — never values).

## 6. Charts and Visualizations
Before each visualization, include a short markdown block explaining:
- **What it shows** and interpretation.
- **Ideal values** ("good" state).
- **Bad values** (problem indicators).
- **A simple example** accessible to anyone.

**Structural rules:**
- Each visualization must be in its **own cell** (or a small dedicated group). Never combine multiple chart definitions in a single cell.
- Use colors/formatting for readability.
- Complex visualization logic must go to `src/charts/<submodule>/`.

## 7. Performance and Tooling
- **Memory-efficient**: Every process must be memory-efficient.
- **Progress tracking**: Use a progress bar showing succeeded, failed, remaining.
- **Logging**: Use the shared logger from `init_notebook`. **Avoid `print`** for operational messages (acceptable only for quick exploratory summaries).
- **Dataframes**: Prefer **Polars** over pandas.
- Notebooks use **JupyterLab** as the interactive surface.
- All package/environment management uses **uv**.
- Python: `>= 3.12`.

## 8. Self-Evaluation Checklist (Pre-PR)
- [ ] First cell is autoreload + loader excluded.
- [ ] Second cell: all imports + `init_notebook`.
- [ ] Third cell: `###` title + Mermaid + `<details>` I/O block.
- [ ] Sections use `#### …`; config/secrets split is documented.
- [ ] Folder README updated if module context changed.
- [ ] Cyclomatic complexity does not exceed 18.
- [ ] No secrets or hardcoded values are present.
