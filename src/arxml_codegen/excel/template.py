from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation


SHEETS: dict[str, list[str]] = {
    "Components": ["ComponentName", "ComponentKind", "PackagePath", "IsComposition", "Description"],
    "DataTypes": ["ADTName", "IDTName", "BaseType", "IsEnum", "CompuMethod", "ValueDefinition", "Description"],
    "PortInterfaces": ["InterfaceName", "InterfaceKind", "DataElementName", "DataTypeADT", "OperationName", "Description"],
    "Operations": ["InterfaceName", "OperationName", "ArgumentName", "ArgumentDirection", "ArgumentADT", "Description"],
    "Ports": ["ComponentName", "PortName", "PortDirection", "InterfaceKind", "InterfaceName", "DataElementName", "OperationName", "InitValue", "ComSpecType", "Description"],
    "Runnables": ["ComponentName", "RunnableName", "Symbol", "Description"],
    "RunnableEvents": ["ComponentName", "RunnableName", "TriggerType", "PeriodMs", "PortName", "OperationName", "DataElementName", "Description"],
    "CompositionConnectors": ["CompositionName", "ProviderComponent", "ProviderPort", "RequesterComponent", "RequesterPort", "ConnectorType", "Description"],
}


EXAMPLE_ROWS: dict[str, list[list[str]]] = {
    "Components": [
        ["total", "Composition", "/ComponentTypes", "TRUE", "Top composition"],
        ["WW_Enh", "Application", "/ComponentTypes", "FALSE", "Enhancement layer"],
        ["WW_Atm", "Application", "/ComponentTypes", "FALSE", "Atomic layer"],
    ],
    "DataTypes": [
        ["ADT_FWasherCmd", "IDT_FWasherCmd", "boolean", "FALSE", "boolean_CompuMethod", "0:OFF;1:ON", "Front washer command"],
        ["ADT_ReturnCode", "IDT_ReturnCode", "uint8", "TRUE", "ReturnCode_CompuMethod", "0:SUCCESS;1:FAILURE;2:FAIL_UNAVAILABLE;3:FAIL_INVALID_PARAM", "Operation return code"],
        ["ADT_FWasherOutput", "IDT_FWasherOutput", "boolean", "FALSE", "boolean_CompuMethod", "0:OFF;1:ON", "Front washer output"],
    ],
    "PortInterfaces": [
        ["rrFWasher", "CS", "", "", "FWasher", "FWasher service interface"],
        ["ifFWasherOutput", "SR", "VbOUT_WW_FWsher_flg", "ADT_FWasherOutput", "", "Front washer output interface"],
    ],
    "Operations": [
        ["rrFWasher", "FWasher", "FWash_Request", "IN", "ADT_FWasherCmd", ""],
        ["rrFWasher", "FWasher", "FWash_Response", "OUT", "ADT_ReturnCode", ""],
    ],
    "Ports": [
        ["WW_Enh", "rrFWasher", "R", "CS", "rrFWasher", "", "FWasher", "", "", "Client calls atom layer"],
        ["WW_Atm", "rrFWasher", "P", "CS", "rrFWasher", "", "FWasher", "", "", "Server implements washer"],
        ["WW_Atm", "pFWasherOutput", "P", "SR", "ifFWasherOutput", "VbOUT_WW_FWsher_flg", "", "0", "nonqueued", "Sender output"],
    ],
    "Runnables": [
        ["WW_Enh", "WW_Enh_Init", "WW_Enh_Init", ""],
        ["WW_Enh", "WW_Enh_Step", "WW_Enh_Step", ""],
        ["WW_Atm", "WW_Atm_Init", "WW_Atm_Init", ""],
        ["WW_Atm", "FWasher", "FWasher", "Operation name and runnable name intentionally match"],
    ],
    "RunnableEvents": [
        ["WW_Enh", "WW_Enh_Init", "Init", "", "", "", "", ""],
        ["WW_Enh", "WW_Enh_Step", "Periodic", "10", "", "", "", ""],
        ["WW_Atm", "WW_Atm_Init", "Init", "", "", "", "", ""],
        ["WW_Atm", "FWasher", "OperationInvoked", "", "rrFWasher", "FWasher", "", ""],
    ],
    "CompositionConnectors": [
        ["total", "WW_Atm", "rrFWasher", "WW_Enh", "rrFWasher", "Assembly", "Enh calls atom service"],
    ],
}


def create_template(path: Path) -> None:
    workbook = Workbook()
    workbook.remove(workbook.active)
    header_fill = PatternFill("solid", fgColor="D9EAF7")
    for sheet_name, headers in SHEETS.items():
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True)
            cell.fill = header_fill
        for row in EXAMPLE_ROWS.get(sheet_name, []):
            sheet.append(row)
        sheet.freeze_panes = "A2"
        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column) + 2
            sheet.column_dimensions[column[0].column_letter].width = min(max(width, 14), 48)

    _add_validations(workbook)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def _add_validations(workbook: Workbook) -> None:
    validations = {
        "Components": {
            "B": '"Application,Composition"',
            "D": '"TRUE,FALSE"',
        },
        "DataTypes": {
            "C": '"boolean,uint8,uint16,uint32,sint8,sint16,sint32,float32"',
            "D": '"TRUE,FALSE"',
        },
        "PortInterfaces": {
            "B": '"SR,CS"',
        },
        "Operations": {
            "D": '"IN,OUT,INOUT"',
        },
        "Ports": {
            "C": '"P,R"',
            "D": '"SR,CS"',
            "I": '"nonqueued,queued"',
        },
        "RunnableEvents": {
            "C": '"Init,Periodic,OperationInvoked,DataReceived"',
        },
        "CompositionConnectors": {
            "F": '"Assembly,Delegation"',
        },
    }
    for sheet_name, column_rules in validations.items():
        sheet = workbook[sheet_name]
        for column, formula in column_rules.items():
            validation = DataValidation(type="list", formula1=formula, allow_blank=True)
            sheet.add_data_validation(validation)
            validation.add(f"{column}2:{column}500")
