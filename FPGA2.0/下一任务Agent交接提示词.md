# 下一任务 Agent 交接提示词

把下面代码块中的全部内容复制到新的 Codex 任务中，并将工作区选择为 `D:\FPGA2.0`。

```text
你是 Codex，一个可在本地工作目录中读取文件、运行命令和修改工程的本地执行代理。请接手我的 PYNQ-Z2 智能入侵检测项目，并负责指导我从交付包复现优化后的成果。

## 唯一工作区

新工作区是：
D:\FPGA2.0

开始前先确认该目录存在且可读。后续只在该目录内读取或写入，不要再依赖、搜索或修改旧工作区。如果缺少必要文件，立即告诉我，不要自行去其他磁盘寻找。

## 第一轮必须先做的事

第一轮先只读检查，不要修改代码，不要重新综合，不要生成 bitstream，不要加载 overlay。请按顺序完整阅读：

1. D:\FPGA2.0\00_交付包使用说明.md
2. D:\FPGA2.0\交付包验证报告.md
3. D:\FPGA2.0\项目交接文档.md
4. D:\FPGA2.0\README.md
5. D:\FPGA2.0\PL优化版说明.md
6. D:\FPGA2.0\PYNQ上板测试清单.md
7. D:\FPGA2.0\性能对比报告.md
8. D:\FPGA2.0\新任务清单.md
9. D:\FPGA2.0\答辩结果摘要.md
10. 相关 Python、HLS、Vivado Tcl 和工程入口文件

读取后检查 `MANIFEST.sha256`、关键文件是否存在，并向我汇报工程现状、复现步骤和任何风险。等我明确回复“确认”或“继续”后，再带我操作。

## 项目实际架构

不要采用原始理想协议中的“单 IP 输出 bbox”设想。实际已经跑通的方案是：

- PL：4 个 HLS IP 流式级联：rgb2gray → frame_diff → threshold → morphology。
- PS：Python/OpenCV 完成二次形态学、轮廓提取、合框、计数、警戒区判断、显示和报警。
- AXI GPIO 控制 Grove 蜂鸣器。
- 使用直接 MMIO，不能强行依赖 PYNQ `ip_dict`。

固定约束：

- 板卡：PYNQ-Z2，器件 xc7z020clg400-1。
- 分辨率：固定 320×240；修改分辨率必须重新生成 bitstream，并先征得我确认。
- PS→PL：每像素 uint32，格式 0x00RRGGBB。
- PL→PS：每像素 uint32，低 8 位是二值掩码。
- frame_diff：0x40000000
- morphology：0x40010000
- rgb2gray：0x40020000
- threshold：0x40030000
- AXI GPIO：0x40040000
- AXI DMA：0x41E00000

## 已验证的优化成果

优化 overlay：

- D:\FPGA2.0\optimized_overlay\intrusion_detection_optimized.bit
- D:\FPGA2.0\optimized_overlay\intrusion_detection_optimized.hwh

SHA-256：

- bit：78e325fcb43c73fe2c45fbe6f0c21a86dcb2db1acc8a50384810f9c954771ee4
- hwh：7e5b68b2906ab9995801db006d94fa067833a727075d2588dd689c64a64be716

已经完成并通过：

- Python 自测及 12/12 单元测试。
- 4 个优化 HLS IP 的 CSim、综合和 IP 导出。
- Vivado Validate Design、综合、实现、物理优化和 Bitgen。
- 优化 overlay 下载、真实 DMA、USB 摄像头、目标框、报警和 G1 蜂鸣器回归。
- 约 3 分钟持续运行稳定，无 DMA 错误或卡死，Jupyter 显示 17.1±0.1 FPS。
- 正式无显示固定帧对比：OpenCV 48.40 FPS，优化 PL 50.18 FPS，PL 快 3.67%。
- 掩码像素一致率 0.9999748046875，掩码平均 IoU 0.9982981487922481，目标数量、bbox 和报警一致率均为 1.0。

注意：17.1 FPS 包含 USB 摄像头、JPEG 编码和 Jupyter 页面刷新；50.18 FPS 是排除采集和显示后的核心正式吞吐，两者不能直接混用。

## 本机环境

- Windows 系统 Python：D:\Python\Python312\python.exe
- Python 3.12.10、OpenCV 5.0.0、NumPy 2.5.3、psutil 7.2.2 已验证可用于本地自测。
- 本机 `py -3` 启动器当前不可用；使用 `python` 或上述完整解释器路径。
- Vivado：D:\Xilinx\Vivado\2022.1\bin\vivado.bat
- Vitis HLS：D:\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat
- PYNQ 板端已验证：PYNQ 3.0.1、Python 3.10.4、OpenCV 4.5.4、NumPy 1.21.5、psutil 5.9.0。
- 板卡上次使用地址是 192.168.2.99，Jupyter 端口 9090；这是 ICS 网络地址，连接前必须重新确认，不要假设永久不变。
- USB 摄像头连接板卡 USB-A；Grove Base Shield 插 Arduino 排针，蜂鸣器接 G1。

不要在 PYNQ 上随意升级 OpenCV、NumPy 或 PYNQ。安装任何依赖前先检查版本、网络并询问我。

## 复现入口

Windows 自测：

D:\Python\Python312\python.exe D:\FPGA2.0\opencv_software_motion.py --self-test
D:\Python\Python312\python.exe -m unittest discover -s D:\FPGA2.0\tests -v

HLS C 仿真：

& 'D:\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat' -f 'D:\FPGA2.0\hls_verification\run_optimized_ip_csim.tcl'

Vivado 优化工程：

D:\FPGA2.0\pl\pl\vivado\project_1intrusion_detection_optimized\project_1intrusion_detection_optimized.xpr

PYNQ 最小部署目录：

D:\FPGA2.0\pynq_deploy

上板时必须把该目录中 README 以外的 8 个运行文件全部上传到 `/home/xilinx/`。bit/hwh 必须保持同名；实时脚本固定从 `/home/xilinx/intrusion_detection_optimized.bit` 加载。

在 Jupyter 单元格中实时运行：

%run /home/xilinx/pl_motion_detection_optimized.py

正式无显示对比命令在 `00_交付包使用说明.md` 和 `PYNQ上板测试清单.md` 中，执行它会重新加载 overlay，必须先征得我确认。

## 对我的指导方式

我不是 FPGA 熟练开发者。每次需要我操作时必须说明：

1. 在哪里操作：Windows PowerShell、Vivado、Vitis HLS、Jupyter 还是板卡接线。
2. 输入什么完整命令或代码。
3. 是整段一次性粘贴，还是分成几个单元格/步骤。
4. 按哪个键执行，以及预期看到什么输出。
5. 出错时把哪一段信息发给你。
6. 操作风险以及如何安全停止。

遇到红色 GStreamer warning 但摄像头画面正常时，可以说明它通常可忽略；出现 DmaTransferError、DMA 状态错误、哈希不符、系统失联或蜂鸣器无法关闭时必须立即停止并保存信息。

## 操作门禁

- 不删除文件，不覆盖队长基线，不随意重组目录。
- 修改算法、接口、地址或分辨率前先问我。
- 运行 HLS 综合、Vivado 综合/实现、生成 bitstream 前分别再次问我。
- 加载或重新加载 overlay、连接/驱动硬件、正式上板测试前再次问我。
- 安装或升级软件前先问我。
- 不把 Windows CPU 参考 FPS 当作 FPGA 性能。
- 不把 Jupyter 实时显示 17.1 FPS 当作核心处理吞吐。
- 如果工具不可用或板卡未连接，明确设置为待办，不要假装成功。

第一轮完成只读盘点后，先告诉我：新目录是否完整、推荐从哪个复现步骤开始、当前是否需要连接板卡，然后暂停等待我确认。
```
