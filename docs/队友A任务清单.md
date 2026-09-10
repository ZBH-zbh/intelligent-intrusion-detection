# 队友 A 任务清单（FPGA 开发）

## 角色定位

负责 PL（FPGA）端开发，包括 Vitis HLS IP 设计、Vivado Block Design 集成、bitstream 生成，以及与 PS 端的联调。

---

## 第 1 周：基础入门

### 任务 A1：学习 AXI-Stream 接口

- **目标**：理解视频流为什么用 AXI-Stream，而不是 AXI-Lite
- **学习内容**：
  - `TVALID`、`TREADY`、`TDATA`、`TLAST`、`TKEEP` 信号含义
  - HLS 中 `#pragma HLS INTERFACE axis` 的用法
  - AXI-Stream 与 AXI-Lite 的区别
- **交付物**：一篇学习笔记，或一段能综合通过的简单 AXI-Stream passthrough 代码
- **截止时间**：第 1 周末
- **验收标准**：能向队长解释 AXI-Stream 的基本握手流程

### 任务 A2：巩固 Vivado Block Design 操作

- **目标**：能独立重建一个简单 Block Design
- **练习内容**：
  - 重新做一遍 rgb2gray 的 Vivado 工程（从 HLS IP 导出到生成 bitstream）
  - 不依赖队长，独立完成
- **交付物**：成功生成 `design_1_wrapper.bit`
- **截止时间**：第 1 周末
- **验收标准**：能独立跑通 HLS → Vivado → bitstream 全流程

### 任务 A3：设计帧差法 HLS 模块架构

- **目标**：把运动检测算法拆分成可综合的 HLS 模块
- **输出模块**：
  - `rgb2gray`：RGB 转灰度
  - `frame_diff`：当前帧与背景帧差分
  - `threshold`：二值化
  - `morphology`：形态学开运算/闭运算
  - `bbox_output`：目标坐标输出
- **交付物**：`docs/HLS模块设计.md`
- **截止时间**：第 1 周末
- **验收标准**：模块划分合理，每个模块的输入输出明确

---

## 第 2 周：HLS IP 开发

### 任务 A4：实现 RGB2Gray HLS 模块

- **输入**：24-bit RGB 像素流（AXI-Stream）
- **输出**：8-bit 灰度像素流（AXI-Stream）
- **公式**：`gray = (R*76 + G*150 + B*29) >> 8`
- **交付物**：`pl/hls/rgb2gray/rgb2gray.cpp` + 可综合的 HLS 工程
- **截止时间**：第 2 周中
- **验收标准**：C/RTL 联合仿真通过，输出结果与软件公式一致

### 任务 A5：实现帧差法 HLS 模块

- **输入**：当前灰度帧 + 背景灰度帧
- **输出**：差分结果（8-bit）
- **功能**：`|current - background|`
- **交付物**：`pl/hls/frame_diff/frame_diff.cpp`
- **截止时间**：第 2 周中
- **验收标准**：RTL 仿真结果与 OpenCV `cv2.absdiff` 一致

### 任务 A6：实现二值化 HLS 模块

- **输入**：差分结果（8-bit）
- **输出**：二值图像素（0 或 255）
- **功能**：阈值可通过 AXI-Lite 配置
- **交付物**：`pl/hls/threshold/threshold.cpp`
- **截止时间**：第 2 周末
- **验收标准**：阈值参数可配置，结果与 OpenCV `cv2.threshold` 一致

### 任务 A7：实现形态学处理 HLS 模块

- **输入**：二值图像素流
- **输出**：去噪后的二值图像素流
- **功能**：开运算去噪 + 闭运算填补小洞
- **交付物**：`pl/hls/morphology/morphology.cpp`
- **截止时间**：第 2 周末
- **验收标准**：RTL 仿真结果与 OpenCV `cv2.morphologyEx` 基本一致

### 任务 A8：实现目标坐标输出模块（可选，难度较高）

- **输入**：二值图像素流
- **输出**：目标数量 + 每个目标的 bounding box（x, y, w, h）
- **说明**：如果 FPGA 资源或时间不够，可先在 PS 端用 OpenCV 做轮廓提取
- **交付物**：`pl/hls/bbox_output/bbox_output.cpp`（如完成）
- **截止时间**：第 3 周中
- **验收标准**：能正确输出运动目标的坐标

---

## 第 3 周：Vivado 集成与 bitstream 生成

### 任务 A9：导出所有 HLS IP

- **目标**：把每个 HLS 模块导出为 Vivado IP（.zip）
- **交付物**：`pl/vivado/ip_repo/` 目录下的多个 zip 文件
- **截止时间**：第 3 周初
- **验收标准**：每个 IP 都能在 Vivado 中正常导入

### 任务 A10：搭建完整 Block Design

- **目标**：在 Vivado 中把所有 IP 和 Zynq PS 连起来
- **内容包括**：
  - Zynq7 Processing System
  - AXI Interconnect
  - AXI-Stream 数据通路
  - HLS IP 之间的连接
  - AXI-Lite 控制接口
- **交付物**：`pl/vivado/intrusion_detection.xpr`
- **截止时间**：第 3 周中
- **验收标准**：Block Design 无红色报错，Validate Design 通过

### 任务 A11：生成 bitstream

- **目标**：生成完整的 bitstream 和硬件 handoff 文件
- **交付物**：
  - `intrusion_detection.bit`
  - `intrusion_detection.hwh`
- **截止时间**：第 3 周中
- **验收标准**：能在 PYNQ 上成功 `Overlay("intrusion_detection.bit")`

### 任务 A12：与队友 B 联调

- **目标**：确保 PS 端能正确配置 PL 参数并读取结果
- **内容**：
  - 配合队友 B 测试 AXI-Lite 寄存器读写
  - 调试 AXI-Stream 视频流传输
  - 解决时序或数据格式问题
- **交付物**：联调记录
- **截止时间**：第 3 周末
- **验收标准**：PS 能调用 PL 处理至少一帧视频

---

## 第 4 周：优化与文档

### 任务 A13：资源与时序优化

- **目标**：如果资源占用过高或时序不满足，进行优化
- **优化方向**：
  - 降低分辨率（640×480 → 320×240）
  - 减少流水线级数
  - 复用存储器
- **交付物**：优化后的 bitstream
- **截止时间**：第 4 周初

### 任务 A14：配合性能对比实验

- **目标**：提供 PL 加速版本，供队友 B 做对比测试
- **交付物**：稳定的 overlay 文件和调用说明
- **截止时间**：第 4 周中

### 任务 A15：整理 FPGA 部分文档

- **目标**：写清楚 FPGA 设计思路、模块说明、遇到的问题
- **交付物**：
  - `docs/FPGA设计说明.md`
  - `docs/联调记录.md`
- **截止时间**：第 4 周末
- **验收标准**：别人能根据文档复现 FPGA 部分

---

## 关键技能要求

- Vitis HLS C/C++ 综合
- Vivado IP Integrator
- AXI-Lite / AXI-Stream 接口
- FPGA 资源与时序分析基础

## 需要阅读的文档

- `docs/接口协议.md`
- `docs/技术预研.md`
- `docs/需求分析.md`
- Xilinx HLS 用户指南
- PYNQ 官方文档
