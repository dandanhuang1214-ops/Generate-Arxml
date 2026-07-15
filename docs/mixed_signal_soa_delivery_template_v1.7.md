# ARXML 鎺ュ彛浜や粯鏂囨。妯℃澘

锛圕lassic AUTOSAR CP 路 淇″彿 + SOA / Sender-Receiver + Client-Server锛?
妯℃澘鐗堟湰锛歏1.7

## 浣跨敤璇存槑

鏈枃妗ｆ槸鈥滆缁嗚璁?鍔熻兘璁捐鈥濆埌 ARXML 鑷姩鐢熸垚宸ュ叿涔嬮棿鐨勪氦浠樺绾︺€傚綋鍓嶉樁娈电洰鏍囧緢鏄庣‘锛氬钩鏇?DaVinci Developer 涓?Classic AUTOSAR CP 鐨勬墜宸ュ缓妯″伐浣滐紝鐢熸垚 DaVinci 鍙鍏ャ€佸彲鍥炲瀵规瘮鐨?ARXML銆?
鏈ā鏉夸笉鐢ㄤ簬 Adaptive AUTOSAR锛屼笉鎻忚堪 SOME/IP Service Discovery銆丒xecution Manifest銆乤ra::com 绛夊唴瀹广€傚悗缁鏋滈渶瑕佹湇鍔￠儴缃叉垨浠ュお缃戠粦瀹氾紝浼氬彟璧锋墿灞曡〃锛屼笉濉炶繘褰撳墠绗竴鐗堛€?
涓婃父鍙渶瑕佸～鍐欏伐鍏锋棤娉曠ǔ瀹氭帹瀵肩殑涓氬姟淇℃伅锛?
- 鏈夊摢浜?SWC锛屼互鍙婂畠浠湪 Composition 閲岀殑瀹炰緥鍚嶏紱
- 鍝簺 Sender/Receiver 淇″彿瀛樺湪锛?- 鍝簺 Client/Server 绔彛瀛樺湪锛岃皝鎻愪緵锛岃皝璋冪敤锛?- Operation 鏈夊摢浜涘弬鏁帮紝鍙傛暟鏂瑰悜鏄粈涔堬紱
- Enum銆丩inear銆丷ecord 绛夋暟鎹被鍨嬬殑涓氬姟瀹氫箟锛?- Runnable 鎬庝箞瑙﹀彂锛?- Runnable 浣跨敤浜嗗摢浜涚鍙ｏ紱
- Composition 鍐呴儴 Assembly Connector 鍜屽閮?Delegation Connector 鎬庝箞杩炪€?
宸ュ叿鑷姩鐢熸垚锛?
- AUTOSAR 鍖呰矾寰勶紱
- ApplicationDataType / ImplementationDataType锛?- CompuMethod / DataConstr锛?- DataTypeMappingSet锛?- SenderReceiverInterface / ClientServerInterface锛?- P-Port / R-Port锛?- Sender/Receiver ComSpec锛?- Client/Server ComSpec锛?- Runnable Event锛?- Assembly / Delegation Connector锛?- UUID 浠ュ強 DaVinci 鍙嚜鍔ㄨˉ鍏ㄧ殑榛樿缁撴瀯銆?
濉啓鍘熷垯锛?
- 涓嶅～鍐欏畬鏁?AUTOSAR Ref 璺緞锛?- 涓嶅～鍐?Excel 鍏ㄩ儴 Sheet锛?- 涓嶅～鍐欏綋鍓嶉樁娈典笉鐢ㄧ殑鍙€夊瓧娈碉紱
- 鏂囨。閲屽啓浜嗕粈涔堬紝宸ュ叿灏辨寜浠€涔堢敓鎴愶紱宸ュ叿涓嶈兘鍙潬鎺ㄥ鐨勫唴瀹瑰繀椤昏繘鍏モ€滄湭鍐抽棶棰樷€濄€?
## 1. 椤圭洰淇℃伅琛?
> 涓嶆柊澧?CP/AP 瀛楁銆傚綋鍓嶉」鐩氨鏄?Classic AUTOSAR CP 鐢熸垚閾捐矾銆?
| 瀛楁 | 濉啓鍊?| 璇存槑 |
| --- | --- | --- |
| 椤圭洰/绯荤粺鍚嶇О |  | 渚嬪 Window / TRK / Wiper |
| 鐩爣 AUTOSAR 鐗堟湰 | 4-3-0 | 褰撳墠鎸?DaVinci R24-11 鍙鍏ョ粨鏋勭敓鎴?|
| 鐢熸垚妯″紡 | mixed_signal_soa | 宸ュ叿鍐呴儴 profile 鍚嶇О锛屽彲淇濇寔榛樿 |
| RootPackage | DaVinci 榛樿璺緞 | 閫氬父涓嶇敤濉紝宸ュ叿浣跨敤缁熶竴 DaVinci 椋庢牸璺緞 |
| 榛樿 Composition 鍚嶇О |  | 蹇呭～锛孲OA 绗竴鐗堝繀椤荤敓鎴?Composition |
| 闇€姹?璇﹁鏉ユ簮 |  | 鏂囨。鍚嶇О銆佺増鏈€佺珷鑺?|
| 濉啓浜?鏃ユ湡 |  | 鍙樻洿杩芥函鐢?|

## 2. SWC 涓?Composition 瀹炰緥琛?
姣忎竴琛屾弿杩颁竴涓?SWC 鎴栦竴涓?Composition銆侰onnector 寮曠敤鐨勬槸 Composition 鍐呴儴鐨勫疄渚嬬鍙ｏ紝鎵€浠?`PrototypeName` 蹇呴』鏄庣‘銆?
| SWC鍚嶇О | PrototypeName | SWC绫诲瀷 | 鏄惁Composition | 璇存槑 |
| --- | --- | --- | --- | --- |
| BOD_Trk_Atm | Inst_Atm | Atomic | false | 鍚庤儗闂ㄥ師瀛愭湇鍔?|
| BOD_Trk_Enh | Inst_Enh | Atomic | false | 鍚庤儗闂ㄥ寮烘湇鍔?|
| BOD_Trk_Soa | Inst_Gen | Atomic | false | 瀵瑰鑱氬悎鏈嶅姟 |
| Trk_Composition | Trk_Composition | Composition | true | 鍚庤儗闂ㄧ粍鍚堢粍浠?|

濉啓瑙勫垯锛?
- `SWC鍚嶇О`锛氱敓鎴?SWC-TYPE 鐨?SHORT-NAME銆?- `PrototypeName`锛氱敓鎴?Composition 鍐呯殑 SW-COMPONENT-PROTOTYPE 鍚嶇О銆?- `SWC绫诲瀷`锛氬綋鍓嶅缓璁彧鍐?`Atomic` 鎴?`Composition`銆?- `鏄惁Composition=true` 鐨勮鐢ㄤ簬鐢熸垚 Composition SWC銆?- SOA 绗竴鐗堝繀椤昏嚦灏戞湁涓€涓?Composition 琛屽拰涓€涓?Atomic 琛屻€?
## 3. S/R 淇″彿鎺ュ彛琛?
鏈〃鍙畾涔?Sender/Receiver Interface 鍜屾暟鎹被鍨嬫睜锛屼笉鐩存帴鍐冲畾鏌愪釜 SWC 涓婄敓鎴?P-Port 杩樻槸 R-Port銆傚疄闄呯鍙ｆ寕杞界敱鈥淩unnable Access 琛ㄢ€濆拰鈥淐onnector 琛ㄢ€濆叡鍚屽喅瀹氥€?
| No | 淇″彿鍚?| 鏁版嵁绫诲埆 | 搴旂敤鏁版嵁绫诲瀷 | 鍐呴儴鏁版嵁绫诲瀷 | 鍐呴儴鑼冨洿 | 鐗╃悊鑼冨洿 | 鍒嗚鲸鐜?| Offset | 鍗曚綅 | 鐘舵€佸€艰〃 | 鍒濆鍊?| 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ntfTrkActSts | Enum | App_TrkActSts | uint8 | 0-255 | 0-255 |  |  | No_Unit | 0=Idle, 1=Opening, 2=Closing | Idle | 鍚庤儗闂ㄥ姩浣滅姸鎬侀€氱煡 | SRD-001 |
| 2 | ntfTrkDutyRat | Value | App_DutyRat | uint8 | 0-255 | 0-100 | 0.3921568627 | 0 | % |  | 0 | 鍗犵┖姣旈€氱煡 | SRD-002 |
| 3 | vbTrkSleepPermit | Boolean | App_boolean | boolean | 0-1 | 0-1 |  |  | No_Unit |  | 0 | 浼戠湢鍏佽 | SRD-003 |

鏁版嵁瑙勫垯锛?
- `鏁版嵁绫诲埆=Enum` 鏃讹紝`鐘舵€佸€艰〃` 蹇呭～锛涚姸鎬佸€艰〃鍐欏灏戯紝宸ュ叿灏辩敓鎴愬灏戯紝涓嶈嚜鍔ㄨˉ鏋氫妇鍊笺€?- `Enum` 鐨?`鍐呴儴鑼冨洿` 鎸夋枃妗ｅ～鍐欑敓鎴?DataConstr锛屼笉鐢ㄥ己琛屾敼鎴愭灇涓惧疄闄呮渶灏?鏈€澶у€笺€?- `鏁版嵁绫诲埆=Value` 涓斿～鍐?`鍒嗚鲸鐜?Offset` 鏃讹紝鐢熸垚 LINEAR CompuMethod銆?- LINEAR 鐨?DataConstr 浣跨敤 `鍐呴儴鑼冨洿`锛孋ompuScale limit 浣跨敤 `鐗╃悊鑼冨洿`銆?- `鍗曚綅` 涓虹┖鏃跺伐鍏风粺涓€浣跨敤 `No_Unit`銆?- `搴旂敤鏁版嵁绫诲瀷` 寤鸿濉啓宸ュ叿鏈€缁堣鐢熸垚鐨?ADT 鍚嶇О锛屼緥濡?`App_DutyRat`锛涗笉瑕佹妸涓氬姟淇″彿鍚嶃€佹帴鍙ｅ悕銆両DT 鍚嶆贩鍦ㄤ竴璧枫€?- `鍐呴儴鏁版嵁绫诲瀷` 鏄?IDT 鍩虹绫诲瀷鎴?IDT Record 鍚嶏紝渚嬪 `uint8`銆乣uint16`銆乣boolean`銆乣Impl_TrkCmdRecord`銆?
## 4. C/S 鏈嶅姟绔彛琛?
姣忎竴琛屾弿杩颁竴涓?Client/Server 绔彛銆傚綋鍓嶉樁娈典笉濉啓 Timeout銆丵ueue 绛夊彲閫夊瓧娈点€?
| OwnerSWC | InterfaceName | PortName | PortRole | OperationName | 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | rrTrkCtrl | Pp_TrkCtrl | Server | rrTrkCtrl | 鎻愪緵鍚庤儗闂ㄦ帶鍒舵湇鍔?| SRD-101 |
| BOD_Trk_Atm | rrTrkCtrl | Rp_TrkCtrl | Client | rrTrkCtrl | 璋冪敤鍚庤儗闂ㄦ帶鍒舵湇鍔?| SRD-102 |

濉啓瑙勫垯锛?
- `OwnerSWC`锛氱鍙ｆ寕鍦ㄥ摢涓?SWC 涓娿€?- `InterfaceName`锛欳lientServerInterface 鍚嶇О锛屽彲琚涓鍙ｅ鐢ㄣ€?- `PortName`锛氱粍浠朵笂鐨勭鍙ｅ悕銆?- `PortRole=Server`锛氱敓鎴?P-Port + Server ComSpec銆?- `PortRole=Client`锛氱敓鎴?R-Port + Client ComSpec銆?- `OperationName`锛欳/S 绔彛蹇呴』濉啓銆?- 褰撳墠闃舵涓嶅湪鏈〃濉啓 `TimeoutMs`銆乣QueueLength`銆侀敊璇爜閰嶇疆绛夊彲閫夐」銆?
## 5. Operation 鍙傛暟琛?
姣忎竴涓?Operation 鍙傛暟涓€琛屻€備綘鍐?`IN` 灏辩敓鎴?IN 鍙傛暟锛屽啓 `OUT` 灏辩敓鎴?OUT 鍙傛暟锛屽啓 `INOUT` 灏辩敓鎴?INOUT 鍙傛暟锛涘伐鍏蜂笉鑷姩鑴戣ˉ ReturnCode銆?
| InterfaceName | OperationName | ArgumentName | Direction | 鏁版嵁绫诲埆 | 搴旂敤鏁版嵁绫诲瀷 | 鍐呴儴鏁版嵁绫诲瀷 | 鍐呴儴鑼冨洿 | 鐗╃悊鑼冨洿 | 鍒嗚鲸鐜?| Offset | 鍗曚綅 | 鐘舵€佸€艰〃 | 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rrTrkCtrl | rrTrkCtrl | TrkCtrlCmd | IN | Enum | App_TrkCtrlCmd | uint8 | 0-255 | 0-255 |  |  | No_Unit | 0=Stop, 1=Open, 2=Close | 鎺у埗鍛戒护 | SRD-111 |
| rrTrkCtrl | rrTrkCtrl | ReturnCode | OUT | Enum | App_ReturnCode | uint8 | 0-255 | 0-255 |  |  | No_Unit | 0=SUCCESS, 1=FAILURE | 杩斿洖缁撴灉 | SRD-112 |
| rrTrkCtrl | rrTrkCtrl | TrkCtrlPayload | IN | Record | App_TrkCtrlPayload | Impl_TrkCtrlPayload |  |  |  |  | No_Unit |  | 鎺у埗缁撴瀯浣撳弬鏁?| SRD-113 |

濉啓瑙勫垯锛?
- `Direction` 鍙啓 `IN`銆乣OUT`銆乣INOUT`銆?- `鏁版嵁绫诲埆=Record` 鏃讹紝`搴旂敤鏁版嵁绫诲瀷` 鍐?Record ADT锛宍鍐呴儴鏁版嵁绫诲瀷` 鍐?Record IDT锛屽苟鍦ㄢ€淩ecord 瀛楁琛ㄢ€濅腑灞曞紑瀛楁銆?- `鏁版嵁绫诲埆=Enum` 鏃讹紝`鐘舵€佸€艰〃` 蹇呭～銆?- `鏁版嵁绫诲埆=Value` 涓旀湁鍒嗚鲸鐜?Offset 鏃讹紝鎸?LINEAR 鐢熸垚銆?
## 6. Record 瀛楁琛?
Record 鍦?SOA 閲屼細澶ч噺鍑虹幇锛屾墍浠ョ粺涓€鐢ㄦ湰琛ㄥ睍寮€銆備笉瑕佹妸 Record 鍐欐垚涓€涓嚜鐒惰瑷€娈佃惤锛屼篃涓嶈鎶婂瓧娈靛杩涗竴涓崟鍏冩牸閲屻€?
| RecordTypeName | ImplementationRecordType | ElementPath | FieldOrder | FieldName | 鏁版嵁绫诲埆 | 搴旂敤鏁版嵁绫诲瀷 | 鍐呴儴鏁版嵁绫诲瀷 | 鍐呴儴鑼冨洿 | 鐗╃悊鑼冨洿 | 鍒嗚鲸鐜?| Offset | 鍗曚綅 | 鐘舵€佸€艰〃 | 鍒濆鍊?| 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| App_TrkCtrlPayload | Impl_TrkCtrlPayload | CallId | 1 | CallId | Value | App_uint16 | uint16 | 0-65535 | 0-65535 |  |  | No_Unit |  | 0 | 璋冪敤 ID |
| App_TrkCtrlPayload | Impl_TrkCtrlPayload | Cmd | 2 | Cmd | Enum | App_TrkCtrlCmd | uint8 | 0-255 | 0-255 |  |  | No_Unit | 0=Stop, 1=Open, 2=Close | Stop | 鎺у埗鍛戒护 |
| App_TrkCtrlPayload | Impl_TrkCtrlPayload | DutyRat | 3 | DutyRat | Value | App_DutyRat | uint8 | 0-255 | 0-100 | 0.3921568627 | 0 | % |  | 0 | 鍗犵┖姣?|

濉啓瑙勫垯锛?
- `RecordTypeName`锛歊ecord 鐨?ApplicationDataType 鍚嶃€?- `ImplementationRecordType`锛歊ecord 鐨?ImplementationDataType 鍚嶃€?- `ElementPath`锛氬瓧娈佃矾寰勶紝鏀寔宓屽锛屼緥濡?`SubRecord.FieldA`銆?- `FieldOrder`锛氬瓧娈甸『搴忥紝褰卞搷 ARXML 杈撳嚭椤哄簭锛屽繀椤荤ǔ瀹氥€?- Record 瀛楁閲岀殑 Enum銆乂alue銆丅oolean銆丩inear 瑙勫垯涓庝俊鍙疯〃涓€鑷淬€?- Record 鍒濆€煎繀椤绘寜瀛楁灞曞紑锛屽伐鍏风敓鎴?RECORD-VALUE-SPECIFICATION銆?
## 7. Runnable 姒傝琛?
鏈〃鍙弿杩?Runnable 鏈韩鍜岃Е鍙戞柟寮忥紝涓嶆弿杩扮鍙ｈ闂粏鑺傘€傜鍙ｈ闂啓鍦ㄤ笅涓€寮犺〃銆?
| 鎵€灞炵粍浠?| Runnable鍚?| 瑙﹀彂绫诲瀷 | 鍛ㄦ湡(ms) | 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | BOD_Trk_Enh_Init | Init |  | 涓婄數鍒濆鍖?| SRD-201 |
| BOD_Trk_Enh | BOD_Trk_Enh_Step | Periodic | 10 | 鍛ㄦ湡浠诲姟 | SRD-202 |
| BOD_Trk_Enh | rrTrkCtrl | OperationInvocation |  | C/S 鏈嶅姟琚皟鐢ㄦ椂瑙﹀彂 | SRD-203 |

瑙﹀彂绫诲瀷瑙勫垯锛?
- `Init`锛氫笂鐢靛垵濮嬪寲銆?- `Periodic`锛氬懆鏈熻Е鍙戯紝蹇呴』濉啓鍛ㄦ湡銆?- `OperationInvocation`锛歋erver 绔?Operation 琚皟鐢ㄦ椂瑙﹀彂銆?- 褰撳墠绗竴鐗堝厛涓嶅己鎺?`DataReception`锛涘鏋滄枃妗ｅ啓浜嗭紝鍏堣繘鍏?gap report 鎴栧悗缁墿灞曘€?
## 8. Runnable Access 琛?
鏈〃鎻忚堪 Runnable 瀹為檯浣跨敤鍝簺绔彛銆傚綋鍓?C/S 绔彛璁块棶璇箟鍙娇鐢ㄤ竴绉嶏細`InvokeOperation`銆?
| 鎵€灞炵粍浠?| Runnable鍚?| AccessType | 淇″彿/绔彛鍚?| OperationName | 璇存槑 |
| --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | BOD_Trk_Enh_Step | DataRead | Rp_TrkActSts |  | 璇诲彇 S/R 杈撳叆 |
| BOD_Trk_Enh | BOD_Trk_Enh_Step | DataWrite | Pp_TrkDutyRat |  | 鍐?S/R 杈撳嚭 |
| BOD_Trk_Enh | rrTrkCtrl | InvokeOperation | Pp_TrkCtrl | rrTrkCtrl | Server Runnable 缁戝畾琚皟鐢ㄧ殑 Operation |
| BOD_Trk_Atm | BOD_Trk_Atm_Step | InvokeOperation | Rp_TrkCtrl | rrTrkCtrl | Client Runnable 鍛ㄦ湡鍐呰皟鐢?Operation |

濉啓瑙勫垯锛?
- `DataRead`锛氳 Runnable 璇诲彇涓€涓?S/R R-Port銆?- `DataWrite`锛氳 Runnable 鍐欎竴涓?S/R P-Port銆?- `InvokeOperation`锛氳 Runnable 鍏宠仈涓€涓?C/S Operation銆?- 瀵?Server 绔紝`InvokeOperation` 涓?`Runnable 姒傝琛╜ 涓?`瑙﹀彂绫诲瀷=OperationInvocation` 閰嶅悎锛岀敓鎴?OperationInvokedEvent銆?- 瀵?Client 绔紝`InvokeOperation` 琛ㄧず鍛ㄦ湡 Runnable 涓皟鐢?required operation锛涘綋鍓嶆ā鏉跨粺涓€鐢ㄨ繖涓瘝琛ㄨ揪 C/S Operation 浣跨敤鍏崇郴銆?- 濡傛灉娌℃湁鍐欐煇涓?access锛屽伐鍏峰氨涓嶇敓鎴愯 Runnable 瀵瑰簲璁块棶鐐癸紝涓嶇寽銆?
## 9. Connector 琛?
SOA 绗竴鐗堝繀椤荤敓鎴?Composition锛屽洜姝?Connector 琛ㄦ槸蹇呭～琛ㄣ€侫ssembly 鍜?Delegation 鏀惧湪鍚屼竴寮犺〃閲屻€?
Endpoint 缁熶竴鍐欐垚锛?
- Composition 鍐呴儴瀹炰緥绔彛锛歚PrototypeName.PortName`
- Composition 瀵瑰绔彛锛歚CompositionName.PortName`

| ConnectorType | ProviderEndpoint | RequesterEndpoint | InterfaceName | 璇存槑 | RequirementId/Source |
| --- | --- | --- | --- | --- | --- |
| Assembly | Inst_Enh.Pp_TrkCtrl | Inst_Atm.Rp_TrkCtrl | rrTrkCtrl | Atm 璋冪敤 Enh 鎺у埗鏈嶅姟 | SRD-301 |
| Assembly | Inst_Enh.Pp_TrkDutyRat | Inst_Gen.Rp_TrkDutyRat | TrkDutyRat | Enh 閫氱煡 Gen | SRD-302 |
| Delegation | Trk_Composition.Pp_TrkCtrl | Inst_Enh.Pp_TrkCtrl | rrTrkCtrl | 瀵瑰鏆撮湶 Server 鏈嶅姟 | SRD-303 |
| Delegation | Trk_Composition.Rp_TrkCtrl | Inst_Atm.Rp_TrkCtrl | rrTrkCtrl | 瀵瑰鏆撮湶 Client 渚濊禆 | SRD-304 |

濉啓瑙勫垯锛?
- `Assembly`锛欳omposition 鍐呴儴涓や釜 prototype 涔嬮棿杩炴帴銆?- `Delegation`锛欳omposition 澶栭儴绔彛涓庡唴閮?prototype 绔彛杩炴帴銆?- C/S 涓?S/R 閮戒娇鐢ㄥ悓涓€寮?Connector 琛ㄣ€?- `ProviderEndpoint` 姘歌繙鍐欐彁渚涙柟绔彛锛歋/R Sender P-Port 鎴?C/S Server P-Port銆?- `RequesterEndpoint` 姘歌繙鍐欎娇鐢ㄦ柟绔彛锛歋/R Receiver R-Port 鎴?C/S Client R-Port銆?- 濡傛灉涓婃父涓嶇‘瀹氭煇涓?Delegation 鏄惁闇€瑕佹毚闇诧紝蹇呴』鍐欏叆鈥滄湭鍐抽棶棰樷€濓紝宸ュ叿涓嶈嚜鍔ㄧ寽鍏ㄩ儴鏆撮湶銆?
## 10. 鏈喅闂琛?
宸ュ叿鏃犳硶鍙潬鎺ㄥ鐨勪俊鎭繀椤昏繘鍏ユ湰琛紝涓嶈兘闈欓粯缂栭€犮€?
| 缂栧彿 | 瀛楁/瀵硅薄 | 闂鎻忚堪 | 寤鸿榛樿鍊?| 璐熻矗浜?| 鐘舵€?| 鍏抽棴缁撹 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  | Open |  |

鐘舵€佸缓璁細

- `Open`锛氬緟纭锛?- `Confirmed`锛氬凡纭锛屽緟鍚屾杩涙枃妗ｏ紱
- `Closed`锛氬凡鍏抽棴銆?
## 11. 涓嶉渶瑕佷笂娓稿～鍐欑殑鍐呭

浠ヤ笅鍐呭鐢卞伐鍏风敓鎴愶紝涓嶅缓璁汉宸ョ淮鎶わ細

- AUTOSAR PackagePath锛?- InterfaceRef锛?- DataElementRef锛?- ApplicationDataTypeRef锛?- ImplementationDataTypeRef锛?- DataTypeMappingSet 璺緞锛?- ComSpecKind锛?- Server/Client ComSpec 榛樿缁撴瀯锛?- 瀹屾暣 Connector 璺緞锛?- UUID锛?- DaVinci 鑷姩琛ュ叏鐨勯粯璁?InvalidationPolicy / SWC-Implementation 绛夌粨鏋勩€?
## 12. V1.7 鐩告瘮 V1.6 鐨勫彉鍖?
| 鐗堟湰 | 鏃ユ湡 | 淇敼浜?| 淇敼璇存槑 |
| --- | --- | --- | --- |
| V1.7 | 2026-07-15 | Codex | 鏀舵暃涓?Classic AUTOSAR CP Developer 骞虫浛妯℃澘锛涢」鐩俊鎭〃涓嶆柊澧?CP/AP 瀛楁锛汼OA 绗竴鐗堝繀椤荤敓鎴?Composition锛汣onnector 鏀寔 Assembly/Delegation锛涘幓鎺?Timeout/Queue 绛夊彲閫夊瓧娈碉紱C/S Runnable Access 缁熶竴浣跨敤 InvokeOperation锛汻ecord 瀛楁琛ㄦ寜 SOA 楂橀鍦烘櫙閲嶅啓 |
| V1.6 | 2026-07-14 | Codex | 鍩轰簬 TRK SOA ARXML 鍙嶆帹锛屾柊澧?PrototypeName锛涙媶鍒?InterfaceName/PortName锛涜ˉ鍏?Runnable TriggerObject锛汣onnector Endpoint 鏀逛负 Instance.Port锛汻ecord 瀛楁鏀逛负閫愯鏈夊簭鎻忚堪 |
