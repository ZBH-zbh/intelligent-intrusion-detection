# HLS 优化说明

更新时间：2026-09-13

## 范围

本轮只新增优化源码副本并执行 C 仿真，没有修改队长原始源码、运行 HLS 综合、替换 Vivado IP 或生成 bitstream。

- 原始源码：`D:\FPGA2.0\pl\pl\hls`
- 优化副本：`D:\FPGA2.0\pl\pl\hls_optimized`
- 优化测试：`D:\FPGA2.0\hls_verification\test_motion_ips_optimized.cpp`
- 仿真入口：`D:\FPGA2.0\hls_verification\run_optimized_ip_csim.tcl`
- 仿真日志：`D:\FPGA2.0\hls_verification\optimized_ip_csim_run.log`

## R10：去除动态帧尺寸乘法

队长版本的循环次数由运行时 `width * height` 产生。旧综合调度报告明确显示该乘法器延迟约 6.91 ns，并在各 IP 中占用约 3 个 DSP。

优化副本把每帧循环次数固定为项目实际约束的 76800。源码中不再存在运行时 `width * height`；函数名、AXI4-Stream 32 位数据接口、width/height/thresh 的 AXI-Lite 参数接口保持不变。

HLS 综合已确认四个动态帧尺寸乘法器被消除：HLS DSP 合计从 14 降到 2，减少 12 个；四个模块的像素循环均保持 II=1。详细数据见 `D:\FPGA2.0\HLS综合对比报告.md`。

## R11：固定 320×240 与错误尺寸保护

四个 IP 都固定消费并输出 76800 个流元素。只有 `width == 320` 且 `height == 240` 时输出正常结果；尺寸寄存器错误时仍完成固定长度的流传输，但把输出数据清零。

这种处理符合当前工程固定 320×240 的约束，并避免 frame_diff 帧缓冲或 morphology 行缓冲因错误参数而越界。PS/DMA 仍必须发送 76800 个 32 位像素；该约束没有改变。

## R09-A：保持 morphology 基线

本轮没有把 morphology 改成开运算。它仍是队长当前实现：

- 3×3 腐蚀；
- 使用以当前输入像素为右下角的因果窗口；
- 前两行和前两列输出清零；
- TLAST 原样传递。

完整帧测试额外放置了一个孤立零像素，验证其影响出现在对应的 3×3 因果输出区域，确保没有无意改变锚点。

## C 仿真结果

Vitis HLS 2022.1 输出：

```text
All optimized HLS IP C tests passed.
INFO: [SIM 211-1] CSim done with 0 errors.
```

覆盖内容：

- RGB32 灰度公式和整帧 TLAST；
- 阈值 30 的严格大于语义；
- 错误 width 参数时整帧输出清零；
- frame_diff 连续两帧状态和 8 位差值；
- morphology 边界、因果锚点和孤立零像素传播。

编译日志中的 `__GMP_LIBGMP_DLL redefined` 来自 Vitis HLS 2022.1 自带头文件，在队长基线与优化版中都会出现；它是警告，CSim 最终为 0 错误。

## 下一门禁

四个顶层的 HLS 综合已经完成。下一步是导出新的 IP 仓库，并在 Vivado 工程副本中替换四个 IP；执行 IP 导出和 Vivado 综合/实现前需要用户再次确认，生成 bitstream 前还要单独确认。
