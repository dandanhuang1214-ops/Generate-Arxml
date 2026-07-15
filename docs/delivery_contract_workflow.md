# ARXML Delivery Contract Workflow

The delivery contract is the new upstream interface between feature design
documents and the Excel-based ARXML generator.

It is intentionally not an Excel mirror. Feature designers fill only the design
decisions that cannot be derived safely:

- signal or service business name;
- provider and consumer SWC;
- value type, data type, range, enum values, unit, and init value;
- runnable trigger and access relationship;
- service operation, parameter direction, timeout, and return semantics.

The tool derives ARXML-oriented details:

- package paths;
- interface refs;
- port names;
- ComSpec kind;
- data type mapping rows;
- default mapping set path;
- default receiver ComSpec fields.

## Templates

Two upstream DOCX templates are supported:

- `ARXML接口交付文档模板_信号驱动模式.docx`
- `ARXML接口交付文档模板_SOA驱动模式.docx`

The signal template is the first-priority workflow. The SOA template is parsed
into the same canonical contract model, but deep service semantics will be
expanded over later iterations.

## Pipeline

```text
DOCX delivery document
  -> canonical contract JSON
  -> open issue report
  -> Excel v2 draft
  -> existing Excel reader and validators
  -> ARXML generation and golden diff
```

## Command

```powershell
python scripts/docx_to_contract.py `
  --input "D:\download\ARXML接口交付文档模板_信号驱动模式.docx" `
  --contract output/signal_contract.json `
  --excel output/signal_contract_draft.xlsx `
  --issues output/signal_contract_issues.md `
  --mode signal
```

For SOA:

```powershell
python scripts/docx_to_contract.py `
  --input "D:\download\ARXML接口交付文档模板_SOA驱动模式.docx" `
  --contract output/soa_contract.json `
  --excel output/soa_contract_draft.xlsx `
  --issues output/soa_contract_issues.md `
  --mode soa
```

## Contract Rules

- Missing critical facts must become `OpenIssue` entries.
- The extractor must not silently invent provider SWC, consumer SWC, data type,
  or init value.
- Inferred fields must remain traceable through `source_status`.
- The Excel draft is a review artifact and generator input, not the upstream
  authoring source.
