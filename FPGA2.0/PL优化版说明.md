# PL Python 优化版说明

更新时间：2026-09-14

## 文件与兼容原则

- 优化版入口：`D:\FPGA2.0\pl_motion_detection_optimized.py`
- 公共算法：`D:\FPGA2.0\motion_common.py`
- 队长原脚本未覆盖：`D:\FPGA2.0\pl_motion_detection_buzzer.py`
- 分辨率仍固定为 320×240，输入仍为 `0x00RRGGBB`，输出仍只取低 8 位。
- AXI-Lite 地址保持交接文档中的实际地址，继续用 MMIO，不依赖 `ip_dict`。
- 已生成独立命名的优化 bit/hwh，没有覆盖队长基线；没有启用 `auto_restart`。

## 本轮改动

1. Overlay 使用 `download=False` 构造后只显式下载一次。
2. DMA 增加 1 秒超时、MM2S/S2MM 错误位检查和完整状态打印，避免无限忙等。
3. 输入使用非缓存 DMA 缓冲区，输出使用可缓存 DMA 缓冲区；DMA 前后显式调用输入 `flush()` 和输出 `invalidate()`。
4. 输入和输出都使用 OpenCV `mixChannels`：输入严格生成 `0x00RRGGBB`，输出等价提取 32-bit 字中的低 8 位，避免在非缓存 CMA 上进行多轮 NumPy 扫描。
5. 掩码后处理、轮廓、合框、报警和绘制统一复用 `motion_common.py`。
6. Jupyter JPEG 显示默认每 2 个处理帧刷新一次，处理 FPS 用最近 30 帧计算。
7. 所有退出路径都尝试关闭蜂鸣器、释放摄像头和 PYNQ 缓冲区。
8. DMA 等待循环默认休眠 100 us；板端实测在保持吞吐的同时把单核 CPU 从约 100% 降到 96.25%。

## 本地验证结果

- Python 单元测试：12/12 通过。
- RGB32 打包和低字节提取：与原公式逐像素完全一致。
- 320×240 打包微基准（Windows 本机，1000 次）：旧方法约 0.3277 ms/帧，新方法约 0.1789 ms/帧，约 1.83×。
- 板端分阶段诊断：原路径 49.43 ms/帧，最终非对称缓冲和双向 `mixChannels` 为 19.70 ms/帧；100 us 轮询实验为 19.63 ms/帧、单核 CPU 96.08%。
- 正式三轮结果：OpenCV 48.40 FPS，优化 PL 50.18 FPS；PL 单核 CPU 96.25%，OpenCV 99.98%。
- 优化 overlay、DMA 连续传输、摄像头、目标框、报警、G1 蜂鸣器和异常清理均已上板验证；约 3 分钟持续回归稳定，未出现 DMA 错误或卡死。

## 上板方式

把以下文件放在 PYNQ 的同一目录：

- `pl_motion_detection_optimized.py`
- `motion_common.py`
- `D:\FPGA2.0\optimized_overlay\intrusion_detection_optimized.bit`
- `D:\FPGA2.0\optimized_overlay\intrusion_detection_optimized.hwh`

复制到 `/home/xilinx/` 后，脚本默认 `BITSTREAM` 已指向 `/home/xilinx/intrusion_detection_optimized.bit`。在 Jupyter 单元中运行：

```python
%run /home/xilinx/pl_motion_detection_optimized.py
```

保持 `DISPLAY_EVERY_N_FRAMES = 2`、`DMA_TIMEOUT_SECONDS = 1.0` 和 `DMA_POLL_SLEEP_SECONDS = 0.0001`。如果出现 `DmaTransferError`，保留异常中两路 `DMASR` 十六进制值，不要反复重载 overlay；该状态可用于判断是数据流未启动、TLAST 缺失还是 DMA 通道错误。

## 已验证边界与后续方向

- PYNQ 3.0.1 已验证支持当前 overlay、缓存同步和可缓存 CMA 缓冲区用法。
- 实时 Jupyter 显示稳定在 17.1±0.1 FPS，受摄像头/JPEG/网页刷新限制，不代表核心吞吐。
- 最终最大耗时是双方共用的 PS 形态学后处理，约 12.17 ms/帧；若需要显著高于 1.04× 的加速，应评估把 7×7 闭运算和 3×3 开运算迁移到 PL。
- 未启用 HLS `auto_restart`；当前每帧启动开销仅约 0.14 ms，收益空间有限。
