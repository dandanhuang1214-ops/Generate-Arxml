from __future__ import annotations

from pathlib import Path
from typing import Iterable

from openpyxl import load_workbook

from arxml_codegen.models.schema import (
    ComponentRow,
    CompositionConnectorRow,
    DataTypeRow,
    OperationRow,
    PortInterfaceRow,
    PortRow,
    RunnableEventRow,
    RunnableRow,
    WorkbookModel,
)


SHEET_ALIASES = {
    "Components": ("Components",),
    "DataTypes": ("DataTypes",),
    "PortInterfaces": ("PortInterfaces",),
    "Operations": ("Operations", "Arguments"),
    "Ports": ("Ports",),
    "Runnables": ("Runnables",),
    "RunnableEvents": ("RunnableEvents",),
    "CompositionConnectors": ("CompositionConnectors", "Connectors"),
}


def _normalize(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "是", "composition"}


def _sheet_rows(worksheet) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in worksheet.iter_rows(values_only=True):
        rows.append([_normalize(cell) for cell in row])
    return rows


def _header_index(header_row: list[str]) -> dict[str, int]:
    return {name: idx for idx, name in enumerate(header_row) if name}


def _cell(row: list[str], mapping: dict[str, int], *keys: str) -> str:
    for key in keys:
        idx = mapping.get(key)
        if idx is not None and idx < len(row):
            return row[idx]
    return ""


def _nonempty(row: Iterable[str]) -> bool:
    return any(cell for cell in row)


def _rows_for(workbook, logical_name: str) -> list[list[str]]:
    for sheet_name in SHEET_ALIASES[logical_name]:
        if sheet_name in workbook.sheetnames:
            return _sheet_rows(workbook[sheet_name])
    return []


def _iter_data_rows(workbook, logical_name: str):
    rows = _rows_for(workbook, logical_name)
    if not rows:
        return
    header = _header_index(rows[0])
    for row in rows[1:]:
        if _nonempty(row):
            yield header, row


def load_workbook_model(path: Path) -> WorkbookModel:
    workbook = load_workbook(path, data_only=True)
    model = WorkbookModel()

    for header, row in _iter_data_rows(workbook, "Components") or []:
        kind = _cell(row, header, "ComponentKind", "ComponentCategory")
        component_name = _cell(row, header, "ComponentName")
        is_composition = _bool(_cell(row, header, "IsComposition")) or kind.lower() == "composition"
        model.components.append(
            ComponentRow(
                component_name=component_name,
                component_kind=kind or ("Composition" if is_composition else "Application"),
                package_path=_cell(row, header, "PackagePath") or "/ComponentTypes",
                is_composition=is_composition,
                description=_cell(row, header, "Description"),
            )
        )

    for header, row in _iter_data_rows(workbook, "DataTypes") or []:
        model.data_types.append(
            DataTypeRow(
                adt_name=_cell(row, header, "ADTName", "DataType", "TypeName"),
                idt_name=_cell(row, header, "IDTName"),
                base_type=_cell(row, header, "BaseType"),
                is_enum=_bool(_cell(row, header, "IsEnum")),
                compu_method=_cell(row, header, "CompuMethod"),
                value_definition=_cell(row, header, "ValueDefinition", "ValueMap"),
                description=_cell(row, header, "Description"),
            )
        )

    for header, row in _iter_data_rows(workbook, "PortInterfaces") or []:
        model.port_interfaces.append(
            PortInterfaceRow(
                interface_name=_cell(row, header, "InterfaceName"),
                interface_kind=_cell(row, header, "InterfaceKind", "PortInterfaceKind"),
                data_element_name=_cell(row, header, "DataElementName"),
                data_type_adt=_cell(row, header, "DataTypeADT", "DataType"),
                operation_name=_cell(row, header, "OperationName"),
                description=_cell(row, header, "Description"),
            )
        )

    for header, row in _iter_data_rows(workbook, "Operations") or []:
        model.operations.append(
            OperationRow(
                interface_name=_cell(row, header, "InterfaceName"),
                operation_name=_cell(row, header, "OperationName"),
                argument_name=_cell(row, header, "ArgumentName"),
                argument_direction=_cell(row, header, "ArgumentDirection"),
                argument_adt=_cell(row, header, "ArgumentADT", "ArgumentType"),
                description=_cell(row, header, "Description"),
            )
        )

    for header, row in _iter_data_rows(workbook, "Ports") or []:
        model.ports.append(
            PortRow(
                component_name=_cell(row, header, "ComponentName"),
                port_name=_cell(row, header, "PortName"),
                port_direction=_cell(row, header, "PortDirection"),
                interface_kind=_cell(row, header, "InterfaceKind", "PortInterfaceKind"),
                interface_name=_cell(row, header, "InterfaceName"),
                data_element_name=_cell(row, header, "DataElementName"),
                operation_name=_cell(row, header, "OperationName"),
                init_value=_cell(row, header, "InitValue"),
                com_spec_type=_cell(row, header, "ComSpecType") or "nonqueued",
                description=_cell(row, header, "Description"),
            )
        )

    for header, row in _iter_data_rows(workbook, "Runnables") or []:
        model.runnables.append(
            RunnableRow(
                component_name=_cell(row, header, "ComponentName"),
                runnable_name=_cell(row, header, "RunnableName"),
                symbol=_cell(row, header, "Symbol") or _cell(row, header, "RunnableName"),
                description=_cell(row, header, "Description"),
            )
        )

        # Backward compatibility with the older template where events lived in Runnables.
        trigger = _cell(row, header, "TriggerType")
        if trigger:
            model.runnable_events.append(
                RunnableEventRow(
                    component_name=_cell(row, header, "ComponentName"),
                    runnable_name=_cell(row, header, "RunnableName"),
                    trigger_type=trigger,
                    period_ms=_cell(row, header, "PeriodMs"),
                    port_name=_cell(row, header, "PortName"),
                    operation_name=_cell(row, header, "OperationName"),
                    description=_cell(row, header, "Description"),
                )
            )

    for header, row in _iter_data_rows(workbook, "RunnableEvents") or []:
        model.runnable_events.append(
            RunnableEventRow(
                component_name=_cell(row, header, "ComponentName"),
                runnable_name=_cell(row, header, "RunnableName"),
                trigger_type=_cell(row, header, "TriggerType"),
                period_ms=_cell(row, header, "PeriodMs"),
                port_name=_cell(row, header, "PortName"),
                operation_name=_cell(row, header, "OperationName"),
                data_element_name=_cell(row, header, "DataElementName"),
                description=_cell(row, header, "Description"),
            )
        )

    for header, row in _iter_data_rows(workbook, "CompositionConnectors") or []:
        model.composition_connectors.append(
            CompositionConnectorRow(
                composition_name=_cell(row, header, "CompositionName"),
                provider_component=_cell(row, header, "ProviderComponent"),
                provider_port=_cell(row, header, "ProviderPort"),
                requester_component=_cell(row, header, "RequesterComponent"),
                requester_port=_cell(row, header, "RequesterPort"),
                connector_type=_cell(row, header, "ConnectorType") or "Assembly",
                description=_cell(row, header, "Description"),
            )
        )

    _infer_missing_data(model)
    return model


def _infer_missing_data(model: WorkbookModel) -> None:
    if not model.port_interfaces:
        seen: set[tuple[str, str]] = set()
        for port in model.ports:
            key = (port.interface_kind.upper(), port.interface_name)
            if port.interface_name and key not in seen:
                seen.add(key)
                model.port_interfaces.append(
                    PortInterfaceRow(
                        interface_name=port.interface_name,
                        interface_kind=port.interface_kind,
                        data_element_name=port.data_element_name,
                        data_type_adt="",
                        operation_name=port.operation_name,
                    )
                )

    if not model.data_types:
        type_names: set[str] = set()
        for port in model.ports:
            if port.interface_kind.upper() == "SR" and port.data_element_name:
                # Older workbooks put the ADT in the DataType column.
                type_names.add(port.description if False else "")
        for operation in model.operations:
            type_names.add(operation.argument_adt)
        for type_name in sorted(t for t in type_names if t):
            model.data_types.append(
                DataTypeRow(
                    adt_name=type_name,
                    idt_name=type_name.replace("ADT_", "IDT_", 1),
                    base_type="uint8",
                )
            )
