# ARXML 接口交付文档模板

（信号 + SOA 混合模式 · Signal + Client/Server）

模板版本 V1.5

## 使用说明

本文档是详细设计与 ARXML 自动生成工具之间的标准接口。填写目标是描述“业务接口契约”，不是手工填写 AUTOSAR 路径。

上游人员只需要填写：

- 有哪些 SWC；
- 哪些信号输入/输出；
- 哪些服务由谁提供、由谁调用；
- Operation 有哪些参数；
- Record / Enum 的业务结构；
- Runnable 怎么触发；
- Composition 内部如何连接。

工具自动生成：

- AUTOSAR 包路径；
- PortInterface 路径；
- ADT / IDT / CompuMethod / DataConstr；
- DataTypeMappingSet；
- R-Port / P-Port；
- ClientComSpec / ServerComSpec；
- Sender/Receiver ComSpec；
- Runnable Event；
- Assembly / Delegation Connector。

填写图例：🟢 必填　🟡 可选　⚪ 工具生成，不建议人工填写

## 1. 项目基本信息

| 字段 | 填写值 | 说明 |
| --- | --- | --- |
| 项目/系统名称🟢 |  | 例如 Window / TRK / Wiper |
| 目标 AUTOSAR 版本⚪ | 4-3-0 | 工具默认 |
| 生成模式⚪ | mixed_signal_soa | 工具默认 |
| RootPackage⚪ | DaVinci默认路径 | 不需要每张表重复填写 |
| 默认 Composition 名🟡 |  | 多 SWC 集成时填写；纯 Atomic 可空 |
| 默认 MappingSet⚪ | /ComponentTypes/MappingSets/DataMapping | 工具默认 |
| 需求/详设来源🟢 |  | 文档名称、版本 |
| 填写人/日期🟢 |  |  |

## 2. 组件清单

只填写真实组件和业务角色，不填写包路径。

| SWC名称🟢 | SWC角色🟢 | 部署域🟡 | 是否Composition🟡 | 说明🟡 |
| --- | --- | --- | --- | --- |
| BOD_PWNR_GenScen | 通用/场景服务 | ZCU_R | false | 右域车窗通用场景服务 |
| BOD_PWNR_Enh | 增强服务 | ZCU_R | false | 右前/右后车窗增强服务 |
| BOD_PWNR_Atm | 原子服务 | ZCU_R | false | 右侧车窗原子服务 |
| BOD_PWNR_Composition | Composition | ZCU_R | true | 右域车窗组合 |

填写规则：

- `SWC名称` 必须是 DaVinci 中希望看到的 SHORT-NAME。
- `SWC角色` 用于人读和后续默认连接规则，可填写：通用/场景服务、增强服务、原子服务、基础服务、Composition。
- `是否Composition` 可空；工具可根据 `SWC角色=Composition` 推导。

## 3. 服务接口清单

每一行描述一个服务端口或服务接口。这里覆盖 C/S，也允许混合写 S/R 通知服务。

| ProviderSWC🟢 | ClientSWC🟢 | 服务名🟢 | 端口名🟢 | Operation名🟡 | 端口角色🟢 | 通信模式🟢 | TimeoutMs🟡 | 说明🟡 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BOD_PWNR_Enh | BOD_PWNR_GenScen | rrWinCtrl | rrWinCtrl | rrWinCtrl | Server | C/S | 100 | 车窗操作服务 |
| BOD_PWNR_GenScen | BOD_PWNR_Enh | rrWinCtrl | rrWinCtrl | rrWinCtrl | Client | C/S | 100 | 调用增强服务 |
| BOD_PWNR_Enh | BOD_PWNR_GenScen | ntfSrvOperSts | ntfSrvOperSts | / | Sender | S/R |  | 通知服务运行状态 |
| BOD_PWNR_GenScen | BOD_PWNR_Enh | ntfSrvOperSts | ntfSrvOperSts | / | Receiver | S/R |  | 接收服务运行状态 |

端口角色规则：

| 端口角色 | 通信模式 | 生成结果 |
| --- | --- | --- |
| Sender | S/R | P-Port + `NONQUEUED-SENDER-COM-SPEC` |
| Receiver | S/R | R-Port + `NONQUEUED-RECEIVER-COM-SPEC` |
| Server | C/S | P-Port + `SERVER-COM-SPEC` |
| Client | C/S | R-Port + `CLIENT-COM-SPEC` |

填写规则：

- `ProviderSWC` 表示服务/信号提供方。
- `ClientSWC` 表示服务/信号使用方。
- 对 C/S，`Operation名` 必须明确。
- 对 S/R 通知，`Operation名` 可填 `/`。
- 不需要填写 InterfaceRef、PackagePath、ComSpecKind，工具推导。

## 4. Operation 参数表

不要把所有参数塞进服务表的一个单元格。每个参数一行，工具据此生成 Argument 和数据类型。

| Operation名🟢 | 参数名🟢 | 方向🟢 | 值类型🟢 | 内部数据类型🟢 | 所属Record🟡 | 取值范围/枚举🟡 | 单位🟡 | 说明🟡 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rrWinCtrl | CallID | IN | Value | uint64 | WinCtrl | 0-4294967295 |  | 调用源 |
| rrWinCtrl | TimeStamp | IN | Value | uint64 | WinCtrl | 0-4294967295 | ms | 时间戳 |
| rrWinCtrl | Prio | IN | Value | uint8 | WinCtrl | 0-255 |  | 优先级 |
| rrWinCtrl | WinCtrlCmd | IN | Enum | uint8 | WinCtrl | 0=NoAction_Stop, 1=MANUAL_UP, 2=MANUAL_DOWN |  | 车窗控制命令 |
| rrWinCtrl | ReturnCode | OUT | Enum | uint8 |  | 0=SUCCESS, 1=FAILURE, 2=FAIL_UNAVAILABLE |  | 返回值 |

填写规则：

- `方向` 支持 `IN`、`OUT`、`INOUT`。
- `值类型=Enum` 时，`取值范围/枚举` 必须写枚举映射。
- `所属Record` 为空表示普通参数；不为空表示该字段属于 Record。
- `内部数据类型` 只填基础类型，例如 `boolean`、`uint8`、`uint16`、`uint32`、`uint64`。

## 5. 数据类型补充表

只有复杂类型、复用类型或需要人工命名时才填写。普通基础类型可由工具推导。

| TypeName🟢 | 类型🟢 | BaseType🟡 | 字段/枚举定义🟢 | 说明🟡 |
| --- | --- | --- | --- | --- |
| WinCtrl | Record |  | CallID:uint64; TimeStamp:uint64; Prio:uint8; WinCtrlCmd:uint8 | 车窗控制参数 |
| SrvOperSts | Record |  | CallID:uint64; TimeStamp:uint64; Prio:uint8; OperSts:uint8 | 服务运行状态 |
| WinCtrlCmd | Enum | uint8 | 0=NoAction_Stop, 1=MANUAL_UP, 2=MANUAL_DOWN | 车窗控制命令 |
| ReturnCode | Enum | uint8 | 0=SUCCESS, 1=FAILURE, 2=FAIL_UNAVAILABLE | 返回码 |

填写规则：

- 如果 Operation 参数表已完整描述 Record 字段，本表可不填。
- 如果多个 Operation 复用同一个 Record 或 Enum，建议填写本表。

## 6. Runnable 与触发

描述 Runnable 的触发方式。不要用图片或嵌入对象。

| SWC🟢 | Runnable名🟢 | 触发类型🟢 | 周期ms🟡 | 绑定端口/Operation🟡 | 说明🟡 |
| --- | --- | --- | --- | --- | --- |
| BOD_PWNR_Enh | BOD_PWNR_Enh_Init | Init | - | - | 上电初始化 |
| BOD_PWNR_Enh | BOD_PWNR_Enh_Step | Periodic | 10 | - | 周期任务 |
| BOD_PWNR_Enh | rrWinCtrl | OperationInvoked | - | rrWinCtrl | 服务调用触发 |

触发类型：

- `Init`：上电初始化；
- `Periodic`：周期触发；
- `OperationInvoked`：C/S 服务被调用时触发；
- `DataReceived`：接收信号触发，后续需要时扩展。

## 7. 信号接口清单

用于混合模式中的 S/R 信号。纯 SOA 服务可不填。

| 接口类型🟢 | SignalName🟢 | 所属SWC🟢 | 对端SWC🟡 | 值类型🟢 | 内部数据类型🟢 | 物理范围🟡 | 状态值表🟡 | 初始值🟢 | 周期ms🟡 | 说明🟡 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SignalIn | VbINP_CAN_WindowLock_flg | BOD_PWNR_Enh | BCM | boolean | boolean | 0-1 |  | 0 | 10 | 车窗锁输入 |
| SignalOut | VbOUT_TRK_SleepPermit_flg | BOD_PWNR_Enh | BCM | boolean | boolean | 0-1 |  | 0 | 10 | 休眠允许输出 |
| SignalOut | VeOUT_WinMode | BOD_PWNR_Enh | BCM | Value | uint8 | 0-255 |  | 0 | 10 | 车窗模式 |

接口类型规则：

| 接口类型 | 生成结果 |
| --- | --- |
| SignalIn | R-Port |
| SignalOut | P-Port |

值类型规则：

- `boolean`：生成 `App_boolean`；
- `Value/uint8/uint16/uint32`：生成共享基础 ADT；
- `Enum`：生成 TEXTTABLE，必须填写状态值表。

## 8. Composition 连接关系

只填写业务连接关系，不填写 AUTOSAR 完整路径。

| 连接场景🟡 | 服务/信号名🟢 | 提供方🟢 | 使用方🟢 | 连接类型🟡 | 说明🟡 |
| --- | --- | --- | --- | --- | --- |
| 内部调用 | rrWinCtrl | BOD_PWNR_Enh.rrWinCtrl | BOD_PWNR_GenScen.rrWinCtrl | Assembly | GenScen 调用 Enh |
| 内部通知 | ntfSrvOperSts | BOD_PWNR_Enh.ntfSrvOperSts | BOD_PWNR_GenScen.ntfSrvOperSts | Assembly | Enh 通知 GenScen |
| 对外暴露 | rrWinCtrl | Composition.rrWinCtrl | BOD_PWNR_Enh.rrWinCtrl | Delegation | 对外暴露车窗控制服务 |

填写规则：

- `提供方` 和 `使用方` 推荐写成 `SWC.Port`。
- `Composition.Port` 表示组合组件外部端口，工具会替换为默认 Composition 名。
- `连接类型` 可填 `Assembly` 或 `Delegation`；为空默认 `Assembly`。
- S/R 和 C/S 都使用同一张连接关系表。

生成规则：

| 连接类型 | 含义 |
| --- | --- |
| Assembly | 内部 SWC 之间连接：Provider P-Port / Server P-Port → Receiver R-Port / Client R-Port |
| Delegation | Composition 外部端口与内部 SWC 端口连接 |

## 9. 未决问题

工具无法可靠推导的信息必须进入未决问题，不能静默编造。

| 编号 | 字段/对象 | 问题描述 | 建议默认值 | 负责人 | 状态 | 关闭结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  | Open |  |

状态建议：

- `Open`：待确认；
- `Confirmed`：已确认，待同步；
- `Closed`：已关闭。

## 10. 不需要上游填写的内容

以下内容由工具生成，不建议人工维护：

- AUTOSAR PackagePath；
- InterfaceRef；
- DataElementRef；
- ApplicationDataTypeRef；
- ImplementationDataTypeRef；
- DataTypeMappingSet 路径；
- ComSpecKind；
- 完整 Connector 路径；
- UUID；
- DaVinci 自动补充的默认 InvalidationPolicy / SWC-Implementation 等。

## 11. 变更记录

| 版本 | 日期 | 修改人 | 修改说明 |
| --- | --- | --- | --- |
| V1.5 | 2026-07-14 | Codex | 新增信号 + SOA 混合模板，覆盖服务、参数、数据类型、Runnable、Connector |
