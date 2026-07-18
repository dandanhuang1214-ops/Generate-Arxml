# Generation Rules

Apply these project-specific rules without expanding them into tutorials.

## Names and references

- Preserve explicit interface, data-element, type, port, Operation, Runnable, and component names.
- Do not add `If`, `SR`, `DE`, `Rp`, or `Pp` prefixes/suffixes unless the source contract explicitly requires them.
- Resolve references by declared identity and package path, not fuzzy name similarity.
- Reject duplicate ADT names in the same package. Allow the same short name only when package paths intentionally differ.

## Primitive and Enum types

- Generate an IDENTICAL CompuMethod for primitive/Boolean Application data types when required by the project mapping rules.
- Generate TEXTTABLE only when the document marks the value type as Enum and provides the actual mappings.
- Preserve exactly the Enum values supplied by the document; do not widen `0..2` to the base type range `0..255`.
- Require Enum initial values to match a declared symbolic value.

## LINEAR conversion and constraints

- Treat a nontrivial resolution or offset as LINEAR conversion input.
- Preserve physical range and internal range independently.
- Write LINEAR internal-to-physical limits according to the generated CompuMethod representation verified against DaVinci output.
- Use the declared Unit. When the project rule requires a UnitRef and no Unit is supplied, use `No_unit`, not `none`.

## Records

- Generate both Application Record and corresponding structure Implementation data types.
- Use `ElementPath` as the canonical nested field identity.
- Preserve explicit implementation-side field names when supplied.
- Generate nested Record categories recursively for ADT, IDT, and initial values.
- Generate `RECORD-VALUE-SPECIFICATION` for Record port initial values; do not emit an Application scalar value specification.

## Ports, Runnables, and services

- Use input/output tables for S/R interface definitions only.
- Build component S/R ports from explicit Runnable Access rows and the matching declared interface.
- Determine C/S port role from the SWC role and connector relationship.
- Allow one C/S port/interface to contain multiple Operations.
- Generate client call access only when explicitly listed.
- Generate server `OperationInvokedEvent` from the server Runnable trigger declaration.
- Generate additional DataRead/DataWrite access inside a server Runnable only when explicitly listed.

## Composition and connectors

- Generate Composition when required by the mixed profile.
- Require both connector endpoints to resolve to existing component prototypes and ports.
- Do not invent missing connectors from matching names alone.

## Validation

- Treat open contract issues, model validation errors, and CORE `ERROR` findings as generation blockers.
- Do not weaken validation to force a requested test artifact unless the user explicitly requests a non-deliverable experiment and the output is clearly marked unsafe.
- Keep optional fields absent when no project rule or source value requires them; do not emit empty XML elements.
