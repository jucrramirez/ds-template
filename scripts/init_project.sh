#!/usr/bin/env bash
set -Eeuo pipefail

on_error() {
  local exit_code="$1"
  local line_no="$2"
  local cmd="$3"
  printf '\nERROR: command failed (exit=%s) at line %s\n  %s\n\n' "$exit_code" "$line_no" "$cmd" >&2
}

trap 'on_error "$?" "$LINENO" "$BASH_COMMAND"' ERR

info() { printf '%s\n' "INFO: $*"; }
warn() { printf '%s\n' "WARN: $*" >&2; }
die()  { printf '%s\n' "ERROR: $*" >&2; exit 1; }

require_cmd() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

prompt_nonempty() {
  local __var_name="$1"
  local __msg="$2"
  local __value=""
  while [[ -z "$__value" ]]; do
    read -r -p "$__msg" __value
  done
  printf -v "$__var_name" '%s' "$__value"
}

prompt_optional() {
  local __var_name="$1"
  local __msg="$2"
  local __value=""
  read -r -p "$__msg" __value || true
  printf -v "$__var_name" '%s' "$__value"
}

is_valid_project_name() {
  # folder + PEP 621 name safe enough for bootstrapping
  [[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]
}

is_valid_python_version() {
  # Accept 3.13 or 3.13.1
  [[ "$1" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]
}

write_file_if_missing() {
  local path="$1"
  local content="$2"
  if [[ -f "$path" ]]; then
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$content" > "$path"
}

normalize_installation_list() {
  local raw="$1"
  local normalized=""
  local item=""

  # Accept comma and/or whitespace separated package names.
  raw="${raw//,/ }"
  for item in $raw; do
    if [[ -z "$normalized" ]]; then
      normalized="$item"
    else
      normalized="${normalized} ${item}"
    fi
  done

  printf '%s' "$normalized"
}

main() {
  require_cmd uv
  require_cmd rsync

  local script_dir repo_root parent_dir target_root
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
  repo_root="$(cd "${script_dir}/.." && pwd -P)"

  cd "$repo_root"
  info "Template root: $repo_root"

  local project_name python_version installations install_packages

  while true; do
    prompt_nonempty project_name "New project name (letters/digits/_/- only): "
    if is_valid_project_name "$project_name"; then
      break
    fi
    warn "Invalid name. Use only letters, digits, '_' or '-', starting with a letter/digit."
  done

  while true; do
    prompt_nonempty python_version "Python version for uv venv (e.g., 3.13): "
    if is_valid_python_version "$python_version"; then
      break
    fi
    warn "Invalid version. Examples: 3.13 or 3.13.1"
  done

  # Module selection
  printf '\nSelect modules to include in the project:\n'
  printf '  1) LLM (includes generic pipelines and provider clients)\n'
  printf '  2) Logger (custom logging setup)\n'
  printf '  3) Serializer (CSV, parquet helpers, etc)\n'
  
  local module_input
  prompt_optional module_input "Enter module numbers to include (e.g. 1 2 3, leave empty for none): "
  
  local include_llm=false
  local include_logger=false
  local include_serializer=false
  
  for num in $module_input; do
    case "$num" in
      1) include_llm=true ;;
      2) include_logger=true ;;
      3) include_serializer=true ;;
      *) warn "Unknown module number: $num — skipping." ;;
    esac
  done

  prompt_optional installations "Install extra packages (comma or space separated, leave empty to skip): "
  install_packages="$(normalize_installation_list "$installations")"

  parent_dir="$(dirname "$repo_root")"
  target_root="${parent_dir}/${project_name}"

  [[ -e "$target_root" ]] && die "Target directory already exists: $target_root"

  info "Creating new project directory from template:"
  info "  $repo_root"
  info "-> $target_root"
  mkdir -p "$target_root"

  # Copy template contents into the new project, excluding local/runtime artifacts.
  rsync -a \
    --exclude ".git/" \
    --exclude ".venv/" \
    --exclude "__pycache__/" \
    --exclude ".pytest_cache/" \
    --exclude ".mypy_cache/" \
    --exclude ".ruff_cache/" \
    --exclude ".ipynb_checkpoints/" \
    --exclude "*.pyc" \
    --exclude ".DS_Store" \
    "${repo_root}/" "${target_root}/"

  cd "$target_root"
  info "Now in new project: $target_root"

  # Remove unselected modules
  if [[ "$include_llm" == false ]]; then
    rm -rf "src/llm"
  fi
  if [[ "$include_logger" == false ]]; then
    rm -rf "src/utils/logger"
  fi
  if [[ "$include_serializer" == false ]]; then
    rm -rf "src/utils/serializer"
  fi

  # Ensure core src packages exist for notebook imports.
  mkdir -p "src/config" "src/utils"
  write_file_if_missing "src/config/__init__.py" '"""Configuration package (YAML loader + settings models)."""'
  write_file_if_missing "src/utils/__init__.py"  '"""Utility package (notebook bootstrap, helpers, etc.)."""'

  # Ensure key directories exist + placeholders for git.
  mkdir -p "notebooks/pipeline" "notebooks/validation" "files/datasets" "files/tmp" "files/exports"
  write_file_if_missing "notebooks/pipeline/.gitkeep"   "placeholder"
  write_file_if_missing "notebooks/validation/.gitkeep" "placeholder"
  write_file_if_missing "files/datasets/.gitkeep"       "placeholder"
  write_file_if_missing "files/tmp/.gitkeep"            "placeholder"
  write_file_if_missing "files/exports/.gitkeep"        "placeholder"

  # Ensure README exists (pyproject references it).
  if [[ ! -f "README.md" ]]; then
    printf '## %s\n\nInitialized with uv. See `scripts/init_project.sh` for bootstrap behavior.\n' \
      "$project_name" > "README.md"
  fi

  if [[ -f "pyproject.toml" ]]; then
    die "pyproject.toml already exists. Refusing to overwrite."
  fi

  info "Writing pyproject.toml"

  # Build the packages array
  local packages_array='"src/config", "src/utils"'
  [[ "$include_llm" == true ]] && packages_array+=', "src/llm"'

  cat > "pyproject.toml" << PYPROJECT
[project]
name = "${project_name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=${python_version}"
dependencies = []

PYPROJECT

  # Optional dependencies for LLM providers
  if [[ "$include_llm" == true ]]; then
    cat >> "pyproject.toml" << PYPROJECT
[project.optional-dependencies]
aws = ["langchain-aws>=0.1.0", "boto3>=1.34.0"]
gemini = ["langchain-google-genai>=1.0.0"]
openai = ["langchain-openai>=0.1.0"]
azure = ["langchain-openai>=0.1.0"]
ollama = ["langchain-ollama>=0.1.0"]

PYPROJECT
  fi

  cat >> "pyproject.toml" << PYPROJECT
[build-system]
requires = ["hatchling>=1.25.0"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = [${packages_array}]
PYPROJECT

  if [[ -d ".venv" ]]; then
    die ".venv already exists. Refusing to overwrite."
  fi

  info "Creating virtual environment with uv."
  uv venv --python "$python_version"

  # Always install core dependencies.
  local core_deps="pydantic python-dotenv tqdm"
  [[ "$include_llm" == true ]] && core_deps="${core_deps} langchain-core"
  
  info "Adding core dependencies: $core_deps"
  # shellcheck disable=SC2086
  uv add $core_deps

  # We no longer prompt to immediately install the provider deps here 
  # since we added them to [project.optional-dependencies]
  if [[ "$include_llm" == true ]]; then
    info "LLM module included. Optional provider dependencies (aws, gemini, openai, azure, ollama) can be installed via uv sync --extra <provider>"
  fi

  if [[ -n "$install_packages" ]]; then
    info "Adding extra dependencies: $install_packages"
    # shellcheck disable=SC2086
    uv add $install_packages
  fi

  info "Locking and syncing environment."
  uv lock
  uv sync

  info "Done."
  printf '\nNext steps:\n' >&2
  [[ -f ".env.example" ]] && printf '  - Copy env:   cp .env.example .env  # then fill values\n' >&2
  printf '  - Activate:   source .venv/bin/activate\n' >&2
  if [[ "$include_llm" == true ]]; then
    printf '  - Providers:  uv sync --extra aws (or gemini, openai, azure, ollama)\n' >&2
  fi
  printf '  - Jupyter:    jupyter lab\n\n' >&2
  
  printf 'Project successfully created at:\n' >&2
  printf '\033[1;32m%s\033[0m\n\n' "$target_root" >&2
}

main "$@"