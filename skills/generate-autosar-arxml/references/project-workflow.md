# Project Workflow

## Repository identity

Confirm these files before operating:

- `pyproject.toml` with project name `arxml-codegen`
- `scripts/docx_to_contract.py`
- `scripts/run_codegen.ps1`
- `scripts/diff_against_golden.py`
- `src/arxml_codegen/`

## Environment check

Use the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -c "import arxml_codegen, docx, lxml, openpyxl, yaml"
```

If imports fail, report the environment problem. Do not rebuild or install packages unless the user asks to repair the environment.

Set `PYTHONPATH=src` only for direct module execution when the editable package is unavailable.

## Primary commands

Inspect CLI options instead of assuming they are unchanged:

```powershell
.\.venv\Scripts\python.exe scripts\docx_to_contract.py --help
.\.venv\Scripts\python.exe -m arxml_codegen.cli --help
```

Use `scripts/docx_to_contract.py` for DOCX-to-contract/Excel/ARXML jobs. Use `scripts/run_codegen.ps1` for an existing Excel plus project YAML job.

## Output layout

Use:

```text
output/
├─ deliverables/<project>/   final contract, Excel, reports, and ARXML
├─ validation/<project>/     golden diff artifacts
├─ references/<project>/     local reference ARXML
├─ drafts/<mode>/            incomplete extraction drafts
└─ temp/                     task-specific configurations and temporary inputs
```

Do not commit `output/`. Do not delete or overwrite unrelated existing output directories.

## Validation behavior

The DOCX pipeline blocks ARXML generation when any of these conditions exists:

- contract `OpenIssue` with status `open`;
- model validation error;
- CORE finding with severity `ERROR`.

The command returns exit code `1` for a blocked model even when contract, Excel, and reports were written successfully. Inspect artifacts before treating it as a program crash.

## Change boundaries

- Preserve user-owned DOCX and Excel files.
- Do not change project code during a review-only or diagnosis-only request.
- If code changes are requested, run targeted tests and then the full test suite in proportion to risk.
- Never modify a Developer-exported golden ARXML.
