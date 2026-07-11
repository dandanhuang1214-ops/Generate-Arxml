# ARXML Codegen

Excel 驱动的 AUTOSAR Classic Platform ARXML 生成工具。目标是用 Excel 作为输入源，生成符合 AUTOSAR 4-3-0 规范的 ARXML，平替 DaVinci Developer 中可规则化、重复性的建模录入工作。

## 技术栈

| 类别 | 技术 |
|------|------|
| 运行时 | Python >= 3.10 |
| Excel 解析 | openpyxl |
| XML 生成 | lxml（命名空间感知，AUTOSAR schema r4.0） |
| 配置解析 | PyYAML |
| 模型定义 | Python dataclasses (slots) |
| 包管理 | pip + setuptools（editable install） |
| 测试 | pytest |
| 代码检查 | ruff |
| 入口脚本 | PowerShell（Windows 环境） |

## 项目结构

```
├── Composition_HornCtrl(2).arxml    # 标准参考模板（Vector DaVinci Developer 导出）
├── config/
│   └── project.yaml                 # 中心配置文件
├── data/
│   └── input/
│       ├── WW_SWC_Design_v2.xlsx    # 生产工作簿（雨刮/洗涤系统）
│       ├── arxml_input_template.xlsx # 空白模板
│       └── test.md                  # 原始需求规格文档
├── docs/
│   ├── prompt.md                    # 权威需求规格
│   ├── excel_template.md            # Excel 模板说明
│   └── ...
├── output/
│   ├── generated_ww_swc.arxml       # 主生成物
│   ├── generation_report.md         # 校验和生成报告
│   └── init_autosar_types.m         # MATLAB Simulink 类型初始化脚本
├── scripts/
│   ├── run_codegen.ps1              # ★ 主入口
│   └── generate_test_excel.py       # 系统模型定义（架构参考）
├── src/arxml_codegen/
│   ├── cli.py                       # 命令行入口
│   ├── excel/
│   │   ├── reader.py                # Excel 工作簿解析
│   │   └── template.py              # Excel 模板创建（20 Sheet）
│   ├── generator/
│   │   └── arxml_writer.py          # ARXML 构建、校验、报告
│   ├── models/
│   │   └── schema.py                # 所有实体的 dataclass 模型（25+ 类型）
│   └── validator/
│       ├── engine.py                # CORE 验证引擎（13 条规则组）
│       ├── finding.py               # 验证发现数据结构
│       └── rules.py                 # AUTOSAR CORE-XXX 验证规则
├── tests/
│   └── test_cli.py                  # 测试套件（10 个测试）
├── pyproject.toml
└── README.md
```

### 数据流

```
Excel (.xlsx)
     │
     ▼
reader.py  ──解析──▶  WorkbookV2Model (dataclasses)
                         │
                         ├──▶  validate_model_v2()  ──内联校验──▶  错误列表
                         │
                         └──▶  build_arxml_v2()    ──生成──▶  ARXML
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
                 ARXML        生成报告.md      CORE 验证
```

## Excel 模板（20 Sheet）

模板支持完整的 AUTOSAR SWC/Composition 建模，包含以下 Sheet：

| Sheet | 用途 |
|---|---|
| `ProjectConfig` | AUTOSAR 版本、RootPackage、默认 MappingSet 路径等项目级配置 |
| `Components` | 组件类型定义（Application SWC / Composition SWC），含 InternalBehavior 和 Implementation 名称 |
| `ComponentPrototypes` | Composition 内的组件实例，如 `Atm_Inst`、`Enh_Inst` |
| `PrimitiveDataTypes` | 基础数据类型（ADT→IDT 映射、BaseType、CompuMethod、DataConstr、UnitRef） |
| `RecordTypes` | 结构体/Record 应用数据类型 |
| `RecordElements` | Record 类型的字段定义及其顺序 |
| `DataTypeMappings` | ADT 到 IDT 显式映射 |
| `CompuMethods` | 计算方法（TEXTTABLE / LINEAR / IDENTICAL） |
| `CompuScales` | 计算方法的比例/文本表条目 |
| `DataConstrs` | 数据约束（上下限） |
| `SRInterfaces` | Sender/Receiver 接口定义 |
| `SRDataElements` | S/R 接口的数据元素 |
| `CSInterfaces` | Client/Server 接口定义 |
| `CSOperations` | C/S 接口的 Operation |
| `CSArguments` | C/S Operation 的参数（方向：IN/OUT/INOUT） |
| `Ports` | 组件端口（方向、接口引用、ComSpec、初值等） |
| `Runnables` | Runnable 定义和 symbol |
| `RunnableEvents` | 触发事件（Init/Periodic/OperationInvoked/DataReceived） |
| `RunnableAccesses` | Runnable 内数据访问点（DataRead/DataWrite/ServerCallPoint） |
| `CompositionConnectors` | 基于 prototype 的 Assembly 连接器 |
| `Units` | 物理单位定义（UNIT-REF 引用） |

## 环境搭建

### 前提条件

- Windows 系统（PowerShell）
- Python 3.10+

### 安装步骤

```powershell
# 1. 进入项目目录
cd D:\work\SOA\code

# 2. 创建虚拟环境
py -3.11 -m venv .venv

# 3. 激活虚拟环境
.venv\Scripts\Activate.ps1

# 4. 安装依赖
python -m pip install --upgrade pip
pip install -e .[dev]

# 5. 验证安装
python -m arxml_codegen.cli --help
pytest
```

## 快速开始

使用 `scripts/run_codegen.ps1` 作为统一入口。

### 创建 Excel 模板

```powershell
.\scripts\run_codegen.ps1 -CreateTemplate data/input/my_template.xlsx
```

### 只校验不生成（Dry Run）

```powershell
.\scripts\run_codegen.ps1 -DryRun
```

### 完整生成

```powershell
.\scripts\run_codegen.ps1
```

### 使用自定义配置

```powershell
.\scripts\run_codegen.ps1 -Config config/my_project.yaml
```

### 手动调用 Python 入口

```powershell
python -m arxml_codegen.cli --config config/project.yaml
python -m arxml_codegen.cli --config config/project.yaml --dry-run
python -m arxml_codegen.cli --create-template data/input/template.xlsx
```

生成物默认路径：

| 文件 | 路径 |
|------|------|
| ARXML | `output/generated_ww_swc.arxml` |
| 报告 | `output/generation_report.md` |
| MATLAB 脚本 | `output/init_autosar_types.m` |

## 配置文件

`config/project.yaml`：

```yaml
project_name: arxml_codegen
schema_version: v2

excel:
  workbook: data/input/WW_SWC_Design_v2.xlsx

generation:
  mode: workbook_to_arxml
  output: output/generated_ww_swc.arxml
  report: output/generation_report.md
  matlab_init: output/init_autosar_types.m
  autosar_version: 4-3-0
```

## 功能范围

### 已支持

- 20 Sheet Excel 输入，覆盖完整 AUTOSAR SWC/Composition 建模
- 生成 AUTOSAR Platform Types（SW-BASE-TYPE: boolean, uint8/16/32/64, sint8/16/32, float32）
- 生成 IMPLEMENTATION-DATA-TYPE 和 APPLICATION-PRIMITIVE-DATA-TYPE
- 生成 APPLICATION-RECORD-DATA-TYPE（结构体类型）
- 生成 COMPU-METHOD（TEXTTABLE / LINEAR / IDENTICAL）含 COMPU-RATIONAL-COEFFS
- 生成 DATA-CONSTR（数据约束）
- 生成 UNIT 定义和 UNIT-REF 引用
- 生成 DATA-TYPE-MAPPING-SET 显式映射
- 生成 Sender-Receiver（S/R）和 Client-Server（C/S）接口
- 生成 APPLICATION-SW-COMPONENT-TYPE，含 Ports、Internal Behavior、Runnables、Events
- 生成 COMPOSITION-SW-COMPONENT-TYPE，含 SW-COMPONENT-PROTOTYPE 和 ASSEMBLY-SW-CONNECTOR
- 触发类型支持：Init、Periodic（TimingEvent）、OperationInvoked、DataReceived
- Runnable 内数据访问点（DataReadPoint、DataWritePoint、ServerCallPoint）
- 内联校验 + CORE-XXX 验证规则（13 条规则组）
- 生成 generation_report.md
- 生成 MATLAB init_autosar_types.m

### 暂不支持

BSW/ECUC、OS task mapping、RTE task mapping、SOME/IP deployment、E2E、SecOC、诊断、NvM 详细配置。

## 校验规则

项目包含两层校验：

### 内联校验（validate_model_v2）

在生成前检查数据完整性和引用一致性：
- 必填字段检查（ComponentName、PackagePath 等）
- BaseType 有效性检查
- ComponentKind 检查（Application/Composition）
- 组件原型引用检查
- 接口引用检查（SR/CS 路径匹配）
- Record 元素类型引用检查
- DataTypeMapping 引用检查
- Runnable/Access 引用检查
- 连接器原型/端口引用检查

### CORE 验证规则

基于 AUTOSAR TR_AutosarModelConstraints 的语义级验证：

| 规则组 | 内容 |
|---|---|
| CORE-010 | 数据类型完整性、CompuMethod 校验、接口引用、CS 参数校验 |
| CORE-020 | SWC 结构完整性、Runnable-Event 关联 |
| CORE-030 | 连接器拓扑一致性、未连接端口检测 |
| CORE-040 | 数据访问端口一致性、触发端口校验 |
| CORE-050 | SHORT-NAME 格式、重名检测 |
| CORE-060 | 时序约束（Period 有效性） |

验证结果提供 Excel 行列定位，例如：
```text
[ERROR] CORE-030-CONNECTOR-DIRECTION [Ports!R12]: Provider 'pBool' must be a P-Port.
[WARNING] CORE-030-CONNECTOR-UNCONNECTED [Ports!R24]: Unconnected port: WW_Enh/rA_FWiperPark
```

## DaVinci Developer 兼容规则

- `DATA-TYPE-MAPPING-SET` 由 ProjectConfig 配置路径
- 每个 `SWC-INTERNAL-BEHAVIOR` 自动引用 DataTypeMappingSet
- `SW-BASE-TYPE` 使用 `CATEGORY=FIXED_LENGTH`
- `BASE-TYPE-ENCODING`：boolean → `BOOLEAN`，无符号整数 → `NONE`，有符号整数 → `2C`
- `IMPLEMENTATION-DATA-TYPE` 自动设置 `TYPE-EMITTER=RTE`
- 标准模板参考：`Composition_HornCtrl(2).arxml`（Vector DaVinci Developer 导出）

## 测试

```powershell
# 运行全部测试
pytest

# 或
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## 开发路线

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 项目脚手架、Excel Reader、S/R 信号生成 | ✅ 完成 |
| Phase 2 | C/S 接口、Operation 参数、Service Port | ✅ 完成 |
| Phase 3 | Runnable、Internal Behavior、Mapping Set | ✅ 完成 |
| Phase 4 | Composition、ComponentPrototype、Connector | ✅ 完成 |
| Phase 5 | v2 统一架构、UNITS 支持、CORE 验证 | ✅ 完成 |

详见 `docs/roadmap.md`。

## 许可证

[待定]
