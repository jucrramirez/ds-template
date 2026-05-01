## Project template (uv + notebooks + src/)

This repository is a notebook-centric Python template that uses `uv` for environment and dependency management.

### Prerequisites

- `bash`
- `uv`
  - macOS (Homebrew): `brew install uv`
  - macOS / Linux / WSL (installer): `curl -LsSf "https://astral.sh/uv/install.sh" | sh`
- `rsync` (typically preinstalled on macOS/Linux)

### Initialize a new project

From this template repo root, run:

```bash
bash scripts/init_project.sh
```

The script asks for:

- Project name
- Python version (for `uv venv --python ...`)
- Installations (optional packages, comma or space separated)

### What the initializer does

- Creates a **new sibling directory** using your project name
- Copies this template into that new directory (without `.git`, `.venv`, caches, or OS artifacts)
- Runs initialization in the new project directory:
  - creates `pyproject.toml`
  - creates `.venv`
  - installs optional packages (if provided)
  - runs `uv lock` and `uv sync`

### Example run

```bash
$ bash scripts/init_project.sh
New project name (letters/digits/_/- only): churn-model
Python version for uv venv (e.g., 3.13): 3.13
Install packages (comma or space separated, leave empty to skip): pandas scikit-learn jupyterlab
INFO: Creating new project directory from template:
INFO:   /Users/you/Repos/ds-template
INFO: → /Users/you/Repos/churn-model
INFO: Now in new project: /Users/you/Repos/churn-model
INFO: Creating virtual environment with uv.
INFO: Adding dependencies: pandas scikit-learn jupyterlab
INFO: Locking and syncing environment.
INFO: Done.
```

Result: your initialized project is created at `../churn-model` (sibling of the template repository).

### Environment variables

- `.env` is ignored by git
- `.env.example` is tracked as the safe template

After initialization:

```bash
cd ../<your-project-name>
cp .env.example .env
source .venv/bin/activate
```

### Template folder tracking

Empty template folders are kept in git via `.gitkeep` placeholders so the structure is preserved when cloning/creating new projects.