---
name: generate-autosar-arxml
description: Operate the Generate-Arxml repository to inspect AUTOSAR Classic delivery DOCX or Excel inputs, extract canonical contracts, produce gap and validation reports, generate DaVinci Developer-compatible ARXML, compare generated output with a Developer-exported golden ARXML, and diagnose import failures. Use for signal, SOA, or mixed SWC/Composition delivery workflows and for project-specific ARXML generation or validation; do not use for AUTOSAR teaching or general DaVinci tutorials.
---

# Generate AUTOSAR ARXML

Use the repository as the deterministic execution engine. Use this skill only to operate, validate, and diagnose that workflow.

## Locate the repository

1. Prefer the current workspace when it contains both `pyproject.toml` with project name `arxml-codegen` and `scripts/docx_to_contract.py`.
2. Otherwise locate the repository before running commands.
3. Treat paths in this skill as relative to the repository root.
4. Use `.venv\Scripts\python.exe` when it exists. Do not silently install or upgrade dependencies.

Read [references/project-workflow.md](references/project-workflow.md) before executing commands.

## Respect the requested action

- For inspection or review, parse the supplied artifact and report issues without generating final ARXML.
- For diagnosis, identify the cause and affected rule without changing code unless the user requests a fix.
- For generation, run extraction, gap checking, validation, and ARXML generation in that order.
- For golden comparison, generate the semantic diff only after both ARXML inputs are identified.
- Never read or inject the DaVinci/AUTOSAR teaching handbook as part of this skill.

## Select the workflow

Inspect the document tables before choosing a profile.

- Use `--mode signal --profile signal_atomic_davinci` for a single Atomic SWC signal delivery.
- Use `--mode mixed --profile mixed_signal_soa` for multi-SWC S/R plus C/S, Composition, and Connector delivery.
- Use `--mode soa` only when the supplied contract is explicitly service-only and the requested output is supported.
- Honor an explicit user-selected mode or profile. If document content conflicts with it, report the conflict instead of silently switching.

Read [references/document-contract.md](references/document-contract.md) when reviewing or extracting DOCX input. Read [references/generation-rules.md](references/generation-rules.md) before accepting the generated model.

## Run the DOCX pipeline

Create a task-specific directory under `output/deliverables/<project>/`. Preserve the source document.

Run:

```powershell
.\.venv\Scripts\python.exe scripts\docx_to_contract.py --input "<input.docx>" --contract "<deliverable>/contract.json" --excel "<deliverable>/model.xlsx" --issues "<deliverable>/issues.md" --report-json "<deliverable>/issues.json" --arxml "<deliverable>/generated.arxml" --generation-report "<deliverable>/generation_report.md" --mode <mode> --profile <profile>
```

Interpret exit code `1` as a blocked contract/model when reports were produced. Read both issue reports. Do not bypass open issues, model validation errors, or CORE errors to force ARXML output.

If the user requested inspection only, omit `--arxml` and `--generation-report`.

## Run the Excel pipeline

For an existing configured workbook, run the dry run first:

```powershell
.\scripts\run_codegen.ps1 -Config "<config.yaml>" -DryRun
```

Run real generation only if the dry run and validation pass:

```powershell
.\scripts\run_codegen.ps1 -Config "<config.yaml>"
```

Do not overwrite `config/project.yaml` for a one-off job. Create a task-specific configuration under `output/temp/` when needed.

## Compare with a golden ARXML

Run:

```powershell
.\.venv\Scripts\python.exe scripts\diff_against_golden.py --generated "<generated.arxml>" --golden "<developer-export.arxml>" --report "<validation>/golden_diff.md" --json "<validation>/golden_diff.json"
```

Treat missing, extra, and mismatched items as review findings rather than automatically assuming the generated or golden side is wrong. Distinguish expected scope differences from generator defects.

## Enforce capability boundaries

Read [references/capability-matrix.md](references/capability-matrix.md) before promising output. Report unsupported features as blocking gaps. Do not approximate unsupported AUTOSAR constructs with S/R, C/S, or handwritten XML.

## Report the result

Return:

1. Selected mode and profile.
2. Input artifact and output directory.
3. Counts of open issues, model errors, and CORE errors.
4. Whether ARXML was generated or intentionally blocked.
5. Clickable paths to contract JSON, Excel, reports, ARXML, and golden diff when present.
6. The smallest actionable list of remaining problems.

Do not claim DaVinci compatibility solely because XML parsing passed. State whether validation was local, golden-based, or confirmed by an actual Developer import.
