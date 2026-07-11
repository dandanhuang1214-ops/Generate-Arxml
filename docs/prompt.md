你现在是精通 AUTOSAR Classic、DaVinci Developer、Vector 工具链、Python 自动化脚本的资深软件架构师。

我要实现一个“Excel 驱动生成 AUTOSAR ARXML”的工具，用于替代 DaVinci Developer 中重复性的 SWC 架构建模和 ARXML 生成过程。

请帮我生成一个完整 Python 工程，要求如下：

一、目标

输入：一个多 Sheet Excel 文件。

输出：
1. 可导入 DaVinci Developer Classic 的 AUTOSAR 4.3.0 ARXML 文件。
2. 生成报告 generation_report.md。
3. 可选 Simulink 类型初始化脚本 init_autosar_types.m。

工具定位：
1. Excel 是建模输入源。
2. Python 脚本负责校验、建模和生成 ARXML。
3. DaVinci Developer 仅作为最终验证工具。
4. 不要求生成 BSW、ECUC、OS Task Mapping、RTE Event-To-Task Mapping、SOME/IP Deployment。

二、Excel Sheet 设计

Excel 至少包含以下 Sheet，并严格按照列名读取。

1. Components

列：
ComponentName
ComponentKind
PackagePath
IsComposition
Description

说明：
ComponentKind 可选 Application 或 Composition。
IsComposition 可选 TRUE 或 FALSE。

2. DataTypes

列：
ADTName
IDTName
BaseType
IsEnum
CompuMethod
ValueDefinition
Description

说明：
BaseType 支持 boolean、uint8、uint16、uint32、sint8、sint16、sint32、float32。
IsEnum 可选 TRUE 或 FALSE。
ValueDefinition 格式示例：
0:OFF;1:ON
0:SUCCESS;1:FAILURE;2:FAIL_UNAVAILABLE;3:FAIL_INVALID_PARAM

3. PortInterfaces

列：
InterfaceName
InterfaceKind
DataElementName
DataTypeADT
OperationName
Description

说明：
InterfaceKind 可选 SR 或 CS。
SR 接口需要 DataElementName 和 DataTypeADT。
CS 接口需要 OperationName。

4. Operations

列：
InterfaceName
OperationName
ArgumentName
ArgumentDirection
ArgumentADT
Description

说明：
ArgumentDirection 可选 IN、OUT、INOUT。
用于 C/S Operation 参数定义。

5. Ports

列：
ComponentName
PortName
PortDirection
InterfaceKind
InterfaceName
DataElementName
OperationName
InitValue
ComSpecType
Description

说明：
PortDirection 可选 P 或 R。
InterfaceKind 可选 SR 或 CS。
S/R Port 使用 ComSpecType，支持 nonqueued、queued。
C/S Port 需要引用 InterfaceName 和 OperationName。

6. Runnables

列：
ComponentName
RunnableName
Symbol
Description

说明：
RunnableName 和 Symbol 都要写入 ARXML。
对于 C/S Server 端 Operation，建议 RunnableName 与 OperationName 保持一致，方便 Simulink Function 映射。

7. RunnableEvents

列：
ComponentName
RunnableName
TriggerType
PeriodMs
PortName
OperationName
DataElementName
AccessType
Description

说明：
TriggerType 支持 Init、Periodic、OperationInvoked、DataReceived。
Periodic 使用 PeriodMs。
OperationInvoked 绑定 C/S PortName + OperationName。
DataReceived 绑定 S/R PortName + DataElementName。

8. CompositionConnectors

列：
CompositionName
ProviderComponent
ProviderPort
RequesterComponent
RequesterPort
ConnectorType
Description

说明：
ConnectorType 支持 Assembly、Delegation。
第一版重点支持 Assembly Connector。

三、ARXML 生成要求

1. AUTOSAR 版本使用 4.3.0。
2. 根节点使用 AUTOSAR namespace：
http://autosar.org/schema/r4.0
3. 生成包结构建议：
/AUTOSAR_Platform/BaseTypes
/DataTypes/ApplicationDataTypes
/DataTypes/ImplementationDataTypes
/DataTypes/CompuMethods
/DataTypes/DataTypeMappings
/PortInterfaces
/ComponentTypes
4. BaseTypes 使用 Vector/DaVinci 友好风格：
ShortName 使用小写，例如 boolean、uint8、uint16。
CATEGORY 使用 FIXED_LENGTH。
boolean 的 BASE-TYPE-ENCODING 使用 BOOLEAN。
无符号整型使用 NONE。
有符号整型使用 2C。
必须生成 NATIVE-DECLARATION，例如 boolean、uint8、uint16。
5. 生成 ApplicationDataType、ImplementationDataType、CompuMethod 和 DataTypeMappingSet。
6. DataTypeMappingSet 路径固定为：
/DataTypes/DataTypeMappings/DataTypeMappingsSet
7. 每个 SWC-INTERNAL-BEHAVIOR 都必须引用 DataTypeMappingSet：
DATA-TYPE-MAPPING-REFS
8. CompuMethod 需要按 ShortName 去重，避免重复 ShortName。
9. 对 enum 类型，根据 ValueDefinition 生成 COMPU-SCALES。
10. 对非 enum 类型，也允许生成简单 CompuMethod。
11. 生成 SR Interface：
SENDER-RECEIVER-INTERFACE
VARIABLE-DATA-PROTOTYPE
TYPE-TREF 指向 ApplicationDataType
12. 生成 CS Interface：
CLIENT-SERVER-INTERFACE
CLIENT-SERVER-OPERATION
ARGUMENT-DATA-PROTOTYPE
DIRECTION
TYPE-TREF 指向 ApplicationDataType
13. 生成 Application SWC：
APPLICATION-SW-COMPONENT-TYPE
P-PORT-PROTOTYPE
R-PORT-PROTOTYPE
INTERNAL-BEHAVIORS
RUNNABLES
EVENTS
14. 生成 Composition SWC：
COMPOSITION-SW-COMPONENT-TYPE
COMPONENT-PROTOTYPES
CONNECTORS
ASSEMBLY-SW-CONNECTOR
15. S/R Sender Port 需要生成 NONQUEUED-SENDER-COM-SPEC 或 QUEUED-SENDER-COM-SPEC，并支持 InitValue。
16. S/R Receiver Port 需要生成 NONQUEUED-RECEIVER-COM-SPEC 或 QUEUED-RECEIVER-COM-SPEC。
17. C/S Client Port 需要生成 REQUIRED-COM-SPECS。
18. C/S Server Port 需要生成 PROVIDED-COM-SPECS。
19. OperationInvokedEvent 需要引用对应 P-Port 和 Operation。
20. TimingEvent 使用 PeriodMs 转换为秒。
21. InitEvent 绑定 Init Runnable。

四、校验规则

请实现 validate_model 或 rule.py，对 Excel 数据做生成前校验。

至少检查：
1. 必填 Sheet 是否存在。
2. 必填列是否存在。
3. ComponentName 是否重复。
4. DataType ADTName 是否重复。
5. PortInterface 是否重复。
6. 同一 Component 下 PortName 是否重复。
7. 同一 Component 下 RunnableName 是否重复。
8. Ports 引用的 Component 是否存在。
9. Ports 引用的 Interface 是否存在。
10. PortInterfaces 中 SR 接口引用的 DataType 是否存在。
11. Operations 引用的 Interface 是否存在。
12. Operations 引用的 ArgumentADT 是否存在。
13. RunnableEvents 引用的 Component/Runnable 是否存在。
14. OperationInvokedEvent 引用的 PortName + OperationName 是否存在。
15. CompositionConnectors 引用的 Component 和 Port 是否存在。
16. 输出 warning：未连接端口。
17. 输出 warning：C/S OperationName 和 RunnableName 不一致，提示 Simulink Function 映射风险。
18. 输出 warning：SR Sender Port 缺少 InitValue。

校验报告需要包含：
Sheet 名
Excel 行号
字段名
错误说明

五、工程结构

请生成如下工程结构：

arxml_codegen_project/
  README.md
  pyproject.toml
  config/
    project.yaml
  data/
    input/
      arxml_input_template.xlsx
  output/
  scripts/
    run_codegen.ps1
    create_excel_template.ps1
  src/
    arxml_codegen/
      __init__.py
      cli.py
      models/
        schema.py
      excel/
        reader.py
        template.py
      generator/
        arxml_writer.py
      rules/
        validator.py
  tests/
    test_reader.py
    test_validator.py

六、脚本入口

1. PowerShell 一键入口：

scripts/run_codegen.ps1

功能：
优先使用 .venv/Scripts/python.exe。
设置 PYTHONPATH=src。
调用：
python -m arxml_codegen.cli --config config/project.yaml
支持：
-DryRun
-CreateTemplate

2. Python CLI：

python -m arxml_codegen.cli --config config/project.yaml
python -m arxml_codegen.cli --config config/project.yaml --dry-run
python -m arxml_codegen.cli --create-template data/input/arxml_input_template.xlsx

七、配置文件

config/project.yaml 内容示例：

excel:
  workbook: data/input/arxml_input_template.xlsx

generation:
  output: output/generated_from_excel.arxml
  report: output/generation_report.md
  matlab_init: output/init_autosar_types.m
  autosar_version: 4-3-0

八、README 内容

README 需要说明：
1. 项目目标。
2. 工程结构。
3. 虚拟环境创建步骤。
4. 依赖安装步骤。
5. 如何创建 Excel 模板。
6. 如何运行 DryRun。
7. 如何生成 ARXML。
8. 如何把 ARXML 导入 DaVinci Developer。
9. 常见报错说明：
Missing data type mapping
ImplementationDataType with inappropriate BaseType reference
Ambiguous ShortNames within a Package
BaseType missing NativeDeclaration
10. 如何复用到新项目：
只改 Excel 和 config/project.yaml 路径。

九、实现要求

1. 使用 Python。
2. 推荐使用 openpyxl 读取/生成 Excel。
3. 推荐使用 lxml.etree 生成 XML，不要用字符串拼接。
4. 所有 XML 文本必须自动转义。
5. 代码结构清晰，可维护。
6. 不要把所有逻辑写在一个文件里。
7. 生成的 ARXML 需要尽量符合 DaVinci Developer Classic 导入习惯。
8. 提供最小样例 Excel，可以生成：
一个 Composition：total
两个 Application SWC：WW_Enh、WW_Atm
一个 C/S 服务：rrFWasher/FWasher
一个 S/R 输出：pFWasherOutput
一个 Assembly Connector：WW_Enh 调用 WW_Atm 服务

十、输出

请直接输出完整工程代码，包括所有文件内容。
如果代码过长，请按文件分段输出。