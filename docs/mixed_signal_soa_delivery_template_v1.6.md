# ARXML 鎺ュ彛浜や粯鏂囨。妯℃澘

锛堜俊鍙?+ SOA 娣峰悎妯″紡 / Signal + Client-Server锛?
妯℃澘鐗堟湰锛歏1.6

## 浣跨敤璇存槑

鏈枃妗ｆ槸鈥滆璁?鍔熻兘璁捐鈥濆埌 ARXML 鑷姩鐢熸垚宸ュ叿涔嬮棿鐨勪氦浠樺绾︺€傚畠鐨勭洰鏍囦笉鏄涓婃父鎵嬪伐濉啓 AUTOSAR 鍏ㄨ矾寰勶紝涔熶笉鏄妸 Excel 鐨勬墍鏈?Sheet 鎼繘 Word锛岃€屾槸鍙～鍐欏伐鍏锋棤娉曠ǔ瀹氭帹瀵肩殑涓氬姟淇℃伅銆?
涓婃父闇€瑕佸～鍐欙細

- 鏈夊摢浜?SWC锛屼互鍙婂畠浠湪 Composition 閲岀殑瀹炰緥鍚嶏紱
- 鍝簺淇″彿杈撳叆/杈撳嚭锛屽摢浜涙湇鍔＄敱璋佹彁渚涖€佺敱璋佽皟鐢紱
- C/S Operation 鐨勫弬鏁般€佹柟鍚戙€佽繑鍥炲€硷紱
- Enum / Record 鐨勪笟鍔″畾涔夛紱
- Runnable 鐨勮Е鍙戞柟寮忥紱
- Composition 鍐呴儴杩炴帴鍜屽澶栨毚闇插叧绯汇€?
宸ュ叿鑷姩鐢熸垚锛?
- AUTOSAR 鍖呰矾寰勶紱
- PortInterface 璺緞锛?- ApplicationDataType / ImplementationDataType锛?- CompuMethod / DataConstr锛?- DataTypeMappingSet锛?- P-Port / R-Port锛?- Sender/Receiver ComSpec锛?- Client/Server ComSpec锛?- Runnable Event锛?- Assembly / Delegation Connector锛?- UUID 浠ュ強 DaVinci 鍙嚜鍔ㄨˉ鍏ㄧ殑榛樿缁撴瀯銆?
濉啓鍥句緥锛氬繀濉?/ 鍙€?/ 宸ュ叿鐢熸垚銆傝〃鏍间腑鏈爣鍙€夌殑瀛楁锛岄粯璁ゆ寜蹇呭～澶勭悊銆?
## 1. 椤圭洰鍩烘湰淇℃伅

| 瀛楁 | 濉啓鍊?| 璇存槑 |
| --- | --- | --- |
| 椤圭洰/绯荤粺鍚嶇О |  | 渚嬪 Window / TRK / Wiper |
| 鐩爣 AUTOSAR 鐗堟湰 | 4-3-0 | 宸ュ叿榛樿鎸?DaVinci 4.3 鍏煎缁撴瀯鐢熸垚 |
| 鐢熸垚妯″紡 | mixed_signal_soa | 宸ュ叿榛樿鍊?|
| RootPackage | DaVinci 榛樿璺緞 | 涓嶉渶瑕佹瘡寮犺〃閲嶅濉啓 |
| 榛樿 Composition 鍚嶇О |  | 澶?SWC 闆嗘垚鏃跺～鍐欙紱绾?Atomic 鍙┖ |
| 榛樿 MappingSet | /ComponentTypes/MappingSets/DataMapping | 宸ュ叿榛樿鍊?|
| 闇€姹?璇﹁鏉ユ簮 |  | 鏂囨。鍚嶇О銆佺増鏈€佺珷鑺?|
| 濉啓浜?鏃ユ湡 |  |  |

## 2. 缁勪欢娓呭崟

鍙～鍐欑湡瀹炵粍浠躲€佷笟鍔¤鑹插拰 Composition 鍐呭疄渚嬪悕锛屼笉濉啓 AUTOSAR 鍖呰矾寰勩€?
| SWC鍚嶇О | PrototypeName | SWC瑙掕壊 | 閮ㄧ讲鍩?| 鏄惁Composition | 璇存槑 |
| --- | --- | --- | --- | --- | --- |
| BOD_Trk_Atm | Inst_Atm | 鍘熷瓙鏈嶅姟 | ZCU_R | false | 琛屾潕绠卞師瀛愭湇鍔?|
| BOD_Trk_Enh | Inst_Enh | 澧炲己鏈嶅姟 | ZCU_R | false | 琛屾潕绠卞寮烘湇鍔?|
| BOD_Trk_Soa | Inst_Gen | 鍦烘櫙/閫氱敤鏈嶅姟 | ZCU_R | false | 瀵瑰鏈嶅姟鑱氬悎 |
| Trk_Composition | Trk_Composition | Composition | ZCU_R | true | 琛屾潕绠辩粍鍚堢粍浠?|

濉啓瑙勫垯锛?
- `SWC鍚嶇О` 鏄?DaVinci 涓笇鏈涚湅鍒扮殑 SWC SHORT-NAME銆?- `PrototypeName` 鏄 SWC 鏀捐繘 Composition 鍚庣殑瀹炰緥鍚嶏紝渚嬪 `Inst_Atm`銆侰onnector 寮曠敤鐨勬槸瀹炰緥绔彛锛屾墍浠ヨ繖涓瓧娈靛緢鍏抽敭銆?- 濡傛灉 `PrototypeName` 涓虹┖锛屽伐鍏峰彲榛樿鐢熸垚 `Inst_<瑙掕壊鎴栫煭鍚?`锛屼絾寤鸿涓婃父鏄庣‘濉啓銆?- `鏄惁Composition` 鍙┖锛涘伐鍏峰彲鏍规嵁 `SWC瑙掕壊=Composition` 鎺ㄥ銆?
## 3. 鏈嶅姟鎺ュ彛娓呭崟

姣忎竴琛屾弿杩颁竴涓鍙ｃ€傛敞鎰忥細鎺ュ彛鍚嶃€佺鍙ｅ悕銆丱peration 鍚嶅繀椤诲垎寮€锛屼笉鑳芥贩鎴愪竴涓€滄湇鍔″悕鈥濄€?
| OwnerSWC | InterfaceName | PortName | PortRole | Communication | OperationName | TimeoutMs | QueueLength | RequirementId | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | rrTrkCtrl | rrTrkCtrl_Enh | Server | C/S | rrTrkCtrl |  | 1 |  | 鎻愪緵琛屾潕绠辨帶鍒舵湇鍔?|
| BOD_Trk_Atm | rrTrkCtrl | rrTrkCtrl_Atm | Client | C/S | rrTrkCtrl | 100 |  |  | 璋冪敤琛屾潕绠辨帶鍒舵湇鍔?|
| BOD_Trk_Enh | ntfTrkActSts | ntfTrkActSts_Enh | Sender | S/R | / |  |  |  | 閫氱煡琛屾潕绠卞姩浣滅姸鎬?|
| BOD_Trk_Soa | ntfTrkActSts | ntfTrkActSts_Gen | Receiver | S/R | / |  |  |  | 鎺ユ敹琛屾潕绠卞姩浣滅姸鎬?|

绔彛瑙掕壊瑙勫垯锛?
| PortRole | Communication | 鐢熸垚缁撴灉 |
| --- | --- | --- |
| Sender | S/R | P-Port + NONQUEUED-SENDER-COM-SPEC |
| Receiver | S/R | R-Port + NONQUEUED-RECEIVER-COM-SPEC |
| Server | C/S | P-Port + SERVER-COM-SPEC |
| Client | C/S | R-Port + CLIENT-COM-SPEC |

濉啓瑙勫垯锛?
- `OwnerSWC` 琛ㄧず杩欎釜绔彛鎸傚湪鍝釜 SWC 涓娿€?- `InterfaceName` 鏄?PortInterface 鍚嶏紝澶氫釜绔彛鍙互澶嶇敤鍚屼竴涓?InterfaceName銆?- `PortName` 鏄粍浠朵笂鐨勭鍙ｅ悕锛屽厑璁稿甫 `_Atm`銆乣_Enh`銆乣_Gen` 绛夎鑹插悗缂€銆?- C/S 绔彛蹇呴』濉啓 `OperationName`锛汼/R 绔彛濉啓 `/`銆?- `QueueLength` 浠?Server ComSpec 浣跨敤锛涗负绌烘椂宸ュ叿榛樿 `1`銆?- `TimeoutMs` 浠?Client ComSpec 浣跨敤锛涗负绌烘椂涓嶅己鍒惰緭鍑恒€?
## 4. Operation 鍙傛暟琛?
涓嶈鎶婃墍鏈夊弬鏁板杩涙湇鍔¤〃鐨勪竴涓崟鍏冩牸銆傛瘡涓弬鏁颁竴琛岋紝宸ュ叿鎹鐢熸垚 Argument 鍜屾暟鎹被鍨嬨€?
| InterfaceName | OperationName | ArgumentName | Direction | ValueType | InternalDataType | RecordType | RangeOrEnum | Unit | RequirementId | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rrTrkCtrl | rrTrkCtrl | TrkCtrlCmd | IN | Enum | uint8 |  | 0=Stop, 1=Open, 2=Close |  |  | 鎺у埗鍛戒护 |
| rrTrkCtrl | rrTrkCtrl | ReturnCode | OUT | Enum | uint8 |  | 0=SUCCESS, 1=FAILURE |  |  | 杩斿洖鍊?|
| rrTrkCinchCmd | rrTrkCinchCmd | TrkCmd | IN | Enum | uint8 |  | 0=NoAction, 1=Cinch |  |  | 鍚稿悎鍛戒护 |
| rrTrkCinchCmd | rrTrkCinchCmd | DutyRat | IN | Value | uint8 |  | 0-100 | % |  | 鍗犵┖姣?|

濉啓瑙勫垯锛?
- `Direction` 鏀寔 `IN`銆乣OUT`銆乣INOUT`銆?- `ValueType=Enum` 鏃讹紝`RangeOrEnum` 蹇呴』濉啓鏋氫妇鏄犲皠銆?- `ValueType=Value` 鏃讹紝`RangeOrEnum` 濉暟鍊艰寖鍥达紝渚嬪 `0-255`銆?- `ValueType=Boolean` 鏃讹紝`InternalDataType` 寤鸿鍐?`boolean`锛岃寖鍥村彲绌烘垨鍐?`0-1`銆?- `RecordType` 涓嶄负绌鸿〃绀鸿鍙傛暟寮曠敤 Record锛汻ecord 瀛楁鍦ㄢ€滄暟鎹被鍨嬭ˉ鍏呰〃鈥濅腑灞曞紑銆?
## 5. 鏁版嵁绫诲瀷琛ュ厖琛?
鍙湁澶嶆潅绫诲瀷銆佸鐢ㄧ被鍨嬫垨闇€瑕佷汉宸ュ懡鍚嶆椂鎵嶅～鍐欍€傛櫘閫?`uint8/uint16/uint32/boolean` 鍙敱宸ュ叿鎺ㄥ涓哄叡浜熀纭€ ADT/IDT銆?
| TypeName | TypeKind | BaseType | FieldOrder | FieldName | FieldType | RangeOrEnum | Unit | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TrkCtrlCmd | Enum | uint8 |  |  |  | 0=Stop, 1=Open, 2=Close |  | 琛屾潕绠辨帶鍒跺懡浠?|
| ReturnCode | Enum | uint8 |  |  |  | 0=SUCCESS, 1=FAILURE |  | 杩斿洖鐮?|
| TrkCtrlRecord | Record |  | 1 | CallID | uint64 | 0-4294967295 |  | 璋冪敤婧?|
| TrkCtrlRecord | Record |  | 2 | TimeStamp | uint64 | 0-4294967295 | ms | 鏃堕棿鎴?|
| TrkCtrlRecord | Record |  | 3 | TrkCtrlCmd | TrkCtrlCmd |  |  | 鎺у埗鍛戒护 |

濉啓瑙勫垯锛?
- `TypeKind` 鏀寔 `Primitive`銆乣Enum`銆乣Record`銆?- `Record` 蹇呴』閫愬瓧娈靛～鍐欙紝涓?`FieldOrder` 涓嶈兘閲嶅銆?- Record 瀛楁椤哄簭浼氬奖鍝?ARXML 杈撳嚭锛屼笉鑳藉彧鍐欐垚涓€娈佃嚜鐒惰瑷€銆?- `Enum` 鐨?`RangeOrEnum` 浣跨敤 `0=SYMBOL, 1=SYMBOL` 鏍煎紡銆?
## 6. Runnable 涓庤Е鍙?
鎻忚堪 Runnable 鐨勮Е鍙戞柟寮忋€備笉瑕佺敤鍥剧墖鎴栧祵鍏ュ璞°€?
| SWC | RunnableName | TriggerType | PeriodMs | TriggerObject | RequirementId | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | BOD_Trk_Enh_Init | Init |  |  |  | 涓婄數鍒濆鍖?|
| BOD_Trk_Enh | BOD_Trk_Enh_Step | Periodic | 10 |  |  | 鍛ㄦ湡浠诲姟 |
| BOD_Trk_Enh | rrTrkCtrl | OperationInvoked |  | rrTrkCtrl.rrTrkCtrl |  | 鏈嶅姟璋冪敤瑙﹀彂 |
| BOD_Trk_Soa | Gen_NTF1 | DataReceived |  | ntfTrkActSts_Gen |  | 鎺ユ敹閫氱煡鍚庤Е鍙?|

瑙﹀彂绫诲瀷锛?
- `Init`锛氫笂鐢靛垵濮嬪寲锛?- `Periodic`锛氬懆鏈熻Е鍙戯紱
- `OperationInvoked`锛欳/S 鏈嶅姟琚皟鐢ㄦ椂瑙﹀彂锛宍TriggerObject` 寤鸿鍐?`InterfaceName.OperationName`锛?- `DataReceived`锛氭帴鏀?S/R 淇″彿瑙﹀彂锛宍TriggerObject` 寤鸿鍐?`PortName` 鎴?`PortName.DataElement`銆?
## 7. 淇″彿鎺ュ彛娓呭崟

鐢ㄤ簬娣峰悎妯″紡涓殑鏅€?Sender/Receiver 淇″彿銆傜函 SOA 鏈嶅姟鍙笉濉€?
| SignalDirection | SignalName | OwnerSWC | Peer | ValueType | InternalDataType | PhysicalRange | EnumValues | InitValue | PeriodMs | RequirementId | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SignalIn | VbINP_CAN_WindowLock_flg | BOD_PWNR_Enh | BCM | Boolean | boolean | 0-1 |  | 0 | 10 |  | 杞︾獥閿佽緭鍏?|
| SignalOut | VbOUT_TRK_SleepPermit_flg | BOD_PWNR_Enh | BCM | Boolean | boolean | 0-1 |  | 0 | 10 |  | 浼戠湢鍏佽杈撳嚭 |
| SignalOut | VeOUT_WinMode | BOD_PWNR_Enh | BCM | Value | uint8 | 0-255 |  | 0 | 10 |  | 杞︾獥妯″紡 |

濉啓瑙勫垯锛?
- `SignalIn` 鐢熸垚 R-Port銆?- `SignalOut` 鐢熸垚 P-Port銆?- `ValueType=Enum` 鏃舵墠鐢熸垚 TEXTTABLE 鏋氫妇锛屼笖蹇呴』濉啓 `EnumValues`銆?- `ValueType=Value/uint8/uint16/uint32` 鏃剁敓鎴愬叡浜熀纭€绫诲瀷鍜?IDENTICAL CompuMethod锛屼笉鍥犱负鈥滅姸鎬佸畾涔夎〃鈥濋噷鏈夋枃瀛楀氨鑷姩鍙樻灇涓俱€?- `InitValue` 瀵?Boolean 寤鸿鍐?`0/1` 鎴?`true/false`锛涘 Value 鍐欐暟鍊硷紱瀵?Enum 鍐欑鍙峰悕銆?
## 8. Composition 杩炴帴鍏崇郴

鍙～鍐欎笟鍔¤繛鎺ュ叧绯伙紝涓嶅～鍐?AUTOSAR 瀹屾暣璺緞銆侲ndpoint 缁熶竴鍐欐垚 `InstanceName.PortName`锛汣omposition 澶栭儴绔彛鍐欐垚 `CompositionName.PortName`銆?
| ConnectorType | ProviderEndpoint | RequesterEndpoint | InterfaceName | RequirementId | 璇存槑 |
| --- | --- | --- | --- | --- | --- |
| Assembly | Inst_Enh.rrTrkCtrl_Enh | Inst_Atm.rrTrkCtrl_Atm | rrTrkCtrl |  | Atm 璋冪敤 Enh |
| Assembly | Inst_Enh.ntfTrkActSts_Enh | Inst_Gen.ntfTrkActSts_Gen | ntfTrkActSts |  | Enh 閫氱煡 Gen |
| Delegation | Trk_Composition.rrTrkCtrl | Inst_Enh.rrTrkCtrl_Enh | rrTrkCtrl |  | 瀵瑰鏆撮湶鎺у埗鏈嶅姟 |
| Delegation | Trk_Composition.ntfTrkActSts | Inst_Gen.ntfTrkActSts_Gen | ntfTrkActSts |  | 瀵瑰鏆撮湶閫氱煡绔彛 |

濉啓瑙勫垯锛?
- `Assembly` 琛ㄧず Composition 鍐呴儴瀹炰緥涔嬮棿杩炴帴銆?- `Delegation` 琛ㄧず Composition 澶栭儴绔彛涓庡唴閮ㄥ疄渚嬬鍙ｈ繛鎺ャ€?- `ProviderEndpoint` 瀵瑰簲鎻愪緵鏂?P-Port / Server Port銆?- `RequesterEndpoint` 瀵瑰簲浣跨敤鏂?R-Port / Client Port銆?- C/S 涓?S/R 閮戒娇鐢ㄥ悓涓€寮犺繛鎺ュ叧绯昏〃銆?- 濡傛灉涓婃父鏃犳硶纭澶栭儴鏆撮湶鍏崇郴锛屽繀椤诲啓鍏モ€滄湭鍐抽棶棰樷€濓紝宸ュ叿涓嶈兘闈欓粯鐚滄祴鎵€鏈?Delegation銆?
## 9. 鏈喅闂

宸ュ叿鏃犳硶鍙潬鎺ㄥ鐨勪俊鎭繀椤昏繘鍏ユ湭鍐抽棶棰橈紝涓嶈兘闈欓粯缂栭€犮€?
| 缂栧彿 | 瀛楁/瀵硅薄 | 闂鎻忚堪 | 寤鸿榛樿鍊?| 璐熻矗浜?| 鐘舵€?| 鍏抽棴缁撹 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  | Open |  |

鐘舵€佸缓璁細

- `Open`锛氬緟纭锛?- `Confirmed`锛氬凡纭锛屽緟鍚屾锛?- `Closed`锛氬凡鍏抽棴銆?
## 10. 涓嶉渶瑕佷笂娓稿～鍐欑殑鍐呭

浠ヤ笅鍐呭鐢卞伐鍏风敓鎴愶紝涓嶅缓璁汉宸ョ淮鎶わ細

- AUTOSAR PackagePath锛?- InterfaceRef锛?- DataElementRef锛?- ApplicationDataTypeRef锛?- ImplementationDataTypeRef锛?- DataTypeMappingSet 璺緞锛?- ComSpecKind锛?- 瀹屾暣 Connector 璺緞锛?- UUID锛?- DaVinci 鑷姩琛ュ叏鐨勯粯璁?InvalidationPolicy / SWC-Implementation 绛夌粨鏋勩€?
## 11. V1.6 鐩告瘮 V1.5 鐨勫彉鍖?
| 鐗堟湰 | 鏃ユ湡 | 淇敼浜?| 淇敼璇存槑 |
| --- | --- | --- | --- |
| V1.6 | 2026-07-14 | Codex | 鍩轰簬 TRK SOA ARXML 鍙嶆帹锛屾柊澧?PrototypeName锛涙媶鍒?InterfaceName/PortName锛涜ˉ鍏?Runnable TriggerObject锛汣onnector Endpoint 鏀逛负 Instance.Port锛汻ecord 瀛楁鏀逛负閫愯鏈夊簭鎻忚堪 |
| V1.5 | 2026-07-14 | Codex | 鏂板淇″彿 + SOA 娣峰悎妯℃澘锛岃鐩栨湇鍔°€佸弬鏁般€佹暟鎹被鍨嬨€丷unnable銆丆onnector |
