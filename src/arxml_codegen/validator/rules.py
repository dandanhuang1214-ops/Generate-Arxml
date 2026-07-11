"""CORE-XXX validation rules — follows AUTOSAR TR_AutosarModelConstraints & ARForge pattern.

Rule numbering:
  CORE-010: DataType & Interface semantics
  CORE-020: SWC structure & Runnable constraints
  CORE-024: Runnable trigger policy
  CORE-025: Port ComSpec semantics
  CORE-030: Connector topology & composition
  CORE-040: AccessPort & DataAccess consistency
  CORE-041: SR connectivity
  CORE-042: SR usage
  CORE-043: CS connectivity
  CORE-044: CS usage
  CORE-045: SR multiplicity (n:1)
  CORE-047: Declared port usage
  CORE-050: Naming & identifier conventions
  CORE-060: Timing & scheduling (incl. SR producer/consumer rate)
"""
from __future__ import annotations

import re
from collections import defaultdict

from arxml_codegen.models.schema import WorkbookV2Model as WorkbookModel
from arxml_codegen.validator.finding import Finding, Severity

# SHORT-NAME regex: letters, digits, underscore, no leading digit
_SHORT_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


# ══════════════════════════════════════════════════════
# CORE-050: Naming & identifiers
# ══════════════════════════════════════════════════════

def check_short_names(model: WorkbookModel) -> list[Finding]:
    """CORE-050: All identifiers must conform to AUTOSAR SHORT-NAME."""
    findings = []
    checks: list[tuple[str, list[tuple[str, str, int]]]] = [
        ("SWC name", [(c.component_name, c.source_sheet, c.row_index) for c in model.components]),
        ("ADT name", [(d.application_type_name, d.source_sheet, d.row_index) for d in model.primitive_data_types]),
        ("Record type name", [(r.application_type_name, r.source_sheet, r.row_index) for r in model.record_types]),
        ("SR interface name", [(i.interface_name, i.source_sheet, i.row_index) for i in model.sr_interfaces]),
        ("CS interface name", [(i.interface_name, i.source_sheet, i.row_index) for i in model.cs_interfaces]),
        ("Port name", [(p.port_name, p.source_sheet, p.row_index) for p in model.ports]),
        ("Runnable name", [(r.runnable_name, r.source_sheet, r.row_index) for r in model.runnables]),
        ("CompuMethod name", [(c.compu_method_name, c.source_sheet, c.row_index) for c in model.compu_methods]),
        ("DataConstr name", [(d.data_constr_name, d.source_sheet, d.row_index) for d in model.data_constrs]),
        ("Prototype name", [(p.prototype_name, p.source_sheet, p.row_index) for p in model.component_prototypes]),
    ]
    for label, items in checks:
        for name, sheet, row in items:
            if not name:
                continue
            if not _SHORT_NAME_RE.match(name):
                findings.append(Finding(
                    code="CORE-050-SHORT-NAME",
                    severity=Severity.ERROR,
                    message=f"{label} '{name}' is not a valid AUTOSAR SHORT-NAME.",
                    location=f"{sheet}!R{row}" if sheet and row else "",
                    suggestion="Use only A-Z/a-z/0-9/_, and do not start with a digit.",
                ))
    return findings


# ══════════════════════════════════════════════════════
# CORE-050-DUPLICATE: Duplicate entity detection
# ══════════════════════════════════════════════════════

def check_duplicate_names(model: WorkbookModel) -> list[Finding]:
    """CORE-050-DUPLICATE: Detect duplicate names per entity type."""
    findings = []
    checks: list[tuple[str, list, callable, str]] = [
        ("ComponentName", model.components, lambda r: r.component_name, "CORE-050-DUP-SWC"),
        ("ADTName", model.primitive_data_types, lambda r: r.application_type_path or r.application_type_name, "CORE-050-DUP-ADT"),
        ("RecordTypeName", model.record_types, lambda r: r.application_type_path or r.application_type_name, "CORE-050-DUP-RECORD"),
        ("SRInterfaceName", model.sr_interfaces, lambda r: r.interface_path or r.interface_name, "CORE-050-DUP-SR-IFACE"),
        ("CSInterfaceName", model.cs_interfaces, lambda r: r.interface_path or r.interface_name, "CORE-050-DUP-CS-IFACE"),
        ("PortName within SWC", model.ports, lambda r: f"{r.component_name}/{r.port_name}", "CORE-050-DUP-PORT"),
        ("RunnableName within SWC", model.runnables, lambda r: f"{r.component_name}/{r.runnable_name}", "CORE-050-DUP-RUNNABLE"),
        ("PrototypeName within Composition", model.component_prototypes, lambda r: f"{r.composition_name}/{r.prototype_name}", "CORE-050-DUP-PROTOTYPE"),
    ]
    for label, rows, key_fn, code in checks:
        seen: dict[str, object] = {}
        for row in rows:
            key = key_fn(row)
            if not key or key.endswith("/"):
                continue
            if key in seen:
                loc = f"{getattr(row, 'source_sheet', '')}!R{getattr(row, 'row_index', 0)}"
                findings.append(Finding(
                    code=code, severity=Severity.ERROR,
                    message=f"{label} '{key_fn(row)}' is duplicated.",
                    location=loc,
                ))
            else:
                seen[key] = row
    return findings


# ══════════════════════════════════════════════════════
# CORE-010: DataType & Interface semantics
# ══════════════════════════════════════════════════════

def check_datatype_completeness(model: WorkbookModel) -> list[Finding]:
    """CORE-010: DataType completeness checks."""
    findings = []
    base_types = {"boolean", "uint8", "uint16", "uint32", "uint64", "sint8", "sint16", "sint32", "float32"}
    for row in model.primitive_data_types:
        loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
        if not row.application_type_name:
            findings.append(Finding("CORE-010-ADT-NO-NAME", Severity.ERROR, "Primitive ADT has no name.", loc))
        if not row.base_type:
            findings.append(Finding("CORE-010-ADT-NO-BASETYPE", Severity.ERROR,
                                    f"ADT '{row.application_type_name}' has no BaseType.", loc))
        elif row.base_type.strip().lower() not in base_types:
            findings.append(Finding("CORE-010-ADT-UNKNOWN-BASETYPE", Severity.ERROR,
                                    f"ADT '{row.application_type_name}' base type '{row.base_type}' is not recognized.",
                                    loc, suggestion=f"Use one of {sorted(base_types)}"))
    for row in model.record_types:
        loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
        if not row.application_type_name:
            findings.append(Finding("CORE-010-RECORD-NO-NAME", Severity.ERROR, "Record ADT has no name.", loc))
    return findings


def check_compu_method_values(model: WorkbookModel) -> list[Finding]:
    """CORE-010-COMPU: Validate CompuMethod/CompuScale table consistency."""
    findings = []
    cm_scales = defaultdict(list)
    for s in model.compu_scales:
        cm_scales[s.compu_method_name].append(s)

    for row in model.compu_methods:
        loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
        category = row.category.strip().upper()
        scales = cm_scales.get(row.compu_method_name, [])
        if category == "TEXTTABLE" and not scales:
            findings.append(Finding("CORE-010-COMPU-TEXTTABLE-EMPTY", Severity.WARNING,
                                    f"CompuMethod '{row.compu_method_name}' is TEXTTABLE but has no CompuScale entries.", loc))
        if category == "LINEAR" and scales:
            # Check for numerator/denominator
            for s in scales:
                if s.numerator and s.denominator:
                    try:
                        float(s.numerator)
                        float(s.denominator)
                    except ValueError:
                        findings.append(Finding("CORE-010-COMPU-SCALE-INVALID", Severity.ERROR,
                                                f"CompuScale for '{row.compu_method_name}' has non-numeric numerator/denominator.", loc))

    # Check scale duplicates per compu method
    for cm_name, scales in cm_scales.items():
        seen_vals = set()
        for s in scales:
            key = (s.lower_limit, s.upper_limit, s.text_value)
            if key in seen_vals and key != ("", "", ""):
                loc = f"{s.source_sheet}!R{s.row_index}"
                findings.append(Finding("CORE-010-COMPU-SCALE-DUPLICATE", Severity.ERROR,
                                        f"CompuScale duplicate for '{cm_name}' at {key}.", loc))
            seen_vals.add(key)
    return findings


def check_port_interface_references(model: WorkbookModel) -> list[Finding]:
    """CORE-010-PORT-IFACE: Port-to-interface reference integrity."""
    findings = []
    sr_ifaces = {row.interface_path: row for row in model.sr_interfaces}
    cs_ifaces = {row.interface_path: row for row in model.cs_interfaces}
    all_ifaces = {**sr_ifaces, **cs_ifaces}

    for row in model.ports:
        loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
        if not row.interface_ref:
            continue
        iface_path = row.interface_ref
        if iface_path not in all_ifaces:
            findings.append(Finding("CORE-010-PORT-UNKNOWN-INTERFACE", Severity.ERROR,
                                    f"Port '{row.port_name}' references unknown interface '{iface_path}'.", loc))
            continue
        # Interface kind must match
        expected_kind = row.interface_kind.upper()
        if expected_kind == "SR" and iface_path not in sr_ifaces:
            findings.append(Finding("CORE-010-PORT-INTERFACE-KIND-MISMATCH", Severity.ERROR,
                                    f"Port '{row.port_name}' expects SR but interface is not SR.", loc))
        if expected_kind == "CS" and iface_path not in cs_ifaces:
            findings.append(Finding("CORE-010-PORT-INTERFACE-KIND-MISMATCH", Severity.ERROR,
                                    f"Port '{row.port_name}' expects CS but interface is not CS.", loc))
    return findings


def check_cs_operation_arguments(model: WorkbookModel) -> list[Finding]:
    """CORE-010-CS-ARGUMENT: Valid direction and no duplicates."""
    findings = []
    op_args = defaultdict(list)
    for row in model.cs_arguments:
        op_args[(row.interface_name, row.operation_name)].append(row)

    for (iface, op_name), args in op_args.items():
        loc = f"{args[0].source_sheet}!R{args[0].row_index}" if args[0].source_sheet else ""
        seen_args = set()
        for arg in args:
            if arg.argument_name in seen_args:
                findings.append(Finding("CORE-010-CS-ARGUMENT-DUPLICATE", Severity.ERROR,
                                        f"Operation '{iface}.{op_name}' has duplicate argument '{arg.argument_name}'.", loc))
            seen_args.add(arg.argument_name)
            if arg.direction.upper() not in ("IN", "OUT", "INOUT"):
                findings.append(Finding("CORE-010-CS-ARGUMENT-DIRECTION", Severity.ERROR,
                                        f"Argument '{arg.argument_name}' direction '{arg.direction}' invalid. Use IN/OUT/INOUT.", loc))
    return findings


# ══════════════════════════════════════════════════════
# CORE-020: SWC structure
# ══════════════════════════════════════════════════════

def check_swc_completeness(model: WorkbookModel) -> list[Finding]:
    """CORE-020: Every Application SWC needs ports and runnables."""
    findings = []
    comp_ports = defaultdict(list)
    comp_runnables = defaultdict(list)
    for p in model.ports:
        comp_ports[p.component_name].append(p)
    for r in model.runnables:
        comp_runnables[r.component_name].append(r)

    for c in model.components:
        if c.component_kind.lower() == "composition":
            continue
        if not comp_ports.get(c.component_name):
            findings.append(Finding("CORE-020-SWC-NO-PORTS", Severity.WARNING,
                                    f"SWC '{c.component_name}' has no ports."))
        if not comp_runnables.get(c.component_name):
            findings.append(Finding("CORE-020-SWC-NO-RUNNABLES", Severity.WARNING,
                                    f"SWC '{c.component_name}' has no runnables."))
    return findings


def check_runnable_event_association(model: WorkbookModel) -> list[Finding]:
    """CORE-020: Each runnable should be referenced by at least one event or access row."""
    findings = []
    runnable_refs = defaultdict(set)
    for e in model.runnable_events:
        runnable_refs[(e.component_name, e.runnable_name)].add(e.trigger_type or "")
    for a in model.runnable_accesses:
        runnable_refs[(a.component_name, a.runnable_name)].add(a.access_type or "")

    for r in model.runnables:
        key = (r.component_name, r.runnable_name)
        if key not in runnable_refs:
            loc = f"{r.source_sheet}!R{r.row_index}" if r.source_sheet else ""
            findings.append(Finding("CORE-020-RUNNABLE-NO-EVENT", Severity.WARNING,
                                    f"Runnable '{r.component_name}.{r.runnable_name}' has no trigger or access definition.", loc))
    return findings


# ══════════════════════════════════════════════════════
# CORE-030: Connector topology
# ══════════════════════════════════════════════════════

def _resolve_prototype_ports(model: WorkbookModel):
    """Resolve prototype-based connectors to component-level ports."""
    prototypes = {(p.composition_name, p.prototype_name): p.component_type_name for p in model.component_prototypes}
    ports = {(p.component_name, p.port_name): p for p in model.ports}
    return prototypes, ports


def check_connector_consistency(model: WorkbookModel) -> list[Finding]:
    """CORE-030: Connector endpoint direction, kind, and interface consistency."""
    findings = []
    prototypes, ports = _resolve_prototype_ports(model)
    compositions = {c.component_name for c in model.components if c.component_kind.lower() == "composition"}

    for row in model.composition_connectors:
        loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
        # Check composition exists
        if row.composition_name not in compositions:
            findings.append(Finding("CORE-030-CONNECTOR-UNKNOWN-COMPOSITION", Severity.ERROR,
                                    f"Composition '{row.composition_name}' does not exist.", loc))
        # Resolve prototypes to component types
        prov_comp = prototypes.get((row.composition_name, row.provider_prototype))
        req_comp = prototypes.get((row.composition_name, row.requester_prototype))
        if not prov_comp:
            findings.append(Finding("CORE-030-CONNECTOR-UNKNOWN-PROTOTYPE", Severity.ERROR,
                                    f"Provider prototype '{row.provider_prototype}' not found in '{row.composition_name}'.", loc))
        if not req_comp:
            findings.append(Finding("CORE-030-CONNECTOR-UNKNOWN-PROTOTYPE", Severity.ERROR,
                                    f"Requester prototype '{row.requester_prototype}' not found in '{row.composition_name}'.", loc))
        if not prov_comp or not req_comp:
            continue
        # Check ports on resolved component types
        pport = ports.get((prov_comp, row.provider_port))
        rport = ports.get((req_comp, row.requester_port))
        if not pport:
            findings.append(Finding("CORE-030-CONNECTOR-UNKNOWN-PORT", Severity.ERROR,
                                    f"Provider port '{prov_comp}/{row.provider_port}' not found.", loc))
        if not rport:
            findings.append(Finding("CORE-030-CONNECTOR-UNKNOWN-PORT", Severity.ERROR,
                                    f"Requester port '{req_comp}/{row.requester_port}' not found.", loc))
        if not pport or not rport:
            continue
        # Provider must be P-Port, Requester must be R-Port
        if pport.port_direction.upper() != "P":
            findings.append(Finding("CORE-030-CONNECTOR-DIRECTION", Severity.ERROR,
                                    f"Provider '{row.provider_port}' must be a P-Port (actual: {pport.port_direction}).", loc))
        if rport.port_direction.upper() != "R":
            findings.append(Finding("CORE-030-CONNECTOR-DIRECTION", Severity.ERROR,
                                    f"Requester '{row.requester_port}' must be an R-Port (actual: {rport.port_direction}).", loc))
        # Interface kind must match
        if pport.interface_kind.upper() != rport.interface_kind.upper():
            findings.append(Finding("CORE-030-CONNECTOR-KIND-MISMATCH", Severity.ERROR,
                                    f"Interface kind mismatch: Provider {pport.interface_kind} vs Requester {rport.interface_kind}.", loc))
        if pport.interface_ref != rport.interface_ref:
            findings.append(Finding("CORE-030-CONNECTOR-INTERFACE-MISMATCH", Severity.ERROR,
                                    f"Interface mismatch: Provider '{pport.interface_ref}' vs Requester '{rport.interface_ref}'.", loc))
    return findings


def check_unconnected_ports(model: WorkbookModel) -> list[Finding]:
    """CORE-030-CONNECTOR-UNCONNECTED: Flag ports not wired in any composition."""
    findings = []
    prototypes, _ = _resolve_prototype_ports(model)
    connected = set()
    for c in model.composition_connectors:
        prov_comp = prototypes.get((c.composition_name, c.provider_prototype))
        req_comp = prototypes.get((c.composition_name, c.requester_prototype))
        if prov_comp:
            connected.add((prov_comp, c.provider_port))
        if req_comp:
            connected.add((req_comp, c.requester_port))

    for row in model.ports:
        key = (row.component_name, row.port_name)
        if key not in connected:
            loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
            findings.append(Finding("CORE-030-CONNECTOR-UNCONNECTED", Severity.WARNING,
                                    f"Unconnected port: {row.component_name}/{row.port_name}", loc,
                                    suggestion="Connect via CompositionConnectors or mark as external-facing."))
    return findings


# ══════════════════════════════════════════════════════
# CORE-040: AccessPort consistency
# ══════════════════════════════════════════════════════

def check_access_port_consistency(model: WorkbookModel) -> list[Finding]:
    """CORE-040: AccessPort must point to existing port with matching direction."""
    findings = []
    ports = {(p.component_name, p.port_name): p for p in model.ports}

    for a in model.runnable_accesses:
        loc = f"{a.source_sheet}!R{a.row_index}" if a.source_sheet else ""
        at = (a.access_type or "").strip().lower()
        at = at.replace(" ", "").replace("_", "")
        if not a.port_name or not at:
            continue
        port = ports.get((a.component_name, a.port_name))
        if not port:
            findings.append(Finding("CORE-040-ACCESS-UNKNOWN-PORT", Severity.ERROR,
                                    f"AccessPort '{a.port_name}' not found on SWC '{a.component_name}'.", loc))
            continue
        # DataRead → must be SR R-Port
        if at == "dataread" and not (port.interface_kind.upper() == "SR" and port.port_direction.upper() == "R"):
            findings.append(Finding("CORE-040-ACCESS-READ-DIRECTION", Severity.ERROR,
                                    f"AccessType=DataRead requires S/R R-Port, but '{a.port_name}' is {port.interface_kind}/{port.port_direction}.", loc))
        # DataWrite → must be SR P-Port
        elif at == "datawrite" and not (port.interface_kind.upper() == "SR" and port.port_direction.upper() == "P"):
            findings.append(Finding("CORE-040-ACCESS-WRITE-DIRECTION", Severity.ERROR,
                                    f"AccessType=DataWrite requires S/R P-Port, but '{a.port_name}' is {port.interface_kind}/{port.port_direction}.", loc))
        # ServerCallPoint → must be CS R-Port
        elif at == "servercallpoint" and not (port.interface_kind.upper() == "CS" and port.port_direction.upper() == "R"):
            findings.append(Finding("CORE-040-ACCESS-CALL-DIRECTION", Severity.ERROR,
                                    f"AccessType=ServerCallPoint requires C/S R-Port, but '{a.port_name}' is {port.interface_kind}/{port.port_direction}.", loc))
    return findings


def check_trigger_port_consistency(model: WorkbookModel) -> list[Finding]:
    """CORE-040-TRIGGER: OperationInvoked requires CS P-Port, DataReceived requires SR R-Port."""
    findings = []
    ports = {(p.component_name, p.port_name): p for p in model.ports}

    for e in model.runnable_events:
        loc = f"{e.source_sheet}!R{e.row_index}" if e.source_sheet else ""
        trigger = (e.trigger_type or "").strip().replace(" ", "").replace("_", "").lower()
        if trigger == "operationinvoked":
            if e.port_name:
                port = ports.get((e.component_name, e.port_name))
                if port and (port.interface_kind.upper() != "CS" or port.port_direction.upper() != "P"):
                    findings.append(Finding("CORE-040-TRIGGER-OI-PORT", Severity.ERROR,
                                            f"OperationInvoked PortName must be a C/S P-Port, but '{e.port_name}' is {port.interface_kind}/{port.port_direction}.", loc))
            if e.operation_name and e.port_name:
                port = ports.get((e.component_name, e.port_name))
                if port and port.operation_name != e.operation_name:
                    findings.append(Finding("CORE-040-TRIGGER-OI-OPERATION", Severity.WARNING,
                                            f"OperationInvoked OperationName '{e.operation_name}' != port operation '{port.operation_name}'.", loc))
        elif trigger == "datareceived":
            if e.port_name:
                port = ports.get((e.component_name, e.port_name))
                if port and (port.interface_kind.upper() != "SR" or port.port_direction.upper() != "R"):
                    findings.append(Finding("CORE-040-TRIGGER-DR-PORT", Severity.ERROR,
                                            f"DataReceived PortName must be an S/R R-Port, but '{e.port_name}' is {port.interface_kind}/{port.port_direction}.", loc))
    return findings


# ══════════════════════════════════════════════════════
# CORE-060: Time & scheduling
# ══════════════════════════════════════════════════════

def check_timing_constraints(model: WorkbookModel) -> list[Finding]:
    """CORE-060: Period > 0 for timing events."""
    findings = []
    for e in model.runnable_events:
        trigger = (e.trigger_type or "").strip().replace(" ", "").replace("_", "").lower()
        if trigger == "periodic":
            try:
                period = float(e.period_ms) if e.period_ms else 0
            except ValueError:
                period = 0
            if period <= 0:
                loc = f"{e.source_sheet}!R{e.row_index}" if e.source_sheet else ""
                findings.append(Finding("CORE-060-TIMING-NO-PERIOD", Severity.ERROR,
                                        f"Periodic event for '{e.runnable_name}' has no valid period.", loc,
                                        suggestion="PeriodMs must be > 0 (in milliseconds)."))
    return findings


# ══════════════════════════════════════════════════════
# CORE-024: Runnable trigger policy (ARForge)
# ══════════════════════════════════════════════════════

def check_runnable_trigger_policy(model: WorkbookModel) -> list[Finding]:
    """CORE-024: Every runnable must have exactly one trigger."""
    findings = []
    events_by_runnable: dict[tuple[str, str], list] = defaultdict(list)
    for e in model.runnable_events:
        events_by_runnable[(e.component_name, e.runnable_name)].append(e)

    for r in model.runnables:
        key = (r.component_name, r.runnable_name)
        events = events_by_runnable.get(key, [])
        triggers = {(e.trigger_type or "").strip().lower() for e in events}
        # Normalize trigger type names
        normalized_triggers = set()
        for t in triggers:
            t = t.replace(" ", "").replace("_", "")
            if t in ("", "none"):
                continue
            normalized_triggers.add(t)
        loc = f"{r.source_sheet}!R{r.row_index}" if r.source_sheet else ""
        if len(normalized_triggers) == 0:
            findings.append(Finding("CORE-024-MISSING-TRIGGER", Severity.ERROR,
                                    f"Runnable '{key[0]}.{key[1]}' has no trigger defined.", loc,
                                    suggestion="Add at least one RunnableEvent (Init/Periodic/OperationInvoked/DataReceived)."))
        elif len(normalized_triggers) > 1:
            findings.append(Finding("CORE-024-MULTIPLE-TRIGGERS", Severity.WARNING,
                                    f"Runnable '{key[0]}.{key[1]}' has multiple trigger types: {sorted(normalized_triggers)}.", loc,
                                    suggestion="A runnable should have exactly one trigger style."))
    return findings


# ══════════════════════════════════════════════════════
# CORE-025: Port ComSpec semantics (ARForge)
# ══════════════════════════════════════════════════════

def check_com_spec_semantics(model: WorkbookModel) -> list[Finding]:
    """CORE-025: Validate ComSpec settings based on interface kind."""
    findings = []
    for row in model.ports:
        loc = f"{row.source_sheet}!R{row.row_index}" if row.source_sheet else ""
        kind = (row.interface_kind or "").strip().upper()
        com_spec = (row.com_spec_kind or "").strip()
        if kind == "SR":
            # SR ports should not have CS-specific fields
            if com_spec and com_spec.upper() in ("CLIENT-COM-SPEC", "SERVER-COM-SPEC"):
                findings.append(Finding("CORE-025-SR-COMSPEC-INVALID", Severity.ERROR,
                                        f"SR port '{row.port_name}' has CS ComSpec '{com_spec}'.", loc,
                                        suggestion="Use NONQUEUED-SENDER-COM-SPEC or NONQUEUED-RECEIVER-COM-SPEC for SR ports."))
            # Validate queue_length for queued modes
            if "QUEUED" in com_spec.upper():
                try:
                    qlen = int(row.queue_length) if row.queue_length else 0
                except ValueError:
                    qlen = 0
                if qlen < 1:
                    findings.append(Finding("CORE-025-SR-QUEUE-LENGTH", Severity.ERROR,
                                            f"SR port '{row.port_name}' has QUEUED ComSpec but queue_length < 1.", loc,
                                            suggestion="QueueLength must be >= 1 for QUEUED ComSpec."))
        elif kind == "CS":
            # CS ports should not have SR-specific fields
            if com_spec and com_spec.upper() not in ("CLIENT-COM-SPEC", "SERVER-COM-SPEC"):
                findings.append(Finding("CORE-025-CS-COMSPEC-INVALID", Severity.ERROR,
                                        f"CS port '{row.port_name}' has SR ComSpec '{com_spec}'.", loc,
                                        suggestion="Use CLIENT-COM-SPEC or SERVER-COM-SPEC for CS ports."))
            # Validate alive_timeout for client ports
            if com_spec.upper() == "CLIENT-COM-SPEC" and row.port_direction.upper() == "R":
                try:
                    timeout = int(row.alive_timeout) if row.alive_timeout else -1
                except ValueError:
                    timeout = -1
                if timeout < 0:
                    findings.append(Finding("CORE-025-CS-TIMEOUT", Severity.WARNING,
                                            f"CS client port '{row.port_name}' has no AliveTimeout set.", loc,
                                            suggestion="Set AliveTimeout >= 0 for CLIENT-COM-SPEC on R-Ports."))
    return findings


# ══════════════════════════════════════════════════════
# CORE-041/042/043/044/045: Connectivity & usage (ARForge)
# ══════════════════════════════════════════════════════

def _build_connectivity_map(model: WorkbookModel):
    """Build port connectivity from composition connectors (resolved via prototypes)."""
    prototypes = {(p.composition_name, p.prototype_name): p.component_type_name for p in model.component_prototypes}
    ports = {(p.component_name, p.port_name): p for p in model.ports}
    # connected[(component, port)] -> list of connected peer (component, port)
    connected: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for c in model.composition_connectors:
        prov_comp = prototypes.get((c.composition_name, c.provider_prototype))
        req_comp = prototypes.get((c.composition_name, c.requester_prototype))
        if prov_comp and req_comp:
            connected[(prov_comp, c.provider_port)].append((req_comp, c.requester_port))
            connected[(req_comp, c.requester_port)].append((prov_comp, c.provider_port))
    return prototypes, ports, connected


def check_sr_connectivity(model: WorkbookModel) -> list[Finding]:
    """CORE-041: Check SR port connectivity — provides need outgoing, requires need incoming."""
    findings = []
    _, ports, connected = _build_connectivity_map(model)
    if not model.component_prototypes:
        return findings  # No composition = skip connectivity checks

    for (comp, port_name), port in ports.items():
        if (port.interface_kind or "").strip().upper() != "SR":
            continue
        loc = f"{port.source_sheet}!R{port.row_index}" if port.source_sheet else ""
        is_connected = (comp, port_name) in connected
        direction = (port.port_direction or "").strip().upper()
        if direction == "P" and not is_connected:
            findings.append(Finding("CORE-041-SR-PROVIDES-NO-OUTGOING", Severity.WARNING,
                                    f"SR P-Port '{comp}/{port_name}' provides data but has no outgoing connector.", loc))
        elif direction == "R" and not is_connected:
            findings.append(Finding("CORE-041-SR-REQUIRES-NO-INCOMING", Severity.WARNING,
                                    f"SR R-Port '{comp}/{port_name}' expects data but has no incoming connector.", loc))
    return findings


def check_sr_usage(model: WorkbookModel) -> list[Finding]:
    """CORE-042: Check connected SR ports are actually used by runnables."""
    findings = []
    _, ports, connected = _build_connectivity_map(model)

    # Build port usage from runnable accesses + data received events
    sr_read_ports: set[tuple[str, str]] = set()
    sr_write_ports: set[tuple[str, str]] = set()
    for a in model.runnable_accesses:
        at = (a.access_type or "").strip().lower().replace(" ", "").replace("_", "")
        if at == "dataread":
            sr_read_ports.add((a.component_name, a.port_name))
        elif at == "datawrite":
            sr_write_ports.add((a.component_name, a.port_name))
    for e in model.runnable_events:
        trigger = (e.trigger_type or "").strip().lower().replace(" ", "").replace("_", "")
        if trigger == "datareceived" and e.port_name:
            sr_read_ports.add((e.component_name, e.port_name))

    for (comp, port_name), port in ports.items():
        if (port.interface_kind or "").strip().upper() != "SR":
            continue
        if (comp, port_name) not in connected:
            continue
        loc = f"{port.source_sheet}!R{port.row_index}" if port.source_sheet else ""
        direction = (port.port_direction or "").strip().upper()
        if direction == "P" and (comp, port_name) not in sr_write_ports:
            findings.append(Finding("CORE-042-SR-PROVIDES-UNUSED", Severity.WARNING,
                                    f"SR P-Port '{comp}/{port_name}' is connected but never written by any runnable.", loc))
        elif direction == "R" and (comp, port_name) not in sr_read_ports:
            findings.append(Finding("CORE-042-SR-REQUIRES-UNUSED", Severity.WARNING,
                                    f"SR R-Port '{comp}/{port_name}' is connected but never read by any runnable.", loc))
    return findings


def check_cs_connectivity(model: WorkbookModel) -> list[Finding]:
    """CORE-043: CS requires port MUST have incoming connector (error level)."""
    findings = []
    _, ports, connected = _build_connectivity_map(model)
    if not model.component_prototypes:
        return findings

    for (comp, port_name), port in ports.items():
        if (port.interface_kind or "").strip().upper() != "CS":
            continue
        loc = f"{port.source_sheet}!R{port.row_index}" if port.source_sheet else ""
        is_connected = (comp, port_name) in connected
        direction = (port.port_direction or "").strip().upper()
        if direction == "R" and not is_connected:
            findings.append(Finding("CORE-043-CS-REQUIRES-NO-INCOMING", Severity.ERROR,
                                    f"CS R-Port '{comp}/{port_name}' calls a server but has no incoming connector.", loc,
                                    suggestion="Connect this port via CompositionConnectors or mark as externally served."))
        elif direction == "P" and not is_connected:
            # Check if any OIE references this port
            has_oie = any(
                (e.component_name == comp and e.port_name == port_name and
                 (e.trigger_type or "").strip().lower().replace(" ", "").replace("_", "") == "operationinvoked")
                for e in model.runnable_events
            )
            if has_oie:
                findings.append(Finding("CORE-043-CS-PROVIDES-NO-INCOMING", Severity.WARNING,
                                        f"CS P-Port '{comp}/{port_name}' has OperationInvokedEvent but no incoming connector.", loc))
    return findings


def check_cs_usage(model: WorkbookModel) -> list[Finding]:
    """CORE-044: Check CS ports are used when connected."""
    findings = []
    _, ports, connected = _build_connectivity_map(model)

    # Build CS port usage from runnable accesses + OIE
    cs_call_ports: set[tuple[str, str]] = set()
    cs_oie_ports: set[tuple[str, str]] = set()
    for a in model.runnable_accesses:
        at = (a.access_type or "").strip().lower().replace(" ", "").replace("_", "")
        if at == "servercallpoint":
            cs_call_ports.add((a.component_name, a.port_name))
    for e in model.runnable_events:
        trigger = (e.trigger_type or "").strip().lower().replace(" ", "").replace("_", "")
        if trigger == "operationinvoked" and e.port_name:
            cs_oie_ports.add((e.component_name, e.port_name))

    for (comp, port_name), port in ports.items():
        if (port.interface_kind or "").strip().upper() != "CS":
            continue
        loc = f"{port.source_sheet}!R{port.row_index}" if port.source_sheet else ""
        direction = (port.port_direction or "").strip().upper()
        is_connected = (comp, port_name) in connected
        if direction == "R" and not is_connected and (comp, port_name) in cs_call_ports:
            findings.append(Finding("CORE-044-CS-CALL-UNCONNECTED", Severity.ERROR,
                                    f"CS R-Port '{comp}/{port_name}' has ServerCallPoint but no connector.", loc))
        if direction == "R" and is_connected and (comp, port_name) not in cs_call_ports:
            findings.append(Finding("CORE-044-CS-REQUIRES-UNUSED", Severity.WARNING,
                                    f"CS R-Port '{comp}/{port_name}' is connected but never called by any runnable.", loc))
        if direction == "P" and is_connected and (comp, port_name) not in cs_oie_ports:
            findings.append(Finding("CORE-044-CS-PROVIDES-UNUSED", Severity.WARNING,
                                    f"CS P-Port '{comp}/{port_name}' is connected but has no OperationInvokedEvent.", loc))
    return findings


def check_sr_multiplicity(model: WorkbookModel) -> list[Finding]:
    """CORE-045: Detect n:1 SR communication (multiple providers to single requires port)."""
    findings = []
    _, ports, connected = _build_connectivity_map(model)

    for (comp, port_name), peers in connected.items():
        port = ports.get((comp, port_name))
        if not port or (port.interface_kind or "").strip().upper() != "SR":
            continue
        direction = (port.port_direction or "").strip().upper()
        if direction != "R":
            continue
        providers = [(c, p) for (c, p) in peers if ports.get((c, p)) and (ports[(c, p)].port_direction or "").strip().upper() == "P"]
        if len(providers) > 1:
            loc = f"{port.source_sheet}!R{port.row_index}" if port.source_sheet else ""
            prov_str = ", ".join(f"{c}/{p}" for c, p in providers)
            findings.append(Finding("CORE-045-SR-N-TO-ONE", Severity.WARNING,
                                    f"SR R-Port '{comp}/{port_name}' receives from {len(providers)} providers: [{prov_str}].", loc,
                                    suggestion="AUTOSAR allows this, but arbitration semantics may be unclear."))
    return findings


# ══════════════════════════════════════════════════════
# CORE-047: Declared port usage (ARForge)
# ══════════════════════════════════════════════════════

def check_declared_port_usage(model: WorkbookModel) -> list[Finding]:
    """CORE-047: Flag SWC ports never used by any runnable behavior."""
    findings = []

    # Build port usage sets from all runnable behavior
    data_read_ports: set[tuple[str, str]] = set()
    data_write_ports: set[tuple[str, str]] = set()
    cs_call_ports: set[tuple[str, str]] = set()
    cs_oie_ports: set[tuple[str, str]] = set()
    dr_ports: set[tuple[str, str]] = set()

    for a in model.runnable_accesses:
        at = (a.access_type or "").strip().lower().replace(" ", "").replace("_", "")
        if at == "dataread":
            data_read_ports.add((a.component_name, a.port_name))
        elif at == "datawrite":
            data_write_ports.add((a.component_name, a.port_name))
        elif at == "servercallpoint":
            cs_call_ports.add((a.component_name, a.port_name))

    for e in model.runnable_events:
        trigger = (e.trigger_type or "").strip().lower().replace(" ", "").replace("_", "")
        if trigger == "operationinvoked" and e.port_name:
            cs_oie_ports.add((e.component_name, e.port_name))
        elif trigger == "datareceived" and e.port_name:
            dr_ports.add((e.component_name, e.port_name))

    for port in model.ports:
        key = (port.component_name, port.port_name)
        kind = (port.interface_kind or "").strip().upper()
        direction = (port.port_direction or "").strip().upper()
        loc = f"{port.source_sheet}!R{port.row_index}" if port.source_sheet else ""

        used = False
        if kind == "SR":
            if direction == "R" and (key in data_read_ports or key in dr_ports):
                used = True
            elif direction == "P" and key in data_write_ports:
                used = True
        elif kind == "CS":
            if direction == "R" and key in cs_call_ports:
                used = True
            elif direction == "P" and key in cs_oie_ports:
                used = True

        if not used:
            findings.append(Finding("CORE-047-PORT-UNUSED", Severity.WARNING,
                                    f"Port '{key[0]}/{key[1]}' ({kind}/{direction}) is never used by any runnable.", loc,
                                    suggestion="Add a RunnableAccess or RunnableEvent referencing this port, or remove it."))
    return findings


# ══════════════════════════════════════════════════════
# CORE-050/051: SR timing relationships (ARForge)
# ══════════════════════════════════════════════════════

def check_sr_timing_relations(model: WorkbookModel) -> list[Finding]:
    """CORE-050/051: Compare periods of connected SR producer/consumer runnables."""
    findings = []
    _, ports, connected = _build_connectivity_map(model)

    if not model.component_prototypes:
        return findings

    # Build runnable -> period map from periodic events
    runnable_period: dict[tuple[str, str], float] = {}
    for e in model.runnable_events:
        trigger = (e.trigger_type or "").strip().lower().replace(" ", "").replace("_", "")
        if trigger == "periodic" and e.period_ms:
            try:
                period = float(e.period_ms)
                if period > 0:
                    runnable_period[(e.component_name, e.runnable_name)] = period
            except ValueError:
                pass

    # Find which runnables access which ports
    port_writers: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    port_readers: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)

    for a in model.runnable_accesses:
        at = (a.access_type or "").strip().lower().replace(" ", "").replace("_", "")
        key = (a.component_name, a.port_name)
        r_key = (a.component_name, a.runnable_name)
        if r_key not in runnable_period:
            continue
        if at == "datawrite":
            port_writers[key].append(r_key)
        elif at == "dataread":
            port_readers[key].append(r_key)

    for e in model.runnable_events:
        trigger = (e.trigger_type or "").strip().lower().replace(" ", "").replace("_", "")
        if trigger == "datareceived" and e.port_name:
            key = (e.component_name, e.port_name)
            r_key = (e.component_name, e.runnable_name)
            if r_key in runnable_period:
                port_readers[key].append(r_key)

    # Walk connectors and compare timing
    for (prov_comp, prov_port), peers in connected.items():
        prov = ports.get((prov_comp, prov_port))
        if not prov or (prov.interface_kind or "").strip().upper() != "SR":
            continue
        if (prov.port_direction or "").strip().upper() != "P":
            continue
        writer_runnables = port_writers.get((prov_comp, prov_port), [])
        if not writer_runnables:
            continue
        producer_period = min(runnable_period[r] for r in writer_runnables)

        for (cons_comp, cons_port) in peers:
            cons = ports.get((cons_comp, cons_port))
            if not cons or (cons.port_direction or "").strip().upper() != "R":
                continue
            reader_runnables = port_readers.get((cons_comp, cons_port), [])
            if not reader_runnables:
                continue
            consumer_period = min(runnable_period[r] for r in reader_runnables)

            if consumer_period < producer_period:
                findings.append(Finding("CORE-050-SR-CONSUMER-FASTER", Severity.WARNING,
                                        f"SR consumer '{cons_comp}/{cons_port}' runs at {consumer_period}ms < producer '{prov_comp}/{prov_port}' at {producer_period}ms.",
                                        suggestion="Consumer may read stale data on some cycles."))
            elif producer_period < consumer_period:
                findings.append(Finding("CORE-051-SR-PRODUCER-FASTER", Severity.WARNING,
                                        f"SR producer '{prov_comp}/{prov_port}' runs at {producer_period}ms < consumer '{cons_comp}/{cons_port}' at {consumer_period}ms.",
                                        suggestion="Producer may overwrite values before consumer reads them."))
    return findings
