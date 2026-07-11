from arxml_codegen.cli import build_parser
from arxml_codegen.excel.template import create_template_v2
from arxml_codegen.excel.reader import load_workbook_v2
from arxml_codegen.generator.arxml_writer import (
    build_arxml_v2,
    validate_model_v2,
)
from arxml_codegen.models.schema import (
    ComponentPrototypeRow,
    ComponentV2Row,
    CompositionConnectorV2Row,
    CSArgumentRow,
    CSInterfaceRow,
    CSOperationRow,
    PortV2Row,
    PrimitiveDataTypeRow,
    RunnableV2Row,
    SRDataElementRow,
    SRInterfaceRow,
    WorkbookV2Model,
)


def _base_model() -> WorkbookV2Model:
    return WorkbookV2Model(
        components=[
            ComponentV2Row("Components", 2, "Enh", "Application", "/ComponentTypes", "", ""),
            ComponentV2Row("Components", 3, "Atm", "Application", "/ComponentTypes", "", ""),
            ComponentV2Row("Components", 4, "Composition_Test", "Composition", "/System", "", ""),
        ],
        primitive_data_types=[
            PrimitiveDataTypeRow("PrimitiveDataTypes", 2, "App_Bool", "/DataTypes/App_Bool", "uint8", "/Platform/uint8", "boolean", "", "", "READ-ONLY"),
        ],
        sr_interfaces=[
            SRInterfaceRow("SRInterfaces", 2, "If_Bool_SR", "/Interfaces/If_Bool_SR", "false"),
        ],
        sr_data_elements=[
            SRDataElementRow("SRDataElements", 2, "If_Bool_SR", "ntfBool", "/DataTypes/App_Bool"),
        ],
        cs_interfaces=[
            CSInterfaceRow("CSInterfaces", 2, "If_Cmd_CS", "/Interfaces/If_Cmd_CS", "false"),
        ],
        cs_operations=[
            CSOperationRow("CSOperations", 2, "If_Cmd_CS", "rrCmd"),
        ],
        cs_arguments=[
            CSArgumentRow("CSArguments", 2, "If_Cmd_CS", "rrCmd", "CmdVal", "IN", "/DataTypes/App_Bool"),
        ],
        ports=[
            PortV2Row("Ports", 2, "Atm", "pBool", "P", "SR", "/Interfaces/If_Bool_SR", "ntfBool", "", "", "", "", "", "", ""),
            PortV2Row("Ports", 3, "Enh", "rBool", "R", "SR", "/Interfaces/If_Bool_SR", "ntfBool", "", "", "", "", "", "", ""),
        ],
        runnables=[
            RunnableV2Row("Runnables", 2, "Enh", "Enh_Init", "Enh_Init"),
        ],
        component_prototypes=[
            ComponentPrototypeRow("ComponentPrototypes", 2, "Composition_Test", "Atm_Inst", "Atm", "/ComponentTypes/Atm"),
            ComponentPrototypeRow("ComponentPrototypes", 3, "Composition_Test", "Enh_Inst", "Enh", "/ComponentTypes/Enh"),
        ],
        composition_connectors=[
            CompositionConnectorV2Row("CompositionConnectors", 2, "Composition_Test", "Atm_Inst", "pBool", "Enh_Inst", "rBool", "Assembly"),
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
    create_template_v2(path)
    from openpyxl import load_workbook

    workbook = load_workbook(path)
    assert workbook["Components"].data_validations.count > 0
    assert workbook["Ports"].data_validations.count > 0
    assert workbook["RunnableEvents"].data_validations.count > 0


def test_empty_component_name_reported() -> None:
    model = _base_model()
    model.components[0].component_name = ""
    errors = validate_model_v2(model)
    assert any("ComponentName" in error for error in errors)


def test_invalid_base_type_reported() -> None:
    model = _base_model()
    model.primitive_data_types[0].base_type = "unknown_type"
    errors = validate_model_v2(model)
    assert any("BaseType" in error for error in errors)


def test_unknown_component_kind_reported() -> None:
    model = _base_model()
    model.components[0].component_kind = "InvalidKind"
    errors = validate_model_v2(model)
    assert any("ComponentKind" in error for error in errors)


def test_v2_template_loads_and_generates_arxml(tmp_path) -> None:
    path = tmp_path / "hornctrl_v2.xlsx"
    create_template_v2(path)
    model = load_workbook_v2(path)
    errors = validate_model_v2(model)
    assert errors == []

    tree = build_arxml_v2(model)
    text = str(tree.getroot().xpath("count(//*[local-name()='SW-COMPONENT-PROTOTYPE'])"))
    assert text == "4.0"


def test_v2_connector_uses_prototype_context(tmp_path) -> None:
    path = tmp_path / "hornctrl_v2.xlsx"
    create_template_v2(path)
    model = load_workbook_v2(path)
    tree = build_arxml_v2(model)
    xml_text = etree_to_text(tree)
    assert "/HORN_CTRL/System/Composition_HornCtrl/Atm_Inst" in xml_text
    assert "/HORN_CTRL/System/Composition_HornCtrl/Enh_Inst" in xml_text
    assert "/HORN_CTRL/System/Composition_HornCtrl/Gen_Inst" in xml_text


def test_v2_template_covers_record_and_linear_compu(tmp_path) -> None:
    path = tmp_path / "hornctrl_v2.xlsx"
    create_template_v2(path)
    model = load_workbook_v2(path)
    tree = build_arxml_v2(model)
    xml_text = etree_to_text(tree)
    assert "APPLICATION-RECORD-DATA-TYPE" in xml_text
    assert "IMPLEMENTATION-DATA-TYPE" in xml_text
    assert "CM_Volt_Linear" in xml_text
    assert "COMPU-RATIONAL-COEFFS" in xml_text


def test_v2_reports_unknown_data_type_ref(tmp_path) -> None:
    path = tmp_path / "hornctrl_v2.xlsx"
    create_template_v2(path)
    model = load_workbook_v2(path)
    model.sr_data_elements[0].application_type_ref = "/HORN_CTRL/ApplicationDataTypes/MissingType"
    errors = validate_model_v2(model)
    assert any("SRDataElements!R2 ApplicationTypeRef" in error for error in errors)


def test_v2_includes_units(tmp_path) -> None:
    path = tmp_path / "hornctrl_v2.xlsx"
    create_template_v2(path)
    model = load_workbook_v2(path)
    tree = build_arxml_v2(model)
    xml_text = etree_to_text(tree)
    assert "UNIT" in xml_text
    assert "FACTOR-SI-TO-UNIT" in xml_text


def etree_to_text(tree) -> str:
    from lxml import etree

    return etree.tostring(tree, encoding="unicode")
