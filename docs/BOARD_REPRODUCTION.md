# PYNQ-Z2 板端复现指南

本指南说明如何把最终版程序在 PYNQ-Z2 上跑通。

## 1. 准备文件

需要把 `FPGA2.0/optimized_overlay/` 和 `FPGA2.0/pynq_deploy/` 里的文件传到 PYNQ。推荐目录：

```bash
/home/xilinx/intrusion_demo/
```

必需文件：

```text
intrusion_detection_optimized.bit
intrusion_detection_optimized.hwh
pl_motion_detection_optimized.py
pynq_compare_motion.py
motion_common.py
opencv_software_motion.py
benchmark_motion.py
```

如需队友 B 的跟踪 / 越线 / Web 配置功能，再上传 `FPGA2.0/new_features/` 下的相关模块。

## 2. 上传方式

### 2.1 用 scp（推荐）

在 PC 上打开 PowerShell / Git Bash：

```bash
cd C:\Users\ZBH\intelligent-intrusion-detection\FPGA2.0
scp optimized_overlay/intrusion_detection_optimized.bit \
   optimized_overlay/intrusion_detection_optimized.hwh \
   pynq_deploy/*.py \
   xilinx@192.168.2.99:/home/xilinx/intrusion_demo/
```

> 把 `192.168.2.99` 换成你 PYNQ 的实际 IP。

### 2.2 用 Jupyter 上传

登录 `http://<pynq-ip>:9090`，在文件浏览器里把文件拖到 `/home/xilinx/intrusion_demo/`。

## 3. 实时演示

SSH 登录 PYNQ：

```bash
ssh xilinx@192.168.2.99
cd /home/xilinx/intrusion_demo
```

### 3.1 在 Jupyter 里运行（有画面）

打开浏览器 `http://<pynq-ip>:9090`，新建 Notebook，执行：

```python
%run pl_motion_detection_optimized.py
```

正常应看到：

- 摄像头画面窗口（或 Jupyter 里的图片输出）
- 绿色目标框
- 警戒区矩形
- 进入警戒区后右上角显示 **ALARM!** 并听到蜂鸣器响

### 3.2 无界面命令行运行

```bash
cd /home/xilinx/intrusion_demo
python3 pl_motion_detection_optimized.py --camera 0 --display 0
```

适合只验证功能而不看画面的场景。

## 4. 正式 OpenCV vs PL 对比测试

```bash
cd /home/xilinx/intrusion_demo
python3 pynq_compare_motion.py \
  --bitstream ./intrusion_detection_optimized.bit \
  --source synthetic \
  --warmup 20 --frames 200 --repeats 3 --min-seconds 5 \
  --opencv-threads 1 --dma-poll-sleep-us 100 \
  --output-root ./pynq_results
```

预期结果（参考）：

| 指标 | 数值 |
|---|---|
| OpenCV FPS | ~48.4 |
| 优化 PL FPS | ~50.2 |
| 相对加速比 | ~1.04× |
| 单核 CPU（OpenCV） | ~99.98% |
| 单核 CPU（PL） | ~96.25% |
| 掩码像素一致率 | > 0.9999 |
| 掩码平均 IoU | > 0.998 |
| 目标数 / bbox / 报警一致率 | 1.0 |

## 5. 校验 bitstream 完整性

在 PYNQ 上执行：

```bash
cd /home/xilinx/intrusion_demo
sha256sum intrusion_detection_optimized.bit intrusion_detection_optimized.hwh
```

应与下面哈希完全一致：

```text
78e325fcb43c73fe2c45fbe6f0c21a86dcb2db1acc8a50384810f9c954771ee4  intrusion_detection_optimized.bit
7e5b68b2906ab9995801db006d94fa067833a727075d2588dd689c64a64be716  intrusion_detection_optimized.hwh
```

## 6. 常见问题

### 6.1 摄像头打不开

- 确认 USB 摄像头插在 PYNQ 的 USB HOST 口，必要时使用带独立供电的 USB Hub。
- 在 PYNQ 上测试：

```bash
python3 -c "import cv2; cap=cv2.VideoCapture(0); print(cap.read())"
```

### 6.2 DMA 超时或画面卡住

- 检查 `.bit` 和 `.hwh` 是否同名且在同一目录。
- 检查各 AXI-Lite IP 地址是否与 `motion_common.py` 一致。
- 若网络 DHCP 导致 Jupyter 断开，建议给 PYNQ 设置静态 IP。

### 6.3 蜂鸣器不响

- 确认 `buzzer.xdc` 引脚约束与实际硬件一致。
- 在 Jupyter 里先跑 `test_buzzer.py` 测试 GPIO。

## 7. 进一步使用新功能

队友 B 新增的跟踪、越线计数、Web 配置等功能位于 `FPGA2.0/new_features/`。

典型用法示例：

```bash
python3 new_features/tracker_server.py --deploy /home/xilinx/intrusion_demo
```

然后用浏览器打开 `http://<pynq-ip>:8080/` 进行拖拽配置。

更多细节见 `FPGA2.0/new_features/README.md`。
