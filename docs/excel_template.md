# Excel Template

Template file:

- `data/input/arxml_input_template.xlsx`

This template is designed for reusable `ARXML` generation.

It includes:

- 5 business sheets
- 1 hidden option sheet
- drop-down selections for common fixed-choice fields

## Sheets

### `Components`

One row per component.

Columns:

- `ComponentName`
- `ComponentCategory`
  Suggested values:
  `Atomic`, `Composition`
- `ComponentTypeName`
  Suggested values:
  `APPLICATION-SW-COMPONENT-TYPE`, `COMPOSITION-SW-COMPONENT-TYPE`
- `PackagePath`
  Current default:
  `/ComponentTypes`
- `Description`

### `Ports`

One row per port.

Columns:

- `ComponentName`
- `PortInterfaceKind`
  Suggested values:
  `SR`, `CS`
- `PortDirection`
  Suggested values:
  `R`, `P`
- `PortName`
- `InterfaceName`
- `DataElementName`
  Mainly used by `SR` ports.
- `DataType`
  Suggested values:
  `Boolean`, `UInt8`, `UInt16`, `SInt8`, `UInt32`, `Enum`
- `InitValue`
  Mainly used by `SR` ports.
- `ComSpecType`
  Suggested values:
  `NONQUEUED-RECEIVER-COM-SPEC`, `NONQUEUED-SENDER-COM-SPEC`
- `OperationName`
  Mainly used by `CS` ports.
- `Description`

### `Arguments`

One row per `CS` operation argument.

Columns:

- `ComponentName`
- `PortName`
- `OperationName`
- `ArgumentName`
- `ArgumentType`
- `ArgumentDirection`
  Suggested values:
  `IN`, `OUT`, `INOUT`
- `Description`

### `ValueMap`

One row per enum or value mapping item.

Columns:

- `TypeName`
- `RawValue`
- `TextValue`
- `Comment`

### `Runnables`

One row per runnable.

Columns:

- `ComponentName`
- `RunnableName`
- `TriggerType`
  Suggested values:
  `Init`, `Period`, `Invocation`
- `PeriodMs`
  Only for `Period`.
- `PortName`
  Mainly for `Invocation`.
- `OperationName`
  Mainly for `Invocation`.
- `Description`

### `Options`

Hidden helper sheet.

Used only for drop-down choices inside the template.

## Notes

- Keep one modeling object per row.
- Do not merge cells.
- Use `Ports` for both `SR` and `CS`.
- Use `Arguments` only for `CS` operation parameters.
- `ValueMap` is mainly for enum-like values.
- If a field has a drop-down, prefer the drop-down value over free text.
