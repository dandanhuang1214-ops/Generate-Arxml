# TRK SOA ARXML 鍙嶆帹锛氭渶灏忎氦浠樺绾︾己鍙?
鍙傝€冩枃浠讹細`C:\Users\20261\Downloads\Trk_Composition2.arxml`

鐩殑锛氫笉鏄畬鏁村鍒?TRK 鐨勬墍鏈夌鍙ｏ紝鑰屾槸鍙嶆帹鈥滀笂娓告枃妗ｆ渶灏戣缁欏摢浜涗俊鎭紝宸ュ叿鎵嶈兘绋冲畾鐢熸垚 SOA / 娣峰悎 ARXML鈥濄€?
## 1. TRK 鏆撮湶鍑虹殑鍏抽敭缁撴瀯

TRK 涓嶆槸鍗?Atomic SWC锛岃€屾槸鍏稿瀷鐨?Composition + 澶?Atomic SWC锛?
| 绫诲瀷 | 鍙嶆帹缁撴灉 |
| --- | --- |
| Composition SWC | `Trk_Composition` |
| Atomic SWC | `BOD_Trk_Atm`銆乣BOD_Trk_Enh`銆乣BOD_Trk_Soa` |
| Composition 鍐呭疄渚?| `Inst_Atm`銆乣Inst_Enh`銆乣Inst_Gen` |
| C/S Interface | 绾?10 涓?|
| S/R Interface | 绾?61 涓?|
| Assembly Connector | 绾?19 涓?|
| Delegation Connector | 绾?58 涓?|
| 浜嬩欢绫诲瀷 | InitEvent銆乀imingEvent銆丏ataReceivedEvent銆丱perationInvokedEvent |

杩欎釜缁撴瀯璇存槑锛歋OA 妯″紡涓嶈兘鍙弿杩扳€滄湇鍔″悕鈥濆拰鈥淪WC 鍚嶁€濓紝蹇呴』鏄庣‘ Composition 瀹炰緥銆佺鍙ｅ悕銆佹帴鍙ｅ悕銆佽繛鎺ョ鐐瑰拰 Runnable 瑙﹀彂瀵硅薄銆?
## 2. 褰撳墠妯℃澘蹇呴』琛ュ厖鐨勪俊鎭?
| 缂哄彛 | 涓轰粈涔堝繀椤昏ˉ | V1.6 涓殑澶勭悊 |
| --- | --- | --- |
| PrototypeName | Connector 寮曠敤 Composition 鍐呯殑瀹炰緥绔彛锛屼笉鏄洿鎺ュ紩鐢?SWC 鍚?| 缁勪欢娓呭崟鏂板 `PrototypeName` |
| InterfaceName 涓?PortName 鍒嗙 | 鍚屼竴涓?Interface 鍙澶氫釜绔彛澶嶇敤锛涚鍙ｅ悕甯稿甫瑙掕壊鍚庣紑 | 鏈嶅姟鎺ュ彛娓呭崟鎷嗘垚 `InterfaceName` / `PortName` |
| PortRole | C/S 涓?S/R 鐨?P/R 鏂瑰悜涓嶅悓锛屼笉鑳藉彧闈?Provider/Client 鏂囨湰鐚?| 鏈嶅姟鎺ュ彛娓呭崟淇濈暀 `PortRole` |
| Runnable TriggerObject | DataReceivedEvent / OperationInvokedEvent 闇€瑕佺粦瀹氱鍙ｆ垨 Operation | Runnable 琛ㄦ柊澧?`TriggerObject` |
| Connector Endpoint | Assembly/Delegation 闇€瑕佸疄渚嬬鍙ｏ紱SWC.Port 涓嶅绮剧‘ | Connector 琛ㄦ敼涓?`Instance.Port` |
| Record 瀛楁椤哄簭 | RecordElement 椤哄簭褰卞搷 ARXML 缁撴瀯 | 鏁版嵁绫诲瀷琛ㄦ柊澧?`FieldOrder` |
| Server QueueLength | TRK ServerComSpec 甯歌 `QUEUE-LENGTH=1` | 鏈嶅姟鎺ュ彛琛ㄦ柊澧?`QueueLength`锛屼负绌洪粯璁?1 |

## 3. 鏈€灏忔牱渚嬶細缁勪欢娓呭崟

| SWC鍚嶇О | PrototypeName | SWC瑙掕壊 | 閮ㄧ讲鍩?| 鏄惁Composition | 璇存槑 |
| --- | --- | --- | --- | --- | --- |
| BOD_Trk_Atm | Inst_Atm | 鍘熷瓙鏈嶅姟 | ZCU_R | false | 琛屾潕绠卞師瀛愭湇鍔?|
| BOD_Trk_Enh | Inst_Enh | 澧炲己鏈嶅姟 | ZCU_R | false | 琛屾潕绠卞寮烘湇鍔?|
| BOD_Trk_Soa | Inst_Gen | 鍦烘櫙/閫氱敤鏈嶅姟 | ZCU_R | false | 瀵瑰鑱氬悎鏈嶅姟 |
| Trk_Composition | Trk_Composition | Composition | ZCU_R | true | 琛屾潕绠辩粍鍚堢粍浠?|

## 4. 鏈€灏忔牱渚嬶細C/S 鏈嶅姟

| OwnerSWC | InterfaceName | PortName | PortRole | Communication | OperationName | TimeoutMs | QueueLength | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | rrTrkCtrl | rrTrkCtrl_Enh | Server | C/S | rrTrkCtrl |  | 1 | 鎻愪緵鎺у埗鏈嶅姟 |
| BOD_Trk_Atm | rrTrkCtrl | rrTrkCtrl_Atm | Client | C/S | rrTrkCtrl | 100 |  | 璋冪敤鎺у埗鏈嶅姟 |

## 5. 鏈€灏忔牱渚嬶細Operation 鍙傛暟

| InterfaceName | OperationName | ArgumentName | Direction | ValueType | InternalDataType | RecordType | RangeOrEnum | Unit | 璇存槑 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rrTrkCtrl | rrTrkCtrl | TrkCtrlCmd | IN | Enum | uint8 |  | 0=Stop, 1=Open, 2=Close |  | 鎺у埗鍛戒护 |
| rrTrkCtrl | rrTrkCtrl | ReturnCode | OUT | Enum | uint8 |  | 0=SUCCESS, 1=FAILURE |  | 杩斿洖鐮?|

## 6. 鏈€灏忔牱渚嬶細Runnable 涓庝簨浠?
| SWC | RunnableName | TriggerType | PeriodMs | TriggerObject | 璇存槑 |
| --- | --- | --- | --- | --- | --- |
| BOD_Trk_Enh | BOD_Trk_Enh_Init | Init |  |  | 鍒濆鍖?|
| BOD_Trk_Enh | BOD_Trk_Enh_Step | Periodic | 10 |  | 鍛ㄦ湡杩愯 |
| BOD_Trk_Enh | rrTrkCtrl | OperationInvoked |  | rrTrkCtrl.rrTrkCtrl | 鏈嶅姟璋冪敤瑙﹀彂 |
| BOD_Trk_Soa | Gen_NTF1 | DataReceived |  | ntfTrkActSts_Gen | 鎺ユ敹閫氱煡瑙﹀彂 |

## 7. 鏈€灏忔牱渚嬶細Connector

| ConnectorType | ProviderEndpoint | RequesterEndpoint | InterfaceName | 璇存槑 |
| --- | --- | --- | --- | --- |
| Assembly | Inst_Enh.rrTrkCtrl_Enh | Inst_Atm.rrTrkCtrl_Atm | rrTrkCtrl | Atm 璋冪敤 Enh |
| Delegation | Trk_Composition.rrTrkCtrl | Inst_Enh.rrTrkCtrl_Enh | rrTrkCtrl | Composition 瀵瑰鏆撮湶鎺у埗鏈嶅姟 |

## 8. 鍙嶆帹缁撹

V1.6 妯℃澘宸茬粡瓒冲浣滀负 SOA/娣峰悎閾捐矾鐨勭涓€鐗堣緭鍏ュ绾︺€傚畠姣?Excel 灏戝緢澶氬瓧娈碉紝浣嗕繚鐣欎簡 DaVinci 寤烘ā涓嶅彲缂虹殑閿氱偣锛?
- Composition 鍐呭疄渚嬪悕锛?- Interface / Port / Operation 涓夎€呭垎绂伙紱
- Runnable 瑙﹀彂瀵硅薄锛?- Assembly / Delegation 杩炴帴绔偣锛?- Record 瀛楁椤哄簭锛?- C/S ComSpec 鐨勫皯閲忓繀瑕侀厤缃€?
涓嬩竴姝ュ缓璁厛瀹炵幇 Contract Schema锛屼笉鐩存帴鏀?ARXML writer銆備篃灏辨槸鍏堣 `docx -> canonical JSON` 鑳借瘑鍒繖浜涘瓧娈碉紝鍐嶅仛 `contract -> excel`锛屾渶鍚庢墠鎵╁睍 `excel -> arxml`銆?
