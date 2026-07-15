# Phase 1 Excel Alignment Plan

This phase keeps Excel as the source of truth and upgrades the project around
DaVinci Developer compatibility evidence. The goal is not to add every AUTOSAR
field at once. The goal is to make each Excel field, validation rule, and ARXML
writer behavior traceable to a real golden ARXML export.

## Current Scope

Excel remains the primary modeling surface for:

- SWC and composition structure
- component prototypes and assembly connectors
- application and implementation data types
- record data types and record elements
- CompuMethod, CompuScale, DataConstr, and Unit definitions
- Sender/Receiver and Client/Server interfaces
- ports, ComSpecs, runnables, events, and runnable accesses

The current template is intentionally broad. Later phases may split or simplify
some sheets, but Phase 1 should avoid large Excel redesigns until the generated
ARXML is measured against a golden export.

## Golden Diff First

Use a DaVinci Developer export as the regression baseline:

- `HORN0.06(1).arxml`

The comparison must not use byte-for-byte diff. UUIDs, ordering, whitespace, and
tool metadata can differ while the model is still semantically equivalent.

The first check-in introduces:

```powershell
python scripts/diff_against_golden.py `
  --generated output/generated_ww_swc.arxml `
  --golden "HORN0.06(1).arxml" `
  --report output/golden_diff_report.md `
  --json output/golden_diff_report.json
```

The script indexes interesting ARXML elements by SHORT-NAME path and compares
semantic summaries for:

- `INIT-VALUE` value-specification structure
- ComSpec fields such as `DATA-FILTER`, `HANDLE-NEVER-RECEIVED`, and
  `HANDLE-OUT-OF-RANGE`
- `COMPU-METHOD` category, scales, text values, and linear coefficients
- `DATA-CONSTR` internal and physical ranges

The generated report is the task list for the next implementation passes.

## Upgrade Order

1. Init value typing
   Add Excel and model support only after the golden diff confirms the exact
   DaVinci shape for numeric, enum, boolean, and record initial values.

2. ComSpec coverage
   Replace hard-coded ComSpec values with optional Excel-driven fields. Write
   optional ARXML elements only when configured or when the golden export proves
   DaVinci emits them by default.

3. CompuMethod and DataConstr consistency
   Add validator checks for CompuScale gap/overlap, DataConstr coverage, and
   physical range consistency for linear methods.

4. Unit and mapping completeness
   Validate `UNIT-REF` existence and ensure every ADT used by interfaces or
   record elements has a DataTypeMapping entry.

5. Tests and docs
   Every new Excel column must have a reader/model change, a writer behavior, a
   validator rule where applicable, and at least one focused test.

## ARForge Reference Points

ARForge is a useful reference because it treats AUTOSAR modeling as a controlled
source-of-truth workflow with schema checks, semantic validation, deterministic
exports, reports, and diffs. This project should keep Excel as the input format,
but borrow these patterns:

- build a reusable validation context/index layer instead of making every rule
  repeatedly scan workbook rows;
- keep finding codes stable and specific enough for Excel users to act on;
- keep one invalid fixture or focused test per rule;
- generate deterministic reports that can be attached to reviews;
- separate "schema/shape validation" from "semantic AUTOSAR validation".

The first implementation step is the golden diff script. The next step should be
small validator additions backed by explicit invalid workbook cases, following
the same test-driven style ARForge uses for invalid YAML examples.

## First Findings To Track

- `Ports.InitValue` is currently untyped, so the writer cannot know whether a
  value is numeric, enum text, boolean, or a record initializer.
- `HANDLE-NEVER-RECEIVED` is currently hard-coded in the writer.
- `check_compu_method_values()` does not yet detect scale gaps, overlaps, or
  coverage against DataConstr.
- The Excel template documentation is older than the v2 workbook structure.
- The local Python virtual environment may need rebuilding before tests and the
  golden diff script can be executed reliably.
