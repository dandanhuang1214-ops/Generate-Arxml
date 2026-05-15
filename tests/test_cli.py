from arxml_codegen.cli import build_parser
from arxml_codegen.excel.template import create_template
from arxml_codegen.generator.arxml_writer import validate_model
from arxml_codegen.models.schema import (
    ComponentRow,
    CompositionConnectorRow,
    DataTypeRow,
    PortInterfaceRow,
    PortRow,
    RunnableRow,
    WorkbookModel,
)


def _base_model() -> WorkbookModel:
    return WorkbookModel(
        components=[
            ComponentRow("Enh", "Application", "/ComponentTypes", source_sheet="Components", row_index=2),
            ComponentRow("Atm", "Application", "/ComponentTypes", source_sheet="Components", row_index=3),
        ],
        data_types=[
            DataTypeRow("ADT_Bool", "IDT_Bool", "boolean", source_sheet="DataTypes", row_index=2),
        ],
        port_interfaces=[
            PortInterfaceRow("ifBool", "SR", "BoolValue", "ADT_Bool", source_sheet="PortInterfaces", row_index=2),
        ],
        ports=[
            PortRow("Atm", "pBool", "P", "SR", "ifBool", "BoolValue", source_sheet="Ports", row_index=2),
            PortRow("Enh", "rBool", "R", "SR", "ifBool", "BoolValue", source_sheet="Ports", row_index=3),
        ],
        runnables=[
            RunnableRow("Enh", "Init", "Enh_Init", source_sheet="Runnables", row_index=2),
        ],
        composition_connectors=[
            CompositionConnectorRow("total", "Atm", "pBool", "Enh", "rBool", source_sheet="CompositionConnectors", row_index=2),
        ],
    )


def test_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.config.parts[-2:] == ("config", "project.yaml")
    assert args.dry_run is False
    assert args.create_template is None


def test_template_validations_are_present(tmp_path) -> None:
    path = tmp_path / "template.xlsx"
    create_template(path)
    from openpyxl import load_workbook

    workbook = load_workbook(path)
    assert workbook["Components"].data_validations.count > 0
    assert workbook["Ports"].data_validations.count > 0
    assert workbook["RunnableEvents"].data_validations.count > 0


def test_invalid_short_name_reports_excel_location() -> None:
    model = _base_model()
    model.data_types[0].adt_name = "ADT&Amp"
    result = validate_model(model)
    assert not result.ok
    assert any("DataTypes!R2 ADTName" in error for error in result.errors)


def test_connector_interface_mismatch_is_reported() -> None:
    model = _base_model()
    model.port_interfaces.append(
        PortInterfaceRow("ifOther", "SR", "OtherValue", "ADT_Bool", source_sheet="PortInterfaces", row_index=3)
    )
    model.ports[1].interface_name = "ifOther"
    result = validate_model(model)
    assert not result.ok
    assert any("connector endpoints must use the same interface name" in error for error in result.errors)
