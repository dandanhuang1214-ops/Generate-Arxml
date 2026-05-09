from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import yaml
from lxml import etree

from arxml_codegen.models.schema import (
    ComponentRow,
    DataTypeRow,
    OperationRow,
    PortInterfaceRow,
    PortRow,
    RunnableEventRow,
    RunnableRow,
    ValidationResult,
    WorkbookModel,
)

NS = "http://autosar.org/schema/r4.0"
NSMAP = {None: NS, "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
XSI = "http://www.w3.org/2001/XMLSchema-instance"

TYPE_MAPPING_REF = "/DataTypes/DataTypeMappings/DataTypeMappingsSet"

BASE_TYPES = {
    "boolean": ("boolean", "8", "BOOLEAN"),
    "bool": ("boolean", "8", "BOOLEAN"),
    "uint8": ("uint8", "8", "NONE"),
    "uint16": ("uint16", "16", "NONE"),
    "uint32": ("uint32", "32", "NONE"),
    "sint8": ("sint8", "8", "2C"),
    "sint16": ("sint16", "16", "2C"),
    "sint32": ("sint32", "32", "2C"),
    "float32": ("float32", "32", "IEEE754"),
}


@dataclass(slots=True)
class GeneratorConfig:
    workbook: Path
    output: Path
    report: Path
    matlab_init: Path | None
    autosar_version: str = "4-3-0"
    template: Path | None = None


def load_config(path: Path) -> GeneratorConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    base_dir = path.parent.parent
    workbook = _resolve(base_dir, data["excel"]["workbook"])
    output = _resolve(base_dir, data["generation"]["output"])
    report = _resolve(base_dir, data["generation"].get("report", "output/generation_report.md"))
    matlab_value = data["generation"].get("matlab_init", "output/init_autosar_types.m")
    template_value = data.get("template", {}).get("arxml")
    return GeneratorConfig(
        workbook=workbook,
        output=output,
        report=report,
        matlab_init=_resolve(base_dir, matlab_value) if matlab_value else None,
        autosar_version=str(data["generation"].get("autosar_version", "4-3-0")),
        template=_resolve(base_dir, template_value) if template_value else None,
    )


def _resolve(base_dir: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base_dir / path).resolve()


def validate_model(model: WorkbookModel) -> ValidationResult:
    result = ValidationResult()
    components = {row.component_name for row in model.components}
    data_types = {row.adt_name for row in model.data_types}
    interfaces = {row.interface_name: row for row in model.port_interfaces}
    ports = {(row.component_name, row.port_name): row for row in model.ports}
    operations = {(row.interface_name, row.operation_name) for row in model.operations}
    runnables = {(row.component_name, row.runnable_name) for row in model.runnables}

    _require_unique(result, "Component", [row.component_name for row in model.components])
    _require_unique(result, "DataType ADT", [row.adt_name for row in model.data_types])
    _require_unique(result, "PortInterface", [row.interface_name for row in model.port_interfaces])
    _require_unique(
        result,
        "Port",
        [f"{row.component_name}/{row.port_name}" for row in model.ports],
    )

    for row in model.components:
        if not row.component_name:
            result.errors.append("Components: ComponentName is required.")
        if not row.package_path.startswith("/"):
            result.errors.append(f"Components/{row.component_name}: PackagePath must start with '/'.")

    for row in model.data_types:
        if not row.adt_name or not row.idt_name or not row.base_type:
            result.errors.append(f"DataTypes/{row.adt_name or '<blank>'}: ADTName, IDTName and BaseType are required.")
        if _base_key(row.base_type) not in BASE_TYPES:
            result.errors.append(f"DataTypes/{row.adt_name}: unsupported BaseType '{row.base_type}'.")

    for row in model.port_interfaces:
        kind = row.interface_kind.upper()
        if kind not in {"SR", "CS"}:
            result.errors.append(f"PortInterfaces/{row.interface_name}: InterfaceKind must be SR or CS.")
        if kind == "SR" and not row.data_element_name:
            result.errors.append(f"PortInterfaces/{row.interface_name}: SR interface needs DataElementName.")
        if kind == "SR" and row.data_type_adt not in data_types:
            result.errors.append(f"PortInterfaces/{row.interface_name}: SR interface needs known DataTypeADT.")
        if kind == "CS" and not any(op.interface_name == row.interface_name for op in model.operations):
            result.errors.append(f"PortInterfaces/{row.interface_name}: CS interface needs at least one Operation row.")

    for row in model.operations:
        if row.interface_name not in interfaces:
            result.errors.append(f"Operations/{row.interface_name}/{row.operation_name}: interface does not exist.")
        if row.argument_direction.upper() not in {"IN", "OUT", "INOUT"}:
            result.errors.append(f"Operations/{row.interface_name}/{row.operation_name}: ArgumentDirection must be IN, OUT or INOUT.")
        if row.argument_adt not in data_types:
            result.errors.append(f"Operations/{row.interface_name}/{row.operation_name}/{row.argument_name}: unknown ADT '{row.argument_adt}'.")

    for row in model.ports:
        if row.component_name not in components:
            result.errors.append(f"Ports/{row.component_name}/{row.port_name}: component does not exist.")
        if row.interface_name not in interfaces:
            result.errors.append(f"Ports/{row.component_name}/{row.port_name}: interface '{row.interface_name}' does not exist.")
            continue
        iface = interfaces[row.interface_name]
        if row.interface_kind.upper() != iface.interface_kind.upper():
            result.errors.append(f"Ports/{row.component_name}/{row.port_name}: InterfaceKind does not match PortInterfaces.")
        if row.port_direction.upper() not in {"P", "R"}:
            result.errors.append(f"Ports/{row.component_name}/{row.port_name}: PortDirection must be P or R.")
        if iface.interface_kind.upper() == "CS" and row.operation_name and (row.interface_name, row.operation_name) not in operations:
            result.errors.append(f"Ports/{row.component_name}/{row.port_name}: operation '{row.operation_name}' does not exist.")

    for row in model.runnable_events:
        if (row.component_name, row.runnable_name) not in runnables:
            result.errors.append(f"RunnableEvents/{row.component_name}/{row.runnable_name}: runnable does not exist.")
        trigger = _trigger_key(row.trigger_type)
        if trigger not in {"init", "periodic", "operationinvoked", "datareceived"}:
            result.errors.append(f"RunnableEvents/{row.component_name}/{row.runnable_name}: unsupported TriggerType '{row.trigger_type}'.")
        if trigger == "operationinvoked":
            port = ports.get((row.component_name, row.port_name))
            if not port or port.interface_kind.upper() != "CS" or port.port_direction.upper() != "P":
                result.errors.append(f"RunnableEvents/{row.component_name}/{row.runnable_name}: OperationInvoked needs a C/S P-Port.")
        if trigger == "datareceived":
            port = ports.get((row.component_name, row.port_name))
            if not port or port.interface_kind.upper() != "SR" or port.port_direction.upper() != "R":
                result.errors.append(f"RunnableEvents/{row.component_name}/{row.runnable_name}: DataReceived needs an S/R R-Port.")

    for row in model.composition_connectors:
        if row.provider_component not in components:
            result.errors.append(f"CompositionConnectors/{row.provider_component}/{row.provider_port}: provider component does not exist.")
        if row.requester_component not in components:
            result.errors.append(f"CompositionConnectors/{row.requester_component}/{row.requester_port}: requester component does not exist.")
        if (row.provider_component, row.provider_port) not in ports:
            result.errors.append(f"CompositionConnectors/{row.provider_component}/{row.provider_port}: provider port does not exist.")
        if (row.requester_component, row.requester_port) not in ports:
            result.errors.append(f"CompositionConnectors/{row.requester_component}/{row.requester_port}: requester port does not exist.")

    connected = {
        (row.provider_component, row.provider_port)
        for row in model.composition_connectors
    } | {
        (row.requester_component, row.requester_port)
        for row in model.composition_connectors
    }
    for row in model.ports:
        if (row.component_name, row.port_name) not in connected:
            result.warnings.append(f"Unconnected port: {row.component_name}/{row.port_name}")

    return result


def build_arxml(model: WorkbookModel, autosar_version: str = "4-3-0") -> etree._ElementTree:
    validation = validate_model(model)
    if not validation.ok:
        raise ValueError("Input validation failed:\n" + "\n".join(validation.errors))

    root = etree.Element(f"{{{NS}}}AUTOSAR", nsmap=NSMAP)
    root.set(f"{{{XSI}}}schemaLocation", f"http://autosar.org/schema/r4.0 AUTOSAR_{autosar_version}.xsd")
    packages = _el(root, "AR-PACKAGES")

    _write_platform_types(packages, model.data_types)
    _write_data_types(packages, model.data_types)
    _write_interfaces(packages, model)
    _write_components(packages, model)
    return etree.ElementTree(root)


def write_outputs(model: WorkbookModel, config: GeneratorConfig) -> ValidationResult:
    validation = validate_model(model)
    config.report.parent.mkdir(parents=True, exist_ok=True)
    config.report.write_text(build_report(model, validation), encoding="utf-8")
    if not validation.ok:
        raise ValueError(f"Input validation failed. See report: {config.report}")

    tree = build_arxml(model, config.autosar_version)
    config.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(config.output), pretty_print=True, xml_declaration=True, encoding="utf-8")
    if config.matlab_init:
        config.matlab_init.parent.mkdir(parents=True, exist_ok=True)
        config.matlab_init.write_text(build_matlab_init(model), encoding="utf-8")
    return validation


def write_arxml(model: WorkbookModel, output_path: Path) -> None:
    tree = build_arxml(model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_path), pretty_print=True, xml_declaration=True, encoding="utf-8")


def build_report(model: WorkbookModel, validation: ValidationResult) -> str:
    lines = [
        "# ARXML Generation Report",
        "",
        "## Summary",
        f"- Components: {len(model.components)}",
        f"- DataTypes: {len(model.data_types)}",
        f"- PortInterfaces: {len(model.port_interfaces)}",
        f"- Operations arguments: {len(model.operations)}",
        f"- Ports: {len(model.ports)}",
        f"- Runnables: {len(model.runnables)}",
        f"- RunnableEvents: {len(model.runnable_events)}",
        f"- CompositionConnectors: {len(model.composition_connectors)}",
        "",
        "## Errors",
    ]
    lines.extend([f"- {item}" for item in validation.errors] or ["- None"])
    lines.extend(["", "## Warnings"])
    lines.extend([f"- {item}" for item in validation.warnings] or ["- None"])
    lines.extend(["", "## Simulink Notes"])
    lines.append("- C/S Function Caller names should align with the imported runnable/function names.")
    lines.append("- Generated `init_autosar_types.m` creates AliasType objects for primitive ADTs.")
    return "\n".join(lines) + "\n"


def build_matlab_init(model: WorkbookModel) -> str:
    lines = [
        "% Auto-generated by arxml-codegen.",
        "% Run this before updating imported Simulink AUTOSAR models.",
        "",
    ]
    for row in sorted(model.data_types, key=lambda item: item.adt_name):
        base = _matlab_base_type(row.base_type)
        lines.extend(
            [
                f"if ~exist('{row.adt_name}', 'var')",
                f"    {row.adt_name} = Simulink.AliasType;",
                f"    {row.adt_name}.BaseType = '{base}';",
                "end",
                "",
            ]
        )
    return "\n".join(lines)


def _write_platform_types(packages: etree._Element, data_types: list[DataTypeRow]) -> None:
    base_pkg = _package(packages, "/AUTOSAR_Platform/BaseTypes")
    base_elements = _elements(base_pkg)
    needed = {_base_key(row.base_type) for row in data_types}
    for base_key in sorted(needed):
        short_name, size, encoding = BASE_TYPES[base_key]
        base_type = _el(base_elements, "SW-BASE-TYPE", uuid=_uuid())
        _el(base_type, "SHORT-NAME", short_name)
        _el(base_type, "CATEGORY", "FIXED_LENGTH")
        _el(base_type, "BASE-TYPE-SIZE", size)
        _el(base_type, "BASE-TYPE-ENCODING", encoding)
        _el(base_type, "NATIVE-DECLARATION", short_name)


def _write_data_types(packages: etree._Element, data_types: list[DataTypeRow]) -> None:
    app_pkg = _package(packages, "/DataTypes/ApplicationDataTypes")
    impl_pkg = _package(packages, "/DataTypes/ImplementationDataTypes")
    compu_pkg = _package(packages, "/DataTypes/CompuMethods")
    mapping_pkg = _package(packages, "/DataTypes/DataTypeMappings")
    app_elements = _elements(app_pkg)
    impl_elements = _elements(impl_pkg)
    compu_elements = _elements(compu_pkg)
    mapping_elements = _elements(mapping_pkg)

    mapping_set = _el(mapping_elements, "DATA-TYPE-MAPPING-SET", uuid=_uuid())
    _el(mapping_set, "SHORT-NAME", "DataTypeMappingsSet")
    maps = _el(mapping_set, "DATA-TYPE-MAPS")
    written_compu_methods: set[str] = set()

    for row in data_types:
        compu_name = row.compu_method or (f"{row.adt_name}_CompuMethod" if row.value_definition else "")

        adt = _el(app_elements, "APPLICATION-PRIMITIVE-DATA-TYPE", uuid=_uuid())
        _el(adt, "SHORT-NAME", row.adt_name)
        _el(adt, "CATEGORY", "VALUE" if not _is_boolean(row.base_type) else "BOOLEAN")
        props = _el(adt, "SW-DATA-DEF-PROPS")
        variants = _el(props, "SW-DATA-DEF-PROPS-VARIANTS")
        conditional = _el(variants, "SW-DATA-DEF-PROPS-CONDITIONAL")
        _el(conditional, "SW-CALIBRATION-ACCESS", "READ-ONLY")
        if compu_name:
            _el(conditional, "COMPU-METHOD-REF", f"/DataTypes/CompuMethods/{compu_name}", DEST="COMPU-METHOD")

        idt = _el(impl_elements, "IMPLEMENTATION-DATA-TYPE", uuid=_uuid())
        _el(idt, "SHORT-NAME", row.idt_name)
        _el(idt, "CATEGORY", "VALUE")
        props = _el(idt, "SW-DATA-DEF-PROPS")
        variants = _el(props, "SW-DATA-DEF-PROPS-VARIANTS")
        conditional = _el(variants, "SW-DATA-DEF-PROPS-CONDITIONAL")
        _el(conditional, "BASE-TYPE-REF", f"/AUTOSAR_Platform/BaseTypes/{_base_short_name(row.base_type)}", DEST="SW-BASE-TYPE")
        _el(conditional, "SW-CALIBRATION-ACCESS", "READ-ONLY")
        if compu_name:
            _el(conditional, "COMPU-METHOD-REF", f"/DataTypes/CompuMethods/{compu_name}", DEST="COMPU-METHOD")
        _el(idt, "TYPE-EMITTER", "RTE")

        if compu_name and compu_name not in written_compu_methods:
            _write_compu_method(compu_elements, compu_name, row)
            written_compu_methods.add(compu_name)

        type_map = _el(maps, "DATA-TYPE-MAP")
        _el(type_map, "APPLICATION-DATA-TYPE-REF", f"/DataTypes/ApplicationDataTypes/{row.adt_name}", DEST="APPLICATION-PRIMITIVE-DATA-TYPE")
        _el(type_map, "IMPLEMENTATION-DATA-TYPE-REF", f"/DataTypes/ImplementationDataTypes/{row.idt_name}", DEST="IMPLEMENTATION-DATA-TYPE")


def _write_compu_method(parent: etree._Element, name: str, row: DataTypeRow) -> None:
    compu = _el(parent, "COMPU-METHOD", uuid=_uuid())
    _el(compu, "SHORT-NAME", name)
    _el(compu, "CATEGORY", "TEXTTABLE" if row.value_definition else "IDENTICAL")
    if not row.value_definition:
        return
    internal = _el(compu, "COMPU-INTERNAL-TO-PHYS")
    scales = _el(internal, "COMPU-SCALES")
    for raw, text in _parse_value_definition(row.value_definition):
        scale = _el(scales, "COMPU-SCALE")
        _el(scale, "LOWER-LIMIT", raw, **{"INTERVAL-TYPE": "CLOSED"})
        _el(scale, "UPPER-LIMIT", raw, **{"INTERVAL-TYPE": "CLOSED"})
        const = _el(scale, "COMPU-CONST")
        _el(const, "VT", text)


def _write_interfaces(packages: etree._Element, model: WorkbookModel) -> None:
    sr_pkg = _package(packages, "/PortInterfaces/SRport")
    cs_pkg = _package(packages, "/PortInterfaces/CSport")
    sr_elements = _elements(sr_pkg)
    cs_elements = _elements(cs_pkg)
    operations_by_interface = _group_operations(model.operations)
    first_arg_by_sr_interface = _sr_type_lookup(model)

    for row in sorted(model.port_interfaces, key=lambda item: item.interface_name):
        if row.interface_kind.upper() == "SR":
            sr = _el(sr_elements, "SENDER-RECEIVER-INTERFACE", uuid=_uuid())
            _el(sr, "SHORT-NAME", row.interface_name)
            _el(sr, "IS-SERVICE", "false")
            data_elements = _el(sr, "DATA-ELEMENTS")
            variable = _el(data_elements, "VARIABLE-DATA-PROTOTYPE", uuid=_uuid())
            _el(variable, "SHORT-NAME", row.data_element_name)
            adt = first_arg_by_sr_interface.get(row.interface_name)
            _el(variable, "TYPE-TREF", f"/DataTypes/ApplicationDataTypes/{adt}", DEST="APPLICATION-PRIMITIVE-DATA-TYPE")
        else:
            cs = _el(cs_elements, "CLIENT-SERVER-INTERFACE", uuid=_uuid())
            _el(cs, "SHORT-NAME", row.interface_name)
            _el(cs, "IS-SERVICE", "false")
            operations = _el(cs, "OPERATIONS")
            for operation_name, args in operations_by_interface[row.interface_name].items():
                operation = _el(operations, "CLIENT-SERVER-OPERATION", uuid=_uuid())
                _el(operation, "SHORT-NAME", operation_name)
                args_node = _el(operation, "ARGUMENTS")
                for arg in args:
                    arg_node = _el(args_node, "ARGUMENT-DATA-PROTOTYPE", uuid=_uuid())
                    _el(arg_node, "SHORT-NAME", arg.argument_name)
                    _el(arg_node, "TYPE-TREF", f"/DataTypes/ApplicationDataTypes/{arg.argument_adt}", DEST="APPLICATION-PRIMITIVE-DATA-TYPE")
                    _el(arg_node, "DIRECTION", arg.argument_direction.upper())
                    _el(arg_node, "SERVER-ARGUMENT-IMPL-POLICY", "USE-ARGUMENT-TYPE")


def _write_components(packages: etree._Element, model: WorkbookModel) -> None:
    component_by_name = {row.component_name: row for row in model.components}
    runnables_by_component = _group_by(model.runnables, lambda row: row.component_name)
    events_by_component = _group_by(model.runnable_events, lambda row: row.component_name)
    ports_by_component = _group_by(model.ports, lambda row: row.component_name)

    for component in model.components:
        pkg = _package(packages, component.package_path)
        elements = _elements(pkg)
        if component.is_composition:
            comp = _el(elements, "COMPOSITION-SW-COMPONENT-TYPE", uuid=_uuid())
            _el(comp, "SHORT-NAME", component.component_name)
            _write_composition_content(comp, component, component_by_name, model)
        else:
            swc = _el(elements, "APPLICATION-SW-COMPONENT-TYPE", uuid=_uuid())
            _el(swc, "SHORT-NAME", component.component_name)
            ports_node = _el(swc, "PORTS")
            for port in ports_by_component.get(component.component_name, []):
                _write_port(ports_node, port)
            _write_internal_behavior(swc, component, runnables_by_component.get(component.component_name, []), events_by_component.get(component.component_name, []), ports_by_component.get(component.component_name, []))


def _write_port(parent: etree._Element, port: PortRow) -> None:
    kind = port.interface_kind.upper()
    direction = port.port_direction.upper()
    if direction == "R":
        node = _el(parent, "R-PORT-PROTOTYPE", uuid=_uuid())
        _el(node, "SHORT-NAME", port.port_name)
        if kind == "SR":
            specs = _el(node, "REQUIRED-COM-SPECS")
            spec = _el(specs, "NONQUEUED-RECEIVER-COM-SPEC")
            _el(spec, "DATA-ELEMENT-REF", f"/PortInterfaces/SRport/{port.interface_name}/{port.data_element_name}", DEST="VARIABLE-DATA-PROTOTYPE")
            _el(spec, "ALIVE-TIMEOUT", "0")
            _el(spec, "ENABLE-UPDATE", "false")
            _el(spec, "HANDLE-NEVER-RECEIVED", "false")
            _el(node, "REQUIRED-INTERFACE-TREF", f"/PortInterfaces/SRport/{port.interface_name}", DEST="SENDER-RECEIVER-INTERFACE")
        else:
            specs = _el(node, "REQUIRED-COM-SPECS")
            spec = _el(specs, "CLIENT-COM-SPEC")
            _el(spec, "OPERATION-REF", f"/PortInterfaces/CSport/{port.interface_name}/{port.operation_name}", DEST="CLIENT-SERVER-OPERATION")
            _el(node, "REQUIRED-INTERFACE-TREF", f"/PortInterfaces/CSport/{port.interface_name}", DEST="CLIENT-SERVER-INTERFACE")
    else:
        node = _el(parent, "P-PORT-PROTOTYPE", uuid=_uuid())
        _el(node, "SHORT-NAME", port.port_name)
        if kind == "SR":
            specs = _el(node, "PROVIDED-COM-SPECS")
            spec = _el(specs, "NONQUEUED-SENDER-COM-SPEC")
            _el(spec, "DATA-ELEMENT-REF", f"/PortInterfaces/SRport/{port.interface_name}/{port.data_element_name}", DEST="VARIABLE-DATA-PROTOTYPE")
            _el(node, "PROVIDED-INTERFACE-TREF", f"/PortInterfaces/SRport/{port.interface_name}", DEST="SENDER-RECEIVER-INTERFACE")
        else:
            specs = _el(node, "PROVIDED-COM-SPECS")
            spec = _el(specs, "SERVER-COM-SPEC")
            _el(spec, "OPERATION-REF", f"/PortInterfaces/CSport/{port.interface_name}/{port.operation_name}", DEST="CLIENT-SERVER-OPERATION")
            _el(spec, "QUEUE-LENGTH", "1")
            _el(node, "PROVIDED-INTERFACE-TREF", f"/PortInterfaces/CSport/{port.interface_name}", DEST="CLIENT-SERVER-INTERFACE")


def _write_internal_behavior(parent: etree._Element, component: ComponentRow, runnables: list[RunnableRow], events: list[RunnableEventRow], ports: list[PortRow]) -> None:
    behavior = _el(_el(parent, "INTERNAL-BEHAVIORS"), "SWC-INTERNAL-BEHAVIOR", uuid=_uuid())
    behavior_name = f"{component.component_name}_InternalBehavior"
    _el(behavior, "SHORT-NAME", behavior_name)
    mapping_refs = _el(behavior, "DATA-TYPE-MAPPING-REFS")
    _el(mapping_refs, "DATA-TYPE-MAPPING-REF", TYPE_MAPPING_REF, DEST="DATA-TYPE-MAPPING-SET")
    events_node = _el(behavior, "EVENTS")
    runnables_node = _el(behavior, "RUNNABLES")
    _el(behavior, "SUPPORTS-MULTIPLE-INSTANTIATION", "false")
    port_map = {port.port_name: port for port in ports}

    for runnable in runnables:
        node = _el(runnables_node, "RUNNABLE-ENTITY", uuid=_uuid())
        _el(node, "SHORT-NAME", runnable.runnable_name)
        _el(node, "MINIMUM-START-INTERVAL", "0")
        _el(node, "CAN-BE-INVOKED-CONCURRENTLY", "false")
        _el(node, "SYMBOL", runnable.symbol or runnable.runnable_name)

    for event in events:
        runnable_ref = f"{component.package_path}/{component.component_name}/{behavior_name}/{event.runnable_name}"
        trigger = _trigger_key(event.trigger_type)
        if trigger == "init":
            node = _el(events_node, "INIT-EVENT", uuid=_uuid())
            _el(node, "SHORT-NAME", f"IE_{event.runnable_name}")
            _el(node, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
        elif trigger == "periodic":
            node = _el(events_node, "TIMING-EVENT", uuid=_uuid())
            _el(node, "SHORT-NAME", f"TE_{event.runnable_name}")
            _el(node, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
            _el(node, "PERIOD", _period_to_seconds(event.period_ms))
        elif trigger == "operationinvoked":
            port = port_map[event.port_name]
            node = _el(events_node, "OPERATION-INVOKED-EVENT", uuid=_uuid())
            _el(node, "SHORT-NAME", f"OIT_{event.runnable_name}_{event.operation_name}")
            _el(node, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
            iref = _el(node, "OPERATION-IREF")
            _el(iref, "CONTEXT-P-PORT-REF", f"{component.package_path}/{component.component_name}/{event.port_name}", DEST="P-PORT-PROTOTYPE")
            _el(iref, "TARGET-PROVIDED-OPERATION-REF", f"/PortInterfaces/CSport/{port.interface_name}/{event.operation_name}", DEST="CLIENT-SERVER-OPERATION")
        elif trigger == "datareceived":
            port = port_map[event.port_name]
            node = _el(events_node, "DATA-RECEIVED-EVENT", uuid=_uuid())
            _el(node, "SHORT-NAME", f"DRE_{event.runnable_name}_{event.port_name}")
            _el(node, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
            iref = _el(node, "DATA-IREF")
            _el(iref, "CONTEXT-R-PORT-REF", f"{component.package_path}/{component.component_name}/{event.port_name}", DEST="R-PORT-PROTOTYPE")
            _el(iref, "TARGET-DATA-ELEMENT-REF", f"/PortInterfaces/SRport/{port.interface_name}/{port.data_element_name}", DEST="VARIABLE-DATA-PROTOTYPE")


def _write_composition_content(parent: etree._Element, composition: ComponentRow, component_by_name: dict[str, ComponentRow], model: WorkbookModel) -> None:
    components_node = _el(parent, "COMPONENTS")
    for component in model.components:
        if component.is_composition:
            continue
        proto = _el(components_node, "SW-COMPONENT-PROTOTYPE", uuid=_uuid())
        _el(proto, "SHORT-NAME", component.component_name)
        _el(proto, "TYPE-TREF", f"{component.package_path}/{component.component_name}", DEST="APPLICATION-SW-COMPONENT-TYPE")

    connectors = [row for row in model.composition_connectors if row.composition_name in {"", composition.component_name}]
    if connectors:
        connectors_node = _el(parent, "CONNECTORS")
        for row in connectors:
            provider = component_by_name[row.provider_component]
            requester = component_by_name[row.requester_component]
            connector = _el(connectors_node, "ASSEMBLY-SW-CONNECTOR", uuid=_uuid())
            _el(connector, "SHORT-NAME", f"{row.provider_component}_{row.provider_port}_TO_{row.requester_component}_{row.requester_port}")
            provider_iref = _el(connector, "PROVIDER-IREF")
            _el(provider_iref, "CONTEXT-COMPONENT-REF", f"{composition.package_path}/{composition.component_name}/{row.provider_component}", DEST="SW-COMPONENT-PROTOTYPE")
            _el(provider_iref, "TARGET-P-PORT-REF", f"{provider.package_path}/{row.provider_component}/{row.provider_port}", DEST="P-PORT-PROTOTYPE")
            requester_iref = _el(connector, "REQUESTER-IREF")
            _el(requester_iref, "CONTEXT-COMPONENT-REF", f"{composition.package_path}/{composition.component_name}/{row.requester_component}", DEST="SW-COMPONENT-PROTOTYPE")
            _el(requester_iref, "TARGET-R-PORT-REF", f"{requester.package_path}/{row.requester_component}/{row.requester_port}", DEST="R-PORT-PROTOTYPE")


def _group_operations(rows: list[OperationRow]) -> dict[str, dict[str, list[OperationRow]]]:
    result: dict[str, dict[str, list[OperationRow]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        result[row.interface_name][row.operation_name].append(row)
    return result


def _sr_type_lookup(model: WorkbookModel) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for iface in model.port_interfaces:
        if iface.interface_kind.upper() != "SR":
            continue
        lookup[iface.interface_name] = iface.data_type_adt
    return lookup


def _group_by(rows, key_func):
    grouped = defaultdict(list)
    for row in rows:
        grouped[key_func(row)].append(row)
    return grouped


def _parse_value_definition(value: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for part in value.replace("\n", ";").split(";"):
        item = part.strip()
        if not item:
            continue
        if ":" in item:
            raw, text = item.split(":", 1)
        elif "=" in item:
            raw, text = item.split("=", 1)
        else:
            raw, text = item, item
        pairs.append((raw.strip(), text.strip()))
    return pairs


def _require_unique(result: ValidationResult, label: str, values: list[str]) -> None:
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        if value in seen:
            result.errors.append(f"{label} '{value}' is duplicated.")
        seen.add(value)


def _uuid() -> str:
    return str(uuid4()).upper()


def _el(parent: etree._Element, name: str, text: str | None = None, **attrs: str) -> etree._Element:
    element = etree.SubElement(parent, f"{{{NS}}}{name}")
    for key, value in attrs.items():
        if key == "uuid":
            element.set("UUID", value)
        else:
            element.set(key, value)
    if text is not None:
        element.text = text
    return element


def _package(root_packages: etree._Element, path: str) -> etree._Element:
    parts = [part for part in path.strip("/").split("/") if part]
    current_parent = root_packages
    current_pkg = None
    for part in parts:
        found = None
        for candidate in current_parent.findall(f"{{{NS}}}AR-PACKAGE"):
            sn = candidate.find(f"{{{NS}}}SHORT-NAME")
            if sn is not None and sn.text == part:
                found = candidate
                break
        if found is None:
            found = _el(current_parent, "AR-PACKAGE")
            _el(found, "SHORT-NAME", part)
            _el(found, "ELEMENTS")
            _el(found, "AR-PACKAGES")
        current_pkg = found
        nested = current_pkg.find(f"{{{NS}}}AR-PACKAGES")
        if nested is None:
            nested = _el(current_pkg, "AR-PACKAGES")
        current_parent = nested
    if current_pkg is None:
        raise ValueError(f"Invalid package path: {path}")
    return current_pkg


def _elements(pkg: etree._Element) -> etree._Element:
    elements = pkg.find(f"{{{NS}}}ELEMENTS")
    if elements is None:
        elements = _el(pkg, "ELEMENTS")
    return elements


def _base_key(value: str) -> str:
    return value.strip().lower()


def _base_short_name(value: str) -> str:
    return BASE_TYPES[_base_key(value)][0]


def _is_boolean(value: str) -> bool:
    return _base_key(value) in {"boolean", "bool"}


def _matlab_base_type(value: str) -> str:
    base_key = _base_key(value)
    if base_key == "bool":
        return "boolean"
    return "single" if base_key == "float32" else base_key


def _trigger_key(value: str) -> str:
    return value.strip().replace(" ", "").replace("_", "").lower()


def _period_to_seconds(period_ms: str) -> str:
    if not period_ms:
        return "0.01"
    value = float(period_ms)
    return f"{value / 1000:.6f}".rstrip("0").rstrip(".")
