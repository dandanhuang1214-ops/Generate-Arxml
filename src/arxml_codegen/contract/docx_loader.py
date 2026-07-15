from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from arxml_codegen.contract.schema import (
    ConnectorContract,
    DataTypeContract,
    DeliveryContract,
    OpenIssue,
    OperationArgumentContract,
    ProjectContract,
    RecordElementContract,
    RunnableContract,
    ServiceContract,
    SignalContract,
    SwcContract,
    status_for,
)


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


@dataclass(slots=True)
class DocxTable:
    table_index: int
    heading: str
    headers: list[str]
    rows: list[dict[str, str]]


@dataclass(slots=True)
class DocxBlocks:
    paragraphs: list[str] = field(default_factory=list)
    tables: list[DocxTable] = field(default_factory=list)


def load_docx_blocks(path: Path) -> DocxBlocks:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))

    blocks = DocxBlocks()
    current_heading = ""
    body = root.find(f"{WORD_NS}body")
    if body is None:
        return blocks

    for child in list(body):
        tag = _local_name(child.tag)
        if tag == "p":
            text = _text(child)
            if text:
                blocks.paragraphs.append(text)
                if _looks_like_heading(text):
                    current_heading = text
        elif tag == "tbl":
            rows = _table_rows(child)
            if rows:
                headers = rows[0]
                table_index = len(blocks.tables) + 1
                blocks.tables.append(
                    DocxTable(
                        table_index=table_index,
                        heading=current_heading,
                        headers=headers,
                        rows=[
                            _zip_row(headers, row, table_index, row_index)
                            for row_index, row in enumerate(rows[1:], start=2)
                            if any(row)
                        ],
                    )
                )
    return blocks


def extract_contract_from_docx(path: Path, *, mode: str = "signal") -> DeliveryContract:
    blocks = load_docx_blocks(path)
    title = blocks.paragraphs[0] if blocks.paragraphs else path.stem
    system_name = _guess_system_name(title)
    root_package = "/" + _short_name(system_name or path.stem).upper()
    contract = DeliveryContract(
        project=ProjectContract(
            system_name=system_name,
            root_package=root_package,
            source_status={
                "system_name": "explicit" if system_name else "missing",
                "root_package": "inferred",
                "target_autosar_version": "defaulted",
                "interface_package": "defaulted",
                "data_type_package": "defaulted",
                "compu_method_package": "defaulted",
                "data_constr_package": "defaulted",
                "unit_package": "defaulted",
                "mapping_set_path": "defaulted",
            },
        ),
        metadata={"source_docx": str(path), "mode": mode},
    )

    for table in blocks.tables:
        headers = [_norm_header(header) for header in table.headers]
        if _has(headers, "字段") and _has(headers, "示例"):
            _apply_project_info(contract, table)
        elif _has(headers, "swc名称") or _has(headers, "swc 名称"):
            contract.swcs.extend(_extract_swcs(table))
        elif _has(headers, "swcname") or (_has(headers, "prototypename") and _has(headers, "swc")):
            contract.swcs.extend(_extract_swcs(table))
        elif _has(headers, "signalname") and (
            _has(headers, "datatype")
            or _has(headers, "applicationdatatype")
            or _has(headers, "internaldatatype")
            or _has(headers, "datacategory")
        ):
            contract.signals.extend(_extract_signals(table))
        elif (_has(headers, "recordtype") or _has(headers, "recordtypename")) and (
            _has(headers, "fieldname") or _has(headers, "elementpath")
        ):
            contract.record_elements.extend(_extract_record_elements(table))
        elif (
            (_has(headers, "信号名") or _has(headers, "输入信号") or _has(headers, "输出信号"))
            and (
                _has(headers, "数据类型")
                or _has(headers, "内部数据类型")
                or _has(headers, "应用数据类型")
            )
        ):
            contract.signals.extend(_extract_signals(table))
        elif _has(headers, "结构体名") and _has(headers, "字段名"):
            contract.record_elements.extend(_extract_record_elements(table))
        elif (
            _has(headers, "servicename")
            or _has(headers, "ownerswc")
            or (_has(headers, "interfacename") and _has(headers, "portname"))
            or _has(headers, "服务名")
            or _has(headers, "服务接口")
        ):
            contract.services.extend(_extract_services(table))
            contract.operation_args.extend(_extract_operation_args(table))
        elif _has(headers, "端口服务名") and _has(headers, "参数名"):
            contract.services.extend(_extract_services(table))
            contract.operation_args.extend(_extract_operation_args(table))
        elif _has(headers, "argumentname") or _has(headers, "参数名"):
            contract.operation_args.extend(_extract_operation_args(table))
        elif _has(headers, "accesstype"):
            contract.runnables.extend(_extract_runnable_access_rows(table))
        elif _has(headers, "runnablename") or _has(headers, "runnable"):
            contract.runnables.extend(_extract_runnables(table))
        elif _has(headers, "connectortype") or (
            _has(headers, "providerendpoint") and _has(headers, "requesterendpoint")
        ):
            contract.connectors.extend(_extract_connectors(table))
        elif _has(headers, "typename") or _has(headers, "类型名"):
            contract.data_types.extend(_extract_data_types(table))

    _derive_signal_endpoints_from_runnables(contract)
    _derive_signals_from_runnable_accesses(contract)
    _derive_data_types(contract)
    _derive_data_types_from_service_args(contract)
    _derive_data_types_from_records(contract)
    _derive_swcs_from_signals(contract)
    _derive_swcs_from_services(contract)
    _add_gap_issues(contract)
    return contract


def _apply_project_info(contract: DeliveryContract, table: DocxTable) -> None:
    values: dict[str, str] = {}
    for row in table.rows:
        key = _pick(row, "字段")
        value = _pick(row, "填写值", "值", "内容", "示例")
        if key and value:
            values[_norm_header(key)] = value

    system_name = _first_value(values, "项目系统名称", "系统名称", "项目名称")
    autosar_version = _first_value(values, "autosar版本", "autosarversion")
    root_package = _first_value(values, "rootpackage", "根包路径", "根包")
    domain = _first_value(values, "domain", "域", "部署域")

    if system_name:
        contract.project.system_name = _guess_system_name(system_name)
        contract.project.root_package = root_package or "/" + _short_name(contract.project.system_name).upper()
        contract.project.source_status["system_name"] = "explicit"
        contract.project.source_status["root_package"] = "explicit" if root_package else "inferred"
    if autosar_version:
        contract.project.target_autosar_version = autosar_version
        contract.project.source_status["target_autosar_version"] = "explicit"
    if domain:
        contract.project.domain = domain
        contract.project.source_status["domain"] = "explicit"


def _extract_swcs(table: DocxTable) -> list[SwcContract]:
    rows = []
    for row in table.rows:
        name = _pick(row, "SWC名称", "SWC 名称", "名称")
        if not name or name.lower() in {"swc名称", "swc 名称"}:
            continue
        kind = _pick(row, "SWC类型", "类型", "是否 Composition") or "Application"
        rows.append(
            SwcContract(
                name=_short_name(name),
                prototype_name=_short_name(_pick(row, "PrototypeName")),
                kind=_normalize_swc_kind(kind),
                layer=_pick(row, "所属层级", "服务部署"),
                domain=_pick(row, "部署域", "服务部署"),
                is_composition=_pick(row, "是否Composition"),
                description=_pick(row, "说明", "SWC描述"),
                requirement_id=_pick(row, "RequirementId", "需求ID"),
                source_status={"name": "explicit", "kind": status_for(kind, "explicit")},
            )
        )
    return rows


def _extract_record_elements(table: DocxTable) -> list[RecordElementContract]:
    rows = []
    for row in table.rows:
        record_type = _pick(row, "RecordType", "结构体名")
        element_name = _pick(row, "ElementName", "FieldName", "字段名")
        if not record_type or not element_name:
            continue
        field_category = _pick(row, "FieldCategory", "字段类别")
        internal_range = _pick(row, "InternalRange", "内部范围")
        physical_range = _pick(row, "PhysicalRange", "物理范围")
        enum_values = _normalize_enum_values(_pick(row, "EnumValues", "状态值表", "枚举值"))
        value_info = enum_values or internal_range or _pick(row, "Range/Enum", "Range", "取值范围/枚举")
        app_field_type = _pick(row, "ApplicationFieldType", "应用字段类型")
        impl_field_type = _pick(row, "ImplementationFieldType", "内部字段类型")
        rows.append(
            RecordElementContract(
                record_type=_short_name(record_type),
                implementation_record_type=_short_name(_pick(row, "ImplementationRecordType")),
                field_order=_pick(row, "FieldOrder"),
                element_name=_short_name(element_name),
                field_category=_normalize_value_type(field_category),
                data_type=_short_name(app_field_type or _pick(row, "DataType", "字段类型", "数据类型", "内部数据类型", "建议数据类型")),
                implementation_field_type=_short_name(impl_field_type),
                internal_range=internal_range,
                physical_range=physical_range,
                resolution=_pick(row, "Resolution"),
                offset=_pick(row, "Offset"),
                range_or_enum=value_info,
                unit=_pick(row, "Unit", "单位"),
                init_value=_pick(row, "InitValue", "初值", "初始值"),
                description=_pick(row, "Description", "说明"),
                source_trace=_source_trace(row),
                source_status={
                    "record_type": "explicit",
                    "element_name": "explicit",
                    "data_type": status_for(_pick(row, "DataType", "字段类型", "数据类型")),
                },
            )
        )
    return rows


def _extract_signals(table: DocxTable) -> list[SignalContract]:
    heading_direction = _direction_from_signal_table(table)
    rows = []
    for row in table.rows:
        signal_name = _pick(row, "SignalName", "信号名", "输入信号", "输出信号")
        if not signal_name:
            continue
        application_type = _pick(row, "ApplicationDataType", "应用数据类型", "DataType", "数据类型", "建议数据类型")
        internal_type = _pick(row, "InternalDataType", "内部数据类型", "参数类型")
        direction = _pick(row, "Direction", "方向") or heading_direction
        value_type = _pick(row, "ValueType", "数据类别", "值类型", "值数据类型")
        internal_range = _pick(row, "InternalRange", "内部范围")
        physical_range = _pick(row, "PhysicalRange", "物理范围")
        range_value = _pick(row, "Range", "范围") or physical_range
        enum_value = _normalize_enum_values(_pick(row, "EnumValues", "状态值表", "值定义"))
        combined_value = _pick(row, "取值范围/状态表")
        combined_enum = _normalize_enum_values(combined_value)
        provider = _pick(row, "ProviderSWC", "生产者SWC", "信号源", "信号来源", "来源模块")
        consumer = _pick(row, "ConsumerSWC", "消费者SWC")
        owner_from_runnable = _component_from_runnable(_pick(row, "所属 Runnable", "所属Runnable"))
        normalized_direction = _normalize_signal_direction(direction) or _infer_signal_direction(signal_name)
        if owner_from_runnable and not consumer and normalized_direction == "input":
            consumer = owner_from_runnable
        if owner_from_runnable and not provider and normalized_direction == "output":
            provider = owner_from_runnable
        if heading_direction == "output" and not provider:
            provider = _pick(row, "所属组件", "所属SWC")
        rows.append(
            SignalContract(
                signal_name=_short_name(signal_name),
                direction=normalized_direction,
                provider_swc=_short_name(provider),
                consumer_swc=_short_name(consumer),
                value_type=_normalize_value_type(value_type),
                data_type=_short_name(
                    application_type
                    or _default_application_type(signal_name, value_type, internal_type)
                ),
                internal_data_type=_short_name(internal_type),
                internal_range=internal_range,
                physical_range=physical_range,
                resolution=_pick(row, "Resolution", "分辨率"),
                offset=_pick(row, "Offset"),
                unit=_pick(row, "Unit", "单位"),
                range=range_value if range_value and range_value != "-" else combined_value if _looks_like_range(combined_value) else "",
                enum_values=(
                    enum_value if _is_enum_value_type(value_type) and enum_value and enum_value != "-"
                    else combined_enum if _is_enum_value_type(value_type) and combined_enum and not _looks_like_range(combined_enum)
                    else ""
                ),
                init_value=_pick(row, "InitValue", "初值", "初始值"),
                period_ms=_pick(row, "PeriodMs", "周期", "周期ms", "周期(ms)"),
                description=_pick(row, "Description", "作用描述", "说明"),
                requirement_id=_pick(row, "RequirementId", "需求ID"),
                source=table.heading,
                source_trace=_source_trace(row),
                source_status={
                    "signal_name": "explicit",
                    "direction": status_for(direction or normalized_direction, "explicit"),
                    "provider_swc": status_for(provider, "explicit"),
                    "consumer_swc": status_for(consumer, "explicit"),
                    "data_type": status_for(application_type, "explicit"),
                    "internal_data_type": status_for(internal_type, "explicit"),
                },
            )
        )
    return rows


def _direction_from_signal_table(table: DocxTable) -> str:
    headers = [_norm_header(header) for header in table.headers]
    if any("输出信号" in header for header in headers):
        return "output"
    if any("输入信号" in header for header in headers):
        return "input"
    if "输出" in table.heading:
        return "output"
    if "输入" in table.heading:
        return "input"
    return ""


def _extract_services(table: DocxTable) -> list[ServiceContract]:
    rows = []
    for row in table.rows:
        service_name = _pick(row, "ServiceName", "服务名", "服务接口", "端口/服务名")
        operation = _pick(row, "OperationName", "Operation", "Operation名", "操作名")
        owner_swc = _pick(row, "OwnerSWC", "ProviderSWC", "服务提供方", "所属SWC")
        interface_name = _pick(row, "InterfaceName", "接口名") or service_name
        port_name = _pick(row, "PortName", "端口名") or service_name or interface_name
        port_role = _pick(row, "PortRole", "端口角色", "PortType", "端口类型")
        communication = _pick(row, "Communication", "通信模式")
        if not service_name and not operation and not interface_name and not port_name:
            continue
        rows.append(
            ServiceContract(
                service_name=_short_name(service_name or interface_name or operation),
                owner_swc=_short_name(owner_swc),
                provider_swc=_short_name(owner_swc),
                client_swc=_short_name(_pick(row, "ClientSWC", "服务调用方")),
                interface_name=_short_name(interface_name),
                port_name=_short_name(port_name),
                operation_name=_short_name(operation or service_name),
                port_role=port_role,
                communication=communication,
                port_type=port_role,
                sync_async=_pick(row, "SyncAsync", "同步异步") or "sync",
                timeout_ms=_pick(row, "TimeoutMs", "超时"),
                queue_length=_pick(row, "QueueLength"),
                description=_pick(row, "Description", "说明", "接口描述"),
                requirement_id=_pick(row, "RequirementId", "需求ID"),
                source_trace=_source_trace(row),
                source_status={
                    "provider_swc": status_for(owner_swc, "explicit"),
                    "client_swc": status_for(_pick(row, "ClientSWC", "服务调用方"), "explicit"),
                },
            )
        )
    return rows


def _extract_swcs(table: DocxTable) -> list[SwcContract]:
    rows = []
    for row in table.rows:
        name = _pick(row, "SWCName", "SWC", "SWC 名称", "SWC名称", "名称")
        if not name:
            continue
        kind = _pick(row, "SWCType", "Type", "服务层级", "类型", "是否 Composition") or "Application"
        is_composition = _pick(row, "IsComposition", "是否Composition", "是否 Composition")
        normalized_kind = "Composition" if is_composition.strip().lower() == "true" or kind.strip().lower() == "composition" else "Application"
        rows.append(
            SwcContract(
                name=_short_name(name),
                prototype_name=_short_name(_pick(row, "PrototypeName")),
                kind=normalized_kind,
                layer=_pick(row, "Layer", "服务层级"),
                domain=_pick(row, "Domain", "部署域"),
                is_composition=is_composition,
                description=_pick(row, "Description", "说明"),
                requirement_id=_pick(row, "RequirementId", "RequirementId/Source", "需求ID"),
                source_status={"name": "explicit", "kind": status_for(kind, "explicit")},
            )
        )
    return rows


def _extract_operation_args(table: DocxTable) -> list[OperationArgumentContract]:
    rows = []
    for row in table.rows:
        arg_name = _pick(row, "ArgumentName", "参数名")
        if not arg_name:
            continue
        rows.append(
            OperationArgumentContract(
                interface_name=_short_name(_pick(row, "InterfaceName")),
                operation_name=_short_name(
                    _pick(row, "OperationName", "Operation", "Operation名", "操作名", "端口/服务名")
                ),
                argument_name=_short_name(arg_name),
                direction=_normalize_arg_direction(_pick(row, "Direction", "方向")),
                value_type=_pick(row, "ValueType", "值类型"),
                internal_data_type=_short_name(_pick(row, "InternalDataType", "内部数据类型")),
                data_type=_short_name(_pick(row, "DataType", "InternalDataType", "数据类型", "内部数据类型", "建议数据类型", "参数类型")),
                range_or_enum=_pick(row, "Range/Enum", "Range", "EnumValues", "范围", "枚举", "取值范围/引用结构体"),
                record_type=_short_name(_pick(row, "RecordType")),
                is_record=_pick(row, "IsRecord", "是否Record"),
                unit=_pick(row, "Unit", "单位"),
                description=_pick(row, "Description", "说明"),
                requirement_id=_pick(row, "RequirementId", "需求ID"),
                source_trace=_source_trace(row),
            )
        )
    return rows


def _extract_runnables(table: DocxTable) -> list[RunnableContract]:
    rows = []
    for row in table.rows:
        runnable_name = _pick(row, "RunnableName", "Runnable", "Runnable名称", "Runnable名", "Runnable 名")
        if not runnable_name:
            continue
        rows.append(
            RunnableContract(
                swc=_short_name(_pick(row, "SWC", "SWC名称", "所属SWC", "所属组件")),
                runnable_name=_short_name(runnable_name),
                trigger_type=_normalize_trigger(_pick(row, "TriggerType", "触发类型")),
                period_ms=_pick(row, "PeriodMs", "周期", "周期(ms)"),
                trigger_object="",
                related_port_or_signal="",
                related_operation="",
                read_signals=_pick(row, "读取信号", "ReadSignals"),
                write_signals=_pick(row, "写入信号", "WriteSignals"),
                description=_pick(row, "Description", "说明"),
                requirement_id=_pick(row, "RequirementId", "需求ID"),
                source_trace=_source_trace(row),
            )
        )
    return rows


def _extract_runnable_access_rows(table: DocxTable) -> list[RunnableContract]:
    rows = []
    for row in table.rows:
        runnable_name = _pick(row, "RunnableName", "Runnable名", "Runnable 名")
        access_type = _normalize_access_type(_pick(row, "AccessType"))
        port_or_signal = _pick(row, "PortOrSignal", "信号/端口名", "信号名", "端口名")
        if not runnable_name or not access_type or not port_or_signal:
            continue
        read_signals = port_or_signal if access_type == "DataRead" else ""
        write_signals = port_or_signal if access_type == "DataWrite" else ""
        related_operation = _pick(row, "OperationName", "Operation") if access_type == "CallOperation" else ""
        if access_type == "OperationInvokedEvent":
            related_operation = _pick(row, "OperationName", "Operation")
        rows.append(
            RunnableContract(
                swc=_short_name(_pick(row, "SWC", "SWC名称", "所属SWC", "所属组件")),
                runnable_name=_short_name(runnable_name),
                trigger_type="",
                related_port_or_signal=_short_name(port_or_signal if access_type in {"CallOperation", "OperationInvokedEvent"} else ""),
                related_operation=_short_name(related_operation),
                read_signals=read_signals,
                write_signals=write_signals,
                description=_pick(row, "Description", "说明"),
                source_trace=_source_trace(row),
                source_status={"access_type": "explicit"},
            )
        )
    return rows


def _extract_data_types(table: DocxTable) -> list[DataTypeContract]:
    rows = []
    for row in table.rows:
        type_name = _pick(row, "TypeName", "类型名")
        if not type_name:
            continue
        rows.append(
            DataTypeContract(
                type_name=_short_name(type_name),
                type_kind=_pick(row, "TypeKind"),
                base_type=_normalize_base_type(_pick(row, "BaseType", "基础类型")),
                compu_method_category=_pick(row, "CompuMethod类型", "CompuMethodCategory"),
                enum_values=_pick(row, "EnumValues", "枚举值"),
                physical_range=_pick(row, "PhysicalRange", "物理范围", "范围"),
                field_order=_pick(row, "FieldOrder"),
                field_name=_short_name(_pick(row, "FieldName")),
                field_type=_short_name(_pick(row, "FieldType")),
                range_or_enum=_pick(row, "RangeOrEnum", "Range/Enum"),
                unit=_pick(row, "Unit", "单位"),
                description=_pick(row, "Description", "说明"),
            )
        )
    return rows


def _extract_connectors(table: DocxTable) -> list[ConnectorContract]:
    rows = []
    for row in table.rows:
        provider_endpoint = _pick(row, "ProviderEndpoint")
        requester_endpoint = _pick(row, "RequesterEndpoint")
        if not provider_endpoint and not requester_endpoint:
            continue
        connector_type = _pick(row, "ConnectorType") or "Assembly"
        rows.append(
            ConnectorContract(
                connector_type=connector_type,
                provider_endpoint=provider_endpoint,
                requester_endpoint=requester_endpoint,
                interface_name=_short_name(_pick(row, "InterfaceName")),
                description=_pick(row, "Description", "说明"),
                requirement_id=_pick(row, "RequirementId", "需求ID"),
                source_trace=_source_trace(row),
                source_status={
                    "connector_type": status_for(connector_type, "defaulted"),
                    "provider_endpoint": status_for(provider_endpoint, "explicit"),
                    "requester_endpoint": status_for(requester_endpoint, "explicit"),
                },
            )
        )
    return rows


def _derive_data_types(contract: DeliveryContract) -> None:
    existing = {item.type_name for item in contract.data_types}
    for signal in contract.signals:
        if not signal.data_type or signal.data_type in existing:
            continue
        category = _compu_category_for_type(signal.value_type, signal.resolution, signal.offset)
        contract.data_types.append(
            DataTypeContract(
                type_name=signal.data_type,
                type_kind=_normalize_value_type(signal.value_type),
                base_type=_normalize_base_type(signal.internal_data_type or signal.data_type),
                compu_method_category=category,
                enum_values=signal.enum_values if _is_enum_value_type(signal.value_type) else "",
                internal_range=signal.internal_range,
                physical_range=signal.physical_range or signal.range,
                resolution=signal.resolution,
                offset=signal.offset,
                implementation_type_name=_short_name(signal.internal_data_type) if _normalize_value_type(signal.value_type) == "Record" else "",
                unit=signal.unit,
                description=f"Derived from signal {signal.signal_name}",
                source_status={
                    "type_name": "explicit",
                    "base_type": "inferred",
                    "compu_method_category": "inferred",
                },
            )
        )
        existing.add(signal.data_type)


def _derive_data_types_from_service_args(contract: DeliveryContract) -> None:
    existing = {item.type_name for item in contract.data_types}
    for arg in contract.operation_args:
        if not arg.data_type or arg.data_type in existing:
            continue
        category = "TEXTTABLE" if arg.range_or_enum and not _looks_like_range(arg.range_or_enum) else "IDENTICAL"
        contract.data_types.append(
            DataTypeContract(
                type_name=arg.data_type,
                base_type=_normalize_base_type(arg.data_type),
                compu_method_category=category,
                enum_values=arg.range_or_enum if category == "TEXTTABLE" else "",
                physical_range=arg.range_or_enum if _looks_like_range(arg.range_or_enum) else "",
                unit=arg.unit,
                description=f"Derived from service argument {arg.operation_name}.{arg.argument_name}",
                source_status={
                    "type_name": "explicit",
                    "base_type": "inferred",
                    "compu_method_category": "inferred",
                },
            )
        )
        existing.add(arg.data_type)


def _derive_data_types_from_records(contract: DeliveryContract) -> None:
    existing = {item.type_name for item in contract.data_types}
    for element in contract.record_elements:
        if element.data_type and element.data_type not in existing:
            category = _compu_category_for_type(element.field_category, element.resolution, element.offset)
            contract.data_types.append(
                DataTypeContract(
                    type_name=element.data_type,
                    type_kind=element.field_category,
                    base_type=_normalize_base_type(element.implementation_field_type or element.data_type),
                    compu_method_category=category,
                    enum_values=element.range_or_enum if category == "TEXTTABLE" else "",
                    internal_range=element.internal_range,
                    physical_range=element.physical_range,
                    resolution=element.resolution,
                    offset=element.offset,
                    unit=element.unit,
                    description=f"Derived from record element {element.record_type}.{element.element_name}",
                    source_status={
                        "type_name": "explicit",
                        "base_type": "inferred",
                        "compu_method_category": "inferred",
                    },
                )
            )
            existing.add(element.data_type)


def _derive_signal_endpoints_from_runnables(contract: DeliveryContract) -> None:
    providers: dict[str, str] = {}
    consumers: dict[str, str] = {}
    for runnable in contract.runnables:
        if not runnable.swc:
            continue
        for signal_name in _split_list(runnable.read_signals):
            consumers.setdefault(_short_name(signal_name), runnable.swc)
        for signal_name in _split_list(runnable.write_signals):
            providers.setdefault(_short_name(signal_name), runnable.swc)

    for signal in contract.signals:
        key = _short_name(signal.signal_name)
        if not signal.provider_swc and key in providers:
            signal.provider_swc = providers[key]
            signal.source_status["provider_swc"] = "inferred"
        if not signal.consumer_swc and key in consumers:
            signal.consumer_swc = consumers[key]
            signal.source_status["consumer_swc"] = "inferred"


def _derive_signals_from_runnable_accesses(contract: DeliveryContract) -> None:
    existing = {_short_name(signal.signal_name) for signal in contract.signals}
    allow_default_signal = _contract_profile(contract) == "signal_atomic_davinci"
    for runnable in contract.runnables:
        for signal_name in _split_list(runnable.read_signals):
            short = _short_name(signal_name)
            if not short or short in existing:
                continue
            if not allow_default_signal:
                _append_access_missing_signal_issue(contract, runnable, short, "DataRead")
                continue
            contract.signals.append(
                SignalContract(
                    signal_name=short,
                    direction="input",
                    consumer_swc=runnable.swc,
                    value_type="Value",
                    data_type="App_uint8",
                    internal_data_type="uint8",
                    internal_range="0-255",
                    physical_range="0-255",
                    init_value="0",
                    description=f"Derived from Runnable Access DataRead {runnable.runnable_name}",
                    source_trace=runnable.source_trace,
                    source_status={
                        "signal_name": "inferred",
                        "direction": "inferred",
                        "consumer_swc": "inferred",
                        "data_type": "defaulted",
                        "internal_data_type": "defaulted",
                    },
                )
            )
            existing.add(short)
        for signal_name in _split_list(runnable.write_signals):
            short = _short_name(signal_name)
            if not short or short in existing:
                continue
            if not allow_default_signal:
                _append_access_missing_signal_issue(contract, runnable, short, "DataWrite")
                continue
            contract.signals.append(
                SignalContract(
                    signal_name=short,
                    direction="output",
                    provider_swc=runnable.swc,
                    value_type="Value",
                    data_type="App_uint8",
                    internal_data_type="uint8",
                    internal_range="0-255",
                    physical_range="0-255",
                    init_value="0",
                    description=f"Derived from Runnable Access DataWrite {runnable.runnable_name}",
                    source_trace=runnable.source_trace,
                    source_status={
                        "signal_name": "inferred",
                        "direction": "inferred",
                        "provider_swc": "inferred",
                        "data_type": "defaulted",
                        "internal_data_type": "defaulted",
                    },
                )
            )
            existing.add(short)


def _append_access_missing_signal_issue(
    contract: DeliveryContract,
    runnable: RunnableContract,
    signal_name: str,
    access_type: str,
) -> None:
    contract.open_issues.append(
        OpenIssue(
            field=f"runnable_access.{runnable.swc}.{runnable.runnable_name}.{access_type}.{signal_name}",
            question=(
                f"Runnable Access 引用了未定义的 S/R 信号 '{signal_name}'。"
                "SOA 模式不会自动创建默认 S/R Interface；请先在 S/R 信号接口表补充该信号的数据类别、ADT、IDT、范围和初值。"
            ),
            suggested_default="",
            status="open",
            source=runnable.source_trace,
        )
    )


def _contract_profile(contract: DeliveryContract) -> str:
    profile = (
        contract.project.generation_profile
        or contract.metadata.get("generation_profile")
        or ""
    ).strip()
    if profile and profile.lower() != "generic":
        return profile
    mode = (contract.metadata.get("mode") or "").strip()
    return "signal_atomic_davinci" if mode in {"", "signal"} else mode


def _derive_swcs_from_signals(contract: DeliveryContract) -> None:
    existing = {item.name for item in contract.swcs}
    for signal in contract.signals:
        for name in [signal.provider_swc, signal.consumer_swc]:
            if not name or name in existing:
                continue
            contract.swcs.append(
                SwcContract(
                    name=name,
                    kind="Application",
                    description=f"Derived from signal {signal.signal_name}",
                    source_status={"name": "explicit", "kind": "defaulted"},
                )
            )
            existing.add(name)


def _derive_swcs_from_services(contract: DeliveryContract) -> None:
    existing = {item.name for item in contract.swcs}
    for service in contract.services:
        for name in [service.provider_swc, service.client_swc]:
            if not name or name in existing:
                continue
            contract.swcs.append(
                SwcContract(
                    name=name,
                    kind="Application",
                    description=f"Derived from service {service.service_name}",
                    source_status={"name": "explicit", "kind": "defaulted"},
                )
            )
            existing.add(name)


def _add_gap_issues(contract: DeliveryContract) -> None:
    seen: set[str] = set()
    for signal in contract.signals:
        base = f"signals.{signal.signal_name}"
        if not signal.direction:
            _append_issue_once(contract, seen, OpenIssue(base + ".direction", "确认信号方向 input/output。"))
        if not signal.provider_swc:
            _append_issue_once(contract, seen, OpenIssue(base + ".provider_swc", "确认信号生产者 SWC。"))
        if not signal.consumer_swc:
            _append_issue_once(contract, seen, OpenIssue(base + ".consumer_swc", "确认信号消费者 SWC。"))
        if not signal.data_type:
            _append_issue_once(contract, seen, OpenIssue(base + ".data_type", "确认信号数据类型。"))
        if not signal.init_value:
            _append_issue_once(
                contract,
                seen,
                OpenIssue(base + ".init_value", "确认 InitValue；若无特殊要求建议填 0。", "0"),
            )


def _table_rows(tbl: ET.Element) -> list[list[str]]:
    rows = []
    for tr in tbl.iter(f"{WORD_NS}tr"):
        row = []
        for tc in tr.iter(f"{WORD_NS}tc"):
            row.append("".join(_text(p) for p in tc.iter(f"{WORD_NS}p")).strip())
        if any(row):
            rows.append(row)
    return rows


def _zip_row(headers: list[str], row: list[str], table_index: int, row_index: int) -> dict[str, str]:
    result = {headers[index]: row[index] if index < len(row) else "" for index in range(len(headers))}
    result["_table_index"] = str(table_index)
    result["_row_index"] = str(row_index)
    return result


def _text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.iter(f"{WORD_NS}t")).strip()


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _looks_like_heading(text: str) -> bool:
    text = (text or "").strip()
    if re.match(r"^[一二三四五六七八九十]+[、.．]", text):
        return True
    heading_words = ("输入信号定义", "输出信号定义", "服务接口定义", "SWC 组件定义", "Trigger Event")
    return any(word in text for word in heading_words)


def _pick(row: dict[str, str], *names: str) -> str:
    normalized = {_norm_header(key): value.strip() for key, value in row.items()}
    for name in names:
        value = normalized.get(_norm_header(name), "")
        if value:
            return value
    return ""


def _first_value(values: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = values.get(_norm_header(key), "")
        if value and value != "-":
            return value
    return ""


def _source_trace(row: dict[str, str]) -> str:
    table = row.get("_table_index", "")
    index = row.get("_row_index", "")
    return f"table:{table},row:{index}" if table and index else ""


def _append_issue_once(contract: DeliveryContract, seen: set[str], issue: OpenIssue) -> None:
    if issue.field in seen:
        return
    seen.add(issue.field)
    contract.open_issues.append(issue)


def _has(headers: list[str], name: str) -> bool:
    needle = _norm_header(name)
    return any(needle == header or needle in header for header in headers)


def _norm_header(value: str) -> str:
    return re.sub(r"[\s_/（）()：:🟢🟡⚪✅*]+", "", value or "").lower()


def _guess_system_name(title: str) -> str:
    text = title.replace("ARXML", "").replace("接口交付文档", "").replace("设计信息清单", "")
    text = text.replace("系统需求规范", "").strip("_- ")
    return _short_name(text) or "ARXML_Project"


def _short_name(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    value = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    if re.match(r"^\d", value):
        value = "N_" + value
    return value


def _clean_reference(value: str) -> str:
    text = (value or "").strip()
    if not text or text == "-":
        return ""
    if "示例" in text:
        return ""
    return text


def _normalize_signal_direction(value: str) -> str:
    text = (value or "").lower()
    if text in {"input", "in", "r", "receiver"} or "输入" in value:
        return "input"
    if text in {"output", "out", "p", "sender"} or "输出" in value:
        return "output"
    return value


def _infer_signal_direction(signal_name: str) -> str:
    text = signal_name.lower()
    if re.match(r"v[be]?inp", text) or "_inp_" in text or "inp_" in text:
        return "input"
    if re.match(r"v[be]?out", text) or "_out_" in text or "out_" in text:
        return "output"
    return ""


def _normalize_swc_kind(value: str) -> str:
    text = (value or "").lower()
    if "composition" in text or "组合" in value or value.strip().lower() == "true":
        return "Composition"
    return "Application"


def _normalize_arg_direction(value: str) -> str:
    text = (value or "").upper()
    return text if text in {"IN", "OUT", "INOUT"} else ""


def _normalize_trigger(value: str) -> str:
    text = (value or "").lower()
    if "周期" in value or "period" in text:
        return "Periodic"
    if "init" in text or "初始化" in value:
        return "Init"
    if "operationinvokedevent" in text or "operationinvoked" in text:
        return "OperationInvoked"
    if "operation" in text or "服务" in value:
        return "OperationInvoked"
    if "data" in text or "信号" in value:
        return "DataReceived"
    return value


def _normalize_access_type(value: str) -> str:
    text = (value or "").strip().lower()
    if text in {"dataread", "read", "读取"} or "read" in text or "读取" in value:
        return "DataRead"
    if text in {"datawrite", "write", "写入"} or "write" in text or "写入" in value:
        return "DataWrite"
    if text in {"operationinvokedevent", "operationinvoked", "operationinvocated", "invokeoperation"}:
        return "OperationInvokedEvent"
    if text in {"calloperation", "servercallpoint"} or "call" in text or "调用" in value:
        return "CallOperation"
    return value


def _normalize_base_type(value: str) -> str:
    text = (value or "").lower()
    if "bool" in text or "布尔" in value:
        return "boolean"
    for item in ["uint8", "uint16", "uint32", "uint64", "sint8", "sint16", "sint32", "float32"]:
        if item in text:
            return item
    if "enum" in text or "枚举" in value:
        return "uint8"
    return "uint8"


def _normalize_value_type(value: str) -> str:
    text = (value or "").strip()
    lower = text.lower()
    if lower in {"enum", "enumeration"} or "枚举" in text:
        return "Enum"
    if lower in {"boolean", "bool"} or "布尔" in text:
        return "Boolean"
    if lower in {"record", "struct", "structure"} or "结构" in text:
        return "Record"
    if lower in {"numeric", "number", "value"}:
        return "Value"
    if lower in {"uint8", "uint16", "uint32", "uint64", "sint8", "sint16", "sint32", "float32"}:
        return "Value"
    return text


def _is_enum_value_type(value: str) -> bool:
    return _normalize_value_type(value).lower() == "enum"


def _type_name_from_value_type(signal_name: str, value_type: str) -> str:
    if not signal_name:
        return ""
    prefix = {
        "boolean": "Bool",
        "numeric": "Num",
        "enum": "Enum",
    }.get((value_type or "").lower(), "Value")
    return f"{prefix}_{signal_name}"


def _default_application_type(signal_name: str, value_type: str, internal_type: str) -> str:
    kind = _normalize_value_type(value_type)
    base = _normalize_base_type(internal_type)
    if kind == "Boolean":
        return "App_boolean"
    if kind == "Enum":
        return f"App_{_short_name(signal_name)}"
    if kind == "Record":
        return f"App_{_short_name(signal_name)}"
    return f"App_{base}"


def _component_from_runnable(value: str) -> str:
    runnable = _short_name(value)
    if not runnable:
        return ""
    for suffix in ["_Init", "_Step", "_Runnable"]:
        if runnable.endswith(suffix):
            return runnable[: -len(suffix)]
    return "_".join(runnable.split("_")[:-1]) if "_" in runnable else ""


def _split_list(value: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"[,，;；、\n]+", value or "")
        if item.strip() and item.strip() != "-"
    ]


def _normalize_enum_values(value: str) -> str:
    text = (value or "").strip()
    if text in {"", "-"}:
        return ""
    if text.startswith(("见", "同")):
        return ""
    text = text.replace("：", "=").replace(":", "=")
    text = re.sub(r"(?<=[A-Za-z0-9_])\s*(?=\d+\s*=)", ";", text)
    text = re.sub(r";+", ";", text)
    return text.strip("; ")


def _looks_like_range(value: str) -> bool:
    return bool(re.search(r"\d+\s*[-~/至]\s*\d+", value or ""))


def _compu_category_for_type(value_type: str, resolution: str = "", offset: str = "") -> str:
    kind = _normalize_value_type(value_type)
    if kind == "Enum":
        return "TEXTTABLE"
    if kind == "Boolean":
        return "TEXTTABLE"
    if _has_linear_conversion(resolution, offset):
        return "LINEAR"
    return "IDENTICAL"


def _has_linear_conversion(resolution: str = "", offset: str = "") -> bool:
    resolution_text = str(resolution or "").strip()
    offset_text = str(offset or "").strip()
    if resolution_text and resolution_text not in {"1", "1.0"}:
        return True
    if offset_text and offset_text not in {"0", "0.0"}:
        return True
    return False


# V1.7 SOA template compatibility overrides.
# Keep these functions at the end of the module so they override the older
# implementations above without touching the historical garbled Chinese header
# compatibility code.
def _extract_services(table: DocxTable) -> list[ServiceContract]:
    rows = []
    for row in table.rows:
        service_name = _pick(row, "ServiceName", "服务名", "服务接口", "端口/服务名")
        operation = _pick(row, "OperationName", "Operation", "Operation名", "操作名")
        owner_swc = _pick(row, "OwnerSWC", "ProviderSWC", "所属SWC", "服务提供方")
        interface_name = _pick(row, "InterfaceName", "接口名") or service_name
        port_name = _pick(row, "PortName", "端口名", "端口/服务名") or service_name or interface_name
        port_role = _normalize_port_role(_pick(row, "PortRole", "PortType", "端口类型", "端口角色"))
        communication = _pick(row, "Communication")
        if not service_name and not operation and not interface_name and not port_name:
            continue

        provider_swc = owner_swc if port_role in {"Server", "Sender", "Provider", "P"} else _pick(row, "ProviderSWC", "服务提供方")
        client_swc = owner_swc if port_role in {"Client", "Receiver", "Requester", "R"} else _pick(row, "ClientSWC", "服务调用方")
        rows.append(
            ServiceContract(
                service_name=_short_name(service_name or interface_name or operation),
                owner_swc=_short_name(owner_swc),
                provider_swc=_short_name(provider_swc),
                client_swc=_short_name(client_swc),
                interface_name=_short_name(interface_name),
                port_name=_short_name(port_name),
                operation_name=_short_name(operation or service_name),
                port_role=port_role,
                communication=communication,
                port_type=port_role,
                sync_async=_pick(row, "SyncAsync") or "sync",
                timeout_ms=_pick(row, "TimeoutMs"),
                queue_length=_pick(row, "QueueLength"),
                description=_pick(row, "Description", "说明", "接口描述"),
                requirement_id=_pick(row, "RequirementId", "RequirementId/Source", "需求ID"),
                source_trace=_source_trace(row),
                source_status={
                    "owner_swc": status_for(owner_swc, "explicit"),
                    "provider_swc": status_for(provider_swc, "explicit"),
                    "client_swc": status_for(client_swc, "explicit"),
                    "port_name": status_for(port_name, "explicit"),
                },
            )
        )
    return rows


def _extract_operation_args(table: DocxTable) -> list[OperationArgumentContract]:
    rows = []
    for row in table.rows:
        arg_name = _pick(row, "ArgumentName", "参数名")
        if not arg_name:
            continue
        enum_values = _normalize_enum_values(_pick(row, "EnumValues", "状态值表", "枚举值"))
        internal_range = _pick(row, "InternalRange", "内部范围")
        rows.append(
            OperationArgumentContract(
                interface_name=_short_name(_pick(row, "InterfaceName", "接口名")),
                operation_name=_short_name(_pick(row, "OperationName", "Operation", "Operation名", "操作名", "端口/服务名")),
                argument_name=_short_name(arg_name),
                direction=_normalize_arg_direction(_pick(row, "Direction", "方向")),
                value_type=_normalize_value_type(_pick(row, "ValueType", "DataCategory", "数据类别", "值类型")),
                internal_data_type=_short_name(_pick(row, "InternalDataType", "ImplementationDataType", "内部数据类型", "参数类型")),
                data_type=_short_name(_pick(row, "ApplicationDataType", "DataType", "应用数据类型", "数据类型", "参数类型")),
                internal_range=internal_range,
                physical_range=_pick(row, "PhysicalRange", "物理范围"),
                resolution=_pick(row, "Resolution", "分辨率"),
                offset=_pick(row, "Offset"),
                enum_values=enum_values,
                range_or_enum=enum_values or internal_range or _pick(row, "Range/Enum", "Range", "取值范围/引用结构体"),
                record_type=_short_name(_pick(row, "RecordType", "Record类型")),
                is_record=_pick(row, "IsRecord"),
                unit=_pick(row, "Unit", "单位"),
                description=_pick(row, "Description", "说明"),
                requirement_id=_pick(row, "RequirementId", "RequirementId/Source", "需求ID"),
                source_trace=_source_trace(row),
            )
        )
    return rows


def _extract_runnable_access_rows(table: DocxTable) -> list[RunnableContract]:
    rows = []
    for row in table.rows:
        runnable_name = _pick(row, "RunnableName", "Runnable名", "Runnable 名")
        access_type = _normalize_access_type(_pick(row, "AccessType"))
        port_or_signal = _pick(row, "PortOrSignal", "PortName", "SignalName", "信号/端口名", "信号名", "端口名")
        if not runnable_name or not access_type or not port_or_signal:
            continue
        read_signals = port_or_signal if access_type == "DataRead" else ""
        write_signals = port_or_signal if access_type == "DataWrite" else ""
        related_operation = _pick(row, "OperationName", "Operation", "Operation名") if access_type in {"CallOperation", "InvokeOperation", "OperationInvokedEvent"} else ""
        rows.append(
            RunnableContract(
                swc=_short_name(_pick(row, "SWC", "OwnerSWC", "ComponentName", "所属组件", "所属SWC")),
                runnable_name=_short_name(runnable_name),
                trigger_type="",
                related_port_or_signal=_short_name(port_or_signal if access_type in {"CallOperation", "InvokeOperation", "OperationInvokedEvent"} else ""),
                related_operation=_short_name(related_operation),
                read_signals=read_signals,
                write_signals=write_signals,
                description=_pick(row, "Description", "说明"),
                source_trace=_source_trace(row),
                source_status={"access_type": "explicit"},
            )
        )
    return rows


def _extract_record_elements(table: DocxTable) -> list[RecordElementContract]:
    rows = []
    for row in table.rows:
        record_type = _pick(row, "RecordTypeName", "RecordType", "结构体名")
        element_name = _pick(row, "FieldName", "ElementName", "ElementPath", "字段名")
        if not record_type or not element_name:
            continue
        field_category = _normalize_value_type(_pick(row, "DataCategory", "FieldCategory", "数据类别", "字段类别"))
        internal_range = _pick(row, "InternalRange", "内部范围")
        enum_values = _normalize_enum_values(_pick(row, "EnumValues", "状态值表", "枚举值"))
        rows.append(
            RecordElementContract(
                record_type=_short_name(record_type),
                implementation_record_type=_short_name(_pick(row, "ImplementationRecordType")),
                field_order=_pick(row, "FieldOrder"),
                element_name=_short_name(element_name),
                field_category=field_category,
                data_type=_short_name(_pick(row, "ApplicationDataType", "ApplicationFieldType", "DataType", "应用数据类型", "应用字段类型", "字段类型")),
                implementation_field_type=_short_name(_pick(row, "InternalDataType", "ImplementationDataType", "ImplementationFieldType", "内部数据类型", "内部字段类型")),
                internal_range=internal_range,
                physical_range=_pick(row, "PhysicalRange", "物理范围"),
                resolution=_pick(row, "Resolution", "分辨率"),
                offset=_pick(row, "Offset"),
                range_or_enum=enum_values or internal_range or _pick(row, "Range/Enum", "Range", "范围"),
                unit=_pick(row, "Unit", "单位"),
                init_value=_pick(row, "InitValue", "初始值", "初值"),
                description=_pick(row, "Description", "说明"),
                source_trace=_source_trace(row),
                source_status={
                    "record_type": "explicit",
                    "element_name": "explicit",
                    "data_type": status_for(_pick(row, "ApplicationDataType", "ApplicationFieldType", "DataType")),
                },
            )
        )
    return rows


def _normalize_trigger(value: str) -> str:
    text = (value or "").strip().lower().replace(" ", "")
    if "period" in text or "周期" in value:
        return "Periodic"
    if "init" in text or "初始化" in value:
        return "Init"
    if "operationinvocation" in text or "operationinvoked" in text or "operationinvokedevent" in text or "服务" in value:
        return "OperationInvoked"
    if "datareception" in text or "datareceived" in text or "信号" in value:
        return "DataReceived"
    return value


def _normalize_access_type(value: str) -> str:
    text = (value or "").strip().lower().replace(" ", "")
    if text in {"dataread", "read"} or "读取" in value:
        return "DataRead"
    if text in {"datawrite", "write"} or "写入" in value:
        return "DataWrite"
    if text in {"invokeoperation", "invokeop"}:
        return "InvokeOperation"
    if text in {"operationinvokedevent", "operationinvoked", "operationinvocated"}:
        return "OperationInvokedEvent"
    if text in {"calloperation", "servercallpoint"}:
        return "CallOperation"
    return value


def _normalize_port_role(value: str) -> str:
    text = (value or "").strip().lower()
    return {
        "server": "Server",
        "client": "Client",
        "provider": "Provider",
        "requester": "Requester",
        "sender": "Sender",
        "receiver": "Receiver",
        "p": "P",
        "r": "R",
    }.get(text, value)


def _derive_data_types_from_service_args(contract: DeliveryContract) -> None:
    existing = {item.type_name for item in contract.data_types}
    for arg in contract.operation_args:
        if not arg.data_type or arg.data_type in existing:
            continue
        category = _compu_category_for_type(arg.value_type, arg.resolution, arg.offset)
        enum_values = arg.enum_values or (arg.range_or_enum if category == "TEXTTABLE" else "")
        contract.data_types.append(
            DataTypeContract(
                type_name=arg.data_type,
                type_kind=_normalize_value_type(arg.value_type),
                base_type=_normalize_base_type(arg.internal_data_type or arg.data_type),
                compu_method_category=category,
                enum_values=enum_values,
                internal_range=arg.internal_range,
                physical_range=arg.physical_range or (arg.range_or_enum if _looks_like_range(arg.range_or_enum) else ""),
                resolution=arg.resolution,
                offset=arg.offset,
                implementation_type_name=_short_name(arg.internal_data_type) if _normalize_value_type(arg.value_type) == "Record" else "",
                unit=arg.unit,
                description=f"Derived from service argument {arg.operation_name}.{arg.argument_name}",
                source_status={
                    "type_name": "explicit",
                    "base_type": "inferred",
                    "compu_method_category": "inferred",
                },
            )
        )
        existing.add(arg.data_type)
