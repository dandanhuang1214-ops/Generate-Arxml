# XX系统 ARXML 接口交付文档

（信号驱动模式 · Signal-Based）

模板版本 V1.2

## 使用说明

本文档是「详细设计文档」与「ARXML 自动生成工具」之间的标准接口。功能设计人员只需要填写信号的业务语义、取值范围、初值、来源去向、触发关系等设计决策，不需要填写完整 AUTOSAR 路径、ComSpec 类型名、DataTypeMapping 路径或端口引用路径。

工具会根据本文档自动生成：

- Excel v2 草稿；
- AUTOSAR ApplicationDataType / ImplementationDataType / CompuMethod / DataConstr；
- SenderReceiverInterface；
- Atomic SWC 的 R-Port / P-Port；
- Runnable 读写访问点；
- DaVinci 风格的 ARXML。

填写图例：🟢 必填（人工设计决策）  🟡 可选（有默认值，特殊情况才填）  ⚪ 工具自动生成，请勿填写

## 一、项目基本信息

以下信息通常由架构/工具侧统一预填，功能设计人员核对无误即可。

| 字段 | 填写方 | 示例 | 说明 |
| --- | --- | --- | --- |
| 项目/系统名称 | 🟢 | TurnLamp / Wiper / Window | 对应交付物的功能模块名 |
| AUTOSAR 版本 | ⚪ | 4-3-0 | 由项目配置统一指定 |
| 生成模式 | ⚪ | SignalAtomicDaVinci | 信号驱动第一版默认一个文档生成一个 Atomic SWC |
| Atomic SWC 名称 | 🟢 | TurnLampCtrl | DaVinci 中的 Application SWC 名称 |
| 默认 Runnable 名称 | 🟢 | TurnLampCtrl_Step | 周期主函数名称 |
| 默认周期(ms) | 🟢 | 10 | 周期 Runnable 的触发周期 |
| 根包路径 RootPackage | ⚪ | DaVinci默认路径 | 信号模式默认使用 /ComponentTypes、/PortInterfaces、/DataTypes 等路径 |
| 负责人 / 版本 / 日期 | 🟢 | 张三 / V1.0 / 2026-07-13 | 用于变更追溯 |

## 二、输入信号定义

每一行描述一个该模块需要接收/读取的信号。

| 信号名 | 值类型🟢 | 内部数据类型🟢 | 物理范围🟢 | 分辨率🟡 | 单位🟡 | 状态值表🟡 | 初始值🟢 | 信号来源🟢 | 周期(ms)🟡 | 作用描述🟢 | RequirementId/Source🟢 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VbINP_HWA_FWiperPark_flg | Boolean | boolean | 0/1 | - | - | - | 0 | 硬线输入 | 10 | 前雨刮电机 Park 位硬线信号，用于归位判断 | SRD-001 |
| VeINP_HWA_Voltage_100mV | Numeric | uint16 | 0~65535（对应 0~6553.5V） | 0.1 | V | - | 0 | 硬线输入(AD采样) | 10 | 车载电压采样，单位 0.1V | SRD-002 |
| VeINP_BCM_LampMode_sts | Enum | uint8 | 0~15 | - | - | 0=OFF, 1=LowBeam, 2=HighBeam, 15=Error_Value | OFF | BCM | 10 | 灯光模式输入 | SRD-003 |

## 三、输出信号定义

每一行描述一个该模块对外发送/写出的信号。字段含义与输入信号表一致。

| 信号名 | 值类型🟢 | 内部数据类型🟢 | 物理范围🟢 | 分辨率🟡 | 单位🟡 | 状态值表🟡 | 初始值🟢 | 信号去向🟢 | 越限处理🟡 | 周期(ms)🟡 | 作用描述🟢 | RequirementId/Source🟢 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VbOUT_WW_FWiperLow_flg | Boolean | boolean | 0/1 | - | - | - | 0 | 硬线输出 | 默认(不处理) | 10 | 前雨刮低速电机输出 | SRD-101 |
| VeOUT_WW_ZCULFWiperSts_sig | Enum | uint8 | 0~7 | - | - | 0=OFF, 1=LS_Speed, 2=HS_Speed, 3=Washwipe, 4=Maintenance, 5=AUTO, 6=INT, 7=MIST | OFF | BCM | 默认(不处理) | 10 | 前雨刮状态输出 | SRD-102 |

## 四、Runnable 与访问关系

请用下表统一描述每个 Runnable 的触发方式及其读写信号。不要以“图片/嵌入对象”的形式交付，必须使用可编辑 Word 表格。

| 所属组件🟢 | Runnable 名🟢 | 触发类型🟢 | 周期(ms)🟢 | 读取信号🟢 | 写入信号🟢 | 说明🟡 |
| --- | --- | --- | --- | --- | --- | --- |
| TurnLampCtrl | TurnLampCtrl_Init | Init | - | - | - | 上电初始化一次 |
| TurnLampCtrl | TurnLampCtrl_Step | Periodic | 10 | VeINP_BCM_LampMode_sts | VbOUT_WW_FWiperLow_flg, VeOUT_WW_ZCULFWiperSts_sig | 主控周期任务 |

触发类型可选：

- Init：上电初始化一次；
- Periodic：周期触发，必须填写周期；
- DataReceived：收到某信号时触发，读取信号列填写触发信号。

## 五、字段填写规则

### 5.1 值类型怎么选

`值类型` 决定信号的 AUTOSAR 语义、CompuMethod 类型、InitValue 写法和校验规则。

| 值类型 | 适用场景 | 生成规则 | 初始值写法 |
| --- | --- | --- | --- |
| Boolean | 只有真假/开关/有效无效两态 | 使用 Boolean ADT/IDT，InitValue 生成 CATEGORY=BOOLEAN | 填 0/1 或 false/true |
| Numeric | 连续数值，例如电压、电流、角度、计数 | 使用数值 ADT/IDT；根据分辨率决定 IDENTICAL 或 LINEAR | 填数字 |
| Enum | 离散状态，例如 OFF/ON/ERROR/MIST/AUTO | 使用 TEXTTABLE CompuMethod；状态值表必须写全 | 推荐填符号名，例如 OFF |

注意：不要为了省事把所有信号都填成 Numeric。如果信号本质是状态量，应填 Enum。Enum 是 DaVinci/RTE 中最容易出错的地方，必须让状态值表、初始值和底层数据类型保持一致。

### 5.2 内部数据类型有什么作用

`内部数据类型` 不是让功能同事填写完整 AUTOSAR IDT 路径，而是告诉工具这个信号底层应该用多宽的数据承载。工具会据此生成或选择 ADT/IDT 映射。

简单理解：

| 文档填写 | 工具理解 | 生成结果示例 |
| --- | --- | --- |
| boolean | 这是 Boolean 信号 | ADT: App_boolean；IDT: boolean / AUTOSAR_Platform Boolean |
| uint8 | 这是 8 位无符号底层存储 | ADT: App_uint8 或 App_<SignalName>；IDT: uint8 |
| uint16 | 这是 16 位无符号底层存储 | ADT: App_uint16 或 App_<SignalName>；IDT: uint16 |
| sint16 | 这是 16 位有符号底层存储 | ADT: App_sint16 或 App_<SignalName>；IDT: sint16 |

具体规则：

- Boolean 信号：`值类型=Boolean` 时，`内部数据类型` 通常填 `boolean`。
- Numeric 信号：`内部数据类型` 选择能覆盖物理范围/内部范围的最小整数类型，例如 0~255 用 `uint8`，0~65535 用 `uint16`。
- Enum 信号：`内部数据类型` 填枚举内部码值所需的底层类型，例如枚举值 0~7 用 `uint8`，0~65535 用 `uint16`。此时工具会优先生成“信号专属 ADT + TEXTTABLE CompuMethod”，再映射到底层 IDT。
- 如果多个信号复用同一套枚举，后续可以在“数据类型补充表”里指定 TypeName，让工具复用同一个 ADT/CompuMethod。

所以它确实最终会影响 IDT，但上游不需要知道完整 IDT 路径，只需要知道这个信号底层是 `boolean`、`uint8`、`uint16` 还是其他基础类型。

### 5.3 状态值表填写规则

Enum 类型必须填写状态值表，格式为：

`0=OFF, 1=ON, 2=Fault, 15=Error_Value`

要求：

- 左边是内部码值，必须是数字；
- 右边是符号名，必须是英文标识符；
- 不要使用中文、空格、斜杠；
- 不允许缺失中间合法状态，除非需求明确保留；
- 如果状态值表引用其他行，可写“同 VeOUT_xxx 状态表”，但首次出现必须写全。

### 5.4 初始值填写规则

| 值类型 | 推荐填写 | 说明 |
| --- | --- | --- |
| Boolean | 0 / 1 | 工具会生成 BOOLEAN InitValue |
| Numeric | 数字 | 必须落在物理范围/DataConstr 内 |
| Enum | 符号名，例如 OFF | 工具会生成 TEXTTABLE 对应的 VT 初值 |

兼容规则：

- 如果旧文档里 Enum 初始值填了 `0`，工具可以根据状态值表转换成 `OFF`，但会在 gap report 中提示“已从内部值推导为符号名”。
- 新文档建议直接填符号名，避免 DaVinci 导入或 RTE 生成阶段歧义。

## 六、可选：数据类型补充表

只有以下情况才需要填写本表：

- 多个信号复用同一套枚举；
- 需要指定统一的 ApplicationDataType 名称；
- 需要明确单位、物理范围、DataConstr 或 CompuMethod；
- 有 Record/复杂类型。

| TypeName | 值类型 | BaseType/内部数据类型 | CompuMethodType | 状态值表 | PhysicalRange | Unit | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LampMode_T | Enum | uint8 | TEXTTABLE | 0=OFF, 1=LowBeam, 2=HighBeam, 15=Error_Value | 0~15 | - | 灯光模式枚举 |

## 七、工具自动生成规则（供核对）

以下内容由工具生成，功能设计人员不用手工填写：

| 对象 | DaVinci 信号模式默认规则 | 示例 |
| --- | --- | --- |
| Component package | /ComponentTypes | /ComponentTypes/TurnLampCtrl |
| Interface package | /PortInterfaces | /PortInterfaces/VeINP_BCM_LampMode_sts |
| Data type package | /DataTypes | /DataTypes/App_uint8 |
| MappingSet | /ComponentTypes/MappingSets/DataMapping | /ComponentTypes/MappingSets/DataMapping |
| S/R Interface 名 | 默认等于信号名 | VeINP_BCM_LampMode_sts |
| DataElement 名 | 默认等于信号名 | VeINP_BCM_LampMode_sts |
| Port 名 | 默认等于信号名 | VeINP_BCM_LampMode_sts |
| Runnable Access | 根据 Runnable 表自动生成 | DataReceivePoint / DataSendPoint |

## 八、未决问题

凡是文档里无法确定、工具也不能可靠推导的信息，必须写入未决问题，不能静默编造。

| 编号 | 字段/信号 | 问题描述 | 建议默认值 | 负责人 | 状态 | 关闭结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  | Open |  |

状态建议使用：

- Open：待确认；
- Confirmed：已确认，待同步进文档；
- Closed：已关闭。

## 九、变更记录

| 版本 | 日期 | 修改人 | 修改说明 |
| --- | --- | --- | --- |
| V1.0 | 2026-05-18 | - | 初版 |
| V1.2 | 2026-07-13 | Codex | 在原信号模板基础上补充 DaVinci 路径、内部数据类型/IDT 规则、Enum 初值规则和需求溯源字段 |
