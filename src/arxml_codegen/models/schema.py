from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SourceRow:
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class ProjectConfigRow(SourceRow):
    key: str = ""
    value: str = ""


@dataclass(slots=True)
class ComponentV2Row(SourceRow):
    component_name: str = ""
    component_kind: str = "Application"
    package_path: str = ""
    internal_behavior_name: str = ""
    implementation_name: str = ""


@dataclass(slots=True)
class ComponentPrototypeRow(SourceRow):
    composition_name: str = ""
    prototype_name: str = ""
    component_type_name: str = ""
    component_type_ref: str = ""


@dataclass(slots=True)
class PrimitiveDataTypeRow(SourceRow):
    application_type_name: str = ""
    application_type_path: str = ""
    implementation_type_name: str = ""
    implementation_type_path: str = ""
    base_type: str = ""
    compu_method_ref: str = ""
    data_constr_ref: str = ""
    calibration_access: str = "READ-ONLY"
    unit_ref: str = ""


@dataclass(slots=True)
class UnitRow(SourceRow):
    unit_name: str = ""
    unit_path: str = ""
    display_name: str = ""
    factor_si_to_unit: str = "1"
    offset_si_to_unit: str = "0"


@dataclass(slots=True)
class RecordTypeRow(SourceRow):
    application_type_name: str = ""
    application_type_path: str = ""
    implementation_type_name: str = ""
    implementation_type_path: str = ""
    calibration_access: str = "READ-ONLY"


@dataclass(slots=True)
class RecordElementRow(SourceRow):
    record_type_name: str = ""
    element_name: str = ""
    application_element_type_ref: str = ""
    implementation_element_type_ref: str = ""
    order: str = ""


@dataclass(slots=True)
class PortRecordInitValueRow(SourceRow):
    component_name: str = ""
    port_name: str = ""
    record_element_path: str = ""
    value: str = ""
    value_type: str = ""


@dataclass(slots=True)
class DataTypeMappingRow(SourceRow):
    mapping_set_path: str = ""
    application_type_ref: str = ""
    implementation_type_ref: str = ""


@dataclass(slots=True)
class CompuMethodRow(SourceRow):
    compu_method_name: str = ""
    compu_method_path: str = ""
    category: str = "IDENTICAL"


@dataclass(slots=True)
class CompuScaleRow(SourceRow):
    compu_method_name: str = ""
    lower_limit: str = ""
    upper_limit: str = ""
    text_value: str = ""
    numerator: str = ""
    denominator: str = ""
    offset: str = ""


@dataclass(slots=True)
class DataConstrRow(SourceRow):
    data_constr_name: str = ""
    data_constr_path: str = ""
    lower_limit: str = ""
    upper_limit: str = ""


@dataclass(slots=True)
class SRInterfaceRow(SourceRow):
    interface_name: str = ""
    interface_path: str = ""
    is_service: str = "false"


@dataclass(slots=True)
class SRDataElementRow(SourceRow):
    interface_name: str = ""
    data_element_name: str = ""
    application_type_ref: str = ""


@dataclass(slots=True)
class CSInterfaceRow(SourceRow):
    interface_name: str = ""
    interface_path: str = ""
    is_service: str = "false"


@dataclass(slots=True)
class CSOperationRow(SourceRow):
    interface_name: str = ""
    operation_name: str = ""


@dataclass(slots=True)
class CSArgumentRow(SourceRow):
    interface_name: str = ""
    operation_name: str = ""
    argument_name: str = ""
    direction: str = ""
    application_type_ref: str = ""


@dataclass(slots=True)
class PortV2Row(SourceRow):
    component_name: str = ""
    port_name: str = ""
    port_direction: str = ""
    interface_kind: str = ""
    interface_ref: str = ""
    data_element_name: str = ""
    operation_name: str = ""
    com_spec_kind: str = ""
    alive_timeout: str = ""
    queue_length: str = ""
    enable_update: str = ""
    handle_never_received: str = ""
    handle_timeout_type: str = ""
    init_value: str = ""
    init_value_type: str = ""


@dataclass(slots=True)
class RunnableV2Row(SourceRow):
    component_name: str = ""
    runnable_name: str = ""
    symbol: str = ""


@dataclass(slots=True)
class RunnableEventV2Row(SourceRow):
    component_name: str = ""
    runnable_name: str = ""
    trigger_type: str = ""
    period_ms: str = ""
    port_name: str = ""
    operation_name: str = ""
    data_element_name: str = ""


@dataclass(slots=True)
class RunnableAccessRow(SourceRow):
    component_name: str = ""
    runnable_name: str = ""
    access_type: str = ""
    port_name: str = ""
    operation_name: str = ""
    data_element_name: str = ""
    access_name: str = ""


@dataclass(slots=True)
class CompositionConnectorV2Row(SourceRow):
    composition_name: str = ""
    provider_prototype: str = ""
    provider_port: str = ""
    requester_prototype: str = ""
    requester_port: str = ""
    connector_type: str = "Assembly"


@dataclass(slots=True)
class WorkbookV2Model:
    project_config: list[ProjectConfigRow] = field(default_factory=list)
    components: list[ComponentV2Row] = field(default_factory=list)
    component_prototypes: list[ComponentPrototypeRow] = field(default_factory=list)
    primitive_data_types: list[PrimitiveDataTypeRow] = field(default_factory=list)
    record_types: list[RecordTypeRow] = field(default_factory=list)
    record_elements: list[RecordElementRow] = field(default_factory=list)
    port_record_init_values: list[PortRecordInitValueRow] = field(default_factory=list)
    data_type_mappings: list[DataTypeMappingRow] = field(default_factory=list)
    compu_methods: list[CompuMethodRow] = field(default_factory=list)
    compu_scales: list[CompuScaleRow] = field(default_factory=list)
    data_constrs: list[DataConstrRow] = field(default_factory=list)
    sr_interfaces: list[SRInterfaceRow] = field(default_factory=list)
    sr_data_elements: list[SRDataElementRow] = field(default_factory=list)
    cs_interfaces: list[CSInterfaceRow] = field(default_factory=list)
    cs_operations: list[CSOperationRow] = field(default_factory=list)
    cs_arguments: list[CSArgumentRow] = field(default_factory=list)
    ports: list[PortV2Row] = field(default_factory=list)
    runnables: list[RunnableV2Row] = field(default_factory=list)
    runnable_events: list[RunnableEventV2Row] = field(default_factory=list)
    runnable_accesses: list[RunnableAccessRow] = field(default_factory=list)
    composition_connectors: list[CompositionConnectorV2Row] = field(default_factory=list)
    units: list[UnitRow] = field(default_factory=list)

    def config(self, key: str, default: str = "") -> str:
        for row in self.project_config:
            if row.key == key:
                return row.value or default
        return default
