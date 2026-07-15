# Excel Template

The v2 workbook is the current source of truth for AUTOSAR Classic SWC,
interface, data type, ComSpec, runnable, and composition modeling.

Template creation:

```powershell
.\scripts\run_codegen.ps1 -CreateTemplate data/input/arxml_input_template.xlsx
```

The template is generated from `src/arxml_codegen/excel/template.py` and read by
`src/arxml_codegen/excel/reader.py`.

## DaVinci Path Strategy

Phase 1 uses DaVinci-style reusable package paths by default:

| Asset | Default path |
|---|---|
| Port interfaces | `/PortInterfaces` |
| Application and project implementation data types | `/DataTypes` |
| CompuMethods | `/DataTypes/CompuMethods` |
| DataConstrs | `/DataTypes/DataConstrs` |
| Units | `/DataTypes/Units` |
| DataTypeMappingSet | `/ComponentTypes/MappingSets/APP_data_mapping` |
| SWC component types | `<RootPackage>/Components` |
| Composition/system model | `<RootPackage>/System` |

The intent is that Window, Wiper, Horn, and later domains can reuse the same
interface and data-type package layout. `RootPackage` remains project-specific
and should mainly contain component and composition structure.

## Sheet Contract

| Sheet | Purpose |
|---|---|
| `ProjectConfig` | Project-level options such as AUTOSAR version and default mapping set path. |
| `Components` | Application SWC and composition component type definitions. |
| `ComponentPrototypes` | Component instances inside a composition. |
| `PrimitiveDataTypes` | Application primitive data types and their implementation type refs, CompuMethod refs, DataConstr refs, and Unit refs. |
| `RecordTypes` | Application and implementation record type definitions. |
| `RecordElements` | Record field definitions and field order. |
| `PortRecordInitValues` | Field-level initial values for ports whose `InitValueType` is `Record`. |
| `DataTypeMappings` | Explicit ADT to IDT mapping set entries. |
| `CompuMethods` | Computation methods such as `TEXTTABLE`, `LINEAR`, and `IDENTICAL`. |
| `CompuScales` | Text table entries or linear rational coefficients. |
| `DataConstrs` | Internal data constraints. |
| `SRInterfaces` | Sender/Receiver interface definitions. |
| `SRDataElements` | Data elements inside S/R interfaces. |
| `CSInterfaces` | Client/Server interface definitions. |
| `CSOperations` | Operations inside C/S interfaces. |
| `CSArguments` | Operation arguments, direction, and application data type refs. |
| `Ports` | Component ports, interface refs, ComSpec kind, timeouts, update behavior, and initial values. |
| `Runnables` | Runnable entities and generated symbols. |
| `RunnableEvents` | Init, periodic, operation-invoked, and data-received events. |
| `RunnableAccesses` | DataRead, DataWrite, and ServerCallPoint usage inside runnables. |
| `CompositionConnectors` | Assembly connectors between component prototypes. |
| `Units` | AUTOSAR unit definitions referenced by primitive data types. |

## Current Port Columns

`Ports` is intentionally kept as one broad sheet during Phase 1.

| Column | Notes |
|---|---|
| `ComponentName` | Must match `Components.ComponentName`. |
| `PortName` | AUTOSAR SHORT-NAME for the port prototype. |
| `PortDirection` | `P` or `R`. |
| `InterfaceKind` | `SR` or `CS`. |
| `InterfaceRef` | Full AUTOSAR path to the interface. |
| `DataElementName` | Used by S/R ports. |
| `OperationName` | Used by C/S ports. |
| `ComSpecKind` | AUTOSAR ComSpec element name. |
| `AliveTimeout` | Used by receiver S/R ports and client ports where applicable. |
| `QueueLength` | Used by queued S/R and server ComSpecs. |
| `EnableUpdate` | Receiver S/R update behavior. |
| `HandleNeverReceived` | Receiver S/R setting. For DaVinci-compatible output it is written before `INIT-VALUE`; default is `false` when omitted by higher-level contract generation. |
| `HandleTimeoutType` | Receiver S/R timeout behavior. |
| `InitValue` | Initial value literal. Its interpretation is controlled by `InitValueType`. |
| `InitValueType` | `Numeric`, `Enum`, `Boolean`, `String`, or `Record`. `Enum` must use a CompuScale symbol name, not a numeric literal. `Record` is expanded through `PortRecordInitValues`. |
| `Description` | Human-readable note. |

## Record InitValue Columns

Use `PortRecordInitValues` only when `Ports.InitValueType=Record`.

| Column | Notes |
|---|---|
| `ComponentName` | Must match the owning port's `Ports.ComponentName`. |
| `PortName` | Must match the owning port's `Ports.PortName`. |
| `RecordElementPath` | Record field path such as `CallID`. Nested paths such as `SubRecord.Field` are reserved for a later recursive expansion pass. |
| `Value` | Initial value for that field. |
| `ValueType` | `Numeric`, `Enum`, `Boolean`, `String`, or `Record`. |
| `Description` | Human-readable note. |

## Phase 1 Maintenance Rules

- Do not add a new Excel column without a matching dataclass field, reader
  mapping, documentation entry, and validator or writer behavior.
- Do not assume DaVinci output shape from memory. Use
  `scripts/diff_against_golden.py` against `HORN0.06(1).arxml` first.
- Treat `Ports.InitValueType=Enum` strictly: the value must be a symbol from the
  related `CompuScales.TextValue` set. Numeric literals such as `0` are rejected
  because DaVinci exports enum initial values as text-table symbols.
- Treat `Ports.InitValueType=Record` strictly: every direct field declared in
  `RecordElements` for the referenced record type must have one
  `PortRecordInitValues` row.
- Treat ComSpec optional fields as evidence-driven. If DaVinci omits an optional
  element when unset, the generator should omit it too.

## ARForge Reference Takeaways

ARForge is YAML-first while this project is Excel-first, so its source format is
not copied. The useful ideas for this project are architectural:

- keep stable validation finding codes;
- keep invalid examples or tests for each rule;
- build reusable validation context indexes before running rules;
- produce deterministic reports and model diffs for review;
- keep export ordering predictable.

These ideas fit the current Excel workflow and should guide Phase 1 cleanup.

## Planned Additions

These fields are not part of the current workbook contract yet. They should be
added only after the golden diff report confirms the expected ARXML shape.

| Candidate Area | Candidate Fields |
|---|---|
| Nested Record InitValue typing | Recursive `SubRecord.Field` expansion. |
| Receiver ComSpec | `RxFilterType`, `RxFilterMask`, `HandleNeverReceived`, `InvalidValue`. |
| Out-of-range handling | `HandleOutOfRange`, `HandleOutOfRangeStatus`. |
| Client ComSpec | `ClientTimeout`. |

## Golden Diff Command

```powershell
python scripts/diff_against_golden.py `
  --generated output/generated_ww_swc.arxml `
  --golden "HORN0.06(1).arxml" `
  --report output/golden_diff_report.md `
  --json output/golden_diff_report.json
```

The generated report should be reviewed before each Phase 1 Excel or ARXML
writer upgrade.
