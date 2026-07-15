# ARXML 鎺ュ彛浜や粯鏂囨。妯℃澘锛氫俊鍙烽┍鍔ㄦā寮?v1.1

> 閫傜敤鑼冨洿锛氬熀浜庝俊鍙风殑 Atomic SWC 寮€鍙戙€?
> 浜や粯鐩爣锛氳宸ュ叿浠庢湰鏂囦欢鎶藉彇淇″彿濂戠害锛岀敓鎴?Excel v2 鑽夌锛屽啀鐢熸垚 DaVinci Developer 鍙鍏ョ殑 ARXML銆?
> 濉啓鍘熷垯锛氬彧濉啓涓氬姟涓嶅彲鎺ㄥ鐨勪俊鎭紱鍖呰矾寰勩€佸畬鏁?AUTOSAR Ref銆丮appingSet銆両nterfaceRef銆侀粯璁?ComSpec 绛夌敱宸ュ叿鐢熸垚銆?
## 1. 椤圭洰涓庡懡鍚嶈鍒?
| 瀛楁 | 濉啓鍊?| 璇存槑 |
| --- | --- | --- |
| 椤圭洰鍚嶇О |  | 渚嬪 TurnLamp / Wiper / Window |
| 绯荤粺/鍩?|  | 渚嬪 Body / ExteriorLight |
| 鐩爣 AUTOSAR 鐗堟湰 | 4.3.0 | 褰撳墠寤鸿 4.3.0锛屼究浜?DaVinci R24-11 瀵煎叆 |
| 鐢熸垚妯″紡 | SignalAtomicDaVinci | 鍥哄畾濉啓 |
| RootPackage |  | 鍙┖锛涗负绌烘椂宸ュ叿浣跨敤 DaVinci 淇″彿妯℃澘璺緞 |
| Atomic SWC 鍚嶇О |  | 淇″彿妯″紡绗竴鐗堝缓璁竴涓枃妗ｅ搴斾竴涓?Atomic SWC |
| 鍛ㄦ湡 Runnable 鍚嶇О |  | 渚嬪 Step / MainFunction / Runnable_10ms |
| 榛樿鍛ㄦ湡 ms |  | 渚嬪 10 / 20 / 50 |
| 闇€姹傛潵婧愭枃妗?|  | SRD/璇﹁/浜や粯鏂囨。鍚嶇О涓庣増鏈?|
| 濉啓浜?鏃ユ湡 |  |  |

## 2. SWC 娓呭崟

| SWC鍚嶇О | SWC绫诲瀷 | 鎵€灞炲眰绾?| 閮ㄧ讲鍩?| 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- |
|  | ApplicationAtomicSwComponentType | Application |  |  |  |

濉啓璇存槑锛?
- 淇″彿椹卞姩绗竴鐗堥粯璁ゅ彧鐢熸垚 Atomic SWC锛屼笉鐢熸垚 Composition銆?- 濡傛灉鍚屼竴鏂囨。鍑虹幇澶氫釜 SWC锛岄渶瑕佹槑纭瘡涓俊鍙峰睘浜庡摢涓?SWC锛涘惁鍒欓粯璁ゅ叏閮ㄥ綊鍏モ€滈」鐩笌鍛藉悕瑙勫垯鈥濅腑鐨?Atomic SWC銆?
## 3. Runnable 涓庤Е鍙?
| SWC | RunnableName | TriggerType | PeriodMs | 鍏宠仈Port/Signal | 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | TimingEvent |  |  |  |  |

濉啓璇存槑锛?
- `TriggerType` 绗竴鐗堟敮鎸?`TimingEvent`銆?- `PeriodMs` 蹇呴』鏄庣‘锛涘鏋滄枃妗ｉ噷娌℃湁鍛ㄦ湡锛岃鍐欏叆鈥滄湭鍐抽棶棰樷€濄€?- 濡傛灉淇″彿璇诲啓鍏ㄩ儴鍙戠敓鍦ㄥ悓涓€涓懆鏈熷嚱鏁帮紝`鍏宠仈Port/Signal` 鍙～ `ALL`銆?
## 4. 杈撳叆淇″彿娓呭崟

| No | SignalName | ProviderModule/SWC | ConsumerSWC | DataType | Unit | Range | EnumValues | InitValue | PeriodMs | CAN/LIN閫氶亾 | CAN淇″彿鍚嶇О | Description | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  | boolean |  | 0..1 |  | 0 |  |  |  |  |  |

濉啓璇存槑锛?
- `SignalName` 寤鸿鐩存帴浣跨敤 DaVinci 閲屾湡鏈涚湅鍒扮殑 PortInterface/Port/DataElement 鍚嶇О锛涘伐鍏蜂細澶嶇敤璇ュ悕绉般€?- `DataType` 鏀寔 `boolean`銆乣uint8`銆乣uint16`銆乣uint32`銆乣sint8`銆乣sint16`銆乣sint32`锛屼互鍙婇」鐩害瀹氱殑搴旂敤绫诲瀷鍚嶃€?- `EnumValues` 鍙湁鏋氫妇/鏂囨湰琛ㄦ椂濉啓锛屾牸寮忓繀椤绘槸 `0=OFF, 1=ON, 15=Error_Value`銆備笉瑕佸彧鍐欒嚜鐒惰瑷€鎻忚堪銆?- `InitValue`锛?  - Boolean 濉?`0/1` 鎴?`false/true`锛?  - Numeric 濉暟瀛楋紱
  - Enum 鎺ㄨ崘濉灇涓剧鍙凤紝渚嬪 `OFF`锛屼篃鍙～鍐呴儴鍊间絾浼氳繘鍏ヤ汉宸ョ‘璁ゆ竻鍗曘€?- `ProviderModule/SWC` 琛ㄧず淇″彿鏉ユ簮锛涘鏋滃彧鏄閮ㄦ€荤嚎鏉ユ簮锛屽彲浠ュ～妯″潡鍚嶆垨缃戠粶鍚嶃€?- `ConsumerSWC` 閫氬父濉湰 Atomic SWC 鍚嶇О銆?
## 5. 杈撳嚭淇″彿娓呭崟

| No | SignalName | ProviderSWC | ConsumerModule/SWC | DataType | Unit | Range | EnumValues | InitValue | PeriodMs | CAN/LIN閫氶亾 | CAN淇″彿鍚嶇О | Description | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  | boolean |  | 0..1 |  | 0 |  |  |  |  |  |

濉啓璇存槑锛?
- `ProviderSWC` 閫氬父濉湰 Atomic SWC 鍚嶇О銆?- `ConsumerModule/SWC` 琛ㄧず淇″彿鍘诲悜锛涘鏋滃彧鏄彂閫佸埌澶栭儴缃戠粶锛屽彲浠ュ～妯″潡鍚嶆垨缃戠粶鍚嶃€?- 杈撳嚭淇″彿浼氱敓鎴?P-Port锛岃緭鍏ヤ俊鍙蜂細鐢熸垚 R-Port銆?
## 6. 鏁版嵁绫诲瀷涓庢灇涓捐ˉ鍏?
| TypeName | BaseType | CompuMethodType | EnumValues | PhysicalRange | Unit | DataConstr | 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | uint8 | TEXTTABLE | 0=OFF, 1=ON | 0..1 |  | 0..1 |  |  |

濉啓璇存槑锛?
- 濡傛灉淇″彿娓呭崟閲岀殑 `EnumValues` 宸茬粡瀹屾暣锛屾湰琛ㄥ彲涓嶅～锛涘鏉傜被鍨嬫垨澶嶇敤绫诲瀷寤鸿濉啓銆?- `CompuMethodType` 鏀寔 `IDENTICAL`銆乣LINEAR`銆乣TEXTTABLE`銆?- 鏋氫妇蹇呴』缁欏嚭鍐呴儴鍊煎埌鏂囨湰绗﹀彿鐨勬槧灏勶紝閬垮厤 DaVinci/RTE 闃舵鍑虹幇鍒濆€煎拰 CompuScale 涓嶄竴鑷淬€?
## 7. 鍙€夐珮绾ч厤缃?
| SignalName | ComSpec閰嶇疆 | DataFilter | HandleNeverReceived | InvalidValue | AliveTimeout | HandleTimeoutType | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | ALWAYS | false |  | 0 |  |  |

濉啓璇存槑锛?
- 鏈〃鍙┖銆備负绌烘椂宸ュ叿浣跨敤 DaVinci 淇″彿妯℃澘榛樿鍊笺€?- `HandleNeverReceived` 涓嶈闅忔剰寮€鍚紱濡傛灉寮€鍚紝寤鸿鍚屾椂鏄庣‘ `InvalidValue`銆?- 绗竴鐗堢敓鎴愬櫒浼樺厛淇濊瘉 DaVinci 鍙鍏ワ紝涓嶅己鍒惰緭鍑烘墍鏈夊彲閫?ComSpec銆?
## 8. 鏈喅闂

| 缂栧彿 | 瀛楁/淇″彿 | 闂鎻忚堪 | 寤鸿榛樿鍊?| 璐熻矗浜?| 鐘舵€?| 鍏抽棴缁撹 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  | Open |  |

濉啓璇存槑锛?
- 宸ュ叿涓嶈兘鍙潬鎺ㄥ鐨勪俊鎭繀椤昏繘鍏ユ湰琛紝涓嶈兘闈欓粯缂栭€犮€?- 鐘舵€佸缓璁娇鐢?`Open`銆乣Confirmed`銆乣Closed`銆?
## 9. 鐢熸垚瑙勫垯鎽樿

宸ュ叿浼氭寜浠ヤ笅榛樿瑙勫垯鐢熸垚 Excel 鍜?ARXML锛?
- Component package锛歚/ComponentTypes`
- Interface package锛歚/PortInterfaces`
- Data type package锛歚/DataTypes`
- MappingSet锛歚/ComponentTypes/MappingSets/DataMapping`
- 淇″彿鎺ュ彛锛氭瘡涓俊鍙蜂竴涓?SenderReceiverInterface銆?- 淇″彿绔彛锛氳緭鍏ヤ俊鍙风敓鎴?R-Port锛岃緭鍑轰俊鍙风敓鎴?P-Port銆?- Interface銆丳ort銆丏ataElement 榛樿鍏辩敤 `SignalName`锛屽榻?DaVinci 鎵嬪伐寤烘ā椋庢牸銆?- Boolean 绫诲瀷浣跨敤骞冲彴 Boolean 鍜?`<CATEGORY>BOOLEAN</CATEGORY>` 鍒濆€笺€?- Numeric 绫诲瀷浣跨敤 `<CATEGORY>VALUE</CATEGORY><V>...</V>`銆?- Enum/TextTable 绫诲瀷浣跨敤 CompuMethod TEXTTABLE锛涘垵鍊煎簲浼樺厛浣跨敤鏋氫妇绗﹀彿銆?
## 10. 浜や粯鐗╂竻鍗?
涓婃父浜や粯鏃跺缓璁悓鏃舵彁渚涳細

- 鏈枃妗ｅ～鍐欏悗鐨?`.docx`锛?- 鐩稿叧 SRD/璇﹁鏂囨。锛?- 濡傛湁 DaVinci 鎵嬪伐鏍蜂緥锛屾彁渚?`.arxml` 浣滀负 golden reference锛?- 濡傛湁鏈喅瀛楁锛屾槑纭礋璐ｄ汉鍜岃鍒掑叧闂椂闂淬€?
