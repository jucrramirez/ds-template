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
die() { printf '%s\n' "ERROR: $*" >&2; exit 1; }

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

prompt_yes_no() {
  local __var_name="$1"
  local __msg="$2"
  local __value=""
  read -r -p "$__msg" __value || true
  __value="$(printf '%s' "$__value" | tr '[:upper:]' '[:lower:]')"
  case "$__value" in
    y|yes) printf -v "$__var_name" 'yes' ;;
    *)     printf -v "$__var_name" 'no' ;;
  esac
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

main() {
  require_cmd uv

  local script_dir repo_root parent_dir current_dir_name target_dir_name target_root
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
  repo_root="$(cd "${script_dir}/.." && pwd -P)"

  cd "$repo_root"
  info "Repo root: $repo_root"

  local project_name python_version install_defaults

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

  prompt_yes_no install_defaults "Install default libraries (pydantic, jupyterlab)? [y/N]: "

  current_dir_name="$(basename "$repo_root")"
  target_dir_name="$project_name"
  parent_dir="$(dirname "$repo_root")"
  target_root="${parent_dir}/${target_dir_name}"

  if [[ "$current_dir_name" != "$target_dir_name" ]]; then
    [[ -e "$target_root" ]] && die "Target directory already exists: $target_root"
    info "Renaming project folder:"
    info "  $repo_root"
    info "→ $target_root"
    mv "$repo_root" "$target_root"

    repo_root="$target_root"
    cd "$repo_root"
    info "Now in: $repo_root"
  else
    info "Folder name already matches project name; no rename needed."
  fi

  # Ensure minimal src packages exist for notebook imports.
  mkdir -p "src/config" "src/utils"
  write_file_if_missing "src/config/__init__.py" '"""Configuration package (YAML loader + settings models)."""'
  write_file_if_missing "src/utils/__init__.py" '"""Utility package (notebook bootstrap, helpers, etc.)."""'

  # Ensure key directories exist + placeholders for git.
  mkdir -p "notebooks/pipeline" "notebooks/validation" "files/datasets" "files/tmp" "files/exports"
  write_file_if_missing "notebooks/pipeline/.gitkeep" "placeholder"
  write_file_if_missing "notebooks/validation/.gitkeep" "placeholder"
  write_file_if_missing "files/datasets/.gitkeep" "placeholder"
  write_file_if_missing "files/tmp/.gitkeep" "placeholder"
  write_file_if_missing "files/exports/.gitkeep" "placeholder"

  # Ensure README exists (pyproject references it).
  if [[ ! -f "README.md" ]]; then
    cat > "README.md" <<EOF
## ${project_name}

Initialized with uv. See \`scripts/init_project.sh\` for bootstrap behavior.
EOF
  fi

  if [[ -f "pyproject.toml" ]]; then
    die "pyproject.toml already exists. Refusing to overwrite."
  fi

  info "Writing pyproject.toml (Hatchling + explicit src packages for notebook imports)."
  cat > "pyproject.toml" <<EOF
[build-system]
requires = ["hatchling>=1.25.0"]
build-backend = "hatchling.build"

[project]
name = "${project_name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=${python_version}"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["src/config", "src/utils"]
EOF

  if [[ -d ".venv" ]]; then
    die ".venv already exists. Refusing to overwrite."
  fi

  info "Creating virtual environment with uv."
  uv venv --python "$python_version"

  if [[ "$install_defaults" == "yes" ]]; then
    info "Adding default dependencies: pydantic, jupyterlab"
    uv add pydantic jupyterlab
  else
    info "Skipping default dependencies."
  fi

  info "Locking and syncing environment (uv.lock will be gitignored)."
  uv lock
  uv sync

  info "Done."
  printf '\nNext steps:\n' >&2
  [[ -f ".env.example" ]] && printf '  - Copy env:   cp .env.example .env  # then fill values\n' >&2
  printf '  - Activate:   source .venv/bin/activate\n' >&2
  printf '  - Jupyter:    jupyter lab\n\n' >&2
}

main "$@"