## Project template (uv + notebooks + src/)

This repository is a notebook-centric Python template that uses `uv` for dependency and environment management. It follows a thin-notebook approach: notebooks orchestrate execution while reusable logic lives in `src/`.

### Prerequisites

- `bash`
- `uv`
  - macOS (Homebrew): `brew install uv`
  - macOS / Linux / WSL: `curl -LsSf "https://astral.sh/uv/install.sh" | sh`
- `rsync`

### Initialize a new project

From the template root:

```bash
bash scripts/init_project.sh
```

The initializer prompts for:

- project name
- Python version (used by `uv venv --python`)
- optional module selection (`llm`, `logger`, `serializer`)
- optional extra dependencies

### What the initializer does

- creates a new sibling directory named after your project
- copies the template into that directory (excluding local artifacts like `.git` and `.venv`)
- removes unselected optional modules (`src/llm`, `src/utils/logger`, `src/utils/serializer`)
- writes a new `pyproject.toml`
- creates `.venv`, installs dependencies, runs `uv lock` and `uv sync`

### Example run

```bash
$ bash scripts/init_project.sh
New project name (letters/digits/_/- only): churn-model
Python version for uv venv (e.g., 3.13): 3.13

Select modules to include in the project:
  1) LLM (includes generic pipelines and provider clients)
  2) Logger (custom logging setup)
  3) Serializer (CSV, parquet helpers, etc)
Enter module numbers to include (e.g. 1 2 3, leave empty for none): 1 2
Install extra packages (comma or space separated, leave empty to skip): jupyterlab polars
INFO: Template root: /home/you/Repos/ds-template
INFO: Creating new project directory from template:
INFO:   /home/you/Repos/ds-template
INFO: -> /home/you/Repos/churn-model
INFO: Now in new project: /home/you/Repos/churn-model
INFO: Writing pyproject.toml
INFO: Creating virtual environment with uv.
INFO: Adding core dependencies: pydantic python-dotenv tqdm langchain-core
INFO: Adding extra dependencies: jupyterlab polars
INFO: Locking and syncing environment.
INFO: Done.
```

### Environment variables

- `.env` is gitignored
- `.env.example` is committed as the safe template

After initialization:

```bash
cd ../<your-project-name>
cp .env.example .env
source .venv/bin/activate
```

### Project structure

- `config/`: versioned runtime configuration (YAML)
- `notebooks/`: orchestration, I/O coordination, and visualizations
- `src/config/`: config loading and typed schemas
- `src/utils/notebooks_setup/`: notebook bootstrap (`init_notebook`, storage setup)
- `src/utils/logger/`: logging and progress utilities
- `src/utils/serializer/`: CSV/JSON/parquet/pickle helpers
- `src/llm/`: optional provider clients and LLM pipeline components
- `files/`: local `datasets/`, `tmp/`, and `exports/` outputs
- `docs/`: coding and notebook rules

For coding and notebook standards, see `docs/agent_rules.md`.