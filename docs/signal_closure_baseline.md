# 纯信号闭环基线

本文档固化当前“信号驱动模式”的已验证能力边界，作为后续 SOA/混合接口开发前的稳定基线。

## 当前闭环

已验证链路：

```text
信号交付 DOCX
  -> canonical contract JSON
  -> Excel v2 workbook
  -> AUTOSAR ARXML
  -> DaVinci Developer 导入/再导出对比
```

当前样本：

- 输入文档：`C:/Users/20261/Downloads/转向灯arxml交付文档.docx`
- 生成物：`output/deliverables/turnlamp/turnlamp.arxml`
- DaVinci 再导出参考：`C:/Users/20261/Downloads/TURNLamp.arxml`

## 已保证规则

### 端口方向

| 文档来源 | 生成结果 |
| --- | --- |
| 输入信号表 / `输入信号` 列 | R-Port / `NONQUEUED-RECEIVER-COM-SPEC` |
| 输出信号表 / `输出信号` 列 | P-Port / `NONQUEUED-SENDER-COM-SPEC` |

当前 TurnLamp 样本结果：

- R-Port：39
- P-Port：20

### 值类型与数据类型

| 文档填写 | 生成策略 |
| --- | --- |
| `值类型=boolean`，`内部数据类型=boolean` | 共享 `App_boolean` |
| `值类型=uint8`，`内部数据类型=uint8` | 共享 `App_uint8` |
| `值类型=uint16`，`内部数据类型=uint16` | 共享 `App_uint16` |
| `值类型=uint32`，`内部数据类型=uint32` | 共享 `App_uint32` |
| `值类型=Enum` | 信号专属 ADT + TEXTTABLE CompuMethod |

重要约束：

- `uint8/uint16/uint32` 不等于 Enum。
- 只有 `值类型=Enum` 才生成 TEXTTABLE。
- 如果 `值类型` 不是 Enum，即使“状态值表”列有内容，也不按 Enum 生成。

### CompuMethod

基础数值类型生成 IDENTICAL CompuMethod：

| ADT | CompuMethod |
| --- | --- |
| `App_uint8` | `CM_App_uint8_Identical` |
| `App_uint16` | `CM_App_uint16_Identical` |
| `App_uint32` | `CM_App_uint32_Identical` |

Boolean 使用平台风格：

- `boolean_CompuMethod`

### InitValue

当前规则对齐 MiscLamp / DaVinci 风格：

| 类型 | ARXML InitValue |
| --- | --- |
| Boolean | `APPLICATION-VALUE-SPECIFICATION` + `CATEGORY=BOOLEAN` + `<V>0/1</V>` |
| Value / uint8 / uint16 / uint32 | `APPLICATION-VALUE-SPECIFICATION` + `CATEGORY=VALUE` + `<V>...</V>` |
| Enum | `APPLICATION-VALUE-SPECIFICATION` + `CATEGORY=VALUE` + `<VT>枚举符号</VT>` |

当前 TurnLamp 样本结果：

- `BOOLEAN`：29
- `VALUE`：30
- `Enum`：0

### Runnable

当前纯信号模式生成：

- Init Runnable
- Periodic Step Runnable
- 输入信号对应 DataRead access
- 输出信号对应 DataWrite access

当前 TurnLamp 样本：

- `TurnLamp_init`
- `TurnLamp_Step`
- DataRead：39
- DataWrite：20

## 当前不覆盖内容

纯信号模式暂不覆盖：

- Client/Server `rr` 端口
- Operation / Argument
- ClientComSpec / ServerComSpec
- OperationInvokedEvent
- CompositionConnectors
- SOA 服务发现 / SOMEIP 扩展

这些能力进入 SOA/混合接口阶段统一设计，不在纯信号模板中继续硬塞。

## DaVinci 再导出差异

与 DaVinci 再导出的 `TURNLamp.arxml` 对比，核心语义一致：

- 端口数量一致
- R/P 方向一致
- Interface / DataElement 数量一致
- ADT / IDT / CompuMethod / DataConstr 数量一致
- DataTypeMapping 数量一致
- Runnable 读写访问数量一致
- InitValue 类别一致

DaVinci 自动补充/调整但当前暂不强制生成的内容：

1. 顶层 AR-PACKAGE 顺序调整；
2. SR Interface 下补 `INVALIDATION-POLICYS`；
3. DataElement 下补 `SW-DATA-DEF-PROPS`；
4. ImplementationDataType 下补 `DATA-CONSTR-REF`；
5. 补 `SWC-IMPLEMENTATION`。

这些差异属于 DaVinci 对齐优化项，后续在“大集合”阶段统一处理。

## 验收命令

```powershell
.\.venv\Scripts\python.exe scripts\docx_to_contract.py `
  --input "C:\Users\20261\Downloads\转向灯arxml交付文档.docx" `
  --profile signal_atomic_davinci `
  --mode signal `
  --contract output\deliverables\turnlamp\turnlamp_contract.json `
  --excel output\deliverables\turnlamp\turnlamp.xlsx `
  --issues output\deliverables\turnlamp\turnlamp_gap.md `
  --report-json output\deliverables\turnlamp\turnlamp_gap.json

.\.venv\Scripts\python.exe -m arxml_codegen.cli `
  --config output\temp\configs\turnlamp_codegen.yaml

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

当前验证结果：

- `pytest`：25 passed
- `ruff`：All checks passed
- ARXML 结构断言：通过
