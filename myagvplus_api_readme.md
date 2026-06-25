# MyAGV Plus API 使用说明

> **注：** 以下 API 均为 Python API，使用前请先安装 `pymycobot` Python SDK 包。

---

## 1. 系统 & 产品信息

### get_system_version()
- **功能:** 获取主固件版本号
- **返回值:** `float` (版本号)

### get_modify_version()
- **功能:** 获取次固件版本号（已修复精度，直接返回真实值）
- **返回值:** `float` (版本号)

### set_debug_state(state)
- **功能:** 设置底层控制板的打印调试状态
- **参数说明:**
  - `state` (int): 填 `0` 看电池信息, `1` 看陀螺仪信息, `2` 看 LED 状态, `4` 看原始串口指令。
- **返回值:** `int` (1: 成功, 0: 失败)
- **调用示例:** `agv.set_debug_state(2)  # 开启 LED 调试打印`

### get_debug_state()
- **功能:** 获取当前生效的调试状态
- **返回值:** `int` (当前调试状态位)
- **调用示例:** `print(agv.get_debug_state())`

### power_on()
- **功能:** 一键开启机器人（自动开启继电器供电并使能所有电机，默认进入速度控制模式）。**注意：** 调用后需要等待大概 6 秒钟让电机启动并校准。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.power_on()`

### power_on_only()
- **功能:** 仅开启机器人继电器为主板供电（但轮子电机依然是失能/软的，推得动）
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.power_on_only()`

### power_off()
- **功能:** 一键关闭机器人（禁用所有轮子电机并切断继电器电源）
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.power_off()`

### is_power_on()
- **功能:** 检查机器人底层继电器电源是否已开启
- **返回值:** `int` (1: 开机, 0: 关机)
- **调用示例:** `status = agv.is_power_on()`

### get_robot_status()
- **功能:** 读取机器人硬件异常状态信息
- **返回值:** `list[int]` `[电池状态, 陀螺仪状态, 电量水平]`
  - 电池状态: 0-正常, 1-异常
  - 陀螺仪状态: 0-正常, 1-异常
  - 电量水平: 0-正常, 1-警告(<=19.6V), 2-低电量(<19V)

### get_all_msg()
- **功能:** 读取电池和陀螺仪数据
- **返回值:** None (注: 当前架构推荐使用 auto-report 获取)

---

## 2. 运动控制

> **注意：** 
> 1. 下列移动与旋转指令的速度参数 `speed` 的有效范围均为 **0.01 ~ 1.5 m/s**。传入越界参数将直接引发 `ValueError`。
> 2. **安全互锁机制**：运动指令下发时，若任意一轮的目标速度为 0（如异常传入），底层将瞬间强制所有车轮速度归 0，防止打滑失控。

### move_forward(speed)
- **功能:** 控制小车向前平移
- **参数说明:** 
  - `speed` (float): **移动速度**，范围 `0.01` 到 `1.50`。超过限制会报错。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.move_forward(0.5)  # 以 0.5m/s 的速度前进`

### move_backward(speed)
- **功能:** 控制小车向后平移
- **参数说明:** 同上
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.move_backward(0.3)  # 缓慢后退`

### move_left_lateral(speed) / move_right_lateral(speed)
- **功能:** 控制麦克纳姆轮小车向左/向右**横向平移**。
- **参数说明:** 速度范围 `0.01` 到 `1.50`。
- **调用示例:** `agv.move_left_lateral(0.5)  # 左横移`

### turn_left(speed) / turn_right(speed)
- **功能:** 控制小车以中心点**原地左转 / 原地右转**。
- **参数说明:** 速度范围 `0.01` 到 `1.50`。
- **调用示例:** `agv.turn_left(0.8)  # 快速左转`

### stop()
- **功能:** 紧急刹车停止所有运动，所有轮子速度设为 0。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.stop()`

### set_auto_report_state(state)
- **功能:** 设置底层数据的自动报告状态
- **参数:** `state` (int): 0-关闭, 1-开启
- **返回值:** `int` (1: 成功, 0: 失败)

### get_auto_report_state()
- **功能:** 获取当前的自动报告状态
- **返回值:** `int` (0: 关闭, 1: 开启)

### get_auto_report_message()
- **功能:** 被动获取最新一次的自动报告数据解析结果（具备底层滑动窗口高频抗错位解析）
- **返回值:** `list`
  - `0`: (list[int]) 机器状态 `[电池状态, 陀螺仪状态, 电量水平]`
  - `1`: (float) 电池电压 1
  - `2`: (float) 电池电压 2
  - `3`: (int) 充电状态
  - `4`: (list[float]) 18 个字节彻底解析出的陀螺仪数据（三轴加速度、三轴角速度、Pitch/Roll/Yaw欧拉角）
  - `5`: (list[int]) 电机状态 (4个电机的状态码)
  - `6`: (int) 电机使能状态 (0: 使能, 1: 禁用)

---

## 3. 电机辅助控制

### set_motor_enable(motor_id, state)
- **功能:** 强制开启或关闭指定轮子（电机）的使能状态（使能即代表轮子变硬并受控，禁用即代表轮子变软可手推）。
- **参数说明:**
  - `motor_id` (int): 填 `1`~`4` 代表单个轮子，填 `254` 代表同时控制全部四个轮子。
  - `state` (int): 填 `0` 禁用/放松，填 `1` 使能/锁定。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.set_motor_enable(1, 0)  # 让1号轮子变软方便手推`

### get_motor_enable_status()
- **功能:** 获取所有电机的在线和使能状态
- **返回值:** `list[int]` `[m1, m2, m3, m4]` (0-代表禁用或离线拔出, 1-代表使能正常)
- **调用示例:** `print(agv.get_motor_enable_status())  # 输出如: [1, 1, 1, 1]`

### get_motor_status()
- **功能:** 获取四个电机的硬件错误码（比如过温、堵转、欠压等）。如果检测到错误，终端会自动打印红字警告。
- **返回值:** `list[int]` 包含四个错误码（0为正常，非0为硬件报错）
- **调用示例:** `print(agv.get_motor_status())  # 输出如: [0, 0, 8, 0] 说明3号轮报错`

### clear_motor_error(motor_id)
- **功能:** 【排障利器】如果 `get_motor_status()` 查出电机报错死锁，调用此接口可以对目标电机进行瞬间重启和复位，无需重启整个小车。
- **参数说明:** `motor_id` 填 `1`~`4` 或者 `254` (复位所有)。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.clear_motor_error(3)  # 清除3号轮子的报错并让其恢复在线`

### get_motor_temps()
- **功能:** 获取各电机 MOS 的当前温度
- **返回值:** `list[float]` `[m1, m2, m3, m4]`

### get_motor_param_cache(motor_id, rid)
- **功能:** 获取电机的缓存参数
- **参数:**
  - `motor_id` (int): 1-4
  - `rid`: 目标参数 ID
- **返回值:** 参数值

### get_motor_positions()
- **功能:** 获取所有电机当前精密转动里程位置（弧度）
- **返回值:** `list[float]` `[m1, m2, m3, m4]`

### get_motor_position(motor_id)
- **功能:** 获取指定电机当前位置
- **参数:** `motor_id` (int): 1-4
- **返回值:** `float` (位置, 弧度)

### get_motor_velocity(motor_id)
- **功能:** 获取指定电机的当前速度
- **参数:** `motor_id` (int): 1-4
- **返回值:** `float`

### get_motor_torque(motor_id)
- **功能:** 获取指定电机的当前扭矩
- **参数:** `motor_id` (int): 1-4
- **返回值:** `float`

### get_motor_error(motor_id)
- **功能:** 获取指定电机的错误码
- **参数:** `motor_id` (int): 1-4
- **返回值:** `int` 错误码

### get_motor_speeds()
- **功能:** 获取所有电机当前转速（已做死区 ±0.1 硬件降噪过滤）
- **返回值:** `list[float]` `[m1, m2, m3, m4]`

### get_motor_torques()
- **功能:** 获取所有电机当前输出扭矩（已做死区 ±0.1 硬件降噪过滤）
- **返回值:** `list[float]` `[m1, m2, m3, m4]`

### get_motor_loss_count()
- **功能:** 获取各电机 CAN 通讯过程中的丢包计数（实时分析拦截到的收发数据包）
- **返回值:** `list[int]` `[m1, m2, m3, m4]`

### enable_motor(motor_id)
- **功能:** 单独使能电机
- **参数:** `motor_id` (int): 1-4
- **返回值:** `int` (1: 成功)

### enable_motor_old(motor_id, control_mode)
- **功能:** 使用旧固件方式使能电机
- **参数:** 
  - `motor_id` (int): 1-4
  - `control_mode`: 控制模式
- **返回值:** `int` (1: 成功)

### disable_motor(motor_id)
- **功能:** 单独禁用电机
- **参数:** `motor_id` (int): 1-4
- **返回值:** `int` (1: 成功)

### set_motor_zero_position(motor_id)
- **功能:** 一键将指定 DM 车轮的当前位置重置为机械零点
- **参数:** `motor_id` (int): 1~4
- **返回值:** `int` (1: 成功)

### change_motor_param(motor_id, rid, value)
- **功能:** 临时修改 DM 电机高级内部控制寄存器（例如最大速度、PID参数等）。
- **参数说明:**
  - `motor_id` (int): 1-4
  - `rid`: 目标寄存器 ID。请直接传入 `pymycobot.DM_CAN.DM_variable` 枚举类中的值（例如 `DM_variable.KP_APR` 代表位置环比例，`DM_variable.VMAX` 代表最大速度限制）。
  - `value`: 需要写入的数值。
- **调用示例:**
  ```python
  from pymycobot.DM_CAN import DM_variable
  agv.change_motor_param(1, DM_variable.KP_APR, 54)  # 修改1号电机位置环P参数为54
  ```

### read_motor_param(motor_id, rid)
- **功能:** 读取 DM 电机内部的指定高级参数或版本信息。
- **参数说明:**
  - `motor_id` (int): 1-4
  - `rid`: 目标寄存器 ID，同样使用 `DM_variable` 枚举传入。
- **调用示例:**
  ```python
  from pymycobot.DM_CAN import DM_variable
  print("最大速度 VMAX:", agv.read_motor_param(2, DM_variable.VMAX))
  print("硬件版本 hw_ver:", agv.read_motor_param(2, DM_variable.hw_ver))
  ```

### save_motor_param(motor_id)
- **功能:** 将修改的 DM 电机参数永久固化保存到 Flash 中，断电不丢失
- **参数:** `motor_id` (int): 1-4
- **返回值:** `int` (1: 成功)

### switch_motor_control_mode(motor_id, control_mode)
- **功能:** 切换电机的控制模式
- **参数:**
  - `motor_id` (int): 1-4
  - `control_mode`: 目标控制模式 (由 `DM_CAN.Control_Type` 提供)

### change_motor_limit_param(motor_type, pmax, vmax, tmax)
- **功能:** 全局修改 Limit_Param 中的电机的 PMAX, VMAX, TMAX 限制
- **参数:**
  - `motor_type`: 电机类型 (由 `DM_CAN.DM_Motor_Type` 提供)
  - `pmax`: 最大位置
  - `vmax`: 最大速度
  - `tmax`: 最大扭矩

### refresh_motor_status_by_id(motor_id)
- **功能:** 刷新并获取电机状态缓存
- **参数:** `motor_id` (int): 1-4
- **返回值:** `int` (1: 成功)

---

## 4. 高级电机控制模式 (MIT/CSP/位置/速度/扭矩)

> **注意：** 在调用以下接口前，必须先使用 `switch_motor_control_mode` 将电机切换至对应的控制模式（例如 `Control_Type.MIT`），且这些指令需要放在一个循环中以一定频率下发，电机才会持续动作（详见 7.6 案例）。

### control_motor_mit(motor_id, kp, kd, q, dq, tau)
- **功能:** 使用 MIT 模式（综合阻抗模式）控制电机。该模式最为底层且灵活。
- **参数说明:**
  - `motor_id` (int): 1-4，代表你要测试的那个轮子。
  - `kp`: **位置刚度 (弹簧硬度)。** 填太大（如>100）电机容易抽搐；安全测试建议填 **`30` 到 `50`**。
  - `kd`: **速度阻尼 (刹车阻力)。** 防止震荡的参数；安全测试建议填 **`0.1` 到 `0.5`** (例如 `0.3`)。
  - `q`: **目标位置 (rad弧度)。** 电机要去的位置；测试时可填 `0`，或传入一个正弦波如 `math.sin(time.time())*5` 让它来回摇摆。
  - `dq`: **目标速度 (rad/s)。** 基础位置刚度测试时，可直接填 **`0`**。
  - `tau`: **前馈力矩。** 基础测试可直接填 **`0`**。
- **调用示例:**
  ```python
  # 让1号电机以安全的软刚度(50)摆动到角度 5
  agv.control_motor_mit(1, kp=50, kd=0.3, q=5, dq=0, tau=0)
  ```

### control_motor_delay(motor_id, kp, kd, q, dq, tau, delay)
- **功能:** 带有通讯延迟控制的 MIT 模式（参数含义同上）。
- **参数:**
  - `delay`: 发送指令后的额外休眠时间（秒），例如 `0.002` (2ms)。

### control_motor_pos_vel(motor_id, p_desired, v_desired)
- **功能:** 在 **位置速度混合模式 (POS_VEL)** 下控制电机。设定电机要去哪个位置，并限制它的最高运动速度。
- **参数说明:**
  - `motor_id` (int): 1-4。
  - `p_desired`: **目标位置 (rad弧度)。** 例如 `10`，代表你要让它转到 10 弧度的位置。
  - `v_desired`: **转动速度 (rad/s)。** 限制它过去的最大速度，例如 `10`。
- **调用示例:**
  ```python
  # 限制最大转速为 10，让 2号电机 慢慢转到 30 弧度的地方
  agv.control_motor_pos_vel(2, p_desired=30, v_desired=10)
  ```

### control_motor_vel(motor_id, v_desired)
- **功能:** 在 **纯速度控制模式 (VEL)** 下控制电机。让电机无视位置，一直保持某个转速。
- **参数说明:**
  - `motor_id` (int): 1-4。
  - `v_desired`: **目标速度 (rad/s)。** 正数正转，负数反转。例如 `5`。
- **调用示例:**
  ```python
  # 让 3号电机 始终以 5.0 的速度匀速转动
  agv.control_motor_vel(3, 5.0)
  ```

### control_motor_pos_force(motor_id, pos_des, vel_des, i_des)
- **功能:** 在 **力位混合模式 (EMIT/POS_FORCE)** 下控制电机。类似 POS_VEL，但在前往该位置的过程中加入了最大电流（输出力）的限制。如果遇到阻力大于该限度，电机将表现出柔性停住。
- **参数说明:**
  - `motor_id` (int): 1-4。
  - `pos_des`: **目标位置 (rad弧度)。**
  - `vel_des`: **目标速度 (rad/s)。** 
  - `i_des`: **目标电流 (限制力矩)。** 范围 `0-10000` (数字越大劲越大)。底层会自动处理缩放比例发给电机。
- **调用示例:**
  ```python
  # 让 4号电机 以较弱的力度转到 5 弧度的位置（遇强阻力会柔性停住）
  agv.control_motor_pos_force(4, pos_des=5, vel_des=10, i_des=100)
  ```

### CSP 周期同步模式 (control_motor_pos_vel_csp / control_motor_vel_csp / control_motor_tor_csp)
- **功能:** CSP 系列模式不经过电机内部的轨迹规划，完全依赖上位机的高频、稳定的控制循环（如严格每 1ms 喂点）。
- **参数说明:** 同上述对应模式（如 `p_desired` 为目标位置，`v_desired` 为目标速度，`tor_desired` 为目标扭矩）。
- **注意:** 测试人员不建议在基础测试中使用 CSP 模式，它主要提供给需要做极高精度上位机多轴联动插补的高阶开发者使用。

---

## 5. IO 控制与通讯

### set_led_mode(mode)
- **功能:** 设置车体四周 LED 灯带的显示模式。
- **参数说明:** 
  - `mode` (int): 填 `0` 恢复默认的电量跑马灯指示，填 `1` 切换为开发者 DIY 颜色控制模式。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.set_led_mode(1)  # 准备自己控制灯光颜色`

### set_led_color(brightness, color)
- **功能:** 控制灯带颜色（前提是已经调用 `set_led_mode(1)`）。
- **参数说明:**
  - `brightness` (int): 亮度大小，填 `0` 到 `255`。
  - `color` (tuple): RGB 颜色组合 `(R, G, B)`，每个值 `0` 到 `255`。
- **返回值:** `int` (1: 成功)
- **调用示例:** `agv.set_led_color(255, (0, 255, 0))  # 设为最亮纯绿色`

### get_pin_input(pin)
- **功能:** 读取主板上额外输入引脚的电平状态。如果不使用短接线，硬件默认状态为低电平 (0)。
- **参数说明:** `pin` (int) 填 `0` 到 `6`（1-6 对应不同物理引脚，0 代表所有引脚）。
- **返回值:** `int` (`0` 为低电平, `1` 为高电平, `-1` 为失败/引脚不存在)
- **调用示例:** `print(agv.get_pin_input(1))  # 查1号引脚电平`

### set_pin_output(pin, state=0)
- **功能:** 控制主板上外围输出引脚的电平，用来测试继电器、气泵或用万用表测电压。默认输出为低电平 (0)。
- **参数说明:**
  - `pin` (int): 引脚编号 `0` 到 `6`（1-6 对应不同物理引脚，0 代表所有引脚）。
  - `state` (int): 填 `0` 输出低电平，填 `1` 输出高电平。默认值为 `0`。
- **调用示例:** `agv.set_pin_output(2, 1)  # 给2号输出引脚供电`

### get_estop_state()
- **功能:** 获取急停按钮状态。内部单独封装读取。
- **返回值:** `int` (0: 释放/未按下/低电平, 1: 处于按下状态/高电平, -1: 读取失败)

### set_fan_state(state=1)
- **功能:** 设置风扇开关状态。硬件默认状态为开启 (1)。
- **参数说明:**
  - `state` (int): 填 `0` 关闭风扇，填 `1` 开启风扇。默认值为 `1`。
- **返回值:** `int` (1: 成功, 0: 失败)
- **调用示例:** `agv.set_fan_state(0)  # 关闭风扇`

### set_communication_state(state)
- **功能:** 切换底层通讯状态模式。当切换至 `1` (Socket) 时，本地串口将智能释放。
- **参数:** `state` (int): 0-串口通讯 (默认), 1-Socket 通讯, 2-蓝牙通讯 (写入本地 MAC)
- **返回值:** `int` (1: 成功, 0: 失败)

### get_communication_state()
- **功能:** 获取当前通讯状态
- **返回值:** `int` (0-串口, 1-Socket, 2-蓝牙)

---

## 6. WiFi & 蓝牙

### get_wifi_ip_port()
- **功能:** 获取 Jetson 设备的 Wi-Fi IP 与端口
- **返回值:** `tuple(str, int)` `("IP地址", 8080)`

### get_wifi_account()
- **功能:** 获取当前连接的 Wi-Fi 账号名称
- **返回值:** `tuple(str, str)` `("SSID", "******")`

### get_bluetooth_address()
- **功能:** 获取本地蓝牙 MAC 地址
- **返回值:** `str` (蓝牙 MAC)

### get_bluetooth_uuid()
- **功能:** 获取蓝牙 UUID 及服务信息
- **返回值:** `tuple(str, str, str)` `(蓝牙名称, 服务UUID, 特征UUID)`

---

## 7. 使用案例

### 7.1 获取 AGVPlus 的系统版本号
```python
from pymycobot import MyAGVPlus

# 初始化 AGVPlus 对象（需传入 DM 电机串口和 ESP32 控制串口）
agv_plus = MyAGVPlus("/dev/myagvplus_controller", baudrate=921600, esp32_port='/dev/ttyUSB0', esp32_baud=115200, debug=True)

# 获取主固件版本号
version = agv_plus.get_system_version()
print(version)
```

### 7.2 控制 AGVPlus 以 0.5m/s 的速度前进并点亮红色 LED 灯
```python
import time
from pymycobot import MyAGVPlus

# 注意：较新的设备ESP32串口可能为 /dev/ttyUSB0 或 /dev/ttyACM0，请视实际情况调整
agv_plus = MyAGVPlus("/dev/myagvplus_controller", baudrate=921600, esp32_port='/dev/ttyUSB0', esp32_baud=115200, debug=True)

# 开启机器人（包含继电器上电和电机使能等过程，需等待几秒钟）
agv_plus.power_on()

# 切换 LED 为 DIY 模式
agv_plus.set_led_mode(1)
# 设置 LED 颜色为红色（亮度 255）
agv_plus.set_led_color(255, (255, 0, 0))

# 控制 AGVPlus 以 0.5m/s 的速度前进
agv_plus.move_forward(0.5)

# 睡眠 3 秒
time.sleep(3)

# 停止移动
agv_plus.stop()

# 关闭机器人电源并禁用电机
agv_plus.power_off()
```

### 7.3 获取网络信息并切换通信模式为 Socket
```python
from pymycobot import MyAGVPlus

agv_plus = MyAGVPlus("/dev/myagvplus_controller", baudrate=921600, esp32_port='/dev/ttyUSB0', esp32_baud=115200, debug=True)

# 获取 AGVPlus 的 WIFI 账号
account, password = agv_plus.get_wifi_account() 
print(f"Account: {account}, Password: {password}")

# 获取 AGVPlus 的 IP 地址和开放端口
ip, port = agv_plus.get_wifi_ip_port()
print(f"IP: {ip}, Port: {port}")

# 将当前通信模式设置为 Socket 模式
set_result = agv_plus.set_communication_state(1)
if set_result == 1:
    print("Set communication mode to Socket successfully.")
else:
    print("Failed to set communication mode to Socket.")
```

### 7.4 高级电机控制: 独立获取电机速度并设置纯速度控制
```python
import time
from pymycobot import MyAGVPlus
from pymycobot.DM_CAN import Control_Type

agv_plus = MyAGVPlus("/dev/myagvplus_controller", baudrate=921600, esp32_port='/dev/ttyUSB0', esp32_baud=115200, debug=True)

agv_plus.power_on()

# 获取电机1当前速度
v1 = agv_plus.get_motor_velocity(1)
print(f"Motor 1 current velocity: {v1}")

# 切换电机1到纯速度模式并设置速度为 1.0 rad/s
agv_plus.switch_motor_control_mode(1, Control_Type.VEL)
agv_plus.control_motor_vel(1, 1.0)
time.sleep(2)

# 停止
agv_plus.control_motor_vel(1, 0.0)
agv_plus.power_off()
```

### 7.5 【必看】启动并使用 Socket 守护进程进行无缝远程控制

Socket 模式能够让您在任意一台连入同一局域网的电脑上零延迟地控制 AGV，完美支持二次开发。

**第一步：在小车主板 (Jetson Nano) 上启动网络守护进程**
打开终端，运行如下命令。该进程会自动运行并“潜伏”在后台，同时不断侦测通讯状态：
```bash
python3 agv_socket_server.py
```
*(注意：该程序运行期间不建议手动使用本地串口脚本强行控制硬件，除非先释放串口。)*

**第二步：通过代码指令触发网络服务接管**
在另一终端或直接通过您的代码调用以下语句（如 7.3 案例所示）：
```python
agv_plus.set_communication_state(1)
```
底层将立刻释放物理串口的使用权！同时后台的 `agv_socket_server.py` 侦测到状态变更，瞬间接管物理硬件并暴露 `9000` 网络端口。

**第三步：在远端个人电脑上像调用本地库一样发号施令**
在局域网内的个人电脑（Win/Mac/Linux）中：
```python
from pymycobot.myagvplussocket import MyAGVPlusSocket
import time

# 连接至小车 IP，并指定 9000 端口
agv = MyAGVPlusSocket("192.168.1.132", 9000)

print(agv.get_motor_speeds()) # 远程读取速度信息
agv.move_left_lateral(0.3)    # 远程控制左横移
time.sleep(2)
agv.stop()
```

### 7.6 高级电机控制模式案例 (MIT/位置速度/速度)

达妙电机的新固件支持在线切换控制模式（MIT、POS_VEL、VEL等），需要以一定的频率持续发送控制指令。以下是使用 AGVPlus 接口对电机进行高级独立控制的示例。

```python
import math
import time
from pymycobot import MyAGVPlus
from pymycobot.DM_CAN import Control_Type

# 初始化 AGVPlus 对象
agv_plus = MyAGVPlus("/dev/myagvplus_controller", baudrate=921600, esp32_port='/dev/ttyUSB0', esp32_baud=115200, debug=True)

# 开启机器人
agv_plus.power_on()

# 以电机 1 为例进行高级控制测试
motor_id = 1

# 1. 切换电机 1 的控制模式为位置速度混合模式 (POS_VEL)
print(f"Switching Motor {motor_id} to POS_VEL mode...")
agv_plus.switch_motor_control_mode(motor_id, Control_Type.POS_VEL)

# 2. 将当前位置设置为机械零点 (可选，视需求而定)
agv_plus.set_motor_zero_position(motor_id)
time.sleep(0.5)

# 3. 循环发送高级控制指令
print("Start controlling Motor 1 in POS_VEL mode...")
i = 0
while i < 1000:
    # 构造一个正弦波位置信号
    q = math.sin(time.time())
    i += 1
    
    # 接口参数说明: control_motor_pos_vel(motor_id, p_desired, v_desired)
    # 此处 q * 8 为目标位置, 30 为期望转动速度
    agv_plus.control_motor_pos_vel(motor_id, q * 8, 30)
    
    # 刷新状态并读取当前信息
    agv_plus.refresh_motor_status_by_id(motor_id)
    pos = agv_plus.get_motor_position(motor_id)
    vel = agv_plus.get_motor_velocity(motor_id)
    tor = agv_plus.get_motor_torque(motor_id)
    
    print(f"Motor {motor_id} POS: {pos:.2f}, VEL: {vel:.2f}, TORQUE: {tor:.2f}")
    
    # 推荐在每帧控制后加上 1ms 的通讯缓冲延时
    time.sleep(0.001)

# 停止单电机指令下发并关机
agv_plus.power_off()
```
