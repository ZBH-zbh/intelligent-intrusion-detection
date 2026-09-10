# 智能入侵检测系统

## 项目简介

基于 AMD/Xilinx PYNQ-Z2 的运动目标检测与入侵报警系统。

本项目参加 AMD/Xilinx 学生开发竞赛，利用 PYNQ-Z2 的 FPGA 可编程逻辑（PL）实现视频预处理加速，ARM 处理系统（PS）运行 Python 应用逻辑，完成实时运动目标检测、入侵判断与报警功能。

## 系统架构

```text
┌─────────────────────────────────────┐
│           USB 摄像头                 │
└─────────────┬───────────────────────┘
              │ USB
┌─────────────▼───────────────────────┐
│      PYNQ-Z2 ARM PS (Python)        │
│  - OpenCV 视频采集                   │
│  - 调用 PL 加速                      │
│  - 目标画框 / 人数统计 / 入侵判断      │
│  - 报警控制 / UI 显示                 │
└─────────────┬───────────────────────┘
              │ AXI-Lite / AXI-Stream
┌─────────────▼───────────────────────┐
│      PYNQ-Z2 FPGA PL                │
│  - RGB 转灰度                        │
│  - 帧差法（Frame Differencing）       │
│  - 二值化（Thresholding）             │
│  - 形态学处理（Morphology）            │
│  - 目标轮廓 / 坐标输出                 │
└─────────────────────────────────────┘
```

## 硬件平台

- **开发板**：PYNQ-Z2（Xilinx Zynq-7020，ARM PS + FPGA PL）
- **摄像头**：罗技 C270i USB 摄像头（720P，UVC 免驱）
- **报警模块**：Grove Buzzer 蜂鸣器
- **扩展坞**：联想 thinkplus USB3.0 集线器（带 Type-C 独立供电）

## 开发环境

- **FPGA 工具链**：Vivado / Vitis HLS 2022.1
- **系统镜像**：PYNQ-Z2 v3.0.1
- **Python 环境**：Python 3.10 + OpenCV + Jupyter Notebook
- **连接方式**：PC 直连 PYNQ-Z2 以太网，静态 IP 192.168.2.100/24

## 团队分工

| 角色 | 负责人 | 主要职责 |
|---|---|---|
| 队长 | - | 系统架构、接口协议、项目管理、文档整理 |
| 队友 A | - | HLS/Vivado FPGA 开发、bitstream 生成 |
| 队友 B | - | Python/OpenCV PS 端开发、UI 显示、报警逻辑 |

## 项目进度

- [x] 基础环境搭建（PYNQ 镜像、Vivado/Vitis HLS、SSH/Jupyter）
- [x] 第一个 HLS IP 学习与 overlay 加载验证（rgb2gray）
- [ ] 帧差法 HLS IP 开发
- [ ] Vivado 视频流 Block Design 集成
- [ ] PYNQ 摄像头采集与显示
- [ ] Python 应用：画框、人数统计、入侵报警
- [ ] PS 纯软件 vs PL 加速对比实验
- [ ] 项目文档整理与答辩准备

## 目录说明

```text
/
├── assets/              # 图片、架构图等静态资源
├── docs/                # 项目文档
├── pl/                  # FPGA 端代码
│   ├── hls/             # Vitis HLS C/C++ 源码
│   └── vivado/          # Vivado 工程文件
├── ps/                  # Python 端代码
│   ├── notebooks/       # Jupyter Notebook
│   └── src/             # Python 模块源码
├── tests/               # 测试脚本与数据
└── README.md            # 项目说明
```

## 快速开始

### 1. 启动 PYNQ-Z2

- 插入烧录好 PYNQ v3.0.1 镜像的 SD 卡
- 连接电源、网线、USB 摄像头
- 启动后通过 SSH 登录：`xilinx@192.168.2.99`

### 2. 加载 overlay

```python
from pynq import Overlay
ol = Overlay("/home/xilinx/xxx.bit")
```

### 3. 运行 Jupyter 应用

在 PYNQ 上启动 Jupyter，在浏览器打开 `http://192.168.2.99:9091`，运行 `ps/notebooks/` 下的 Notebook。

## 参考资料

- [PYNQ 官方文档](https://pynq.readthedocs.io/)
- [Xilinx PYNQ GitHub](https://github.com/Xilinx/PYNQ)
- AMD/Xilinx 学生开发竞赛要求文档
