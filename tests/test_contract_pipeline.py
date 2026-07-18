from __future__ import annotations

import zipfile

from arxml_codegen.contract.docx_loader import _add_gap_issues, extract_contract_from_docx
from arxml_codegen.contract.excel_builder import build_workbook_rows, write_contract_excel
from arxml_codegen.contract.gap_report import build_gap_report, gap_report_markdown
from arxml_codegen.contract.schema import (
    DeliveryContract,
    DataTypeContract,
    OperationArgumentContract,
    ProjectContract,
    RecordElementContract,
    RunnableContract,
    ServiceContract,
    SignalContract,
    SwcContract,
)
from arxml_codegen.excel.reader import load_workbook_v2
from arxml_codegen.generator.arxml_writer import validate_model_v2
from arxml_codegen.validator.engine import run_all as run_core_validation


def test_signal_contract_docx_to_excel(tmp_path) -> None:
    docx = tmp_path / "signal.docx"
    _write_minimal_docx(
        docx,
        [
            ("XX系统 ARXML 接口交付文档", None),
            (
                "二、输入信号定义",
                [
                    ["信号名", "值类型🟢", "建议数据类型🟢", "物理范围🟢", "单位🟡", "初始值🟢", "信号来源🟢", "作用描述🟢"],
                    ["VehicleSpeed", "Numeric", "VehicleSpeed_T", "0-250", "kmh", "0", "SpeedSensor", "Vehicle speed"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx)
    assert len(contract.signals) == 1
    assert contract.signals[0].provider_swc == "SpeedSensor"

    excel = tmp_path / "draft.xlsx"
    write_contract_excel(contract, excel)
    model = load_workbook_v2(excel)
    assert model.sr_interfaces
    assert model.ports


def test_signal_contract_accepts_internal_data_type_header(tmp_path) -> None:
    docx = tmp_path / "signal_internal_type.docx"
    _write_minimal_docx(
        docx,
        [
            ("XX系统 ARXML 接口交付文档", None),
            (
                "二、输入信号定义",
                [
                    ["信号名", "值类型🟢", "内部数据类型🟢", "物理范围🟢", "单位🟡", "初始值🟢", "信号来源🟢", "作用描述🟢"],
                    ["LampMode", "Enum", "uint8", "0-15", "-", "OFF", "BCM", "Lamp mode"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx)

    assert len(contract.signals) == 1
    assert contract.signals[0].data_type == "App_LampMode"
    assert contract.signals[0].internal_data_type == "uint8"
    assert contract.signals[0].provider_swc == "BCM"


def test_signal_atomic_profile_maps_enum_numeric_init_to_text_symbol(tmp_path) -> None:
    docx = tmp_path / "signal_enum_init.docx"
    _write_minimal_docx(
        docx,
        [
            ("XX系统 ARXML 接口交付文档", None),
            (
                "二、输入信号定义",
                [
                    ["信号名", "值类型🟢", "内部数据类型🟢", "物理范围🟢", "状态值表🟡", "初始值🟢", "信号来源🟢", "作用描述🟢"],
                    ["LampMode", "Enum", "uint8", "0-15", "0=OFF, 1=LowBeam, 15=Error_Value", "1", "BCM", "Lamp mode"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["所属组件", "Runnable名", "AccessType", "信号/端口名", "OperationName", "说明"],
                    ["TurnLamp", "TurnLamp_Step", "DataRead", "LampMode", "", "read"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    rows = build_workbook_rows(contract)
    port = rows["Ports"][0]

    assert port["InitValueType"] == "Enum"
    assert port["InitValue"] == "LowBeam"


def test_signal_atomic_profile_adds_identical_compu_method_for_numeric_base_type(tmp_path) -> None:
    docx = tmp_path / "signal_numeric_compu.docx"
    _write_minimal_docx(
        docx,
        [
            ("XX系统 ARXML 接口交付文档", None),
            (
                "二、输入信号定义",
                [
                    ["信号名", "值类型🟢", "内部数据类型🟢", "物理范围🟢", "初始值🟢", "信号来源🟢", "作用描述🟢"],
                    ["LampLevel", "Numeric", "uint8", "0-100", "0", "BCM", "Lamp level"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    rows = build_workbook_rows(contract)

    app_uint8 = next(row for row in rows["PrimitiveDataTypes"] if row["ApplicationTypeName"] == "App_uint8")
    assert app_uint8["CompuMethodRef"] == "/DataTypes/CompuMethods/CM_App_uint8_Identical"
    assert {
        "CompuMethodName": "CM_App_uint8_Identical",
        "CompuMethodPath": "/DataTypes/CompuMethods/CM_App_uint8_Identical",
        "Category": "IDENTICAL",
        "Description": "Shared uint8 conversion method",
    } in rows["CompuMethods"]


def test_signal_atomic_profile_treats_uint8_value_type_as_value_not_enum(tmp_path) -> None:
    docx = tmp_path / "turnlamp_value_type.docx"
    _write_minimal_docx(
        docx,
        [
            ("转向灯arxml交付文档", None),
            (
                "2.  输入信号定义",
                [
                    ["No", "输入信号", "值类型", "内部数据类型", "物理范围", "状态值表", "初始值", "信号来源", "作用描述"],
                    ["1", "VeINP_PDU_PowerMode_sig", "uint8", "uint8", "0-255", "0=OFF, 1=ON", "0", "BCM", "Power mode"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["所属组件", "Runnable名", "AccessType", "信号/端口名", "OperationName", "说明"],
                    ["TurnLamp", "TurnLamp_Step", "DataRead", "VeINP_PDU_PowerMode_sig", "", "read"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    assert len(contract.signals) == 1
    assert contract.signals[0].signal_name == "VeINP_PDU_PowerMode_sig"
    assert contract.signals[0].value_type == "Value"
    assert contract.signals[0].enum_values == ""

    rows = build_workbook_rows(contract)
    port = rows["Ports"][0]

    assert port["InitValueType"] == "Value"
    assert port["InitValue"] == "0"
    assert not any(row["Category"] == "TEXTTABLE" and "PowerMode" in row["CompuMethodName"] for row in rows["CompuMethods"])


def test_signal_atomic_profile_uses_output_signal_header_for_p_ports(tmp_path) -> None:
    docx = tmp_path / "turnlamp_output_direction.docx"
    _write_minimal_docx(
        docx,
        [
            ("转向灯arxml交付文档", None),
            (
                "接口定义",
                [
                    ["No", "输入信号", "值类型", "内部数据类型", "物理范围", "初始值", "信号来源", "作用描述"],
                    ["1", "VbINP_Test_flg", "boolean", "boolean", "0-1", "0", "BCM", "Input"],
                ],
            ),
            (
                "接口定义",
                [
                    ["No", "输出信号", "值数据类型", "内部数据类型", "物理范围", "初始值", "越限处理", "作用描述"],
                    ["1", "VbOUT_Test_flg", "boolean", "boolean", "0-1", "0", "默认（不处理）", "Output"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    assert [(signal.signal_name, signal.direction) for signal in contract.signals] == [
        ("VbINP_Test_flg", "input"),
        ("VbOUT_Test_flg", "output"),
    ]

    rows = build_workbook_rows(contract)
    directions = {row["PortName"]: row["PortDirection"] for row in rows["Ports"]}

    assert directions == {}


def test_signal_atomic_profile_supports_new_signal_type_columns_and_linear(tmp_path) -> None:
    docx = tmp_path / "new_signal_template.docx"
    _write_minimal_docx(
        docx,
        [
            ("转向灯arxml交付文档", None),
            (
                "输入信号定义",
                [
                    [
                        "No",
                        "输入信号",
                        "数据类别",
                        "应用数据类型",
                        "内部数据类型",
                        "内部范围",
                        "物理范围",
                        "分辨率",
                        "Offset",
                        "单位",
                        "状态值表",
                        "初始值",
                        "信号来源",
                        "作用描述",
                    ],
                    ["1", "ntfDutyRat", "Value", "App_DutyRat", "uint16", "0-1000", "0-100", "0.1", "0", "%", "", "0", "BCM", "Duty ratio"],
                    ["2", "ntfReturnCode", "Enum", "App_ReturnCode", "uint8", "0-255", "", "", "", "", "0=Success1=Fail2=Fail_Invalid", "Success", "BCM", "Return code"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    rows = build_workbook_rows(contract)

    duty = next(row for row in rows["PrimitiveDataTypes"] if row["ApplicationTypeName"] == "App_DutyRat")
    assert duty["ImplementationTypeName"] == "uint16"
    assert duty["CompuMethodRef"] == "/DataTypes/CompuMethods/CM_App_DutyRat_Linear"
    assert duty["DataConstrRef"] == "/DataTypes/DataConstrs/DC_App_DutyRat"
    assert {
        "CompuMethodName": "CM_App_DutyRat_Linear",
        "LowerLimit": "0",
        "UpperLimit": "100",
        "Numerator": "0.1",
        "Denominator": "1",
        "Offset": "0",
    } in rows["CompuScales"]
    assert {
        "DataConstrName": "DC_App_DutyRat",
        "DataConstrPath": "/DataTypes/DataConstrs/DC_App_DutyRat",
        "LowerLimit": "0",
        "UpperLimit": "1000",
        "Description": "Derived from signal ntfDutyRat",
    } in rows["DataConstrs"]

    enum_type = next(row for row in rows["PrimitiveDataTypes"] if row["ApplicationTypeName"] == "App_ReturnCode")
    assert enum_type["CompuMethodRef"] == "/DataTypes/CompuMethods/CM_App_ReturnCode_TextTable"
    assert enum_type["DataConstrRef"] == "/DataTypes/DataConstrs/DC_App_ReturnCode"
    assert {
        "DataConstrName": "DC_App_ReturnCode",
        "DataConstrPath": "/DataTypes/DataConstrs/DC_App_ReturnCode",
        "LowerLimit": "0",
        "UpperLimit": "255",
        "Description": "Derived from signal ntfReturnCode",
    } in rows["DataConstrs"]


def test_signal_atomic_profile_parses_runnable_access_table(tmp_path) -> None:
    docx = tmp_path / "access_table.docx"
    _write_minimal_docx(
        docx,
        [
            ("转向灯arxml交付文档", None),
            (
                "输入信号定义",
                [
                    ["No", "输入信号", "数据类别", "应用数据类型", "内部数据类型", "内部范围", "物理范围", "初始值", "信号来源", "作用描述"],
                    ["1", "VeINP_A", "Value", "App_uint8", "uint8", "0-255", "0-255", "0", "BCM", "Input A"],
                ],
            ),
            (
                "输出信号定义",
                [
                    ["No", "输出信号", "数据类别", "应用数据类型", "内部数据类型", "内部范围", "物理范围", "初始值", "信号来源", "作用描述"],
                    ["1", "VbOUT_X", "Boolean", "App_boolean", "boolean", "0-1", "0-1", "0", "TurnLamp", "Output X"],
                ],
            ),
            (
                "Runnable 概览",
                [
                    ["所属组件", "Runnable 名", "触发类型", "周期(ms)", "说明"],
                    ["TurnLamp", "TurnLamp_Step", "Periodic", "10", "Main"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["所属组件", "Runnable名", "AccessType", "信号/端口名", "OperationName", "说明"],
                    ["TurnLamp", "TurnLamp_Step", "DataRead", "VeINP_A", "", "read"],
                    ["TurnLamp", "TurnLamp_Step", "DataWrite", "VbOUT_X", "", "write"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    rows = build_workbook_rows(contract)
    accesses = {
        (row["RunnableName"], row["AccessType"], row["PortName"])
        for row in rows["RunnableAccesses"]
    }

    assert ("TurnLamp_Step", "DataRead", "VeINP_A") in accesses
    assert ("TurnLamp_Step", "DataWrite", "VbOUT_X") in accesses


def test_signal_atomic_profile_derives_missing_signals_from_access_table(tmp_path) -> None:
    docx = tmp_path / "access_only_signal.docx"
    _write_minimal_docx(
        docx,
        [
            ("转向灯arxml交付文档", None),
            (
                "Runnable Access",
                [
                    ["所属组件", "Runnable名", "AccessType", "信号/端口名", "OperationName", "说明"],
                    ["TurnLamp", "TurnLamp_Step", "DataRead", "VeINP_A", "", "read"],
                    ["TurnLamp", "TurnLamp_Step", "DataWrite", "VbOUT_X", "", "write"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    assert {signal.signal_name for signal in contract.signals} == {"VeINP_A", "VbOUT_X"}

    rows = build_workbook_rows(contract)
    ports = {row["PortName"]: row["PortDirection"] for row in rows["Ports"]}

    assert ports["VeINP_A"] == "R"
    assert ports["VbOUT_X"] == "P"


def test_soa_profile_reports_missing_sr_signal_from_access_table(tmp_path) -> None:
    docx = tmp_path / "soa_missing_sr_signal.docx"
    _write_minimal_docx(
        docx,
        [
            ("SOA接口交付文档", None),
            (
                "SWC and Composition",
                [
                    ["SWCName", "PrototypeName", "SWCType", "IsComposition", "Description"],
                    ["BOD_Trk_Enh", "Inst_Enh", "Atomic", "false", "enh"],
                    ["Trk_Composition", "Trk_Composition", "Composition", "true", "composition"],
                ],
            ),
            (
                "Runnable Overview",
                [
                    ["SWC", "RunnableName", "TriggerType", "PeriodMs", "Description"],
                    ["BOD_Trk_Enh", "BOD_Trk_Enh_Step", "Periodic", "10", "main"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["SWC", "RunnableName", "AccessType", "PortOrSignal", "OperationName", "Description"],
                    ["BOD_Trk_Enh", "BOD_Trk_Enh_Step", "DataRead", "ntfMissing", "", "missing signal"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx, mode="soa")
    contract.project.generation_profile = "mixed_signal_soa"

    assert {signal.signal_name for signal in contract.signals} == set()
    assert any("ntfMissing" in issue.question for issue in contract.open_issues)

    rows = build_workbook_rows(contract)
    assert not rows["SRInterfaces"]
    assert not rows["Ports"]

    excel = tmp_path / "soa_missing_sr_signal.xlsx"
    write_contract_excel(contract, excel)
    model = load_workbook_v2(excel)
    report = build_gap_report(contract, model, validate_model_v2(model), run_core_validation(model))
    markdown = gap_report_markdown(report)

    assert report.counts["open_issues"] >= 1
    assert "ntfMissing" in markdown
    assert "未定义的 S/R 信号" in markdown


def test_mixed_profile_reuses_davinci_signal_type_and_access_rules(tmp_path) -> None:
    docx = tmp_path / "mixed_signal_soa.docx"
    _write_minimal_docx(
        docx,
        [
            ("Mixed CP delivery", None),
            (
                "Project",
                [
                    ["字段", "填写值", "说明"],
                    ["项目/系统名称", "ALM", ""],
                    ["目标 AUTOSAR 版本", "4-3-0", ""],
                    ["生成模式", "mixed_signal_soa", ""],
                    ["RootPackage", "DaVinci 默认路径", ""],
                ],
            ),
            (
                "SWCs",
                [
                    ["SWCName", "PrototypeName", "SWCType", "IsComposition", "Description"],
                    ["ALM_Enh", "Inst_Enh", "Atomic", "false", "enh"],
                    ["ALM_Atm", "Inst_Atm", "Atomic", "false", "atm"],
                    ["ALM_Composition", "ALM_Composition", "Composition", "true", "composition"],
                ],
            ),
            (
                "Signals",
                [
                    [
                        "SignalName", "ValueType", "ApplicationDataType", "InternalDataType",
                        "InternalRange", "PhysicalRange", "Resolution", "Offset", "Unit",
                        "EnumValues", "InitValue", "Description",
                    ],
                    ["ntfTrkDutyRat", "Value", "App_DutyRat", "uint8", "0-255", "0-100", "0.1", "0", "%", "", "0", "duty"],
                    ["vbTrkSleepPermit", "Boolean", "App_boolean", "boolean", "0-1", "0-1", "", "", "No_Unit", "", "0", "sleep"],
                    ["ntfStatus", "Record", "App_Status", "Impl_Status", "", "", "", "", "", "", "", "status"],
                ],
            ),
            (
                "Record",
                [
                    [
                        "RecordTypeName", "ImplementationRecordType", "FieldOrder", "FieldName",
                        "DataCategory", "ApplicationDataType", "InternalDataType", "InternalRange",
                        "PhysicalRange", "Resolution", "Offset", "Unit", "EnumValues", "InitValue",
                    ],
                    ["App_Status", "Impl_Status", "1", "CallId", "Value", "App_uint16", "uint16", "0-65535", "0-65535", "", "", "No_Unit", "", "0"],
                ],
            ),
            (
                "Runnable Overview",
                [
                    ["SWC", "RunnableName", "TriggerType", "PeriodMs", "Description"],
                    ["ALM_Enh", "ALM_Enh_Step", "Periodic", "10", "step"],
                    ["ALM_Atm", "rrTrkCtrl_Atm_rrTrkCtrl", "OperationInvocation", "", "server"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["SWC", "RunnableName", "AccessType", "PortOrSignal", "OperationName", "Description"],
                    ["ALM_Enh", "ALM_Enh_Step", "DataRead", "ntfTrkDutyRat", "", "read duty"],
                    ["ALM_Atm", "rrTrkCtrl_Atm_rrTrkCtrl", "DataRead", "vbTrkSleepPermit", "", "read sleep"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx, mode="soa")
    rows = build_workbook_rows(contract)

    assert contract.project.system_name == "ALM"
    assert contract.project.generation_profile == "mixed_signal_soa"
    assert contract.project.root_package == "/ComponentTypes"
    assert not contract.open_issues
    assert {row["InterfaceName"] for row in rows["SRInterfaces"]} == {
        "ntfTrkDutyRat", "vbTrkSleepPermit", "ntfStatus",
    }
    assert {
        (row["InterfaceName"], row["DataElementName"])
        for row in rows["SRDataElements"]
    } == {
        ("ntfTrkDutyRat", "ntfTrkDutyRat"),
        ("vbTrkSleepPermit", "vbTrkSleepPermit"),
        ("ntfStatus", "ntfStatus"),
    }
    assert {
        (row["ComponentName"], row["PortName"], row["PortDirection"])
        for row in rows["Ports"] if row["InterfaceKind"] == "SR"
    } == {
        ("ALM_Enh", "ntfTrkDutyRat", "R"),
        ("ALM_Atm", "vbTrkSleepPermit", "R"),
    }
    assert not any(
        row["PortName"].startswith(("Rp_", "Pp_"))
        for row in rows["Ports"] if row["InterfaceKind"] == "SR"
    )

    primitive_names = {row["ApplicationTypeName"] for row in rows["PrimitiveDataTypes"]}
    assert "App_Status" not in primitive_names
    status = next(row for row in rows["RecordTypes"] if row["ApplicationTypeName"] == "App_Status")
    assert status["ImplementationTypeName"] == "Impl_Status"
    boolean = next(row for row in rows["PrimitiveDataTypes"] if row["ApplicationTypeName"] == "App_boolean")
    assert boolean["CompuMethodRef"] == "/AUTOSAR_Platform/CompuMethods/boolean_CompuMethod"
    uint16 = next(row for row in rows["PrimitiveDataTypes"] if row["ApplicationTypeName"] == "App_uint16")
    assert uint16["CompuMethodRef"] == "/DataTypes/CompuMethods/CM_App_uint16_Identical"
    assert any(
        row["CompuMethodPath"] == "/DataTypes/CompuMethods/CM_App_uint16_Identical"
        for row in rows["CompuMethods"]
    )
    duty = next(row for row in rows["PrimitiveDataTypes"] if row["ApplicationTypeName"] == "App_DutyRat")
    assert duty["CompuMethodRef"] == "/DataTypes/CompuMethods/CM_App_DutyRat_Linear"
    assert duty["UnitRef"] == ""
    assert {row["UnitPath"] for row in rows["Units"]} == {"/DataTypes/Units/No_Unit"}
    assert {
        "CompuMethodName": "CM_App_DutyRat_Linear",
        "LowerLimit": "0",
        "UpperLimit": "100",
        "Numerator": "0.1",
        "Denominator": "1",
        "Offset": "0",
    } in rows["CompuScales"]
    assert {
        (row["ComponentName"], row["RunnableName"], row["PortName"], row["DataElementName"])
        for row in rows["RunnableAccesses"] if row["AccessType"] == "DataRead"
    } == {
        ("ALM_Enh", "ALM_Enh_Step", "ntfTrkDutyRat", "ntfTrkDutyRat"),
        ("ALM_Atm", "rrTrkCtrl_Atm_rrTrkCtrl", "vbTrkSleepPermit", "vbTrkSleepPermit"),
    }


def test_mixed_profile_uses_cs_port_role_not_name_prefix() -> None:
    contract = DeliveryContract(
        project=ProjectContract(
            system_name="RoleTest",
            generation_profile="mixed_signal_soa",
        ),
        swcs=[
            SwcContract(name="ClientSwc", kind="Application"),
            SwcContract(name="Composition_RoleTest", kind="Composition"),
        ],
        services=[
            ServiceContract(
                service_name="RunService",
                owner_swc="ClientSwc",
                client_swc="ClientSwc",
                interface_name="RunService",
                port_name="ClientCall",
                operation_name="RunService",
                port_role="Client",
            )
        ],
        runnables=[
            RunnableContract(
                swc="ClientSwc",
                runnable_name="ClientSwc_Step",
                trigger_type="Periodic",
                period_ms="10",
            ),
            RunnableContract(
                swc="ClientSwc",
                runnable_name="ClientSwc_Step",
                related_port_or_signal="ClientCall",
                related_operation="RunService",
            ),
        ],
    )

    rows = build_workbook_rows(contract)

    assert {
        (row["AccessType"], row["PortName"], row["OperationName"])
        for row in rows["RunnableAccesses"]
    } == {("ServerCallPoint", "ClientCall", "RunService")}


def test_operation_argument_keeps_explicit_interface_name() -> None:
    contract = DeliveryContract(
        project=ProjectContract(
            system_name="OperationTest",
            generation_profile="mixed_signal_soa",
        ),
        services=[
            ServiceContract(service_name="A", interface_name="IfA", operation_name="Run"),
            ServiceContract(service_name="B", interface_name="IfB", operation_name="Run"),
        ],
        operation_args=[
            OperationArgumentContract(
                interface_name="IfB",
                operation_name="Run",
                argument_name="Value",
                direction="IN",
                value_type="Value",
                data_type="App_uint8",
                internal_data_type="uint8",
            )
        ],
    )

    rows = build_workbook_rows(contract)

    assert rows["CSArguments"][0]["InterfaceName"] == "IfB"


def test_contract_report_flags_multi_operation_port_and_adt_conflict() -> None:
    contract = DeliveryContract(
        project=ProjectContract(
            system_name="ReportTest",
            generation_profile="mixed_signal_soa",
        ),
        services=[
            ServiceContract(
                service_name="Service",
                owner_swc="Server",
                interface_name="Service",
                port_name="ServicePort",
                operation_name="OpA",
                port_role="Server",
            ),
            ServiceContract(
                service_name="Service",
                owner_swc="Server",
                interface_name="Service",
                port_name="ServicePort",
                operation_name="OpB",
                port_role="Server",
            ),
        ],
        signals=[
            SignalContract(
                signal_name="SigA",
                value_type="Value",
                data_type="App_X",
                internal_data_type="uint8",
                init_value="0",
            ),
            SignalContract(
                signal_name="SigB",
                value_type="Record",
                data_type="App_X",
                internal_data_type="Impl_X",
            ),
        ],
        data_types=[
            DataTypeContract(
                type_name="App_X",
                type_kind="Value",
                base_type="uint8",
            )
        ],
    )

    _add_gap_issues(contract)
    fields = {issue.field for issue in contract.open_issues}

    assert "services.Server.ServicePort.operations" in fields
    assert "data_types.App_X.conflict" in fields


def test_signal_atomic_profile_uses_record_init_values_for_record_ports(tmp_path) -> None:
    docx = tmp_path / "record_init.docx"
    _write_minimal_docx(
        docx,
        [
            ("转向灯arxml交付文档", None),
            (
                "输入信号定义",
                [
                    ["No", "输入信号", "数据类别", "应用数据类型", "内部数据类型", "初始值", "信号来源", "作用描述"],
                    ["1", "ntfWinCtrl", "Record", "App_WinCtrl", "Impl_WinCtrl", "", "", "Record signal"],
                ],
            ),
            (
                "Record字段表",
                [
                    ["RecordType", "ImplementationRecordType", "FieldOrder", "FieldName", "FieldCategory", "ApplicationFieldType", "ImplementationFieldType", "InternalRange", "PhysicalRange", "Resolution", "Offset", "Unit", "EnumValues", "InitValue"],
                    ["App_WinCtrl", "Impl_WinCtrl", "1", "CallID", "Value", "App_CallID", "uint64", "0-4294967295", "0-4294967295", "", "", "", "", "0"],
                    ["App_WinCtrl", "Impl_WinCtrl", "2", "Cmd", "Enum", "App_WinCmd", "uint8", "0-255", "", "", "", "", "0=STOP;1=UP", "STOP"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["所属组件", "Runnable名", "AccessType", "信号/端口名", "OperationName", "说明"],
                    ["TurnLamp", "TurnLamp_Step", "DataRead", "ntfWinCtrl", "", "read record"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    rows = build_workbook_rows(contract)
    port = next(row for row in rows["Ports"] if row["PortName"] == "ntfWinCtrl")

    assert port["InitValueType"] == "Record"
    assert {
        "ComponentName": "TurnLamp",
        "PortName": "ntfWinCtrl",
        "RecordElementPath": "Cmd",
        "Value": "STOP",
        "ValueType": "Enum",
        "Description": "Init for App_WinCtrl.Cmd",
    } in rows["PortRecordInitValues"]


def test_mixed_profile_preserves_nested_record_application_and_implementation_names(tmp_path) -> None:
    contract = DeliveryContract(
        project=ProjectContract(generation_profile="mixed_signal_soa"),
        record_elements=[
            RecordElementContract(
                record_type="App_Outer",
                implementation_record_type="Impl_Outer",
                field_order="1",
                element_name="NestedAppField",
                implementation_element_name="NestedImplField",
                field_category="Record",
                data_type="App_Inner",
                implementation_field_type="Impl_Inner",
            ),
            RecordElementContract(
                record_type="App_Inner",
                implementation_record_type="Impl_Inner",
                field_order="1",
                element_name="Value",
                implementation_element_name="RawValue",
                field_category="Value",
                data_type="App_uint8",
                implementation_field_type="uint8",
            ),
        ],
    )

    excel = tmp_path / "nested_record.xlsx"
    write_contract_excel(contract, excel)
    model = load_workbook_v2(excel)
    outer = next(row for row in model.record_elements if row.record_type_name == "App_Outer")

    assert outer.element_name == "NestedAppField"
    assert outer.implementation_element_name == "NestedImplField"
    assert outer.element_category == "Record"
    assert outer.application_element_type_ref == "/DataTypes/App_Inner"
    assert outer.implementation_element_type_ref == "/DataTypes/Impl_Inner"

    from arxml_codegen.generator.arxml_writer import build_arxml_v2

    xml = build_arxml_v2(model)
    namespace = {"a": "http://autosar.org/schema/r4.0"}
    outer_adt = next(
        node
        for node in xml.xpath("//a:APPLICATION-RECORD-DATA-TYPE", namespaces=namespace)
        if node.findtext("a:SHORT-NAME", namespaces=namespace) == "App_Outer"
    )
    outer_idt = next(
        node
        for node in xml.xpath("//a:IMPLEMENTATION-DATA-TYPE", namespaces=namespace)
        if node.findtext("a:SHORT-NAME", namespaces=namespace) == "Impl_Outer"
    )
    assert outer_adt.findtext(".//a:APPLICATION-RECORD-ELEMENT/a:CATEGORY", namespaces=namespace) == "STRUCTURE"
    assert outer_adt.find(".//a:TYPE-TREF", namespaces=namespace).get("DEST") == "APPLICATION-RECORD-DATA-TYPE"
    assert outer_idt.findtext(".//a:IMPLEMENTATION-DATA-TYPE-ELEMENT/a:SHORT-NAME", namespaces=namespace) == "NestedImplField"


def test_signal_atomic_profile_distinguishes_operation_invocation_trigger_from_access_binding(tmp_path) -> None:
    docx = tmp_path / "operation_invoked_event.docx"
    _write_minimal_docx(
        docx,
        [
            ("SOA接口交付文档", None),
            (
                "Runnable 概览",
                [
                    ["所属组件", "Runnable 名", "触发类型", "周期(ms)", "说明"],
                    ["ServerSwc", "rrTrkCtrl", "operation invocation", "", "server invoked"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["所属组件", "Runnable名", "AccessType", "信号/端口名", "OperationName", "说明"],
                    ["ServerSwc", "rrTrkCtrl", "OperationInvokedEvent", "rrTrkCtrl_Enh", "rrTrkCtrl", "server invoked binding"],
                    ["ServerSwc", "rrTrkCtrl2", "OperationInvokedEvent", "rrTrkCtrl_Enh", "rrTrkCtrl", "server invoked inferred"],
                ],
            ),
        ],
    )
    contract = extract_contract_from_docx(docx)
    contract.project.generation_profile = "signal_atomic_davinci"

    trigger_row = contract.runnables[0]
    access_binding_row = contract.runnables[1]
    assert trigger_row.trigger_type == "OperationInvoked"
    assert trigger_row.related_port_or_signal == ""
    assert trigger_row.related_operation == ""
    assert access_binding_row.trigger_type == ""
    assert access_binding_row.related_port_or_signal == "rrTrkCtrl_Enh"
    assert access_binding_row.related_operation == "rrTrkCtrl"

    rows = build_workbook_rows(contract)
    events = {
        (row["RunnableName"], row["TriggerType"], row["PortName"], row["OperationName"])
        for row in rows["RunnableEvents"]
    }
    assert ("rrTrkCtrl", "OperationInvoked", "rrTrkCtrl_Enh", "rrTrkCtrl") in events
    assert ("rrTrkCtrl2", "OperationInvoked", "rrTrkCtrl_Enh", "rrTrkCtrl") in events


def test_soa_contract_docx_to_excel(tmp_path) -> None:
    docx = tmp_path / "soa.docx"
    _write_minimal_docx(
        docx,
        [
            ("XX系统 ARXML 接口交付文档", None),
            (
                "二、SWC 组件定义",
                [
                    ["SWC 名称🟢", "服务层级🟢", "部署域🟢", "是否 Composition🟢", "说明🟡"],
                    ["WindowEnh", "Enh", "Left", "false", "Window enhancement"],
                ],
            ),
            (
                "四、服务接口定义",
                [
                    ["所属SWC🟢", "端口/服务名🟢", "Operation名🟡", "端口类型🟢", "参数名🟢", "方向🟢", "参数类型🟢", "取值范围/引用结构体🟢", "单位🟡", "说明🟡"],
                    ["WindowEnh", "WindowService", "getPosition", "Getter", "Position", "OUT", "uint8", "0-100", "%", "Get window position"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx, mode="soa")
    assert len(contract.services) == 1
    assert len(contract.operation_args) == 1

    excel = tmp_path / "soa.xlsx"
    write_contract_excel(contract, excel)
    model = load_workbook_v2(excel)
    assert model.cs_interfaces
    assert model.cs_arguments


def test_soa_v17_contract_uses_explicit_ports_runnables_and_connectors(tmp_path) -> None:
    docx = tmp_path / "soa_v17.docx"
    _write_minimal_docx(
        docx,
        [
            ("Classic AUTOSAR CP SOA Delivery", None),
            (
                "SWC and Composition",
                [
                    ["SWCName", "PrototypeName", "SWCType", "IsComposition", "Description"],
                    ["BOD_Trk_Atm", "Inst_Atm", "Atomic", "false", "atomic"],
                    ["BOD_Trk_Enh", "Inst_Enh", "Atomic", "false", "enh"],
                    ["Trk_Composition", "Trk_Composition", "Composition", "true", "composition"],
                ],
            ),
            (
                "C/S Service Ports",
                [
                    ["OwnerSWC", "InterfaceName", "PortName", "PortRole", "OperationName", "Description"],
                    ["BOD_Trk_Enh", "rrTrkCtrl", "Pp_TrkCtrl", "Server", "rrTrkCtrl", "server port"],
                    ["BOD_Trk_Atm", "rrTrkCtrl", "Rp_TrkCtrl", "Client", "rrTrkCtrl", "client port"],
                ],
            ),
            (
                "Operation Arguments",
                [
                    [
                        "InterfaceName",
                        "OperationName",
                        "ArgumentName",
                        "Direction",
                        "DataCategory",
                        "ApplicationDataType",
                        "InternalDataType",
                        "InternalRange",
                        "PhysicalRange",
                        "EnumValues",
                        "Description",
                    ],
                    ["rrTrkCtrl", "rrTrkCtrl", "TrkCtrlCmd", "IN", "Enum", "App_TrkCtrlCmd", "uint8", "0-255", "0-255", "0=Stop, 1=Open", "cmd"],
                    ["rrTrkCtrl", "rrTrkCtrl", "ReturnCode", "OUT", "Enum", "App_ReturnCode", "uint8", "0-255", "0-255", "0=SUCCESS, 1=FAILURE", "return"],
                ],
            ),
            (
                "Runnable Overview",
                [
                    ["SWC", "RunnableName", "TriggerType", "PeriodMs", "Description"],
                    ["BOD_Trk_Enh", "rrTrkCtrl", "OperationInvocation", "", "server invoked"],
                    ["BOD_Trk_Atm", "BOD_Trk_Atm_Step", "Periodic", "10", "client periodic"],
                ],
            ),
            (
                "Runnable Access",
                [
                    ["SWC", "RunnableName", "AccessType", "PortOrSignal", "OperationName", "Description"],
                    ["BOD_Trk_Atm", "BOD_Trk_Atm_Step", "InvokeOperation", "Rp_TrkCtrl", "rrTrkCtrl", "client call"],
                ],
            ),
            (
                "Connector",
                [
                    ["ConnectorType", "ProviderEndpoint", "RequesterEndpoint", "InterfaceName", "Description"],
                    ["Assembly", "Inst_Enh.Pp_TrkCtrl", "Inst_Atm.Rp_TrkCtrl", "rrTrkCtrl", "assembly"],
                    ["Delegation", "Trk_Composition.Pp_TrkCtrl", "Inst_Enh.Pp_TrkCtrl", "rrTrkCtrl", "delegation"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx, mode="soa")
    contract.project.composition_name = "Trk_Composition"
    contract.project.generation_profile = "mixed_signal_soa"

    rows = build_workbook_rows(contract)

    assert {row["PrototypeName"] for row in rows["ComponentPrototypes"]} == {"Inst_Atm", "Inst_Enh"}
    assert {
        (row["ComponentName"], row["PortName"], row["PortDirection"], row["OperationName"])
        for row in rows["Ports"]
        if row["InterfaceKind"] == "CS"
    } == {
        ("BOD_Trk_Enh", "Pp_TrkCtrl", "P", "rrTrkCtrl"),
        ("BOD_Trk_Atm", "Rp_TrkCtrl", "R", "rrTrkCtrl"),
    }
    assert {
        (row["ComponentName"], row["RunnableName"], row["TriggerType"], row["PortName"], row["OperationName"])
        for row in rows["RunnableEvents"]
    } == {
        ("BOD_Trk_Enh", "rrTrkCtrl", "OperationInvoked", "Pp_TrkCtrl", "rrTrkCtrl"),
        ("BOD_Trk_Atm", "BOD_Trk_Atm_Step", "Periodic", "", ""),
    }
    assert {
        (row["ComponentName"], row["RunnableName"], row["AccessType"], row["PortName"], row["OperationName"])
        for row in rows["RunnableAccesses"]
    } == {
        ("BOD_Trk_Atm", "BOD_Trk_Atm_Step", "ServerCallPoint", "Rp_TrkCtrl", "rrTrkCtrl"),
    }
    assert {
        (row["ConnectorType"], row["ProviderPrototype"], row["ProviderPort"], row["RequesterPrototype"], row["RequesterPort"])
        for row in rows["CompositionConnectors"]
    } == {
        ("Assembly", "Inst_Enh", "Pp_TrkCtrl", "Inst_Atm", "Rp_TrkCtrl"),
        ("Delegation", "Trk_Composition", "Pp_TrkCtrl", "Inst_Enh", "Pp_TrkCtrl"),
    }

    excel = tmp_path / "soa_v17.xlsx"
    write_contract_excel(contract, excel)
    model = load_workbook_v2(excel)
    assert model.cs_interfaces
    assert model.cs_arguments


def test_gap_report_includes_open_issues_and_core_summary(tmp_path) -> None:
    docx = tmp_path / "signal_gap.docx"
    _write_minimal_docx(
        docx,
        [
            ("XX系统 ARXML 接口交付文档", None),
            (
                "二、输入信号定义",
                [
                    ["信号名", "值类型🟢", "建议数据类型🟢", "物理范围🟢", "单位🟡", "信号来源🟢", "作用描述🟢"],
                    ["VehicleSpeed", "Numeric", "VehicleSpeed_T", "0-250", "kmh", "SpeedSensor", "Vehicle speed"],
                ],
            ),
        ],
    )

    contract = extract_contract_from_docx(docx)
    excel = tmp_path / "draft.xlsx"
    write_contract_excel(contract, excel)
    model = load_workbook_v2(excel)
    report = build_gap_report(
        contract,
        model,
        validate_model_v2(model),
        run_core_validation(model),
    )
    markdown = gap_report_markdown(report)

    assert report.counts["open_issues"] >= 1
    assert any(item.kind == "open_issue" for item in report.items)
    assert "ARXML Delivery Gap Report" in markdown
    assert "CORE Summary" in markdown


def _write_minimal_docx(path, blocks) -> None:
    body = []
    for paragraph, table in blocks:
        body.append(f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>")
        if table:
            body.append("<w:tbl>")
            for row in table:
                body.append("<w:tr>")
                for cell in row:
                    body.append(f"<w:tc><w:p><w:r><w:t>{cell}</w:t></w:r></w:p></w:tc>")
                body.append("</w:tr>")
            body.append("</w:tbl>")

    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(body)
        + "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "")
        archive.writestr("word/document.xml", document)
