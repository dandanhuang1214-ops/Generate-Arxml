信号名
数据类型
值定义
作用描述
HWA 硬件输入
VbINP_HWA_FWiperPark_flg
boolean
0x00：Invalid
0x01：Valid
前雨刮电机 Park 位硬线信号（滤波30ms），用于归位判断、周期计数、RLS 同步
VbINP_HWA_RWiperPark_flg
boolean
0x00：Invalid
0x01：Valid
后雨刮电机 Park 位信号，后雨刮归位控制依据
VbINP_HWA_DCDCModeSts_sig
uint8
0x0: Standby
0x1: Buck
0x2: UdcLnkDischarge
0x3: Failure
直流电源模式
VbINP_HWA_FWiperMistSts_flg
boolean
0x00：Invalid
0x01：Valid
前雨刮点刮硬件开关，需持续有效 T≥100ms 后响应

VbINP_HWA_WasherLiquidLow_flg
boolean
0x00:Inactive
0x01:Active
清洗液液位传感器，持续30s低电平触发报警，6s恢复消警
VbINP_HWA_IGNFeedBackIN_flg
boolean
0x00：Invalid
0x01：Valid
IGN 点火反馈，Limphome 使能条件之一
VbINP_HWA_RLSTimeOut_flg
boolean
0x0:正常
0x1:丢失
RLS 光传感器 LIN 通信超时，触发 AUTO 模式低速归位停止
VeINP_HWA_Voltage_100mV
uint16
90~160（9~16V 正常范围）
车载电压采样（单位100mV），越限时禁止所有雨刮动作
CAN 总线输入 — 前雨刮/洗涤相关
VeINP_CAN_ETRSFrontWiperSwitchStatus_sig
uint8
0x0:OFF
0x1:Auto
0x2:Low
0x3:High
0x4~0x7: Reserved
前雨刮 ETRS 拨杆档位，主模式触发源
VeINP_CAN_ETRSFrontWasherSwitchStatus_sig
uint8
0x0:OFF
0x1:MIST
0x2:Front Washer
0x3:Reserved
前洗涤 ETRS 拨杆，0x2触发前洗涤，0x1触发点刮（T≥100ms）
VeINP_CAN_ICMWiprWashVoiceReq_sig
uint8
0x0: Inactive
0x1: Active
0x2~0x3: Reserved
语音洗涤请求（事件型），3s超时自动关闭
VbINP_CAN_ICMMaintenanceReq_flg
boolean
0x0:No Request
0x1:Request
前雨刮维护模式请求，跳变有效（进入/退出切换）
VeINP_CAN_ICMRainSensitivity_sig

uint8
0x0:No Request
0x1: More Insensitive
0x2: Insensitive
0x3: Normal
0x4: Sensitive
0x5: More Sensitive(reserve)
0x6: Most Sensitive(reserve)
0x7: Most Insensitive(reserve)
ICM 下发 Auto 档灵敏度设置，写 EEPROM 持久化，断电记忆
VeINP_CAN_RLSRQWiperSPD_sig
uint8
0:No / 1:LS / 2:HS
RLS 雨量速度请求 V1（保留兼容）
VeINP_CAN_RLSRQWiperSPDV2_sig
uint8
0x0: No wiping
0x1: Low Speed
0x2~0xD: Not Used
0xE: High Speed
0xF: Invalid Value
RLS 雨量速度请求 V2（主用），LIN→CAN 路由
VbINP_CAN_RLSFaultRain_flg
boolean
0x0: Normal Status
0x1: Status Fault
RLS 故障标志，AUTO 模式低速完成当前周期后停止，上报故障状态
VeINP_CAN_IDMFwiperReq_sig
uint8
0x0:NO Request
0x1:MIST
0x2:LS speed
0x3: HS Speed
0x4: Washwipe
0x5-0x7:Reserved
智驾 IDM 前雨刮请求，RLS 与 IDM 冲突时优先 RLS
VeINP_CAN_ICMWashModeSwSts_sig
uint8
0x0:OFF
0x1:Fixed car wash
0x2:Mobile car wash
0x3:Reserved
ICM 洗涤模式开关状态
VeINP_CAN_ICMOTASts_sig
uint8
0x0:Normal Status
0x1:OTA Status
0x2:Reserved
0x3:Reserved
OTA 升级期间禁止雨刮部分动作（NoPreconditions 条件之一）
VeINP_CAN_ICMRearWiperReq_sig
uint8
0x0:No action
0x1:OFF
0x2: ON
0x3:Reserve
ICM 后雨刮手动请求，0x2触发3s间歇动作
VbINP_CAN_ICMRearWashSwSts_sig
uint8
0x0:No action
0x1:OFF
0x2: ON
0x3:Reserve
ICM 后洗涤开关，运行3s自动关闭，与前洗涤互斥
VeINP_CAN_ICMRearMaintenanceReq_flg
boolean
0x0: No request
0x1: Request
后雨刮维修模式请求，跳变有效
VeINP_ICMFWindAndNozheatingReq_sig
uint8
0x0:No Request
0x1:OFF
0x2:ON
0x3:Reserved
ICM 前风挡+喷嘴加热请求，持续>20min 自动关闭
VeINP_CAN_IDMZCULHeater_sig
uint8
0x0: No request
0x1: Request
IDM 加热请求，仅驱动前喷嘴加热（不含风挡）
VeINP_CAN_VCU1NActualGear_sig
uint8
0x0: Init
0x1: P
0x2: N
0x3: R
0x4: D
0xF: Error Value
实际挡位，R 档上升沿触发后雨刮联动；P/N 挡限制 IDM 智驾控制
VbINP_CAN_VCU1FActualGear_flg
boolean
0x0: Invalid
0x1: Valid
挡位信号有效性标志，需同时有效才响应
EPRM 存储输入
VbINP_EPRM_MaintenanceFromEE_flg
boolean
0x0:No Request
0x1:Request
上电时从 EEPROM 读取前雨刮维护模式标志，恢复上次状态
VbINP_EPRM_RearMaintenanceFromEE_flg
boolean
0x0:No Request
0x1:Request
上电时从 EEPROM 读取后雨刮维护模式标志
VeINP_EPRM_ZCULRainSensitivityStsFromEE_sig
uint8
0x0:Most Insensitive(reserve) 
0x1: More Insensitive 
0x2: Insensitive 
0x3: Normal 
0x4: Sensitive
0x5:More Sensitive(reserve) 
0x6:Most Sensitive(reserve) 
0x7: Reserved 
上电时从 EEPROM 读取上次灵敏度设置，ICM 失联时维持此值
整车状态输入
VeOUT_PDU_PowerMode_sig
uint8
0x0: OFF
0x1: ON
0x2: RUN
0x3: Reserved
整车电源模式，非OFF为雨刮使能前提；OFF触发归位后休眠
VbOUT_PDU_PowerModeValid_flg
boolean
0x0：Invalid
0x1：Valid
电源模式有效性，需与 PowerMode 同时有效
VeOUT_PDU_ZCULSystemPowerSource_sig

uint8
0x0:Off 
0x1:Key ON 
0x2:OTA ON 0x3:Remote ON
0x4:智能补电
0x5-0x7:Reserved 
系统供电来源，影响 Park 位归位逻辑判断
VeOUT_CMS_ZCULCarMode_sig
uint8
0x0: Factory Mode
0x1: Normal Mode
0x2: Transport Mode
0x3: Factory Test Mode
0x4: Exhibition Mode
0x5: Safety Mode
0x6: Dyno Mode（车毂模式）
0x7-0xF: Reserved
整车工作模式，洗车/展车模式触发 WASHMODE 状态禁止自动雨刮
VbOUT_CMS_ZCULWipingInhibit_flg
boolean
0x0:Not Inhibit
0x1:Inhibit
CMS 自动雨刮禁止标志（WashMode 条件之一）
VeOUT_ALM_ZCULAntiThelfSts_sig
uint8
0x0: Disarm 
0x1: Armed
0x2: Prearm
0x3: Alarm
防盗状态，Armed/Alarm 跳变立即关闭所有雨刮输出
VuINP_CFG_V23Type_sig
uint8
0x0000：默认功能【标配】
0x0001：六合一电机【S59-2025年型】
0x0002：可配置功能2【S59-2025右舵】
0x0003：高配【S59-2025左舵】
0x0004：可配置功能4【S59D增程】
0x0005：可配置功能5【S59D增程左舵】
0x0006：可配置功能6【S59D增程反切】
0x0007：三合一电机【S59-2025年型401km】
0x0008：低配【S59-2025左舵低配】
0x0007-0x00FF：预留
0x0100: 可配置功能1【S5D增程】
0x0101: 可配置功能2【S5D增程国际】
0x0102-0xFFFF：预留
车型硬件配置，区分不同规格的雨刮参数
信号名
数据类型
值定义
作用描述
VbOUT_WW_FWiperLow_flg
boolean
0x00：Invalid
0x01：Valid
前雨刮低速电机输出
VbOUT_WW_FWiperHigh_flg
boolean
0x00：Invalid
0x01：Valid
前雨刮低速电机输出
VbOUT_WW_FWsher_flg
boolean
0x00：Invalid
0x01：Valid
前雨刮洗涤电机输出
VbOUT_WW_RearFWiper_flg
boolean
0x00：Invalid
0x01：Valid
后雨刮雨刮电机输出
VbOUT_WW_RearFWsher_flg
boolean
0x00：Invalid
0x01：Valid
后雨刮洗涤电机输出
VbOUT_WW_FWindHeater_flg
boolean
0x00：Invalid
0x01：Valid
前风挡加热电机输出
VbOUT_WW_FNozzleHeater_flg
boolean
0x00：Invalid
0x01：Valid
前喷嘴加热电机输出

VeOUT_WW_ZCULFWiperSts_sig
enum
0x00: OFF
0x01: LS speed
0x02: HS Speed
0x03: Washwipe
0x04: Maintenance Mode
0x05: AUTO
0x06: INT
0x07: MIST
前雨刮状态输出
VeOUT_WW_ZCULFwiperSWSts_sig

enum
0x00: OFF
0x01: LS speed
0x02: HS Speed
0x03: Washwipe
0x04: Maintenance Mode
0x05: AUTO
0x06: INT
0x07: MIST
前雨刮开关状态输出
VbOUT_WW_ZCULFwiperwashingSts_flg
boolean
0x00: OFF
0x01: ON
前雨刮洗涤状态输出
VeOUT_WW_ZCULRearWiperSts_flg
boolean
0x00: OFF
0x01: ON
后雨刮状态输出
VeOUT_WW_ZCUL_RearWashWiperSts_flg
boolean
0x00: OFF
0x01: ON
后雨刮洗涤状态输出
VbOUT_WW_ZCULParkPosition_flg
boolean
0x00：Invalid
0x01：Valid
前雨刮停止位状态输出
VbOUT_WW_ZCULAutoWipingInhibit_flg
boolean
0x00：Invalid
0x01：Valid
洗车模式禁用状态输出
VeOUT_WW_ZCULRainSensitivitySts_sig
enum
0x0:Most Insensitive(reserve) 
0x1: More Insensitive 
0x2: Insensitive 
0x3: Normal 
0x4: Sensitive
0x5:More Sensitive(reserve) 
0x6:Most Sensitive(reserve) 
0x7: Reserved 
光雨量传感器灵敏度状态输出
VeOUT_WW_ZCULRainSensitivityStsToEE_sig
enum
0x0:Most Insensitive(reserve) 
0x1: More Insensitive 
0x2: Insensitive 
0x3: Normal 
0x4: Sensitive
0x5:More Sensitive(reserve) 
0x6:Most Sensitive(reserve) 
0x7: Reserved 
光雨量传感器灵敏度写入E2ROM状态输出

VbOUT_WW_ZCULRainSensorFailSts_flg
boolean
0x00：Invalid
0x01：Valid
光雨量传感器故障状态输出
VbOUT_WW_MaintenanceToEE_flg
boolean
0x00:Inactive
0x01:Active
前雨刮维修模式写入E2ROM状态输出
VbOUT_WW_RearMaintenanceToEE_flg
boolean
0x00:Inactive
0x01:Active
后雨刮维修模式写入E2ROM状态输出
VbOUT_WW_ZCUL_WashingLiquidLow_flg
boolean
0x00:Inactive
0x01:Active
洗涤液位报警状态输出
VbOUT_CAN_ZCUL_FWindAndNozheatingSts_flg
boolean
0x00:Inactive
0x01:Active
前风挡和前喷嘴加热状态输出
说明
服务名
端口名
端口类型
入参参数名
入参数据类型
入参值定义
出参参数名
出参值定义
关联的信号输出端口
前雨刮执行类服务
BOD_FWiper_Atm

rrFWiper

Server端
FWiperCmd
enum

0x0:Stop 
0x1:Low
0x2:High
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_FWiperLow_flg；VbOUT_WW_FWiperHigh_flg
前洗涤驱动服务
BOD_FWasher_Atm

rrFWasher
Server端

FWasherCmd
boolean
0x0：ON
0x1：OFF
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_FWsher_flg
后雨刮执行类服务

BOD_RWiper_Atm

rrRWiper

Server端
RWiperCmd

boolean
0x0：ON
0x1：OFF
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_RearFWiper_flg
后洗涤喷嘴驱动服务
BOD_RWasher_Atm

rrRWasher
Server端
RWasherCmd
boolean
0x0：ON
0x1：OFF
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_RearFWsher_flg
前风挡加热驱动

BOD_FWindHeater_Atm

rrFWindHeater
Server端
FWindHeaterCmd
boolean
0x0：ON
0x1：OFF
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_FWindHeater_flg
前喷嘴加热驱动服务

BOD_FNozzleHeater_Atm

rrFNozzleHeater
Server端
FNozzleHeaterCmd
boolean
0x0：ON
0x1：OFF
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_FNozzleHeater_flg
雨刮/洗涤运行状态上报服务
BOD_WiperStatus_Atm

rrWiperStatus
Server端

FWiperSts；
FWiperSWSts；
FWashingSts；
RWiperSts；
RWiperWashSts；
ParkPositionSts；
AutoWipingInhibit

Enum；
Enum；
boolean；
Enum；
boolean；
boolean；
boolean；
boolean
0x0:OFF
0x1:LS
0x2:HS
0x3:Wash
0x4:Maint
0x5:AUTO
0x6:INT
0x7:MIST
0x0: OFF
0x1: MIST
0x2: LS speed
0x3: HS Speed
0x4: AUTO
0x5: INT
0x6: Reserved
0x7: Invalid
0x0：OFF
0x1：ON
0x0：OFF
0x1：ON
0x0：OFF
0x1：ON
0x0：OFF
0x1：ON
0x0：OFF
0x1：ON
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VeOUT_WW_ZCULFWiperSts_sig
VeOUT_WW_ZCULFwiperSWSts_sig
VbOUT_WW_ZCULFwiperwashingSts_flg
VeOUT_WW_ZCULRearWiperSts_flg
VeOUT_WW_ZCUL_RearWashWiperSts_flg
VbOUT_WW_ZCULParkPosition_flg
VbOUT_WW_ZCULAutoWipingInhibit_flg

雨量传感器状态与灵敏度记忆归并服务
BOD_RainSensor_Atm

rrRainSensor
Server端
RainSensitivitySts；
RainSensitivityToEE；
RainSensorFailSts

Enum；
Enum；
boolean

1、2.
0x0:Most Insensitive(reserve) 
0x1: More Insensitive 
0x2: Insensitive 
0x3: Normal 
0x4: Sensitive
0x5:More Sensitive(reserve) 
0x6:Most Sensitive(reserve) 
0x7: Reserved 
3.
0x0:Normal
0x1：Fault
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VeOUT_WW_ZCULRainSensitivitySts_sig
VeOUT_WW_ZCULRainSensitivityStsToEE_sig
VbOUT_WW_ZCULRainSensorFailSts_flg
维修状态上报服务
BOD_Maintenance_Atm

rrMaintenance
Server端
FMaintenanceToEE；
RMaintenanceToEE；
RWMaintModeSts
boolean；
boolean；
boolean
0x0:Inactive
0x1:Active
0x0:Inactive
0x1:Active
0x0：ON
0x1：OFF
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_MaintenanceToEE_flg
VbOUT_WW_RearMaintenanceToEE_flg
VeOUT_WW_ZCULRWMaintModeSts_flg

清洗液报服务
BOD_WashLiquid_Atm

rrWashLiquid
Server端
WashingLiquidLow

boolean
0x0:Inactive
0x1:Active
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_ZCUL_WashingLiquidLow_flg
加热状态服务
BOD_HeaterStatus_Atm

rrHeaterStatus
Server端
FWindHeaterSts；
FNozzleHeaterSts
boolean；
boolean
0x0:Inactive
0x1:Active
0x0:Inactive
0x1:Active
ReturnCode
0x0:SUCCESS（成功）
0x1:FAILURE（失败）
0x2:FAIL_UNAVAILABLE（不可达失败）
0x3:FAIL_INVALID_PARAM(参数无效失败)
Others：Invalid
VbOUT_WW_FWindHeater_flg
VbOUT_WW_FNozzleHeater_flg
VbOUT_CAN_ZCUL_FWindAndNozheatingSts_flg