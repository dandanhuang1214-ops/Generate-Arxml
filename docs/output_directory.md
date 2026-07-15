# Output Directory Layout

`output/` is a local generated-artifact workspace. It is ignored by Git.

Recommended layout:

| Directory | Purpose |
|---|---|
| `output/deliverables/<project>/` | Final files for user/DaVinci validation, such as ARXML, generated Excel, contract JSON, and gap reports. |
| `output/references/<name>/` | Reference ARXML copied from DaVinci or manually modeled examples. |
| `output/validation/<name>/` | Golden diff reports, generated comparison ARXML, and validation reports. |
| `output/drafts/<mode>/` | Early signal/SOA workflow drafts that are not ready for DaVinci import. |
| `output/legacy/` | Older generated outputs retained for comparison only. |
| `output/temp/` | Temporary configs, copied source documents, and embedded workbook extracts. |
| `output/matlab/` | Generated MATLAB initialization helpers. |

Current primary TurnLamp deliverable:

```text
output/deliverables/turnlamp/turnlamp_signal_atomic.arxml
```

Do not commit files from `output/`. If a generated artifact should become a
stable test fixture or public example, copy it to a deliberate source-controlled
location such as `examples/` or `tests/fixtures/`.
