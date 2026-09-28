# HLS 独立验证

该目录只用于验证队长交付的四个 HLS 源文件，不修改原有 HLS 工程，也不生成 bitstream。

运行 Vitis HLS 2022.1 C 仿真：

```powershell
& 'D:\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat' -f 'D:\FPGA2.0\hls_verification\run_current_ip_csim.tcl'
```

测试覆盖 RGB 打包/灰度公式、阈值边界、前后帧差分状态、当前 3×3 腐蚀的边界与 TLAST 传递。生成目录固定为 `D:\FPGA2.0\hls_verification\build`。

运行优化副本的 C 仿真：

```powershell
& 'D:\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat' -f 'D:\FPGA2.0\hls_verification\run_optimized_ip_csim.tcl' -l 'optimized_ip_csim_run.log'
```

优化版测试固定处理完整的 320×240 帧，并额外验证尺寸寄存器错误时输出清零。该命令仍然只执行 C 仿真，不执行 HLS 综合。

经用户单独确认后，运行四个优化 IP 的 HLS 综合：

```powershell
& 'D:\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat' -f 'D:\FPGA2.0\hls_verification\run_optimized_ip_csynth.tcl' -l 'optimized_ip_csynth_run.log'
```

综合工程生成在 `D:\FPGA2.0\hls_verification\build\optimized_csynth`。该脚本不包含 `export_design`，不会导出 IP 或生成 bitstream。
