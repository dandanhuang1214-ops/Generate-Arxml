# Delivery Document Contract

## Source of truth

Treat explicit document content and confirmed canonical contract values as facts. Track inferred and defaulted values separately. Never fill a missing business decision merely to make generation pass.

## Signal Atomic profile

Require enough information to determine:

- Atomic SWC name;
- input and output S/R interface definitions;
- signal/data-element names;
- Application and Implementation data types;
- primitive, Enum, Boolean, or Record semantics;
- physical/internal ranges, resolution, offset, and unit when applicable;
- initial values;
- Runnable names and triggers;
- one Runnable Access row for each declared read or write.

Input/output signal tables define S/R Application Port Interfaces and data elements. Component port instances come from Runnable Access rows. A referenced S/R port that is absent from the signal definitions is an error; do not synthesize an interface.

## Mixed signal/SOA profile

In addition to signal facts, require enough information to determine:

- participating SWCs and roles;
- C/S interface and port names;
- Operations and every IN/OUT/INOUT argument;
- argument data types, including Records;
- client call access and server `OperationInvokedEvent` trigger;
- Composition prototypes;
- assembly or delegation connector endpoints.

A client Runnable calling an Operation uses a call access. A server Runnable is triggered by `OperationInvokedEvent`. Other DataRead/DataWrite accesses inside the server Runnable are generated only when explicitly listed.

## Matching rules

- Match S/R Runnable Access to an existing declared signal/port name exactly.
- Do not guess suffixes such as `_Enh`, `_Atm`, `Rp`, `Pp`, `If`, or `SR`.
- Use role and connector endpoints to determine C/S required/provided ports.
- Permit multiple Operations in one C/S interface and port.
- Do not require an artificial call access on the server side.

## Blocking gaps

Create or retain an open issue for missing or contradictory:

- direction or SWC role;
- Application/Implementation type identity;
- Enum value map or Enum initial symbol;
- Record field type/path;
- Operation argument direction/type;
- Runnable trigger target;
- Runnable S/R access target;
- connector endpoint.

Do not generate final ARXML while any blocking gap remains.
