from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ComponentRow:
    component_name: str
    component_kind: str
    package_path: str
    is_composition: bool = False
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class DataTypeRow:
    adt_name: str
    idt_name: str
    base_type: str
    is_enum: bool = False
    compu_method: str = ""
    value_definition: str = ""
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class PortInterfaceRow:
    interface_name: str
    interface_kind: str
    data_element_name: str = ""
    data_type_adt: str = ""
    operation_name: str = ""
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class OperationRow:
    interface_name: str
    operation_name: str
    argument_name: str
    argument_direction: str
    argument_adt: str
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class PortRow:
    component_name: str
    port_name: str
    port_direction: str
    interface_kind: str
    interface_name: str
    data_element_name: str = ""
    operation_name: str = ""
    init_value: str = ""
    com_spec_type: str = "nonqueued"
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class RunnableRow:
    component_name: str
    runnable_name: str
    symbol: str = ""
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class RunnableEventRow:
    component_name: str
    runnable_name: str
    trigger_type: str
    period_ms: str = ""
    port_name: str = ""
    operation_name: str = ""
    data_element_name: str = ""
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class CompositionConnectorRow:
    composition_name: str
    provider_component: str
    provider_port: str
    requester_component: str
    requester_port: str
    connector_type: str = "Assembly"
    description: str = ""
    source_sheet: str = ""
    row_index: int = 0


@dataclass(slots=True)
class WorkbookModel:
    components: list[ComponentRow] = field(default_factory=list)
    data_types: list[DataTypeRow] = field(default_factory=list)
    port_interfaces: list[PortInterfaceRow] = field(default_factory=list)
    operations: list[OperationRow] = field(default_factory=list)
    ports: list[PortRow] = field(default_factory=list)
    runnables: list[RunnableRow] = field(default_factory=list)
    runnable_events: list[RunnableEventRow] = field(default_factory=list)
    composition_connectors: list[CompositionConnectorRow] = field(default_factory=list)


@dataclass(slots=True)
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors
