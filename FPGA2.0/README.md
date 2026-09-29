# PYNQ-Z2 智能入侵检测：PL 优化与 OpenCV 对比

更新时间：2026-09-14

## 1. 当前结论

项目以队长已跑通的 4 个 HLS IP 级联方案为基线：

```text
PS RGB32 -> AXI DMA -> rgb2gray -> frame_diff -> threshold -> morphology
         <- AXI DMA <- 二值掩码低 8 位
PS: 轮廓、面积过滤、合框、警戒区、蜂鸣器
```

优化 HLS、独立 IP 仓库、Vivado 工程和 bit/hwh 均已生成并完成上板回归。实现后 LUT 减少 5.84%、寄存器减少 8.71%、DSP 减少 81.25%，100 MHz 时序通过。PYNQ 正式对比中，OpenCV 为 48.40 FPS，优化 PL 为 50.18 FPS（1.04×），PL 单核 CPU 为 96.25%，低于 OpenCV 的 99.98%；五项效果一致性全部通过。摄像头、目标框、报警和 G1 蜂鸣器联动均已验证。

## 2. 固定接口

- 器件：PYNQ-Z2，`xc7z020clg400-1`
- 分辨率：320×240
- 输入：PS→PL，每像素 uint32，格式 `0x00RRGGBB`
- 输出：PL→PS，每像素 uint32，低 8 位为二值掩码
- frame_diff：`0x40000000`
- morphology：`0x40010000`
- rgb2gray：`0x40020000`
- threshold：`0x40030000`
- AXI GPIO：`0x40040000`
- AXI DMA：`0x41E00000`

板端代码继续使用直接 MMIO，不依赖 `ip_dict`。

## 3. 运行环境分工

| 环境 | 用途 |
|---|---|
| Windows 本地 | Python 自动测试、OpenCV 算法验证、本地参考基准、HLS/Vivado 构建 |
| PYNQ PS ARM | 正式 OpenCV vs 真实 PL 性能/一致性对比、摄像头和蜂鸣器验收 |

正式性能对比必须在 PYNQ PS 上进行。Windows 数据只能证明软件和统计流程可运行，不能代表 PL 加速效果。

## 4. 主要交付物

| 交付物 | 路径 |
|---|---|
| OpenCV 纯软件版 | `D:\FPGA2.0\opencv_software_motion.py` |
| 公共后处理 | `D:\FPGA2.0\motion_common.py` |
| 优化 PL 实时版 | `D:\FPGA2.0\pl_motion_detection_optimized.py` |
| Windows 本地基准 | `D:\FPGA2.0\benchmark_motion.py` |
| PYNQ 正式对比工具 | `D:\FPGA2.0\pynq_compare_motion.py` |
| PYNQ 分阶段诊断工具 | `D:\FPGA2.0\pynq_profile_motion.py` |
| 优化 bit/hwh | `D:\FPGA2.0\optimized_overlay` |
| 优化 HLS 源码 | `D:\FPGA2.0\pl\pl\hls_optimized` |
| 优化 Vivado 工程 | `D:\FPGA2.0\pl\pl\vivado\project_1intrusion_detection_optimized` |
| 优化建议 | `D:\FPGA2.0\优化建议清单.md` |
| 新任务清单 | `D:\FPGA2.0\新任务清单.md` |
| HLS 综合对比 | `D:\FPGA2.0\HLS综合对比报告.md` |
| Vivado 实现对比 | `D:\FPGA2.0\Vivado实现对比报告.md` |
| 性能对比总表 | `D:\FPGA2.0\性能对比报告.md` |
| 最终 PYNQ 原始结果 | `D:\FPGA2.0\results\pynq_final_20260914_081017` |
| 上板步骤 | `D:\FPGA2.0\PYNQ上板测试清单.md` |

## 5. Windows 验证

```powershell
D:\FPGA2.0\.venv\Scripts\python.exe D:\FPGA2.0\opencv_software_motion.py --self-test
D:\FPGA2.0\.venv\Scripts\python.exe -m unittest discover -s D:\FPGA2.0\tests -v
D:\FPGA2.0\.venv\Scripts\python.exe D:\FPGA2.0\benchmark_motion.py --source synthetic --warmup 20 --frames 200 --repeats 3 --min-seconds 1.0 --output-root D:\FPGA2.0\results
```

当前自动测试结果为 12/12 通过。已有本地基准结果位于：

`D:\FPGA2.0\results\20260913_145855`

## 6. PYNQ 正式对比复现

加载 overlay 前先获得上板确认。把 bit/hwh 和 Python 文件放到同一工作目录，然后执行无显示、无摄像头、无蜂鸣器的固定帧测试：

```bash
cd /home/xilinx
python3 pynq_compare_motion.py \
  --bitstream /home/xilinx/intrusion_detection_optimized.bit \
  --source synthetic --warmup 20 --frames 200 --repeats 3 \
  --min-seconds 5 --opencv-threads 1 --dma-poll-sleep-us 100 \
  --output-root /home/xilinx/pynq_results
```

该命令会实际下载 bitstream。详细前置检查和故障处理见 `PYNQ上板测试清单.md`。

## 7. 已验证与边界

已验证：HLS CSim/综合/IP 导出，Vivado Validate Design/综合/布局布线/物理优化/Bitgen，Windows 自动测试 12/12，PYNQ 环境和 OpenCV 自测，真实 overlay/DMA，正式 FPS/CPU/一致性，以及摄像头和蜂鸣器联动。

板端环境：Python 3.10.4、OpenCV 4.5.4、NumPy 1.21.5、psutil 5.9.0、PYNQ 3.0.1。优化版已完成约 3 分钟持续回归，实时 Jupyter 演示稳定在 17.1±0.1 FPS，受摄像头、JPEG 和网页刷新限制；正式无显示吞吐以 `pynq_final_20260914_081017` 为准。

不要把 Windows 的 7779.55 FPS 或 HLS CPU 参考的 2666.68 FPS 写成 FPGA 性能。
