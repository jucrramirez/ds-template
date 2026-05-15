# Documentation Guidelines

Guidelines for writing documentation, including READMEs, notebook markdown cells, and Python docstrings.

## 0. Response Rules (Meta)
- Always follow **all rules** in this document. When in doubt, ask.
- Be concise. Return only what is requested unless an explanation is necessary.
- Use precise language. Avoid vague verbs like "handle", "process", or "manage" — prefer "validate", "parse", "emit", "return".
- If a rule conflicts with a user request, apply the rule and explain why.

## 1. Docstrings (Python Modules, Classes, Functions)
- **Module-level**: Every script needs a brief summary docstring at the top.
- **Google Format**: Every class, function, and method must use Google-format docstrings, including a brief usage example.
- **[SUGGESTION]** Adhere to PEP 257 (e.g., use triple double quotes `"""`, include a summary line, a blank line, and a broader description).
- **[SUGGESTION]** Ensure internal `_methods` have at least a brief explanation if their purpose isn't immediately obvious.

**Example:**
```python
def compute_similarity(*, text_a: str, text_b: str) -> float:
    """Computes cosine similarity between two text strings.

    Args:
        text_a: First input string.
        text_b: Second input string.

    Returns:
        A float between 0 and 1 representing similarity.

    Example:
        score = compute_similarity(text_a="hello world", text_b="hello")
    """
```

## 2. Notebook Documentation Cells
### Intro Markdown Cell (Required)
The third cell of every notebook must be the intro markdown:
```markdown
### Human-readable notebook title

1–2 short paragraphs: what it does, what it reads, what it writes.

flowchart LR
  InputData --> Transform --> Output

<details>
<summary>Notebook I/O</summary>

> **Config:** YAML keys/sections this notebook uses.
>
> **Parameters:** uppercase knobs defined in the notebook.
>
> **Input:** tables/files/APIs consumed (and upstream notebook link if relevant).
>
> **Output:** artifacts produced (paths under files/) or tables written.

</details>
```

### Section Markdown
- Every notebook section must start with `#### Section name`.
- Must include a brief markdown summary of the process, including examples of transformations applied in that section.
- Specific implementation details must be documented in the notebook markdown, NOT in `src/`.

### Configuration Section
Include a `#### Configuration` section detailing:
- Applicable YAML keys.
- Applicable env var names (names only — never values).

### Charts and Visualizations
Before each visualization, add a markdown block explaining:
- **What it shows** and how to interpret.
- **Ideal values** ("good" state).
- **Bad values** ("problem").
- **A simple example** that anyone can understand, regardless of technical background.

## 3. Project & Folder Documentation
### Folder-level README (`notebooks/<module>/README.md`)
Each notebook module directory needs a README describing:
- Brief description of the module.
- Execution order.
- Expected data format and schema (for documents, tables, images, etc.) to enable other team members to use it without reverse-engineering the pipeline.
- Inputs and outputs.
- Relevant config keys and env var names (no values).
- Pipeline-wide Mermaid diagrams and file naming tables may be stored here to keep individual notebooks shorter.

### Repository README
- Document the expected environment and kernel (Python version, install steps).
- **[SUGGESTION]** Keep the root `README.md` regularly updated with any new dependencies or global setup instructions.

## 4. Self-Evaluation Checklist
- [ ] Google format docstrings used with usage examples.
- [ ] Notebooks contain standard I/O `<details>` blocks and Mermaid diagrams.
- [ ] Visualizations documented with good/bad value examples.
- [ ] Folder-level README created/updated for relevant modules.
