# Signal Atomic DaVinci 绂荤嚎鎿嶄綔鎵嬪唽

鏈祦绋嬬敤浜庘€滃熀浜庝俊鍙峰紑鍙戔€濈殑鍗?Atomic SWC 浜や粯锛屼緥濡?MiscLamp銆乀urnLamp銆乄iper銆乄indow 涓煇涓姛鑳?SWC銆?
## 寤烘ā瑙勫垯

`signal_atomic_davinci` profile 瀵归綈褰撳墠鎵嬪伐 DaVinci 椋庢牸锛?
| 瀵硅薄 | 鐢熸垚瑙勫垯 |
|---|---|
| SWC | `/ComponentTypes/{SwcName}` |
| MappingSet | `/ComponentTypes/MappingSets/DataMapping` |
| Interface | `/PortInterfaces/{SignalName}` |
| DataElement | `{SignalName}` |
| Port | `{SignalName}`锛屼笉鍔?`Rp_` / `Pp_` |
| 杈撳叆淇″彿 | `R-PORT-PROTOTYPE` |
| 杈撳嚭淇″彿 | `P-PORT-PROTOTYPE` |
| Composition / Connector | 涓嶇敓鎴愶紝鎸夊閮ㄨ竟鐣岀鍙ｅ鐞?|
| RunnableAccess | 鍛ㄦ湡 Runnable 鑷姩璇诲彇鍏ㄩ儴杈撳叆銆佸啓鍏ㄩ儴杈撳嚭 |

## 鏍囧噯浜や粯鏂囨。寤鸿瀛楁

淇″彿妯″紡鏍囧噯鏂囨。浠嶄互 Word/DOCX 涓轰氦浠樿浇浣擄紝琛ㄦ牸搴斿敖閲忎娇鐢ㄧ湡瀹?Word 琛ㄦ牸銆傝嫢涓婃父浣跨敤宓屽叆 Excel锛屽伐鍏蜂篃鍙綔涓虹壒娈婃儏鍐佃鍙栵紝浣嗕笉寤鸿浣滀负鍞竴鏍囧噯銆?
### Runnable 琛?
| 瀛楁 | 蹇呭～ | 绀轰緥 |
|---|---|---|
| 鎵€灞濻WC | 鏄?| `TurnLamp` |
| 瑙﹀彂鐨凴unnable | 鏄?| `TurnLamp_Step` |
| 瑙﹀彂绫诲瀷 | 鏄?| `Init` / `Periodic` |
| 鍛ㄦ湡 | Periodic 蹇呭～ | `10ms` |
| 璇存槑 | 鍚?| `涓诲懆鏈烺unnable` |

### 杈撳叆淇″彿 / 杈撳嚭淇″彿琛?
| 瀛楁 | 蹇呭～ | 绀轰緥 |
|---|---|---|
| 杈撳叆淇″彿 / 杈撳嚭淇″彿 | 鏄?| `VbINP_CAN_xxx_sig` |
| 杈撳叆妯″潡 / 杈撳嚭妯″潡 | 鏄?| `CAN` / `HWA` / `TurnLamp` |
| 鏁版嵁绫诲瀷 | 鏄?| `boolean` / `uint8` / `uint16` / `uint32` |
| CAN/LIN閫氶亾 | 鍚?| `BD1_CANFD4` |
| 璇存槑 | 鍚?| `鐢垫簮妯″紡` |
| EnumValues / 鏋氫妇鍊?| 鏋氫妇淇″彿蹇呭～ | `0=OFF, 1=ON, 2=Invalid` |
| InitValue | 鍚?| `OFF` 鎴?`0` |
| CAN淇″彿鍚嶇О | 鍚?| `PowerMode` |
| 瀵瑰簲淇″彿搴旂敤鍦烘櫙 | 鍚?| `杩滅▼瀵昏溅` |

Enum 寤鸿鏄庣‘鍐欐垚 `鍐呴儴鍊?绗﹀彿鍚峘銆備笉瑕佸彧鍐欒嚜鐒惰瑷€璇存槑銆?
Boolean 鍙互涓嶅啓 EnumValues锛屽伐鍏烽粯璁や娇鐢ㄥ钩鍙?boolean銆?
## 绂荤嚎鐢熸垚鍛戒护

鎵€鏈夋楠ら兘鍦ㄦ湰鍦版墽琛岋紝涓嶄緷璧栫綉缁溿€?
```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe scripts\docx_to_contract.py `
  --input "D:\path\to\浜や粯鏂囨。.docx" `
  --contract output\swc_contract.json `
  --excel output\swc_signal_atomic.xlsx `
  --issues output\swc_gap_report.md `
  --report-json output\swc_gap_report.json `
  --mode signal `
  --profile signal_atomic_davinci
```

鐢熸垚 ARXML锛?
```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m arxml_codegen.cli --config output\swc_config.yaml
```

閰嶇疆鏂囦欢绀轰緥锛?
```yaml
project_name: swc_signal_atomic
schema_version: v2

excel:
  workbook: output/swc_signal_atomic.xlsx

generation:
  mode: workbook_to_arxml
  output: output/swc_signal_atomic.arxml
  report: output/swc_signal_atomic_generation_report.md
  autosar_version: 4-3-0
```

## DaVinci 瀵煎叆鍓嶆鏌?
閲嶇偣妫€鏌ワ細

- `NONQUEUED-RECEIVER-COM-SPEC` 椤哄簭搴斾负锛?  `DATA-ELEMENT-REF` 鈫?`USES-END-TO-END-PROTECTION` 鈫?`ALIVE-TIMEOUT` 鈫?`ENABLE-UPDATE` 鈫?`FILTER` 鈫?`HANDLE-NEVER-RECEIVED` 鈫?`INIT-VALUE`
- Boolean InitValue 浣跨敤 `<CATEGORY>BOOLEAN</CATEGORY>` + `<V>0</V>` 鎴?`<V>1</V>`銆?- Enum InitValue 浣跨敤 CompuScale 绗﹀彿鍚嶃€?- 鍗?Atomic 淇″彿浜や粯涓嶇敓鎴?CompositionConnector锛屽洜姝も€滄湭杩炴帴绔彛鈥濈被鎻愮ず灞炰簬杈圭晫寤烘ā鎻愮ず锛屼笉鏄?ARXML 缁撴瀯閿欒銆?
## 閫傜敤杈圭晫

閫傚悎锛?
- 鍗?Atomic SWC
- 绾?S/R 淇″彿鎺ュ彛
- 杈撳叆/杈撳嚭淇″彿琛ㄩ┍鍔?- DaVinci 涓悗缁敱浣跨敤鑰呴獙璇佹垨琛ヨ繛鎺ュ叧绯?
涓嶉€傚悎锛?
- Client/Server 鏈嶅姟鎺ュ彛
- 澶?SWC Composition 鍐呴儴杩炴帴
- Record 绫诲瀷鍙傛暟
- 澶嶆潅 ComSpec 绛栫暐锛屼緥濡?invalid value銆乼imeout substitution銆丒2E profile

SOA 妯″紡鍚庣画搴斿熀浜庡崟鐙殑鎵嬪伐 DaVinci ARXML 鏍锋湰寤虹珛 profile銆?
