# ARXML Codegen

Excel 驱动的 AUTOSAR Classic SWC/Composition ARXML 生成工具。它的定位是平替 DaVinci Developer 中可规则化、重复性的建模录入工作：用 Excel 作为输入源，用脚本生成 ARXML，再用 DaVinci Developer 做导入和一致性验证。

## 功能范围

- 从一个多 Sheet Excel 读取架构输入。
- 生成 `DataTypes`、`PortInterfaces`、`Application SWC`、`Composition`、`Ports`、`Runnables`、`RunnableEvents`、`Assembly Connectors`。
- 支持 S/R sender/receiver 端口和 C/S client/server 端口。
- 生成 `generation_report.md`，输出错误、警告和 Simulink 风险提示。
- 生成 `init_autosar_types.m`，为 Simulink 补 `ADT_xxx` AliasType，避免 Function Caller 找不到 boolean/uint8 类型对象。

暂不生成 BSW/ECUC、OS task mapping、RTE task mapping、SOME/IP deployment、E2E、SecOC、诊断、NvM 详细配置。

## Excel Sheets

模板包含这些 Sheet：

- `Components`：组件名、组件类型、`PackagePath`、是否 Composition。
- `DataTypes`：`ADTName`、`IDTName`、`BaseType`、是否枚举、`CompuMethod`、值定义。
- `PortInterfaces`：接口名、S/R 或 C/S、DataElement、SR 数据类型、Operation。
- `Operations`：C/S operation 参数名、参数方向、参数 ADT 类型。
- `Ports`：组件端口、P/R 方向、接口引用、初值。
- `Runnables`：Runnable 名和 symbol。
- `RunnableEvents`：`Init`、`Periodic`、`OperationInvoked`、`DataReceived` 触发。
- `CompositionConnectors`：Provider/Requester 组件端口连接。

## 快速开始

在 VS Code 终端进入工程目录：

```powershell
cd D:\work\SOA\code
```

生成或刷新 Excel 模板：

```powershell
.\scripts\run_codegen.ps1 -CreateTemplate data/input/arxml_input_template.xlsx
```

只校验 Excel，不生成 ARXML：

```powershell
.\scripts\run_codegen.ps1 -DryRun
```

生成 ARXML、报告和 MATLAB 初始化脚本：

```powershell
.\scripts\run_codegen.ps1
```

默认输出：

- `output/generated_from_excel.arxml`
- `output/generation_report.md`
- `output/init_autosar_types.m`

## DaVinci Developer 兼容规则

生成器已经内置以下规则，避免 Developer 导入时报常见 DataType 错误：

- `DataTypeMappingSet` 固定生成在 `/DataTypes/DataTypeMappings/DataTypeMappingsSet`。
- 每个 `SWC-INTERNAL-BEHAVIOR` 自动引用上述 `DataTypeMappingSet`。
- `CompuMethod` 按 ShortName 去重，同名对象只生成一次，例如多个 boolean 类型共用 `boolean_CompuMethod`。
- `BaseTypes` 使用 Vector 常见小写命名，例如 `boolean`、`uint8`、`uint16`。
- `SW-BASE-TYPE` 使用 `CATEGORY=FIXED_LENGTH`。
- `BASE-TYPE-ENCODING` 按底层类型生成：boolean 用 `BOOLEAN`，无符号整数用 `NONE`，有符号整数用 `2C`。
- `SW-BASE-TYPE` 自动生成 `NATIVE-DECLARATION`，例如 `boolean`、`uint8`，避免 `ImplementationDataType` 引用 BaseType 时被 Developer 判定缺少平台类型声明。

这些规则用于解决以下 Developer 校验问题：

- `Missing data type mapping`
- `ImplementationDataType with inappropriate BaseType reference`
- `Ambiguous ShortNames within a Package`

## 命名约束

为了兼容 Simulink 导入，C/S 服务建议固定为：

```text
PortName      = rrFWasher
OperationName = FWasher
RunnableName  = FWasher
```

端口名体现通信方式，operation/runnable 名体现动作语义。这样可以减少 Function Caller 与 Server Function 名称不一致导致的映射问题。

## Developer 导入建议

第一次验证脚本生成结果时，推荐使用空 workspace/project 导入：

```text
D:\work\SOA\code\output\generated_from_excel.arxml
```

如果在已有工程反复导入，建议先删除本次生成的顶层包后保存并重开工程：

```text
AUTOSAR_Platform
DataTypes
PortInterfaces
ComponentTypes
```

最稳妥的方式仍然是新建空 workspace 验证，因为旧工程里残留的 BaseTypes、CompuMethods、DataTypeMappingSet 可能造成误判。

## 验证

已用模板样例跑通过：

```powershell
.\.venv\Scripts\python.exe -m pytest
.\scripts\run_codegen.ps1 -DryRun
```

并确认生成的 `output/generated_from_excel.arxml` 是可解析 XML。DaVinci Developer 导入结果是后续准入标准。
