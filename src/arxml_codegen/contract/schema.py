from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


FieldSource = Literal["explicit", "inferred", "defaulted", "missing"]


@dataclass(slots=True)
class OpenIssue:
    field: str
    question: str
    suggested_default: str = ""
    owner: str = ""
    status: str = "open"
    source: str = ""


@dataclass(slots=True)
class ProjectContract:
    system_name: str = ""
    root_package: str = "/ARXML_PROJECT"
    generation_profile: str = "generic"
    composition_name: str = ""
    interface_package: str = "/PortInterfaces"
    data_type_package: str = "/DataTypes"
    compu_method_package: str = "/DataTypes/CompuMethods"
    data_constr_package: str = "/DataTypes/DataConstrs"
    unit_package: str = "/DataTypes/Units"
    mapping_set_path: str = "/ComponentTypes/MappingSets/APP_data_mapping"
    domain: str = ""
    target_autosar_version: str = "4-3-0"
    component_prefix: str = ""
    interface_prefix: str = "If"
    data_type_prefix: str = "App"
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class SwcContract:
    name: str = ""
    prototype_name: str = ""
    kind: str = "Application"
    layer: str = ""
    domain: str = ""
    is_composition: str = ""
    description: str = ""
    requirement_id: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class SignalContract:
    signal_name: str = ""
    direction: str = ""
    provider_swc: str = ""
    consumer_swc: str = ""
    value_type: str = ""
    data_type: str = ""
    internal_data_type: str = ""
    internal_range: str = ""
    physical_range: str = ""
    resolution: str = ""
    offset: str = ""
    unit: str = ""
    range: str = ""
    enum_values: str = ""
    init_value: str = ""
    period_ms: str = ""
    description: str = ""
    requirement_id: str = ""
    source: str = ""
    source_trace: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class DataTypeContract:
    type_name: str = ""
    type_kind: str = ""
    base_type: str = ""
    compu_method_category: str = ""
    enum_values: str = ""
    internal_range: str = ""
    physical_range: str = ""
    resolution: str = ""
    offset: str = ""
    implementation_type_name: str = ""
    field_order: str = ""
    field_name: str = ""
    field_type: str = ""
    range_or_enum: str = ""
    unit: str = ""
    description: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class ServiceContract:
    service_name: str = ""
    owner_swc: str = ""
    provider_swc: str = ""
    client_swc: str = ""
    interface_name: str = ""
    port_name: str = ""
    operation_name: str = ""
    port_role: str = ""
    communication: str = ""
    port_type: str = ""
    sync_async: str = "sync"
    timeout_ms: str = ""
    queue_length: str = ""
    description: str = ""
    requirement_id: str = ""
    source_trace: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class OperationArgumentContract:
    interface_name: str = ""
    operation_name: str = ""
    argument_name: str = ""
    direction: str = ""
    value_type: str = ""
    internal_data_type: str = ""
    data_type: str = ""
    internal_range: str = ""
    physical_range: str = ""
    resolution: str = ""
    offset: str = ""
    enum_values: str = ""
    range_or_enum: str = ""
    record_type: str = ""
    is_record: str = ""
    unit: str = ""
    description: str = ""
    requirement_id: str = ""
    source_trace: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class RecordElementContract:
    record_type: str = ""
    implementation_record_type: str = ""
    field_order: str = ""
    element_name: str = ""
    field_category: str = ""
    data_type: str = ""
    implementation_field_type: str = ""
    internal_range: str = ""
    physical_range: str = ""
    resolution: str = ""
    offset: str = ""
    range_or_enum: str = ""
    unit: str = ""
    init_value: str = ""
    description: str = ""
    source_trace: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class RunnableContract:
    swc: str = ""
    runnable_name: str = ""
    trigger_type: str = ""
    period_ms: str = ""
    trigger_object: str = ""
    related_port_or_signal: str = ""
    related_operation: str = ""
    read_signals: str = ""
    write_signals: str = ""
    description: str = ""
    requirement_id: str = ""
    source_trace: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class ConnectorContract:
    connector_type: str = ""
    provider_endpoint: str = ""
    requester_endpoint: str = ""
    interface_name: str = ""
    description: str = ""
    requirement_id: str = ""
    source_trace: str = ""
    source_status: dict[str, FieldSource] = field(default_factory=dict)


@dataclass(slots=True)
class DeliveryContract:
    project: ProjectContract = field(default_factory=ProjectContract)
    swcs: list[SwcContract] = field(default_factory=list)
    signals: list[SignalContract] = field(default_factory=list)
    data_types: list[DataTypeContract] = field(default_factory=list)
    record_elements: list[RecordElementContract] = field(default_factory=list)
    services: list[ServiceContract] = field(default_factory=list)
    operation_args: list[OperationArgumentContract] = field(default_factory=list)
    runnables: list[RunnableContract] = field(default_factory=list)
    connectors: list[ConnectorContract] = field(default_factory=list)
    open_issues: list[OpenIssue] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DeliveryContract":
        return cls(
            project=ProjectContract(**dict(data.get("project") or {})),
            swcs=[SwcContract(**item) for item in list(data.get("swcs") or [])],
            signals=[SignalContract(**item) for item in list(data.get("signals") or [])],
            data_types=[DataTypeContract(**item) for item in list(data.get("data_types") or [])],
            record_elements=[
                RecordElementContract(**item)
                for item in list(data.get("record_elements") or [])
            ],
            services=[ServiceContract(**item) for item in list(data.get("services") or [])],
            operation_args=[
                OperationArgumentContract(**item)
                for item in list(data.get("operation_args") or [])
            ],
            runnables=[RunnableContract(**item) for item in list(data.get("runnables") or [])],
            connectors=[
                ConnectorContract(**item) for item in list(data.get("connectors") or [])
            ],
            open_issues=[OpenIssue(**item) for item in list(data.get("open_issues") or [])],
            metadata=dict(data.get("metadata") or {}),
        )


def status_for(value: str, fallback: FieldSource = "explicit") -> FieldSource:
    return fallback if value else "missing"
