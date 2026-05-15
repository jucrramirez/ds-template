# Complex Code Guidelines

Guidelines for adding or refactoring complex code (in `src/`, outside notebooks).

## 0. Response Rules (Meta)
- Always follow **all rules** in this document. When in doubt, ask.
- Be concise. Return only what is requested unless an explanation is necessary.
- Use precise language. Avoid vague verbs like "handle", "process", or "manage" — prefer "validate", "parse", "emit", "return".
- If a rule conflicts with a user request, apply the rule and explain why.

## 1. Core Principles
- **Fat libraries**: Reusable logic belongs in `src/`.
- **Single source of truth**: Runtime parameters live in versioned YAML config.
- **Secrets stay out of git**: Use `.env` for credentials.
- **No data reads in `src/`**: `src/` must **never** read data directly; notebooks pass data/parameters.

## 2. Project Structure & Placement
- Place definitions in the correct module/submodule under `src/`. Create one if needed.
- If existing code matches the new module's purpose, migrate it there.
- Align import paths with directory layout (e.g., `src/config/loader.py` -> `config.loader`).
- **LLM Prompts**: Belong in `src/` unless explicitly specified. Never in YAML.
- **Complex Charts**: Logic goes to `src/charts/<submodule>/` if it does not fit cleanly in a notebook cell.

## 3. Naming and Clarity
- Use **descriptive, purpose-driven names**.
- **Never use generic names** (`x`, `y`, `z`, `var`, `tmp`, `data`, `result`).
- Keep names **domain-agnostic**: Don't reference specific YAML keys, attributes, or sections.
- Avoid duplicate/redundant definitions.
- **No default values** for parameters unless explicitly requested (must be documented).
- Always use **keyword-only arguments** (use `*` separator in function definitions).
- **[SUGGESTION]** Limit line length to 88 or 100 characters for readability (e.g., Black/Ruff standard).
- **[SUGGESTION]** Avoid mutable default arguments in functions (use `None` instead).

## 4. Strict Type Annotations
- **100% type-annotated**: Every class, function, method, and variable.
- **Never use `Any`**.
- Explicitly bind and annotate return values if the type isn't obvious:
  ```python
  # Correct
  results: list[str] = process_items(items=batch, max_retries=3)
  
  # Incorrect
  results = process_items(batch, 3)
  ```

## 5. Classes, OOP, and Data Models
- Use **Pydantic**:
  - `BaseModel` for external data/config validation.
  - `@dataclass` for internal structured data with lightweight validation.
- Don't force OOP if it doesn't improve readability.
- Add Pydantic validators only when necessary; use `__post_init__` / `__post_init_post_parse` instead of `super().__init__`.
- **[SUGGESTION]** Use Python's `pathlib` for file path manipulation instead of `os.path` for robust cross-platform compatibility.

## 6. Performance, Safety, and Complexity
- Processes must be **memory-efficient**.
- **Cyclomatic complexity must never exceed 18.**
- Avoid `for` loops if vectorized/functional/time-efficient alternatives exist.
- Use `yield` for batching definitions.
- Avoid infinite loops.
- **[SUGGESTION]** Prefer list comprehensions or generator expressions over `for` loops for simple mapping/filtering.

## 7. External APIs and Resource-Intensive Processes
Must implement all of the following:
- **Exception handling**: Timeouts, rate limits ("Too Many Requests"), threading, exponential backoff, session expiry.
- **Retry logic** for failing items.
- **Checkpoints every N batches**: Save to `files/tmp/` efficiently. Delete after completion unless requested otherwise.
- **Real batching**: Aligned with upstream docs (e.g., max documents per request).

## 8. Logging
- Standard format: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`.
- Ensure CLI output matches notebook output via shared configuration.

## 9. Tooling & Environment
- **Python**: `>= 3.12`.
- **Dependencies & Environments**: Managed with **uv** (`uv sync`).
- **Dataframes**: Prefer **Polars** over pandas for tabular ETL.
- **Packaging**: Prefer editable installs from repo root.

## 10. Self-Evaluation Checklist
- [ ] All functions/variables 100% type-annotated; no `Any`.
- [ ] Uses Pydantic `BaseModel` or `@dataclass` appropriately.
- [ ] Keyword arguments used at call sites.
- [ ] No secrets or hardcoded values.
- [ ] Code properly modularized in `src/`.
- [ ] Complexity <= 18.
- [ ] API calls have retries, exceptions, and checkpoints.
