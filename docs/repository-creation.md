## Repository creation standard (notebook-centric data pipelines)

This document defines a reusable standard for creating a **notebook-driven, config-driven Python repository** that keeps notebooks consistent, code reusable, configuration validated, and secrets safe.

This is intended to be a **copy/adapt checklist** for new repositories (not a domain-specific pipeline manual).

---

### Goals (why this standard exists)

- **Consistency**: predictable repo structure across projects (Python layout, configs, notebooks, artifacts, scripts).
- **Onboarding**: contributors quickly find “where things live” and how notebooks relate to library code.
- **Safety**: secrets never enter git; heavy artifacts stay out of version control while paths remain documented.
- **Reproducibility**: a kernel restart + “run all” produces the same logical outcome (given identical data and environment).

---

### Core principles (non‑negotiable)

- **Single source of truth for behavior**: runtime knobs live in **versioned configuration** (YAML or similar), not scattered as hardcoded strings across notebooks.
- **Thin notebooks, fat libraries**: notebooks **sequence** steps and set parameters; reusable logic lives in importable `src/` packages.
- **Safe handling of secrets**: credentials and environment-specific endpoints come from **environment variables** (e.g., `.env`), never committed.
- **Controlled data footprint**: large outputs go to dedicated directories (e.g., `files/`) and are excluded from version control by pattern.

---

### Repository template tree (recommended “standard” layout)

Use this as the target structure for new repos. Names are examples—adapt domain packages, but keep the boundaries.

```text
<repo-root>/
├── README.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env.example
├── docs/
│   ├── repository-creation.md
│   ├── code-quality.md
│   └── <project-docs>.md
├── config/
│   └── pipeline_config.yaml
├── src/
│   ├── config/                 # YAML loader + Pydantic models + path helpers
│   │   ├── loader.py
│   │   └── models.py
│   ├── utils/                  # notebook bootstrap helpers (e.g., init_notebook)
│   │   └── notebook_init.py
│   ├── logger/                 # shared logging configuration + progress utilities
│   ├── serializer/             # consistent read/write helpers (parquet/json/csv/...)
│   ├── batch/                  # retries, checkpoints, failure lists, refresh hooks
│   ├── db/                     # db client, query helpers, inserts
│   ├── cloud/                  # aws/sdk clients (or aws/ depending on your naming)
│   ├── llm/                    # LLM callers, structured outputs, observability hooks
│   ├── embeddings/             # embeddings callers + batching
│   ├── transforms/             # reusable transforms/normalization
│   └── <domain>/               # domain-specific modules (keep them separated)
├── notebooks/
│   ├── pipeline/               # ordered stages (often numeric prefixes)
│   │   ├── README.md
│   │   ├── 00_<stage>.ipynb
│   │   └── ...
│   ├── validation/             # smoke tests / evaluations
│   │   └── ...
│   └── exploratory/            # optional; policy is team-specific
├── files/
│   ├── datasets/
│   ├── tmp/
│   └── exports/
├── scripts/
│   ├── setup_<env>.sh          # optional: runtime + kernel + cloud profile setup
│   └── db_bridge.sh            # optional: kubectl port-forward / tunnels
└── templates/
    └── notebook_template.ipynb
```

---

### This template repository (current structure)

This tree reflects what currently exists in this template repo (use it as the “starting point”, then fill in the missing standard files as your project matures).

```text
project-template/
├── .env.example
├── config/
│   └── pipeline_config.yaml
├── docs/
├── files/
│   ├── datasets/
│   ├── exports/
│   └── tmp/
├── notebooks/
├── scripts/
├── src/
│   └── utils/
└── templates/
    └── notebook_template.ipynb
```

---

### Stack and tooling (baseline)

- **Python**: set `requires-python >= 3.12` in `pyproject.toml`.
- **Dependencies**: use **uv** (`uv sync`) .
- **Notebooks**: use **JupyterLab** (or a managed studio equivalent) as the primary interactive surface when the project is notebook-driven.
- **Dataframes**: prefer **Polars** over pandas for tabular ETL.
- **Packaging `src/`**:
    - If notebooks import project code as packages, configure an installable package surface (ADD uses **Hatch** and an explicit wheel package list).
    - Register packages only when real modules exist—**avoid empty wheel config**.
    - Prefer editable installs from the repo root to avoid `sys.path` hacks in notebooks.
    - Keep import paths aligned with directory layout so IDEs and type checkers behave consistently.

---

### Bootstrap checklist (step-by-step)

#### 1) Repository skeleton

- [ ] Create the project directory.
- [ ] Initialize version control (`git init` or equivalent).
- [ ] Add root **`README.md`** (purpose, prerequisites, install/run steps, pointers to `docs/`).
- [ ] Create top-level folders: `src/`, `config/`, `notebooks/`, `files/`, `scripts/`, `docs/`, `templates/`.

#### 2) Python environment and packaging

- [ ] Add **`pyproject.toml`**:

  - project metadata (name, description)
  - `requires-python`
  - runtime dependencies
  - build backend (e.g. Hatchling)
  - optional explicit package list if you ship only part of `src/`
- [ ] Generate and commit a **lockfile** (e.g. `uv.lock`) if your team uses one.
- [ ] Document how to create a virtual environment and install the repo in **editable** mode so `import ...` works in Jupyter.
- [ ] Pin/install a Jupyter frontend (e.g. JupyterLab) if notebooks are first-class.

#### 3) Ignore rules and artifacts policy

- [ ] Add `.gitignore` rules for:

  - `.env` (and `.env.local` if used)
  - virtual environments
  - notebook checkpoints (`.ipynb_checkpoints`)
  - build artifacts
  - large artifacts under `files/` (parquet, tmp, exports), as adopted
- [ ] If an empty directory must exist in git, add a placeholder (`README` or `.gitkeep`).

#### 4) Secrets and environment variables

- [ ] Never commit `.env`. Ensure it is ignored.
- [ ] Commit **`.env.example`**:

  - same variable names as `.env`
  - placeholder values only
  - short comments; **no real credentials**
- [ ] Document in the README how teammates obtain a filled `.env` via a secure channel (not chat logs).
- [ ] Load `.env` via `python-dotenv` (`load_dotenv()`) from the project root, typically inside notebook initialization.

#### 5) Configuration (YAML + validation)

- [ ] Create a default config (YAML preferred) under `config/` for **non-secret** settings:

  - paths and storage-relative directories
  - schema/table/column lists
  - aggregation keys
  - model IDs and non-secret knobs
  - batch/concurrency settings
- [ ] Implement a loader under `src/config/` that parses YAML into **validated models** (Pydantic or similar) and fails fast with clear errors.
- [ ] Add helpers that resolve configured relative paths against the **project root** (local and SageMaker/CI should behave the same).
- [ ] Document how to use an alternate config file with the same schema (e.g. `config_path=...`).

#### 6) Library code under `src/`

- [ ] Split responsibilities into packages (create only what you need initially):

  - `config/` (loader + models)
  - external clients (`db/`, `cloud/`)
  - `batch/` (retries, checkpoints)
  - serializers
  - `logger/`
  - `utils/` including a shared `init_notebook`
  - domain transforms
- [ ] Keep notebooks thin as logic stabilizes—move reusable logic from cells into `src/`.
- [ ] Add an `ensure_storage_dirs()` helper if notebooks must create `datasets/tmp/exports` automatically.
- [ ] Design for safe reruns early (especially if jobs are expensive):

  - idempotent stages where possible
  - checkpointed or dated outputs so reruns are safe
  - clear separation of IO and pure transforms (pure transforms are easier to test)

#### 7) Notebooks (required structure)

- [ ] Create `notebooks/pipeline/` (or `stages/`) for ordered steps.
- [ ] Create `notebooks/validation/` for smoke tests/evaluation notebooks.
- [ ] Add a README beside each major notebook folder (`notebooks/<module>/README.md`) with:

  - execution order
  - I/O summary
  - relevant config keys and env vars (names only)
  - optional: pipeline-wide Mermaid diagrams and file naming tables so individual notebooks stay shorter
- [ ] Start new notebooks from `templates/notebook_template.ipynb`.
- [ ] Decide how to handle exploratory/one-off notebooks (tracked vs gitignored; review expectations) and document the policy.

#### 8) Scripts and operations (optional)

- [ ] Add `scripts/` for repeated setup (dependency installs, kernel registration, cloud SSO hints, tunnels).
- [ ] Use clear section headers and fail-fast shell options (e.g. `set -e` in bash).
- [ ] Document required tools (`kubectl`, AWS CLI, SSO setup, etc.) in the README.

#### 9) Quality and collaboration (optional but recommended)

- [ ] Add formatter/linter configuration (e.g. Ruff) if the team uses it.
- [ ] Add minimal tests for pure functions in `src/` once logic grows beyond notebooks.
- [ ] Define branch/review policy for changes to **config** and **pipeline notebooks** that affect production behavior.

#### 10) First milestone (prove the template works)

- [ ] One end-to-end path: install env → load config → run the first notebook → produce an artifact under the agreed directory.
- [ ] Update `README.md` with the exact commands used.

---

### Secrets vs configuration (repeatable rule)

- **`.env`**: secrets + environment-specific endpoints (never committed).
- **YAML under `config/`**: non-secret knobs, paths, model IDs, schema/table/column lists, feature flags.

**Never** store secrets in YAML. **Never** store long prompt strings in YAML.

---

### Configuration discipline (repeatable rule)

- Prefer a **single YAML** file (or a small, documented set) for non-secret parameters.
- Do not hardcode values that belong in YAML—change YAML once, then reload.
- Config is commonly loaded once per process:
    - after editing YAML, **restart the Jupyter kernel** and re-run from the top
    - after editing the config loader module (Pydantic models), **restart the kernel** (autoreload is unreliable for model definitions)
- If your loader caches configuration, document how to reset that cache for advanced multi-config workflows; the default expectation is to restart the kernel/process.

---

### Notebook conventions (required)

#### Cell order (required)

1) **Code**: autoreload and exclude the config loader from autoreload.
2) **Code**: all imports + `config, logger = init_notebook(__name__)`.
3) **Markdown**: intro (title, purpose, Mermaid diagram, collapsible I/O).

4+) alternating markdown `####` sections + code cells.

**Do not** place a large markdown title before the autoreload cell. The first executable cell must be autoreload so “Run all” behaves consistently.

#### Autoreload + config loader exclusion (first cell)

```python
%load_ext autoreload
%autoreload 2
%aimport -config.loader  # adjust to match your project’s loader module path
```

Reason: Pydantic config models and cached config do not always hot-reload cleanly; excluding the loader avoids subtle bugs.

#### Initialization (second cell)

Use a single initializer (e.g. `init_notebook(__name__)`) that:

- loads `.env`
- loads and validates YAML into a typed config object
- returns a shared logger

Avoid duplicating `load_dotenv()` across multiple cells unless you have a documented exception.

Keep all notebook imports in this second cell; do not split imports across many cells unless a later cell is clearly optional.

#### Parameters / knobs (recommended)

- Define user-tunable parameters as **uppercase** variables near the top of the relevant section (or in a dedicated parameters cell), for example `DATA_SOURCE`, `SAMPLE_SIZE`, feature flags.
- Prefer reading defaults and lists from `config` (YAML) rather than duplicating them inline.

#### Notebook headings

- Use `###` for the notebook title (in the intro markdown cell), not `#`.
- Use `#### Section name` for step sections (Configuration, Load, Transform, Save, Validation, …).
- Prefer sentence-style short names; avoid numbering unless the repo standardizes on it for long linear pipelines.
- Exploratory notebooks may add a final `#### Notes`, `#### Alternatives`, or `#### References` section.

#### Intro markdown (third cell)

- Title line: `### Human-readable notebook title`
- 1–2 short paragraphs: what it does, what it reads, what it writes.
- Mermaid diagram:
    - use `flowchart LR` (or similar)
    - **no spaces in node IDs**
    - quote edge labels that contain parentheses, commas, or brackets
    - avoid HTML in labels
- Collapsible I/O block:

```markdown
<details>
<summary>Notebook I/O</summary>

> **Config:** YAML keys / sections this notebook uses.
>
> **Parameters:** uppercase knobs defined in the notebook.
>
> **Input:** tables/files/APIs consumed (and upstream notebook link if relevant).
>
> **Output:** artifacts produced (paths under `files/`) or tables written.

</details>
```

Use **relative links** where applicable (upstream notebooks, module README, config file). Reference environment variables by **name only** and point to `.env.example` rather than any real `.env` values.

#### Logging

- Prefer the shared logger (`logger.info(...)`) for operational messages so output matches CLI formatting.
- Use a shared logging configuration so notebook output matches CLI output (standard format: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`).
- Avoid `print` for pipeline-style logging (fine for quick exploratory displays).

#### Kernel restart rule (repeatable)

After changing **YAML** or the **config loader** code, **restart the kernel** and re-run from the top.

#### Notebook metadata and kernel expectations

- Prefer an `nbformat` compatible with the team’s JupyterLab version.
- Avoid hand-editing notebook JSON unless necessary.
- Document the expected environment/kernel in the repo `README.md` (for example, Python version and the team’s install steps).

---

### Charts and visualizations (required notebook standard)

- Each visualization must be preceded by a short description that includes:
    - what it shows and how to interpret it
    - ideal values and “bad” values (thresholds, colors, ranges)
    - a simple example a non-specialist can understand
- Each visualization must be defined in its **own cell (or a dedicated small group of cells)**.
    - Never include more than one visualization calculation/definition in a single cell.
- If visualization logic becomes too complex for a notebook cell, move it to `src/charts/<submodule>/` and keep the notebook focused on orchestration.

---

### Artifacts, storage, and path rules

- Use a structured artifact root (example: `files/datasets`, `files/tmp`, `files/exports`) and document meanings in README and config.
- Gitignore large generated files (e.g. `*.parquet`, `files/tmp/**`, exports) but keep predictable directory structure (placeholders allowed).
- Prefer **relative paths** resolved from the project root so local, SageMaker, and CI behave the same.

---

### Scripts and optional operations (AWS / EKS / DB)

Not every project needs this. When you do need parity with an existing ADD-style setup:

- Prefer copying and adapting known-good scripts (update project name, kernel name, env validation blocks) rather than reinventing.
- Typical utilities:
    - `setup_*.sh`: uv, kubectl, AWS SSO/profile wiring, kubeconfig, Jupyter kernel registration, shell aliases
    - `db_bridge.sh`: kubectl port-forward for PostgreSQL

---

### Troubleshooting quick reference

| Symptom                               | What to check                                                               |
| ------------------------------------- | --------------------------------------------------------------------------- |
| Expired AWS token                     | Re-run SSO login/refresh; long jobs may need a `refresh_fn` on API clients. |
| Pydantic `ValidationError` at startup | YAML shape vs models; missing required sections.                            |
| DB connection errors                  | Port-forward running? SSO valid? `.env` host/port correct?                  |
| Stale config in notebook              | Restart kernel after YAML or loader changes.                                |
| Missing parquet / inputs              | Upstream notebook not run; wrong date suffix; path in config.               |
| Rate limits                           | Lower concurrency/batch size; add backoff in batch layer.                   |
| OOM                                   | Smaller chunks; larger instance; clear large frames between steps.          |
| Resume after interrupt                | Checkpoint-aware code paths; rerun from top to skip completed work.         |

---

### Docs policy (tracked vs local)

- Decide explicitly whether `docs/` is **versioned** (recommended for standards and runbooks) or treated as local notes.
- Avoid a blanket `docs/*` ignore unless you intentionally want docs untracked and have an alternative place for versioned documentation.

---