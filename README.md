## Project template (uv + notebooks + src/)

This repository is a notebook-centric Python template that uses `uv` for environment and dependency management. It promotes a "thin notebooks, fat libraries" approach where complex logic resides in reusable Python modules and notebooks are kept clean for execution and reporting.

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

### Project Structure & Modules

The repository follows a strict separation of concerns:

- **`config/`**: YAML files defining pipeline parameters and paths. Use this as the single source of truth for runtime configurations.
- **`notebooks/`**: Directory for Jupyter notebooks. Notebooks should be thin, mainly responsible for sequencing steps, I/O, and visualizations. Logic belongs in `src/`.
- **`src/`**: Core reusable logic.
  - **`config/`**: Contains the YAML loader and Pydantic schemas validating the configuration.
  - **`logger/`**: Centralized logging setup and progress bar utilities.
  - **`llm/`**: Modular LLM integration with providers (AWS, Azure, OpenAI, Gemini, Ollama) and protocols for generating embeddings and chat completions.
  - **`utils/`**: Helper scripts, including `notebooks_setup` to automatically load config, initialize loggers, and manage storage directories.
- **`files/`**: Local storage for `datasets/`, `tmp/`, and `exports/`. These are git-ignored to prevent data leaks.
- **`docs/`**: Project guidelines and coding standards.

### Adapting to Your Needs

To tailor this template to your project:
1. **Define Schemas**: Update `src/config/schemas.py` with the parameters your pipeline needs, and modify `config/config.yaml` accordingly.
2. **Develop Modules**: Add domain-specific Python packages in `src/`. For instance, you could add `src/data_processing` or `src/charts`. Ensure all code is typed and well-documented.
3. **Build Notebooks**: Create specialized notebooks in subfolders of `notebooks/`. Every notebook should utilize `init_notebook` from `src.utils.notebooks_setup` to start its environment. Keep logic out of the notebooks.
4. **Environment**: Add necessary credentials to `.env`. Manage dependencies entirely through `uv`.

### Important Considerations & Guidelines

- **Zero Data in Git**: Avoid committing any data files or output plots. Keep them in `files/` or your remote storage.
- **Type Annotations**: All modules in `src/` should be 100% type annotated.
- **Docstrings**: Maintain Google-format docstrings for all classes and functions.
- **Single Source of Truth**: All parameters should come from `config.yaml`, never hardcoded in scripts or notebooks.
- **Detailed Rules**: See the `.agents/rules/coding-rules.md` for comprehensive guidelines on notebook structure, coding practices, and performance constraints. 

### Template folder tracking

Empty template folders are kept in git via `.gitkeep` placeholders so the structure is preserved when cloning/creating new projects.