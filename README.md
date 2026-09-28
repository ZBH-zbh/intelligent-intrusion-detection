# PYNQ-Z2 智能入侵检测系统 / Intelligent Intrusion Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 **AMD/Xilinx PYNQ-Z2** 的实时运动目标检测与入侵报警边缘节点。PL（FPGA）完成视频预处理加速，PS（ARM + Python）运行应用逻辑，适用于竞赛演示与轻量级工业周界检测场景。

> 本仓库为两位队友交付内容的合并最终版：
> - 队友 A：PL / HLS / Vivado 优化（绿框与系统优化）
> - 队友 B：`new_features` 跟踪、越线计数、Web 配置、录制回放等新功能

---

## 1. 系统架构

```text
USB 摄像头 (罗技 C270i)
        │
        ▼
┌─────────────────────────────┐
│  PYNQ-Z2 ARM PS (Python)    │
│  - OpenCV 采集 / 打包       │
│  - AXI DMA 下发 / 回读      │
│  - 目标跟踪 / 越线计数      │
│  - 入侵判断 / 蜂鸣器 / Web  │
└───────────┬─────────────────┘
            │ AXI-Lite / AXI-Stream
            ▼
┌─────────────────────────────┐
│  PYNQ-Z2 FPGA PL            │
│  rgb2gray → frame_diff      │
│  → threshold → morphology   │
│  (固定 320×240，0x00RRGGBB) │
└─────────────────────────────┘
```

---

## 2. 硬件与软件环境

| 项目 | 版本 / 型号 |
|---|---|
| 开发板 | PYNQ-Z2 (`xc7z020clg400-1`) |
| 系统镜像 | PYNQ v3.0.1 |
| 摄像头 | 罗技 C270i（UVC） |
| 报警 | Grove Buzzer（AXI GPIO） |
| FPGA 工具链 | Vivado / Vitis HLS 2022.1 |
| Python | 3.10+（PYNQ 环境） |
| 关键库 | OpenCV 4.x、NumPy、pynq |

---

## 3. 目录结构

```text
.
├── assets/                  # 架构图、演示图片
├── docs/                    # 项目文档（需求、接口协议、复现指南等）
├── FPGA2.0/                 # 核心交付包（PL + PS + 测试）
│   ├── pl/pl/hls            # 基线 HLS 源码
│   ├── pl/pl/hls_optimized  # 优化版 HLS 源码（固定 320×240，DSP 大幅减少）
│   ├── pl/pl/vivado         # Vivado 工程与 IP 仓库
│   ├── optimized_overlay/   # 推荐部署 bitstream + hwh
│   ├── pynq_deploy/         # 上板最小部署集（Python + bit/hwh）
│   ├── new_features/        # 跟踪、越线、Web 配置、录制回放
│   ├── tests/               # Python 单元测试
│   └── *.md 报告与说明      # HLS/Vivado/性能对比报告
├── deploy_tools/            # PC 端部署 / 诊断 / 录制辅助脚本
├── reproduction_results/    # 板上复现结果与 Notebook
├── check_env.ps1            # Windows 环境自检脚本
├── LICENSE
└── README.md
```

---

## 4. 快速开始（板上复现）

### 4.1 上传到 PYNQ

把以下文件传到 PYNQ 的 `/home/xilinx/intrusion_demo/`（或任意工作目录）：

```bash
# 在 PC 上（示例用 scp）
scp FPGA2.0/optimized_overlay/intrusion_detection_optimized.bit \
   FPGA2.0/optimized_overlay/intrusion_detection_optimized.hwh \
   FPGA2.0/pynq_deploy/*.py \
   xilinx@192.168.2.99:/home/xilinx/intrusion_demo/
```

> 若使用队友 B 的跟踪/Web 功能，需要同时上传 `FPGA2.0/new_features/` 中的相关模块。

### 4.2 运行实时演示

SSH 登录 PYNQ：

```bash
ssh xilinx@192.168.2.99
cd /home/xilinx/intrusion_demo
```

在 Jupyter Notebook 中执行：

```python
%run pl_motion_detection_optimized.py
```

或使用无界面摄像头测试：

```bash
python3 pl_motion_detection_optimized.py --camera 0 --display 0
```

### 4.3 正式 OpenCV vs PL 对比

```bash
cd /home/xilinx/intrusion_demo
python3 pynq_compare_motion.py \
  --bitstream ./intrusion_detection_optimized.bit \
  --source synthetic \
  --warmup 20 --frames 200 --repeats 3 --min-seconds 5 \
  --opencv-threads 1 --dma-poll-sleep-us 100 \
  --output-root ./pynq_results
```

详细步骤见 [`docs/复现指南.md`](docs/复现指南.md)。

---

## 5. 关键性能指标（PYNQ 实测）

| 指标 | OpenCV 纯软件 | 优化 PL | 说明 |
|---|---|---|---|
| FPS | 48.40 | 50.18 | 固定 320×240 合成帧 |
| 相对加速比 | 1.00× | 1.04× | 受限于当前 PL 仅做前级预处理 |
| 单核 CPU | 99.98% | 96.25% | PL 减轻了部分 PS 负担 |
| 五项一致性 | - | 全部通过 | 掩码像素一致率 > 0.9999，IoU > 0.998 |

完整报告见 `FPGA2.0/性能对比报告.md`。

---

## 6. AXI 地址映射

| 模块 | 基地址 | 配置 |
|---|---|---|
| `frame_diff` | `0x40000000` | width / height |
| `morphology` | `0x40010000` | 3×3 腐蚀，右下锚点 |
| `rgb2gray` | `0x40020000` | width / height |
| `threshold` | `0x40030000` | width / height / thresh |
| AXI GPIO | `0x40040000` | 蜂鸣器 |
| AXI DMA | `0x41E00000` | DMA 控制 |

更多接口细节见 [`docs/接口协议.md`](docs/接口协议.md)。

---

## 7. 主要交付文件校验

优化版 overlay（推荐上板使用）：

```text
SHA256 (intrusion_detection_optimized.bit) =
  78e325fcb43c73fe2c45fbe6f0c21a86dcb2db1acc8a50384810f9c954771ee4
SHA256 (intrusion_detection_optimized.hwh) =
  7e5b68b2906ab9995801db006d94fa067833a727075d2588dd689c64a64be716
```

---

## 8. 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

---

## 9. 致谢

- AMD/Xilinx 学生开发竞赛
- PYNQ 开源社区
- 本项目由队长 + 队友 A（FPGA 优化）+ 队友 B（软件新功能）协作完成
