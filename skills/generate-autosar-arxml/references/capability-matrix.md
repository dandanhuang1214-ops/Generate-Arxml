# Capability Matrix

Check the current code and tests when the request depends on a boundary; this file records the present baseline and may lag later implementation.

## Supported baseline

- Primitive ADT, IDT, and DataTypeMapping
- IDENTICAL, LINEAR, and TEXTTABLE CompuMethods
- Basic internal/physical DataConstr and Unit references
- Application Record and structure IDT
- Nested Record definitions and recursive Record initial values
- Nonqueued S/R
- Basic synchronous C/S with multiple Operations per interface
- Atomic SWC ports, Internal Behavior, Runnables, and supported Events
- Init, Periodic, OperationInvoked, and DataReceived triggers
- DataRead, DataWrite, and client Operation call access
- Single-level Composition
- Assembly and basic delegation connectors
- Canonical DOCX contract, Excel v2 output, gap reports, CORE validation, and golden semantic diff

## Partial

- Queued S/R: workbook fields exist, but the DOCX contract workflow is not fully open or closed-loop verified.
- DataConstr/Unit: supported for the project's current basic forms, not every AUTOSAR variation.
- SOA: current scope is AUTOSAR Classic C/S modeling, not Adaptive AUTOSAR or SOME/IP deployment.

## Unsupported baseline

- Asynchronous C/S
- ModeSwitchInterface and Mode Declaration Groups
- Mode Entry, Mode Exit, OnTransition, Mode Disabling, and Mode acknowledgement
- Multi-level/nested Composition
- E2E, SecOC, invalidation, and complex DataFilter behavior
- IRV, ExclusiveArea, PIM, NvM detailed configuration
- BSW/ECUC, OS/RTE task mapping
- SOME/IP deployment and Service Discovery configuration
- Diagnostic stack generation

Report any requested unsupported feature as a blocking capability gap. Do not substitute another AUTOSAR communication mechanism.
