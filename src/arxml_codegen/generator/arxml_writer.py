from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import yaml
from lxml import etree

from arxml_codegen.models.schema import UnitRow, WorkbookV2Model

NS = "http://autosar.org/schema/r4.0"
NSMAP = {None: NS, "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
XSI = "http://www.w3.org/2001/XMLSchema-instance"

BASE_TYPES = {
    "boolean": ("boolean", "8", "BOOLEAN"),
    "uint8": ("uint8", "8", "NONE"),
    "uint16": ("uint16", "16", "NONE"),
    "uint32": ("uint32", "32", "NONE"),
    "uint64": ("uint64", "64", "NONE"),
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


def load_config(path: Path) -> GeneratorConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    base_dir = path.parent.parent
    workbook = _resolve(base_dir, data["excel"]["workbook"])
    output = _resolve(base_dir, data["generation"]["output"])
    report = _resolve(base_dir, data["generation"].get("report", "output/generation_report.md"))
    matlab_value = data["generation"].get("matlab_init", "output/init_autosar_types.m")
    return GeneratorConfig(
        workbook=workbook,
        output=output,
        report=report,
        matlab_init=_resolve(base_dir, matlab_value) if matlab_value else None,
        autosar_version=str(data["generation"].get("autosar_version", "4-3-0")),
    )


def _resolve(base_dir: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base_dir / path).resolve()


def write_outputs(model: WorkbookV2Model, config: GeneratorConfig) -> None:
    write_arxml_v2(model, config.output)
    _write_report(config.report, model, [])


def _write_report(path: Path, model: WorkbookV2Model, errors: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ARXML Generation Report",
        "",
        "## Summary",
        "",
        f"- Components: {len(model.components)}",
        f"- Component prototypes: {len(model.component_prototypes)}",
        f"- Primitive data types: {len(model.primitive_data_types)}",
        f"- Record types: {len(model.record_types)}",
        f"- SR interfaces: {len(model.sr_interfaces)}",
        f"- CS interfaces: {len(model.cs_interfaces)}",
        f"- Ports: {len(model.ports)}",
        f"- Runnables: {len(model.runnables)}",
        f"- Runnable events: {len(model.runnable_events)}",
        f"- Runnable accesses: {len(model.runnable_accesses)}",
        f"- Composition connectors: {len(model.composition_connectors)}",
        "",
        "## Validation",
        "",
    ]
    if errors:
        lines.extend(f"- ERROR: {error}" for error in errors)
    else:
        lines.append("- No validation errors.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_arxml_v2(model: WorkbookV2Model) -> etree._ElementTree:
    version = model.config("AutosarVersion", "4-3-0")
    root = etree.Element(f"{{{NS}}}AUTOSAR", nsmap=NSMAP)
    root.set(f"{{{XSI}}}schemaLocation", f"http://autosar.org/schema/r4.0 AUTOSAR_{version}.xsd")
    packages = _el(root, "AR-PACKAGES")

    _write_platform(packages, model)
    _write_units(packages, model)
    _write_compu_methods(packages, model)
    _write_data_constrs(packages, model)
    _write_application_types(packages, model)
    _write_custom_implementation_types(packages, model)
    _write_mapping_sets(packages, model)
    _write_interfaces(packages, model)
    _write_components(packages, model)
    return etree.ElementTree(root)


def write_arxml_v2(model: WorkbookV2Model, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    build_arxml_v2(model).write(str(output_path), pretty_print=True, xml_declaration=True, encoding="utf-8")


def summarize_v2(model: WorkbookV2Model) -> str:
    return (
        f"Loaded v2: {len(model.components)} components, "
        f"{len(model.component_prototypes)} prototypes, "
        f"{len(model.primitive_data_types)} primitive types, "
        f"{len(model.record_types)} record types, "
        f"{len(model.sr_interfaces)} SR interfaces, "
        f"{len(model.cs_interfaces)} CS interfaces, "
        f"{len(model.ports)} ports, "
        f"{len(model.runnables)} runnables, "
        f"{len(model.composition_connectors)} connectors."
    )


def validate_model_v2(model: WorkbookV2Model) -> list[str]:
    errors: list[str] = []
    components = {row.component_name: row for row in model.components}
    compositions = {row.component_name for row in model.components if row.component_kind.lower() == "composition"}
    sr_interfaces = {row.interface_path: row for row in model.sr_interfaces}
    cs_interfaces = {row.interface_path: row for row in model.cs_interfaces}
    cs_operations = {(row.interface_name, row.operation_name) for row in model.cs_operations}
    ports = {(row.component_name, row.port_name): row for row in model.ports}
    runnables = {(row.component_name, row.runnable_name) for row in model.runnables}
    prototypes = {(row.composition_name, row.prototype_name): row for row in model.component_prototypes}
    app_type_refs = {row.application_type_path for row in model.primitive_data_types}
    app_type_refs.update(row.application_type_path for row in model.record_types)
    impl_type_refs = {row.implementation_type_path for row in model.record_types}
    impl_type_refs.update(f"/AUTOSAR_Platform/ImplementationDataTypes/{name}" for name, _, _ in BASE_TYPES.values())

    def loc(row, field: str) -> str:
        return f"{row.source_sheet}!R{row.row_index} {field}:"

    for row in model.components:
        if not row.component_name:
            errors.append(f"{loc(row, 'ComponentName')} ComponentName is required.")
        if not row.package_path.startswith("/"):
            errors.append(f"{loc(row, 'PackagePath')} PackagePath must start with '/'.")
        if row.component_kind.lower() not in {"application", "composition"}:
            errors.append(f"{loc(row, 'ComponentKind')} ComponentKind must be Application or Composition.")

    seen_component_names: set[str] = set()
    for row in model.components:
        if row.component_name in seen_component_names:
            errors.append(f"{loc(row, 'ComponentName')} duplicated component name '{row.component_name}'.")
        seen_component_names.add(row.component_name)

    for row in model.component_prototypes:
        if row.composition_name not in compositions:
            errors.append(f"{loc(row, 'CompositionName')} unknown composition '{row.composition_name}'.")
        if row.component_type_name not in components:
            errors.append(f"{loc(row, 'ComponentTypeName')} unknown component type '{row.component_type_name}'.")
        if not row.component_type_ref:
            errors.append(f"{loc(row, 'ComponentTypeRef')} ComponentTypeRef is required.")

    for row in model.primitive_data_types:
        if not row.application_type_path.startswith("/"):
            errors.append(f"{loc(row, 'ApplicationTypePath')} ApplicationTypePath must start with '/'.")
        if not row.implementation_type_path.startswith("/"):
            errors.append(f"{loc(row, 'ImplementationTypePath')} ImplementationTypePath must start with '/'.")
        if row.base_type.lower() not in BASE_TYPES:
            errors.append(f"{loc(row, 'BaseType')} unsupported BaseType '{row.base_type}'.")

    for row in model.record_types:
        if not row.application_type_path.startswith("/"):
            errors.append(f"{loc(row, 'ApplicationTypePath')} ApplicationTypePath must start with '/'.")
        if not row.implementation_type_path.startswith("/"):
            errors.append(f"{loc(row, 'ImplementationTypePath')} ImplementationTypePath must start with '/'.")

    for row in model.record_elements:
        if row.application_element_type_ref not in app_type_refs:
            errors.append(f"{loc(row, 'ApplicationElementTypeRef')} unknown application data type ref '{row.application_element_type_ref}'.")
        if row.implementation_element_type_ref not in impl_type_refs:
            errors.append(f"{loc(row, 'ImplementationElementTypeRef')} unknown implementation data type ref '{row.implementation_element_type_ref}'.")

    for row in model.data_type_mappings:
        if row.application_type_ref not in app_type_refs:
            errors.append(f"{loc(row, 'ApplicationTypeRef')} unknown application data type ref '{row.application_type_ref}'.")
        if row.implementation_type_ref not in impl_type_refs:
            errors.append(f"{loc(row, 'ImplementationTypeRef')} unknown implementation data type ref '{row.implementation_type_ref}'.")

    for row in model.sr_data_elements:
        if row.application_type_ref not in app_type_refs:
            errors.append(f"{loc(row, 'ApplicationTypeRef')} unknown application data type ref '{row.application_type_ref}'.")

    for row in model.cs_arguments:
        if row.application_type_ref not in app_type_refs:
            errors.append(f"{loc(row, 'ApplicationTypeRef')} unknown application data type ref '{row.application_type_ref}'.")

    for row in model.ports:
        if row.component_name not in components:
            errors.append(f"{loc(row, 'ComponentName')} unknown component '{row.component_name}'.")
        if row.port_direction not in {"P", "R"}:
            errors.append(f"{loc(row, 'PortDirection')} PortDirection must be P or R.")
        if row.interface_kind == "SR":
            if row.interface_ref not in sr_interfaces:
                errors.append(f"{loc(row, 'InterfaceRef')} unknown SR interface ref '{row.interface_ref}'.")
            if row.operation_name:
                errors.append(f"{loc(row, 'OperationName')} SR port must not bind OperationName.")
        elif row.interface_kind == "CS":
            iface = cs_interfaces.get(row.interface_ref)
            if iface is None:
                errors.append(f"{loc(row, 'InterfaceRef')} unknown CS interface ref '{row.interface_ref}'.")
            elif (iface.interface_name, row.operation_name) not in cs_operations:
                errors.append(f"{loc(row, 'OperationName')} unknown CS operation '{row.operation_name}' on interface '{iface.interface_name}'.")
        else:
            errors.append(f"{loc(row, 'InterfaceKind')} InterfaceKind must be SR or CS.")

    seen_ports: set[tuple[str, str]] = set()
    for row in model.ports:
        key = (row.component_name, row.port_name)
        if key in seen_ports:
            errors.append(f"{loc(row, 'PortName')} duplicated port '{row.component_name}/{row.port_name}'.")
        seen_ports.add(key)

    for row in model.runnables:
        if row.component_name not in components:
            errors.append(f"{loc(row, 'ComponentName')} unknown component '{row.component_name}'.")

    seen_runnables: set[tuple[str, str]] = set()
    for row in model.runnables:
        key = (row.component_name, row.runnable_name)
        if key in seen_runnables:
            errors.append(f"{loc(row, 'RunnableName')} duplicated runnable '{row.component_name}/{row.runnable_name}'.")
        seen_runnables.add(key)

    for row in model.runnable_events:
        if (row.component_name, row.runnable_name) not in runnables:
            errors.append(f"{loc(row, 'RunnableName')} unknown runnable '{row.component_name}/{row.runnable_name}'.")
        if row.trigger_type not in {"Init", "Periodic", "OperationInvoked", "DataReceived"}:
            errors.append(f"{loc(row, 'TriggerType')} TriggerType must be Init, Periodic, OperationInvoked or DataReceived.")
        if row.port_name and (row.component_name, row.port_name) not in ports:
            errors.append(f"{loc(row, 'PortName')} unknown port '{row.component_name}/{row.port_name}'.")

    for row in model.runnable_accesses:
        if (row.component_name, row.runnable_name) not in runnables:
            errors.append(f"{loc(row, 'RunnableName')} unknown runnable '{row.component_name}/{row.runnable_name}'.")
        if row.port_name and (row.component_name, row.port_name) not in ports:
            errors.append(f"{loc(row, 'PortName')} unknown port '{row.component_name}/{row.port_name}'.")

    for row in model.composition_connectors:
        if row.composition_name not in compositions:
            errors.append(f"{loc(row, 'CompositionName')} unknown composition '{row.composition_name}'.")
            continue
        provider_proto = prototypes.get((row.composition_name, row.provider_prototype))
        requester_proto = prototypes.get((row.composition_name, row.requester_prototype))
        if provider_proto is None:
            errors.append(f"{loc(row, 'ProviderPrototype')} unknown provider prototype '{row.provider_prototype}'.")
            continue
        if requester_proto is None:
            errors.append(f"{loc(row, 'RequesterPrototype')} unknown requester prototype '{row.requester_prototype}'.")
            continue
        provider_port = ports.get((provider_proto.component_type_name, row.provider_port))
        requester_port = ports.get((requester_proto.component_type_name, row.requester_port))
        if provider_port is None:
            errors.append(f"{loc(row, 'ProviderPort')} unknown provider port '{provider_proto.component_type_name}/{row.provider_port}'.")
            continue
        if requester_port is None:
            errors.append(f"{loc(row, 'RequesterPort')} unknown requester port '{requester_proto.component_type_name}/{row.requester_port}'.")
            continue
        if provider_port.port_direction != "P" or requester_port.port_direction != "R":
            errors.append(f"{loc(row, 'ConnectorType')} assembly connector must connect P provider to R requester.")
        if provider_port.interface_kind != requester_port.interface_kind or provider_port.interface_ref != requester_port.interface_ref:
            errors.append(f"{loc(row, 'ConnectorType')} connector endpoints must use the same interface kind and InterfaceRef.")

    return errors


def _write_platform(packages: etree._Element, model: WorkbookV2Model) -> None:
    used = {row.base_type.lower() for row in model.primitive_data_types if row.base_type}
    for ref in [row.implementation_type_ref for row in model.data_type_mappings]:
        name = _short(ref).lower()
        if name in BASE_TYPES:
            used.add(name)

    base_elements = _elements(_package(packages, "/AUTOSAR_Platform/BaseTypes"))
    impl_elements = _elements(_package(packages, "/AUTOSAR_Platform/ImplementationDataTypes"))
    for key in sorted(used):
        if key not in BASE_TYPES:
            continue
        name, size, encoding = BASE_TYPES[key]
        base = _el(base_elements, "SW-BASE-TYPE", uuid=_uuid())
        _el(base, "SHORT-NAME", name)
        _el(base, "CATEGORY", "FIXED_LENGTH")
        _el(base, "BASE-TYPE-SIZE", size)
        _el(base, "BASE-TYPE-ENCODING", encoding)
        _el(base, "NATIVE-DECLARATION", name)

        impl = _el(impl_elements, "IMPLEMENTATION-DATA-TYPE", uuid=_uuid())
        _el(impl, "SHORT-NAME", name)
        _el(impl, "CATEGORY", "VALUE")
        props = _sw_props(impl)
        _el(props, "BASE-TYPE-REF", f"/AUTOSAR_Platform/BaseTypes/{name}", DEST="SW-BASE-TYPE")
        _el(props, "SW-CALIBRATION-ACCESS", "READ-ONLY")
        _el(impl, "TYPE-EMITTER", "RTE")


def _write_compu_methods(packages: etree._Element, model: WorkbookV2Model) -> None:
    scales = defaultdict(list)
    for row in model.compu_scales:
        scales[row.compu_method_name].append(row)
    for row in model.compu_methods:
        elements = _elements(_package(packages, _pkg(row.compu_method_path)))
        compu = _el(elements, "COMPU-METHOD", uuid=_uuid())
        _el(compu, "SHORT-NAME", _short(row.compu_method_path) or row.compu_method_name)
        _el(compu, "CATEGORY", row.category or "IDENTICAL")
        if row.category.upper() == "TEXTTABLE":
            internal = _el(compu, "COMPU-INTERNAL-TO-PHYS")
            scale_node = _el(internal, "COMPU-SCALES")
            for scale in scales.get(row.compu_method_name, []):
                sc = _el(scale_node, "COMPU-SCALE")
                _el(sc, "LOWER-LIMIT", scale.lower_limit, **{"INTERVAL-TYPE": "CLOSED"})
                _el(sc, "UPPER-LIMIT", scale.upper_limit or scale.lower_limit, **{"INTERVAL-TYPE": "CLOSED"})
                const = _el(sc, "COMPU-CONST")
                _el(const, "VT", scale.text_value)
        elif row.category.upper() == "LINEAR":
            internal = _el(compu, "COMPU-INTERNAL-TO-PHYS")
            scale_node = _el(internal, "COMPU-SCALES")
            scale = scales.get(row.compu_method_name, [None])[0]
            sc = _el(scale_node, "COMPU-SCALE")
            coeffs = _el(sc, "COMPU-RATIONAL-COEFFS")
            numerator = _el(coeffs, "COMPU-NUMERATOR")
            _el(numerator, "V", (scale.offset if scale and scale.offset else "0"))
            _el(numerator, "V", (scale.numerator if scale and scale.numerator else "1"))
            denominator = _el(coeffs, "COMPU-DENOMINATOR")
            _el(denominator, "V", (scale.denominator if scale and scale.denominator else "1"))


def _write_units(packages: etree._Element, model: WorkbookV2Model) -> None:
    if not model.units:
        return
    units_by_pkg: dict[str, list[UnitRow]] = defaultdict(list)
    for row in model.units:
        units_by_pkg[_pkg(row.unit_path or "/Units")].append(row)
    for pkg_path, rows in units_by_pkg.items():
        pkg = _package(packages, pkg_path)
        elements = _elements(pkg)
        for row in rows:
            unit = _el(elements, "UNIT", uuid=_uuid())
            _el(unit, "SHORT-NAME", row.unit_name)
            if row.display_name:
                _el(unit, "DISPLAY-NAME", row.display_name)
            _el(unit, "FACTOR-SI-TO-UNIT", row.factor_si_to_unit or "1")
            _el(unit, "OFFSET-SI-TO-UNIT", row.offset_si_to_unit or "0")


def _write_data_constrs(packages: etree._Element, model: WorkbookV2Model) -> None:
    for row in model.data_constrs:
        elements = _elements(_package(packages, _pkg(row.data_constr_path)))
        constr = _el(elements, "DATA-CONSTR", uuid=_uuid())
        _el(constr, "SHORT-NAME", _short(row.data_constr_path) or row.data_constr_name)
        rules = _el(constr, "DATA-CONSTR-RULES")
        rule = _el(rules, "DATA-CONSTR-RULE")
        internal = _el(rule, "INTERNAL-CONSTRS")
        _el(internal, "LOWER-LIMIT", row.lower_limit, **{"INTERVAL-TYPE": "CLOSED"})
        _el(internal, "UPPER-LIMIT", row.upper_limit, **{"INTERVAL-TYPE": "CLOSED"})


def _write_application_types(packages: etree._Element, model: WorkbookV2Model) -> None:
    for row in model.primitive_data_types:
        elements = _elements(_package(packages, _pkg(row.application_type_path)))
        adt = _el(elements, "APPLICATION-PRIMITIVE-DATA-TYPE", uuid=_uuid())
        _el(adt, "SHORT-NAME", _short(row.application_type_path) or row.application_type_name)
        _el(adt, "CATEGORY", "BOOLEAN" if row.base_type.lower() == "boolean" else "VALUE")
        props = _sw_props(adt)
        _el(props, "SW-CALIBRATION-ACCESS", row.calibration_access or "READ-ONLY")
        if row.compu_method_ref:
            _el(props, "COMPU-METHOD-REF", row.compu_method_ref, DEST="COMPU-METHOD")
        if row.data_constr_ref:
            _el(props, "DATA-CONSTR-REF", row.data_constr_ref, DEST="DATA-CONSTR")
        if row.unit_ref:
            _el(props, "UNIT-REF", row.unit_ref, DEST="UNIT")

    elements_by_record = defaultdict(list)
    for elem in model.record_elements:
        elements_by_record[elem.record_type_name].append(elem)
    for row in model.record_types:
        elements = _elements(_package(packages, _pkg(row.application_type_path)))
        record = _el(elements, "APPLICATION-RECORD-DATA-TYPE", uuid=_uuid())
        _el(record, "SHORT-NAME", _short(row.application_type_path) or row.application_type_name)
        _el(record, "CATEGORY", "STRUCTURE")
        rec_elems = _el(record, "ELEMENTS")
        for elem in sorted(elements_by_record.get(row.application_type_name, []), key=lambda item: int(item.order or 0)):
            app_elem = _el(rec_elems, "APPLICATION-RECORD-ELEMENT", uuid=_uuid())
            _el(app_elem, "SHORT-NAME", elem.element_name)
            _el(app_elem, "CATEGORY", "VALUE")
            _el(app_elem, "TYPE-TREF", elem.application_element_type_ref, DEST="APPLICATION-DATA-TYPE")


def _write_custom_implementation_types(packages: etree._Element, model: WorkbookV2Model) -> None:
    elements_by_record = defaultdict(list)
    for elem in model.record_elements:
        elements_by_record[elem.record_type_name].append(elem)
    for row in model.record_types:
        elements = _elements(_package(packages, _pkg(row.implementation_type_path)))
        impl = _el(elements, "IMPLEMENTATION-DATA-TYPE", uuid=_uuid())
        _el(impl, "SHORT-NAME", _short(row.implementation_type_path) or row.implementation_type_name)
        _el(impl, "CATEGORY", "STRUCTURE")
        subs = _el(impl, "SUB-ELEMENTS")
        for elem in sorted(elements_by_record.get(row.application_type_name, []), key=lambda item: int(item.order or 0)):
            sub = _el(subs, "IMPLEMENTATION-DATA-TYPE-ELEMENT", uuid=_uuid())
            _el(sub, "SHORT-NAME", elem.element_name)
            _el(sub, "CATEGORY", "TYPE_REFERENCE")
            props = _sw_props(sub)
            _el(props, "IMPLEMENTATION-DATA-TYPE-REF", elem.implementation_element_type_ref, DEST="IMPLEMENTATION-DATA-TYPE")
        _el(impl, "TYPE-EMITTER", "RTE")


def _write_mapping_sets(packages: etree._Element, model: WorkbookV2Model) -> None:
    grouped = defaultdict(list)
    default = model.config("DefaultMappingSetPath", "/ComponentTypes/MappingSets/APP_data_mapping")
    for row in model.data_type_mappings:
        grouped[row.mapping_set_path or default].append(row)
    for path, rows in grouped.items():
        elements = _elements(_package(packages, _pkg(path)))
        mapping = _el(elements, "DATA-TYPE-MAPPING-SET", uuid=_uuid())
        _el(mapping, "SHORT-NAME", _short(path))
        maps = _el(mapping, "DATA-TYPE-MAPS")
        for row in rows:
            m = _el(maps, "DATA-TYPE-MAP")
            _el(m, "APPLICATION-DATA-TYPE-REF", row.application_type_ref, DEST="APPLICATION-DATA-TYPE")
            _el(m, "IMPLEMENTATION-DATA-TYPE-REF", row.implementation_type_ref, DEST="IMPLEMENTATION-DATA-TYPE")


def _write_interfaces(packages: etree._Element, model: WorkbookV2Model) -> None:
    sr_elements = defaultdict(list)
    for row in model.sr_data_elements:
        sr_elements[row.interface_name].append(row)
    for row in model.sr_interfaces:
        elements = _elements(_package(packages, _pkg(row.interface_path)))
        iface = _el(elements, "SENDER-RECEIVER-INTERFACE", uuid=_uuid())
        _el(iface, "SHORT-NAME", _short(row.interface_path) or row.interface_name)
        _el(iface, "IS-SERVICE", row.is_service.lower())
        data_elements = _el(iface, "DATA-ELEMENTS")
        for de in sr_elements.get(row.interface_name, []):
            var = _el(data_elements, "VARIABLE-DATA-PROTOTYPE", uuid=_uuid())
            _el(var, "SHORT-NAME", de.data_element_name)
            _el(var, "TYPE-TREF", de.application_type_ref, DEST="APPLICATION-DATA-TYPE")

    args = defaultdict(list)
    for row in model.cs_arguments:
        args[(row.interface_name, row.operation_name)].append(row)
    ops = defaultdict(list)
    for row in model.cs_operations:
        ops[row.interface_name].append(row)
    for row in model.cs_interfaces:
        elements = _elements(_package(packages, _pkg(row.interface_path)))
        iface = _el(elements, "CLIENT-SERVER-INTERFACE", uuid=_uuid())
        _el(iface, "SHORT-NAME", _short(row.interface_path) or row.interface_name)
        _el(iface, "IS-SERVICE", row.is_service.lower())
        operations = _el(iface, "OPERATIONS")
        for op in ops.get(row.interface_name, []):
            op_node = _el(operations, "CLIENT-SERVER-OPERATION", uuid=_uuid())
            _el(op_node, "SHORT-NAME", op.operation_name)
            arg_node = _el(op_node, "ARGUMENTS")
            for arg in args.get((row.interface_name, op.operation_name), []):
                a = _el(arg_node, "ARGUMENT-DATA-PROTOTYPE", uuid=_uuid())
                _el(a, "SHORT-NAME", arg.argument_name)
                _el(a, "TYPE-TREF", arg.application_type_ref, DEST="APPLICATION-DATA-TYPE")
                _el(a, "DIRECTION", arg.direction)
                _el(a, "SERVER-ARGUMENT-IMPL-POLICY", "USE-ARGUMENT-TYPE")


def _write_components(packages: etree._Element, model: WorkbookV2Model) -> None:
    ports_by_component = defaultdict(list)
    for row in model.ports:
        ports_by_component[row.component_name].append(row)
    runnables_by_component = defaultdict(list)
    for row in model.runnables:
        runnables_by_component[row.component_name].append(row)
    events_by_component = defaultdict(list)
    for row in model.runnable_events:
        events_by_component[row.component_name].append(row)
    accesses_by_component = defaultdict(list)
    for row in model.runnable_accesses:
        accesses_by_component[row.component_name].append(row)

    for comp in model.components:
        elements = _elements(_package(packages, comp.package_path))
        if comp.component_kind.lower() == "composition":
            node = _el(elements, "COMPOSITION-SW-COMPONENT-TYPE", uuid=_uuid())
            _el(node, "SHORT-NAME", comp.component_name)
            _write_composition(node, comp, model)
        else:
            node = _el(elements, "APPLICATION-SW-COMPONENT-TYPE", uuid=_uuid())
            _el(node, "SHORT-NAME", comp.component_name)
            ports = _el(node, "PORTS")
            for port in ports_by_component.get(comp.component_name, []):
                _write_port(ports, port)
            _write_behavior(node, comp, model, runnables_by_component[comp.component_name], events_by_component[comp.component_name], accesses_by_component[comp.component_name])


def _write_port(parent: etree._Element, port) -> None:
    pdir = port.port_direction.upper()
    kind = port.interface_kind.upper()
    node = _el(parent, "P-PORT-PROTOTYPE" if pdir == "P" else "R-PORT-PROTOTYPE", uuid=_uuid())
    _el(node, "SHORT-NAME", port.port_name)
    if pdir == "P":
        specs = _el(node, "PROVIDED-COM-SPECS")
        if kind == "SR":
            spec = _el(specs, port.com_spec_kind or "NONQUEUED-SENDER-COM-SPEC")
            _el(spec, "DATA-ELEMENT-REF", f"{port.interface_ref}/{port.data_element_name}", DEST="VARIABLE-DATA-PROTOTYPE")
            _init_value(spec, port.init_value or "0")
            _el(node, "PROVIDED-INTERFACE-TREF", port.interface_ref, DEST="SENDER-RECEIVER-INTERFACE")
        else:
            spec = _el(specs, port.com_spec_kind or "SERVER-COM-SPEC")
            _el(spec, "OPERATION-REF", f"{port.interface_ref}/{port.operation_name}", DEST="CLIENT-SERVER-OPERATION")
            _el(spec, "QUEUE-LENGTH", port.queue_length or "1")
            _el(node, "PROVIDED-INTERFACE-TREF", port.interface_ref, DEST="CLIENT-SERVER-INTERFACE")
    else:
        specs = _el(node, "REQUIRED-COM-SPECS")
        if kind == "SR":
            spec = _el(specs, port.com_spec_kind or "NONQUEUED-RECEIVER-COM-SPEC")
            _el(spec, "DATA-ELEMENT-REF", f"{port.interface_ref}/{port.data_element_name}", DEST="VARIABLE-DATA-PROTOTYPE")
            _el(spec, "ALIVE-TIMEOUT", port.alive_timeout or "0")
            _el(spec, "ENABLE-UPDATE", (port.enable_update or "false").lower())
            _init_value(spec, port.init_value or "0")
            _el(spec, "HANDLE-NEVER-RECEIVED", "false")
            _el(spec, "HANDLE-TIMEOUT-TYPE", port.handle_timeout_type or "NONE")
            _el(node, "REQUIRED-INTERFACE-TREF", port.interface_ref, DEST="SENDER-RECEIVER-INTERFACE")
        else:
            spec = _el(specs, port.com_spec_kind or "CLIENT-COM-SPEC")
            _el(spec, "OPERATION-REF", f"{port.interface_ref}/{port.operation_name}", DEST="CLIENT-SERVER-OPERATION")
            _el(node, "REQUIRED-INTERFACE-TREF", port.interface_ref, DEST="CLIENT-SERVER-INTERFACE")


def _write_behavior(parent: etree._Element, comp, model: WorkbookV2Model, runnables, events, accesses) -> None:
    behavior = _el(_el(parent, "INTERNAL-BEHAVIORS"), "SWC-INTERNAL-BEHAVIOR", uuid=_uuid())
    behavior_name = comp.internal_behavior_name or f"{comp.component_name}_InternalBehavior"
    _el(behavior, "SHORT-NAME", behavior_name)
    maps = _el(behavior, "DATA-TYPE-MAPPING-REFS")
    _el(maps, "DATA-TYPE-MAPPING-REF", model.config("DefaultMappingSetPath", "/ComponentTypes/MappingSets/APP_data_mapping"), DEST="DATA-TYPE-MAPPING-SET")
    events_node = _el(behavior, "EVENTS")
    runnables_node = _el(behavior, "RUNNABLES")
    _el(behavior, "SUPPORTS-MULTIPLE-INSTANTIATION", "false")

    accesses_by_runnable = defaultdict(list)
    for access in accesses:
        accesses_by_runnable[access.runnable_name].append(access)
    ports = {row.port_name: row for row in model.ports if row.component_name == comp.component_name}

    for runnable in runnables:
        r = _el(runnables_node, "RUNNABLE-ENTITY", uuid=_uuid())
        _el(r, "SHORT-NAME", runnable.runnable_name)
        _el(r, "MINIMUM-START-INTERVAL", "0")
        _el(r, "CAN-BE-INVOKED-CONCURRENTLY", "false")
        _el(r, "SYMBOL", runnable.symbol or runnable.runnable_name)
        call_points = [a for a in accesses_by_runnable.get(runnable.runnable_name, []) if a.access_type == "ServerCallPoint"]
        if call_points:
            cps = _el(r, "SERVER-CALL-POINTS")
            for call in call_points:
                p = ports[call.port_name]
                sc = _el(cps, "SYNCHRONOUS-SERVER-CALL-POINT", uuid=_uuid())
                _el(sc, "SHORT-NAME", call.access_name or f"SC_{call.port_name}_{call.operation_name}")
                iref = _el(sc, "OPERATION-IREF")
                _el(iref, "CONTEXT-R-PORT-REF", f"{comp.package_path}/{comp.component_name}/{call.port_name}", DEST="R-PORT-PROTOTYPE")
                _el(iref, "TARGET-REQUIRED-OPERATION-REF", f"{p.interface_ref}/{call.operation_name}", DEST="CLIENT-SERVER-OPERATION")
                _el(sc, "TIMEOUT", "0")

    for event in events:
        runnable_ref = f"{comp.package_path}/{comp.component_name}/{behavior_name}/{event.runnable_name}"
        t = event.trigger_type
        if t == "Init":
            e = _el(events_node, "INIT-EVENT", uuid=_uuid())
            _el(e, "SHORT-NAME", f"{event.runnable_name}_InitEvent")
            _el(e, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
        elif t == "Periodic":
            e = _el(events_node, "TIMING-EVENT", uuid=_uuid())
            _el(e, "SHORT-NAME", f"TMT_{event.runnable_name}")
            _el(e, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
            _el(e, "PERIOD", _period(event.period_ms))
        elif t == "OperationInvoked":
            p = ports[event.port_name]
            e = _el(events_node, "OPERATION-INVOKED-EVENT", uuid=_uuid())
            _el(e, "SHORT-NAME", f"OIT_{event.runnable_name}_{event.port_name}_{event.operation_name}")
            _el(e, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
            iref = _el(e, "OPERATION-IREF")
            _el(iref, "CONTEXT-P-PORT-REF", f"{comp.package_path}/{comp.component_name}/{event.port_name}", DEST="P-PORT-PROTOTYPE")
            _el(iref, "TARGET-PROVIDED-OPERATION-REF", f"{p.interface_ref}/{event.operation_name}", DEST="CLIENT-SERVER-OPERATION")
        elif t == "DataReceived":
            p = ports[event.port_name]
            e = _el(events_node, "DATA-RECEIVED-EVENT", uuid=_uuid())
            _el(e, "SHORT-NAME", f"DRT_{event.runnable_name}_{event.port_name}_{event.data_element_name}")
            _el(e, "START-ON-EVENT-REF", runnable_ref, DEST="RUNNABLE-ENTITY")
            iref = _el(e, "DATA-IREF")
            _el(iref, "CONTEXT-R-PORT-REF", f"{comp.package_path}/{comp.component_name}/{event.port_name}", DEST="R-PORT-PROTOTYPE")
            _el(iref, "TARGET-DATA-ELEMENT-REF", f"{p.interface_ref}/{event.data_element_name or p.data_element_name}", DEST="VARIABLE-DATA-PROTOTYPE")


def _write_composition(parent: etree._Element, comp, model: WorkbookV2Model) -> None:
    protos = [row for row in model.component_prototypes if row.composition_name == comp.component_name]
    proto_types = {row.prototype_name: row for row in protos}
    comps = _el(parent, "COMPONENTS")
    for proto in protos:
        p = _el(comps, "SW-COMPONENT-PROTOTYPE", uuid=_uuid())
        _el(p, "SHORT-NAME", proto.prototype_name)
        _el(p, "TYPE-TREF", proto.component_type_ref, DEST="APPLICATION-SW-COMPONENT-TYPE")
    connectors = [row for row in model.composition_connectors if row.composition_name == comp.component_name]
    if connectors:
        nodes = _el(parent, "CONNECTORS")
        component_by_name = {row.component_name: row for row in model.components}
        for row in connectors:
            provider_proto = proto_types[row.provider_prototype]
            requester_proto = proto_types[row.requester_prototype]
            provider_comp = component_by_name[provider_proto.component_type_name]
            requester_comp = component_by_name[requester_proto.component_type_name]
            c = _el(nodes, "ASSEMBLY-SW-CONNECTOR", uuid=_uuid())
            _el(c, "SHORT-NAME", f"{row.provider_prototype}_{row.provider_port}_{row.requester_prototype}_{row.requester_port}")
            pi = _el(c, "PROVIDER-IREF")
            _el(pi, "CONTEXT-COMPONENT-REF", f"{comp.package_path}/{comp.component_name}/{row.provider_prototype}", DEST="SW-COMPONENT-PROTOTYPE")
            _el(pi, "TARGET-P-PORT-REF", f"{provider_comp.package_path}/{provider_comp.component_name}/{row.provider_port}", DEST="P-PORT-PROTOTYPE")
            ri = _el(c, "REQUESTER-IREF")
            _el(ri, "CONTEXT-COMPONENT-REF", f"{comp.package_path}/{comp.component_name}/{row.requester_prototype}", DEST="SW-COMPONENT-PROTOTYPE")
            _el(ri, "TARGET-R-PORT-REF", f"{requester_comp.package_path}/{requester_comp.component_name}/{row.requester_port}", DEST="R-PORT-PROTOTYPE")


def _init_value(parent: etree._Element, value: str) -> None:
    init = _el(parent, "INIT-VALUE")
    spec = _el(init, "APPLICATION-VALUE-SPECIFICATION")
    _el(spec, "CATEGORY", "VALUE")
    sw_vc = _el(spec, "SW-VALUE-CONT")
    sw_phys = _el(sw_vc, "SW-VALUES-PHYS")
    _el(sw_phys, "V", value)


def _sw_props(parent: etree._Element) -> etree._Element:
    props = _el(parent, "SW-DATA-DEF-PROPS")
    variants = _el(props, "SW-DATA-DEF-PROPS-VARIANTS")
    return _el(variants, "SW-DATA-DEF-PROPS-CONDITIONAL")


def _period(ms: str) -> str:
    return f"{float(ms or '10') / 1000:.6f}".rstrip("0").rstrip(".")


def _pkg(path: str) -> str:
    parts = path.strip("/").split("/")
    return "/" + "/".join(parts[:-1])


def _short(path: str) -> str:
    return path.strip("/").split("/")[-1] if path else ""


def _uuid() -> str:
    return str(uuid4()).upper()


def _el(parent: etree._Element, name: str, text: str | None = None, **attrs: str) -> etree._Element:
    node = etree.SubElement(parent, f"{{{NS}}}{name}")
    for key, value in attrs.items():
        node.set("UUID" if key == "uuid" else key, value)
    if text is not None:
        node.text = text
    return node


def _package(root_packages: etree._Element, path: str) -> etree._Element:
    parent = root_packages
    current = None
    for part in [p for p in path.strip("/").split("/") if p]:
        found = None
        for candidate in parent.findall(f"{{{NS}}}AR-PACKAGE"):
            sn = candidate.find(f"{{{NS}}}SHORT-NAME")
            if sn is not None and sn.text == part:
                found = candidate
                break
        if found is None:
            found = _el(parent, "AR-PACKAGE")
            _el(found, "SHORT-NAME", part)
            _el(found, "ELEMENTS")
            _el(found, "AR-PACKAGES")
        current = found
        nested = current.find(f"{{{NS}}}AR-PACKAGES")
        if nested is None:
            nested = _el(current, "AR-PACKAGES")
        parent = nested
    if current is None:
        raise ValueError(f"Invalid package path: {path}")
    return current


def _elements(pkg: etree._Element) -> etree._Element:
    elements = pkg.find(f"{{{NS}}}ELEMENTS")
    if elements is None:
        elements = _el(pkg, "ELEMENTS")
    return elements
