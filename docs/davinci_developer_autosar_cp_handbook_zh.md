# DaVinci Developer 与 AUTOSAR CP 中文知识手册

> 面向当前 `Generate-Arxml` 项目和第一次系统学习 DaVinci Developer 的使用者。
>
> 基准版本：AUTOSAR Classic Platform R24-11。本文不是官方规范的逐句翻译，而是工程选择指南。

## 1. 这本手册解决什么问题

官方资料经常先讲元模型、类图和约束，但工程人员真正遇到的问题通常是：

- 这是一个“值”、一个“状态”，还是一个“服务”？
- 应该用 S/R、C/S 还是 ModeSwitch？
- Runnable 为什么既有 Trigger，又有 Access Point？
- Queue、异步、Timeout 什么时候值得配置？
- 两个 Composition 怎样连接？
- 一个 Developer 配置最终会生成什么 RTE API？

本手册采用固定的理解顺序：

```text
业务语义
  → AUTOSAR 对象选择
  → Port / Interface / DataType
  → Runnable Trigger / Access
  → Composition Connector
  → RTE 行为
  → ARXML 结构
```

学习时不要从 ARXML 标签开始背。先理解对象负责什么，再看它在 ARXML 中怎样表达。

---

## 2. 一张图理解 Developer 中的主要对象

```text
DataType 层
  ADT ──DataTypeMapping──> IDT
   │                       │
   ├─ CompuMethod         └─ 最终 C 类型/RTE 实现表示
   ├─ DataConstr
   └─ Unit

Interface 层
  S/R Interface | C/S Interface | ModeSwitch Interface
          │
Port 层   P-Port / R-Port / PR-Port + ComSpec
          │
Behavior 层
  Runnable ── Trigger/Event
           └─ Access Point
          │
Composition 层
  ComponentPrototype + Assembly/Delegation Connector
          │
Integration 层
  RTE、ECU Extract、Task Mapping、BSW 配置
```

Developer 的重点是前五层；更下游的 OS Task、BSW 和 ECU 配置通常由 DaVinci Configurator 负责。

---

## 3. 最常见术语

| 英文 | 中文理解 | 不要误解为 |
|---|---|---|
| SWC Type | 软件组件“类型/蓝图” | 某个 ECU 上唯一实例 |
| Component Prototype | SWC Type 在 Composition 中的实例 | 新的数据类型 |
| Port Interface | 端口双方共同遵循的通信契约 | 组件实际端口 |
| P-Port | Provided Port，提供能力或数据 | 永远是数据输出；C/S 中它是 Server |
| R-Port | Required Port，需要能力或数据 | 永远是数据输入；C/S 中它是 Client |
| Data Element | S/R Interface 中传递的数据项 | Component Port 名称 |
| Operation | C/S Interface 中可调用的函数契约 | Runnable |
| Runnable | RTE 可调度的软件执行入口 | OS Task |
| Event/Trigger | 什么情况下激活 Runnable | Runnable 内部读写动作 |
| Access Point | Runnable 执行时访问什么 Port/Data/Operation | 激活 Runnable 的原因 |
| ComSpec | 某个 Port 上的通信策略 | Interface 本身的数据结构 |
| Connector | Composition 中 Port 与 Port 的连接 | 总线 Signal Mapping |

最重要的两个区分：

```text
Interface ≠ Port
Trigger ≠ Access
```

---

## 4. 数据类型：ADT、IDT、CompuMethod、DataConstr

### 4.1 ADT 与 IDT

Application Data Type（ADT）描述业务意义：

```text
App_WindowPosition
物理意义：车窗位置
物理范围：0..100 %
```

Implementation Data Type（IDT）描述代码实现：

```text
Impl_WindowPosition
实现类型：uint16
内部范围：0..10000
```

它们通过 DataTypeMapping 关联：

```text
App_WindowPosition → Impl_WindowPosition
```

这样业务接口可以保持稳定，而底层实现表示可以按平台调整。

### 4.2 CompuMethod

CompuMethod 回答：内部值怎样解释为物理值？

常用类型：

| Category | 什么时候用 | 示例 |
|---|---|---|
| IDENTICAL | 内部值与物理值相同 | 计数器 0..255 |
| LINEAR | 存在分辨率或 Offset | 电流、温度、位置 |
| TEXTTABLE | 数值对应枚举符号 | OFF=0、ON=1 |

线性换算按当前项目约定：

```text
physical = offset + resolution × internal
```

例子：

```text
内部类型：uint16
内部范围：0..65535
Resolution：0.01
Offset：0
物理范围：0..655.35 A
```

对应：

```text
physical = 0 + 0.01 × internal
```

AUTOSAR 官方把 CompuMethod 定义为内部表示与物理值之间的关系，并给出了 LINEAR 的 numerator/denominator 示例。[AUTOSAR Application Interfaces User Guide](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_EXP_AIUserGuide.pdf)

### 4.3 DataConstr

DataConstr 回答：哪些内部值是合法的？

例子：底层使用 `uint16`，但产品只允许 0..1000：

```text
IDT 容量：0..65535
DataConstr：0..1000
```

不要把“基础类型能表示的范围”和“业务允许范围”混为一谈。

Enum 也应使用实际合法范围。例如只定义 0、1、2 时，DataConstr 通常应与项目策略一致地表达实际合法范围或明确保留值，而不是无意识写成 0..255。

### 4.4 Record 与嵌套 Record

Record 相当于结构体：

```c
typedef struct {
    uint16 CallId;
    uint8  Cmd;
} TrkCtrlPayload;
```

嵌套 Record：

```c
typedef struct {
    uint32 OnDuration;
    uint32 OffDuration;
} HornPeriodMode;

typedef struct {
    uint64 CallId;
    HornPeriodMode PeriodMode;
} HornCtrlMode;
```

ADT Record 和 IDT Record 都需要各自建立，两个 Record 也分别需要 DataTypeMapping。

---

## 5. 三种常用通信方式怎样选

### 5.1 Sender/Receiver：共享状态或连续数据

把它理解为：

```text
生产者发布数据，消费者读取数据
```

适合：

- 电源模式当前值；
- 车速；
- 温度；
- 车窗当前位置；
- 开关状态；
- 故障状态；
- 周期采样值。

典型 RTE API：

```c
Rte_Read_Port_Data(&value);
Rte_Write_Port_Data(value);
```

### 5.2 Client/Server：请求对方执行动作

把它理解为：

```text
Client 调用一个 Operation，Server 执行并返回结果
```

适合：

- 请求门锁执行解锁；
- 请求电机执行动作；
- 查询一个需要计算或封装的结果；
- 有明确 IN/OUT 参数和返回错误的操作。

典型 RTE API：

```c
Rte_Call_Port_Operation(...);
```

### 5.3 ModeSwitch：让 RTE 理解“系统当前处于什么模式”

ModeSwitch 不是普通枚举信号的另一种写法。它的价值是让 RTE 和 Runnable 调度逻辑理解模式语义。

适合：

- 进入某模式时触发 Runnable；
- 离开某模式时触发 Runnable；
- 某些模式下禁止某个 Event 激活 Runnable；
- 组件作为 Mode Manager 发布模式；
- 组件读取当前 RTE Mode；
- 需要 Mode Switch Acknowledge。

---

## 6. ModeSwitch 从零理解

### 6.1 Mode 是什么

ModeDeclarationGroup 定义一组互斥模式：

```text
PowerModeGroup
├─ OFF
├─ ACC
├─ ON
├─ CRANK
└─ POST_RUN
```

同一时刻只能处于其中一个模式。

AUTOSAR 定义 ModeDeclarationGroup 为一组互斥 Mode，并规定一个 ModeDeclarationGroup 实例只能由一个 Mode Manager 切换。[AUTOSAR Mode Management Requirements](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_RS_ModeManagement.pdf)

### 6.2 ModeSwitchInterface 包含什么

核心对象：

```text
ModeDeclarationGroup
        ↓
ModeDeclarationGroupPrototype
        ↓
ModeSwitchInterface
        ↓
Mode P-Port / Mode R-Port
```

一个 ModeSwitchInterface 最多关联一个 ModeDeclarationGroupPrototype，这是 AUTOSAR 为控制复杂度规定的。[AUTOSAR Software Component Template](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_TPS_SoftwareComponentTemplate.pdf)

### 6.3 三种角色

#### Mode Manager

负责决定并切换模式：

```c
Rte_Switch_PowerMode_CurrentMode(RTE_MODE_PowerMode_ON);
```

它通常持有 Mode P-Port。

#### Mode User

读取当前模式或响应模式变化：

```c
mode = Rte_Mode_PowerMode_CurrentMode();
```

它通常持有 Mode R-Port。

#### Mode Requester

请求切换模式，但不一定有最终决定权。例如多个组件都请求电源状态变化，Mode Manager/BswM 仲裁后才真正切换。

“请求模式”与“发布最终模式”不要混为一谈。

### 6.4 Mode 能怎样影响 Runnable

常见用法：

| 配置 | 效果 |
|---|---|
| On Mode Entry | 进入 ON 时激活 Runnable |
| On Mode Exit | 离开 ON 时激活 Runnable |
| On Transition | OFF → ON 时激活 Runnable |
| Mode Disabling | OFF 模式下禁止周期 Event 激活 Runnable |
| Read Mode | Runnable 执行中读取当前模式 |
| Mode Switch Acknowledge | 模式发布者确认切换已被处理 |

Vector Developer 的 Runnable 编辑器明确支持 Mode Entry、Mode Exit、Transition、Mode Disabling、Read Mode 和 Send Mode Switch 等配置。[Vector Runnable Entities](https://help.vector.com/davinci-developer-classic/current/en/help/html/defining_runnable_entities.html)

#### Transition Value 到底是什么

Developer 中的 `Transition Value` 对应 ARXML 的 `ON-TRANSITION-VALUE`。它是一个**保留的正整数编码**，供 RTE 生成器在程序中表示“该 ModeMachineInstance 正处于两个稳定模式之间的切换阶段”。它不是：

- 一个需要加入 Mode Declaration 列表的普通模式；
- “下一模式”的值；
- 切换耗时或超时时间；
- 一条允许 `A → B` 的状态迁移规则；
- Runnable 的 `On Transition` Trigger。

例如：

```text
PowerModeGroup（EXPLICIT_ORDER）
OFF       = 0
ACC       = 1
ON        = 2
POST_RUN  = 3

Transition Value = 255
```

这里 `255` 只表示“切换处理中”，不能再分配给任何正常 Mode Declaration。AUTOSAR 将 `onTransitionValue` 定义为可选的 `PositiveInteger`，用于以程序值表示两个状态之间的过渡；官方 WdgM 示例使用正常模式值 `0..4`、Transition Value `255`。[AUTOSAR Modeling Show Cases](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_TR_ModelingShowCases.pdf) [AUTOSAR Watchdog Manager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf)

并非所有 Mode Group 都必须填写它。AUTOSAR 的 EcuM 标准 Mode Group 就没有配置 On Transition Value。因此项目没有“切换中状态必须以数值暴露”的需求时可以留空；需要异步切换、跨核同步、切换确认，或代码必须区分“稳定模式/正在切换”时再配置。[AUTOSAR ECU State Manager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_ECUStateManager.pdf)

#### Mode Entry、Mode Exit 和 On Transition 的关系

三者都属于 `SwcModeSwitchEvent`，但匹配条件不同：

| Trigger | 何时匹配 | 典型用途 |
|---|---|---|
| On Mode Exit `ON` | 从 `ON` 离开，不关心目标模式 | 停止执行器、保存上下文、释放 ON 专用资源 |
| On Transition `ON → POST_RUN` | 只匹配这一条指定迁移 | 执行该路径独有的交接动作 |
| On Mode Entry `POST_RUN` | 进入 `POST_RUN`，不关心来源模式 | 初始化该模式资源、启动延时关窗逻辑 |

它们在语义上前后衔接，但**配置上不要求成对出现**。只需要进入初始化，就只配 Entry；只需要离开清理，就只配 Exit；只有行为依赖明确的起点和终点时才配 On Transition。

以 `ON → POST_RUN` 为例，单核上的概念时序是：

```text
ON 稳定
  │ Mode Manager 请求切换到 POST_RUN
  ▼
阻止下一模式不允许的 Event，并等待受影响 Runnable 结束
  ▼
On Mode Exit(ON)
  ▼
On Transition(ON → POST_RUN)
  ▼
On Mode Entry(POST_RUN)
  ▼
更新 Mode Disabling，POST_RUN 稳定
  ▼
Mode Switch Acknowledge（如果启用）
```

AUTOSAR RTE 规定的完整处理顺序是：激活 mode disabling、等待受影响实体结束、执行并等待 OnExit、执行并等待 OnTransition、执行并等待 OnEntry、更新 mode disabling，最后触发 ModeSwitchAckEvent。多核场景下各核可并行执行，若要求跨核严格阶段同步，还需要在 RTE 配置中增加同步点。[AUTOSAR Mode Management Guide](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_EXP_ModeManagementGuide.pdf)

#### 一个车窗电源模式的实用配置

```text
Mode Group: WindowPowerMode
Modes: OFF=0, ON=1, POST_RUN=2
Initial Mode: OFF
Transition Value: 留空（第一版不需要观察切换中状态）

Window_EnterOn
  Trigger: On Mode Entry ON
  行为: 初始化电机控制上下文

Window_ExitOn
  Trigger: On Mode Exit ON
  行为: 停止 PWM、保存位置

Window_10ms
  Trigger: TimingEvent 10 ms
  Mode Disabling: OFF、POST_RUN
```

这里 Entry/Exit 负责边界动作，Mode Disabling 负责稳定模式期间是否允许周期 Runnable 被激活。不要只配 Entry/Exit，却忘记限制原来的 10 ms 周期 Event；两者解决的是不同问题。

### 6.5 电源模式到底应不应该用 ModeSwitch

使用下面的判断：

#### 只作为车窗算法条件

```c
if (PowerMode == ON) {
    WindowEnable = true;
}
```

优先使用普通 nonqueued S/R Enum。

#### 要控制 Runnable 生命周期

```text
OFF：禁止 WindowControl_10ms
ON：允许 WindowControl_10ms
进入 POST_RUN：触发一次延时关窗处理
```

优先考虑 ModeSwitch。

#### 两种语义都存在

可以同时存在：

- 网络或业务层发布 `PowerModeSignal`；
- PowerMode Manager 根据输入进行仲裁；
- Manager 再通过 ModeSwitchInterface 发布 RTE Mode。

这不是重复建模：一个是输入事实，一个是经过仲裁后的系统运行模式。

### 6.6 最容易犯的错误

- 名称带 `Mode` 就一律建 ModeSwitch；
- 多个 SWC 同时切换同一个 ModeGroup；
- 把 Mode Request 当成最终 Mode；
- 使用 ModeSwitch，但 Runnable 并没有 Entry/Exit/Disabling/ReadMode 等行为；
- 用普通 S/R Enum，却又期待 RTE 自动禁止 Runnable。

---

## 7. Runnable：Trigger 与 Access 必须分开理解

### 7.1 Trigger：为什么执行

常见 Trigger：

| Trigger | 为什么执行 |
|---|---|
| InitEvent | SWC 初始化 |
| TimingEvent | 周期到达 |
| DataReceivedEvent | 收到指定数据 |
| OperationInvokedEvent | Server Operation 被调用 |
| ModeSwitchEvent | 进入/退出/切换模式 |

### 7.2 Access：执行时干什么

常见 Access：

| Access | 执行时做什么 |
|---|---|
| DataRead | 读取 nonqueued S/R 数据 |
| DataWrite | 写入 nonqueued S/R 数据 |
| Receive/Send | 收发 queued S/R 数据 |
| ServerCallPoint | Client 调用 C/S Operation |
| ReadMode | 读取当前 Mode |
| ModeSwitchPoint | 发布 Mode 切换 |

例子：

```text
WindowCtrl_10ms
Trigger：TimingEvent 10 ms
Access：
  - DataRead PowerMode
  - DataRead WindowSwitch
  - DataWrite MotorCommand
```

它不是由 PowerMode 触发，只是在执行时读取 PowerMode。

Server 例子：

```text
DoorLock_ServerRunnable
Trigger：OperationInvokedEvent Unlock
Access：
  - DataRead VehicleSpeed
  - DataWrite LockStatus
```

OperationInvokedEvent 是触发；读取车速和写状态才是 Access。

---

## 8. Queue 什么时候使用

### 8.1 Nonqueued：只关心最新值

新值覆盖旧值：

```text
10 → 20 → 30
消费者读取时得到 30
```

适合：

- 电源模式；
- 车速；
- 温度；
- 位置；
- 当前故障状态；
- 当前开关状态。

### 8.2 Queued：每一条都要处理

值按顺序进入队列：

```text
OPEN → STOP → CLOSE
消费者必须按顺序获取三条
```

适合：

- 命令流；
- 离散事件；
- 每次请求都不能丢失；
- 生产者可能短时间连续发送；
- 消费者处理速度可能暂时较慢。

不应仅仅因为 Developer 里能填写 QueueLength 就使用 Queue。

### 8.3 QueueLength 怎么考虑

至少考虑：

```text
最大突发产生速率
× 最长消费者阻塞时间
× 安全余量
```

QueueLength 不是越大越好：它会增加内存，并可能让消费者处理过时命令。

---

## 9. 同步和异步 C/S 什么时候使用

### 9.1 同步调用

Client 调用后等待 Server 返回：

```text
Client Runnable ──Call──> Server
Client 等待 <──────────── Result
```

适合：

- 本 ECU 内；
- 执行时间短；
- 最坏执行时间明确；
- Client 必须立即使用返回值。

风险：Server 太慢会阻塞 Client Runnable。

### 9.2 异步调用

Client 发起调用后继续执行，结果后续获取：

```text
Client ──Async Call──> Server
Client 继续运行
Client <── Result/Event ── Server
```

适合：

- 操作耗时较长；
- 执行时间不稳定；
- 跨 ECU；
- Client 不允许阻塞；
- 存储、诊断或复杂硬件动作。

结果处理方式可能包括：

- Polling；
- Waiting；
- Operation Call Return Event；
- 不关心返回结果。

选择异步并不代表“性能一定更好”，它会引入状态管理、超时、重复调用和结果关联问题。

---

## 10. Composition 与跨功能域通信

### 10.1 Composition 是什么

Composition SWC Type 是一个结构化容器，内部包含 ComponentPrototype 和 Connector。它不是 Runnable 的直接执行实体。

### 10.2 Assembly Connector

连接同一父 Composition 下两个子实例的相容 Port：

```text
ProviderPrototype.P-Port
    → RequesterPrototype.R-Port
```

### 10.3 Delegation Connector

把内部子组件 Port 暴露为 Composition 外部 Port：

```text
Composition 外部 Port
    ↔ 内部 ComponentPrototype.Port
```

### 10.4 电源 Composition 与车窗 Composition

推荐结构：

```text
VehicleTopComposition
├─ PowerModeComposition_Inst
│  └─ P-Port PowerMode
└─ WindowComposition_Inst
   └─ R-Port PowerMode
```

内部连接：

```text
PowerModeAtomic.P-Port
  → Delegation
PowerModeComposition.P-Port

WindowComposition.R-Port
  → Delegation
WindowAtomic.R-Port
```

顶层连接：

```text
PowerModeComposition_Inst.PowerMode
  → Assembly
WindowComposition_Inst.PowerMode
```

跨越 Composition 边界时必须逐层委托，不能让顶层 Connector 直接引用孙级 Atomic SWC。

Developer 的 Data Exchange Analysis 会结合 Assembly/Delegation Connector、Runnable Access、OperationInvoked Trigger 和 DataMapping 检查完整数据交换链。[Vector Data Exchange Analysis](https://help.vector.com/davinci-developer-classic/current/en/help/html/data_exchange_analysis_editor.html)

### 10.5 一个 Provider 给多个 Consumer

例如 PowerMode 同时给车窗、雨刮、灯光：

```text
PowerMode.P-Port
  ├─→ Window.R-Port
  ├─→ Wiper.R-Port
  └─→ Lamp.R-Port
```

在 Composition 中通常体现为多条 Assembly Connector。每个 Consumer 保持自己的 R-Port 和 ComSpec。

---

## 11. ComSpec 应该怎样理解

ComSpec 是“这个 Port 怎样通信”，不是“Interface 传什么”。

### S/R 常见配置

| 配置 | 解决的问题 |
|---|---|
| InitValue | RTE 初始化时使用什么值 |
| AliveTimeout | 多久没更新视为超时 |
| EnableUpdate | 是否允许更新接收缓存 |
| HandleNeverReceived | 从未接收到数据时怎样处理 |
| Filter | 哪些变化才需要传播/处理 |
| QueueLength | 队列能保存多少条 |
| E2E | 通信数据保护 |

### C/S 常见配置

| 配置 | 解决的问题 |
|---|---|
| QueueLength | Server 未及时处理时可排队多少次调用 |
| Timeout | 同步/异步等待多长时间 |
| Operation Ref | 该 Port 配置针对哪个 Operation |

AUTOSAR 将 ComSpec 定义为附着在 PortPrototype 上的通信属性，不同 Interface 类型只能使用对应种类的 ComSpec。[AUTOSAR Software Component Template](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_TPS_SoftwareComponentTemplate.pdf)

---

## 12. 在 Developer 中学习一个配置的固定方法

每次看到陌生配置，不要只问“这个框填什么”，按下面六问分析：

1. 它属于 DataType、Interface、Port、Runnable 还是 Composition？
2. 它改变的是数据结构、通信行为还是调度行为？
3. 不配置时默认行为是什么？
4. 它最终会影响哪个 RTE API 或 Event？
5. 它与哪些其他配置存在前置依赖？
6. Developer 导出后对应哪些 ARXML 标签？

例如看到 `Mode Disabling`：

```text
所属：Runnable Event
改变：调度行为
前置：组件必须有 Mode R-Port
作用：指定模式下 Event 不激活 Runnable
ARXML：MODE-DEPENDENCY / DISABLED-MODE-IREFS 等相关结构
```

---

## 13. 建议的 Developer 实操练习

### 练习 1：基础 S/R

- 建 `App_PowerMode` Enum；
- 建 S/R Interface；
- 建一个 Provider 和一个 Consumer；
- Consumer 周期 Runnable DataRead；
- Composition Assembly 连接；
- 用 Data Exchange Analysis 检查。

### 练习 2：LINEAR

- `uint16` 内部范围 0..65535；
- Resolution 0.01；
- Unit A；
- 观察 ADT、CompuMethod、DataConstr 和 IDT。

### 练习 3：同步 C/S

- 一个 Operation；
- IN、OUT 参数；
- Client 周期 Runnable 建 ServerCallPoint；
- Server 建 OperationInvokedEvent。

### 练习 4：ModeSwitch

- 建 `PowerModeGroup`；
- Manager 发布 Mode；
- Window 组件 ReadMode；
- 配置 ON Entry Event；
- 配置 OFF 时禁用周期 Event；
- 比较它与普通 Enum S/R 的差异。

### 练习 5：多层 Composition

- 建 PowerMode Composition；
- 建 Window Composition；
- 分别添加 Delegation；
- 在 VehicleTopComposition 中添加 Assembly；
- 检查完整链路。

---

## 14. 当前生成器能力对照

| 能力 | 当前状态 |
|---|---|
| Primitive ADT/IDT/Mapping | 已支持 |
| IDENTICAL/LINEAR/TEXTTABLE | 已支持 |
| DataConstr/Unit | 已支持基础形式 |
| Record/嵌套 Record | 已支持 |
| 嵌套 Record 初值 | 已支持递归生成 |
| Nonqueued S/R | 已支持 |
| Queued S/R | Excel 层有基础字段，文档链路未完整开放 |
| 同步 C/S | 已支持基础形式 |
| 异步 C/S | 未支持 |
| ModeSwitchInterface | 未支持 |
| 单层 Composition | 已支持 |
| 多层 Composition | 未支持 |
| Assembly/基础 Delegation | 已支持 |
| Mode Entry/Exit/Disabling | 未支持 |
| E2E/Invalidation/复杂 Filter | 未支持 |
| IRV/ExclusiveArea/PIM | 未支持 |

本表用于防止把“Developer 可以配置”误认为“当前生成器已经支持”。

---

## 15. 我们后续怎样交互学习

以后你遇到任何 Developer 配置，可以提供以下任意一种材料：

- Developer 界面截图；
- 你手工配置后导出的 ARXML；
- 一个业务场景；
- 配置项英文名称；
- 导入错误截图。

我们固定按下面格式讨论：

```text
1. 中文直觉解释
2. 它解决什么问题
3. 什么时候应该用
4. 什么时候不应该用
5. 与其他配置的依赖关系
6. Developer 中的典型操作
7. 对应 ARXML 结构
8. 当前生成器是否支持
9. 是否值得加入标准交付文档
```

确认后的结论继续补进本手册，使它逐步变成当前项目自己的 Developer 知识库。

---

## 16. 精选官方资料

不建议一开始通读全部规范，只保留下面几份：

1. [AUTOSAR Software Component Template R24-11](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_TPS_SoftwareComponentTemplate.pdf)
   查 Port、Interface、ComSpec、Runnable、Mode、Composition 的正式定义。

2. [AUTOSAR Application Interfaces User Guide R24-11](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_EXP_AIUserGuide.pdf)
   学 ADT、CompuMethod、Unit 和常见数据建模示例。

3. [AUTOSAR Mode Management Requirements R24-11](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_RS_ModeManagement.pdf)
   理解 Mode、Mode Manager、Requester 与仲裁。

4. [Vector DaVinci Developer Runnable Entities](https://help.vector.com/davinci-developer-classic/current/en/help/html/defining_runnable_entities.html)
   查 Developer 中 Trigger、Access、同步/异步、Mode 等实际配置能力。

5. [Vector Data Exchange Analysis](https://help.vector.com/davinci-developer-classic/current/en/help/html/data_exchange_analysis_editor.html)
   检查 Component、Port、Runnable 和 Connector 是否真正形成通信闭环。

阅读原则：先按本手册理解工程场景，遇到有争议的细节时，再跳到对应官方章节核实。
