# PYNQ-Z2 上板测试清单

本清单已于 2026-09-14 在 PYNQ-Z2 上执行通过，也可用于后续复现。每次加载 overlay、操作摄像头和测试蜂鸣器前仍需确认。

## 里程碑 A：连接和环境检查

1. 确认 PYNQ-Z2 正常启动，电脑能访问板卡 Jupyter 页面。
2. 打开 Terminal 或 Notebook，运行：

```bash
python3 --version
python3 -c "import cv2; print('opencv', cv2.__version__)"
python3 -c "import pynq; print('pynq', pynq.__version__)"
python3 -c "import psutil; print('psutil', psutil.__version__)"
jupyter --version
```

预期：五条命令都正常打印版本。任何包缺失时先停止，不要直接升级 PYNQ 系统包；记录完整报错，再决定是否联网安装。

本次实测版本：Python 3.10.4、OpenCV 4.5.4、NumPy 1.21.5、psutil 5.9.0、PYNQ 3.0.1。

## 里程碑 B：上传和校验

上传到 `/home/xilinx/`：

- `intrusion_detection_optimized.bit`
- `intrusion_detection_optimized.hwh`
- `motion_common.py`
- `opencv_software_motion.py`
- `benchmark_motion.py`
- `pl_motion_detection_optimized.py`
- `pynq_compare_motion.py`

在板端校验：

```bash
cd /home/xilinx
sha256sum intrusion_detection_optimized.bit intrusion_detection_optimized.hwh
```

预期：

- BIT：`78e325fcb43c73fe2c45fbe6f0c21a86dcb2db1acc8a50384810f9c954771ee4`
- HWH：`7e5b68b2906ab9995801db006d94fa067833a727075d2588dd689c64a64be716`

哈希不同则停止，不加载 overlay。

## 里程碑 C：固定帧正式对比

此步骤会下载优化 bitstream，但不访问摄像头、不驱动蜂鸣器：

```bash
cd /home/xilinx
python3 pynq_compare_motion.py \
  --bitstream /home/xilinx/intrusion_detection_optimized.bit \
  --source synthetic --warmup 20 --frames 200 --repeats 3 \
  --min-seconds 5 --opencv-threads 1 --dma-poll-sleep-us 100 \
  --output-root /home/xilinx/pynq_results
```

预期：命令打印 6 条轮次结果，最后给出结果目录和五项一致性指标。将整个时间戳结果目录下载回 `D:\FPGA2.0\results\pynq\`。

本次正式结果已保存到 `D:\FPGA2.0\results\pynq_final_20260914_081017`：OpenCV 48.40 FPS，优化 PL 50.18 FPS；PL 单核 CPU 96.25%，OpenCV 99.98%。

如果发生 `DmaTransferError`，停止重复尝试并保存 MM2S/S2MM `DMASR` 十六进制值。

## 里程碑 D：真实视频复测

此项为可选扩展，当前正式结论使用确定性合成帧。若需要答辩现场的视频复测，先把固定的 320×240 测试视频上传为 `/home/xilinx/test.mp4`，再运行同一命令，仅把 `--source synthetic` 改为：

```bash
--source /home/xilinx/test.mp4
```

视频至少需要 220 帧。程序会先读入同一批帧，再分别交给两个后端，视频读取不计入性能时间。

## 里程碑 E：实时功能回归

固定帧 benchmark 通过后，连接 USB 摄像头，在 Jupyter 中执行：

```python
%run /home/xilinx/pl_motion_detection_optimized.py
```

逐项确认：

- 摄像头输出为 320×240 或能稳定缩放到该尺寸。
- 首帧不误报。
- 运动目标有框，静止后告警消失。
- 警戒区重叠时显示 ALARM。
- 蜂鸣器只在告警时动作，停止程序后保持关闭。
- 基础验收连续运行至少 3 分钟，无 DMA 超时或卡死；如需长时间现场展示，可选做 10 分钟压力测试并观察是否有明显内存增长。

2026-09-14 已完成约 3 分钟持续回归：摄像头、目标框、报警、G1 蜂鸣器、中断和资源释放全部通过，未出现 DMA 错误或卡死，Jupyter 实时显示稳定在 17.1±0.1 FPS。该结果满足基本稳定性验收；若答辩需要长时间现场演示，可再选做 10 分钟压力测试。

## 停止条件

出现以下任一情况立即停止并保留日志：overlay 下载失败、bit/hwh 哈希不符、DMA 错误位、DMA 超时、系统失联、蜂鸣器无法关闭。不要通过反复重载 overlay 掩盖故障。
