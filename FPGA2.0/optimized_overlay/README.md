# 优化 Overlay 交付说明

生成时间：2026-09-13  
目标器件：PYNQ-Z2，`xc7z020clg400-1`  
生成工具：Vivado 2022.1

## 文件

- `intrusion_detection_optimized.bit`：优化 PL bitstream。
- `intrusion_detection_optimized.hwh`：与 bitstream 对应的硬件描述。两个文件必须保持相同主文件名并放在同一目录。
- `timing_summary_before_bitstream.rpt`：写 bitstream 前的时序复核。
- `drc_before_bitstream.rpt`：写 bitstream 前的 DRC 复核。
- `SHA256SUMS.txt`：交付文件校验值。

## 生成验收

- Vivado：`Bitgen Completed Successfully`
- bitstream 大小：4,045,676 字节
- WNS：+0.225 ns
- WHS：+0.031 ns
- DRC：0 Error、0 Critical Warning、4 Warning、2 Advisory
- 优化 HLS `COREREVISION`：`2114784485`

## 固定接口

| 模块 | AXI-Lite 基地址 |
|---|---:|
| frame_diff | `0x40000000` |
| morphology | `0x40010000` |
| rgb2gray | `0x40020000` |
| threshold | `0x40030000` |
| AXI GPIO | `0x40040000` |
| AXI DMA | `0x41E00000` |

分辨率固定 320×240。PS→PL 为每像素 32-bit `0x00RRGGBB`；PL→PS 二值掩码低 8 位有效。

## 上板方式与验证状态

将以下 4 个文件复制到 PYNQ 的 `/home/xilinx/`：

1. 本目录中的 `intrusion_detection_optimized.bit`
2. 本目录中的 `intrusion_detection_optimized.hwh`
3. `D:\FPGA2.0\pl_motion_detection_optimized.py`
4. `D:\FPGA2.0\motion_common.py`

然后在 Jupyter 中运行：

```python
%run /home/xilinx/pl_motion_detection_optimized.py
```

2026-09-14 已完成上板验收：bit/hwh 哈希匹配，overlay 下载、DMA、摄像头、检测框、报警、G1 蜂鸣器和资源释放均正常；约 3 分钟持续运行稳定，Jupyter 实时显示 17.1±0.1 FPS。正式无显示固定帧结果为 OpenCV 48.40 FPS、优化 PL 50.18 FPS，详见 `D:\FPGA2.0\results\pynq_final_20260914_081017`。
