# Agent 提示词：安装并配置 Vivado / Vitis HLS 2022.1

> 直接整段复制给新的 harness 会话使用。
> 本提示词中的路径、大小、密码、加密状态均已由前一个 Agent 实测核实，不需要重新猜测或下载。

---

```text
你是运行在 Windows 本机的执行代理。请帮我安装并配置 Vivado / Vitis HLS 2022.1，
使其能够复现我本机上的 PYNQ-Z2 智能入侵检测 FPGA 工程。安装包已经下载好了，不要联网下载任何安装器。

## 一、已核实的事实（直接用，不要重新探测）

### 安装包位置与形态
- 目录：E:\vivado\13_Vivado_2022.1\
- 文件：Xilinx_Unified_2022.1_0420_0327.zip.001 ~ .zip.008（共 8 个分卷）
- 总大小：73.81 GB（前 7 卷各 10,000,000,000 字节，第 8 卷 9,253,114,183 字节）
- 这是【单个 zip 的字节分卷】，不是 zip 内建分卷。拼接后即得到完整的
  Xilinx_Unified_2022.1_0420_0327.zip
- 压缩包【已加密】：zip local header 的 general purpose flag = 0x0001，
  压缩方法 method = 8（deflate），属于传统 ZipCrypto（不是 AES）
- 解压密码：AriesOpenFPGA
  （记录在 E:\vivado\13_Vivado_2022.1\解压密码.txt）
- 压缩包内顶层目录为 Xilinx_Unified_2022.1_0420_0327/，
  内含 api-ms-win-core-*.dll 等文件，即【完整离线安装器的展开内容】

### 其他相关文件
- E:\vivado\一定要看我.txt —— 说明文件
- E:\vivado\13_Vivado_2022.1\Vivado2022.2安装教程.pdf —— 教程（版本 2022.2，可参考）
- E:\vivado\license\license_ip_2037.lic 和 license_ip_2110_12.lic —— IP 授权文件
- 本机已装 WinRAR（C:\Program Files\WinRAR\WinRAR.exe）和 bsdtar（tar 命令）
- 本机【没有】7-Zip

### 本机环境
- 系统：Windows，当前用户 asus（属于 Administrators，但进程是未提权的 UAC 过滤令牌）
- E: 盘可用空间 848.8 GB
- 已建好 E:\fpga\env（Python 3.12.10 + venv 已就位，本项目 Python 侧已复现通过）
- 工程目录：E:\fpga\project\FPGA2.0
- 已有复现指南：E:\fpga\project\复现指南.md
- 已有自检脚本：E:\fpga\project\check_env.ps1

## 二、硬约束（必须遵守）

1. **版本必须是 2022.1，不要换版本。**
   工程的 .xpr 和 .bd 都是 Vivado 2022.1 生成的，Vivado 无法打开比自己新版本创建的工程。
   装 2021.x 会导致工程打不开。

2. **安装目录必须是 E:\fpga\env\Xilinx。**
   【绝对不要用 E:\app\vivado】—— E:\app 是 DSH harness 的安装目录，
   其 NTFS 权限对普通用户只有 ReadAndExecute，未提权进程无法创建子目录
   （实测 mkdir 返回 Access is denied）。这是 Windows 权限限制，不是沙箱限制，
   不要尝试提权绕过，直接使用 E:\fpga\env\Xilinx。

3. **不要联网下载安装器，不要登录 AMD 账号。** 安装包已在本地。

4. **不要删除 E:\vivado 下的任何原始文件。** 磁盘空间足够，不需要为了省空间删源包。
   如果确实需要回收空间，只在【全部验证通过之后】再单独问我。

5. **不要修改工程里的任何文件**，除了下面第四节明确列出的验证动作。
   特别是不要动 pl\pl\hls_optimized 下的源码和 optimized_overlay 下的 bit/hwh。

## 三、执行步骤

### 步骤 1：准备解压（先问我确认再执行）
风险提示：这一步会写入大量数据（拼接 73.81 GB + 解压约 75 GB），耗时可能数十分钟到数小时。
执行前先告诉我预计占用空间和耗时，等我确认。

推荐方案（本机没有 7-Zip，先装一个再解压最稳）：
1. 从官网下载 7-Zip 安装到 E:\fpga\env\tools\7-Zip
   （7-Zip 原生支持 .001/.002 分卷和 ZipCrypto 加密 zip，也方便命令行自动化）
2. 直接用 7-Zip 打开 .zip.001 即可识别整个分卷组，无需手工拼接：
   7z.exe x E:\vivado\13_Vivado_2022.1\Xilinx_Unified_2022.1_0420_0327.zip.001 -pAriesOpenFPGA -oE:\fpga\env\vivado_installer

备选方案（如果不想装 7-Zip）：
1. 用 cmd 拼接：copy /b 001+002+...+008 得到完整 zip
2. 用 WinRAR 解压到 E:\fpga\env\vivado_installer，密码 AriesOpenFPGA
   注意：WinRAR 对 .zip.001 命名的支持不稳定，所以拼接这一步不能省。

解压完成后确认 E:\fpga\env\vivado_installer\Xilinx_Unified_2022.1_0420_0327\ 下
存在安装器入口（通常是 xsetup.exe 或 xsetup.bat，以及 data\ 目录）。把实际入口文件名告诉我。

### 步骤 2：选择安装组件（先问我确认再执行）
用安装器的 batch 模式做无人值守安装。Xilinx 统一安装器支持：
  xsetup.exe -b ConfigGen        （生成配置，交互一次）
  xsetup.exe -b Install -c <config.txt> -l <log>

选组件时严格按下面来，不要多选（多选会多占几十 GB）：
- 版本：Vivado ML Standard（标准版即可，Zynq-7020 在免费范围内，无需付费 License）
- 必选组件：Vivado、Vitis HLS
- 不要选：Vitis Embedded、PetaLinux、Model Composer、Vitis Analyzer 之外的东西、
  以及任何 Documentation/Example 包（除非体积很小）
- 器件支持：只勾 Zynq-7000 和 7 Series
  （本工程目标器件是 xc7z020clg400-1，即 PYNQ-Z2）
- 安装目录：E:\fpga\env\Xilinx

关于 License：E:\vivado\license 下的 .lic 文件先不要加载。
本工程只用到 Zynq PS、AXI DMA、AXI GPIO、AXI Interconnect、proc_sys_reset
和 4 个自研 HLS IP，全部属于免费范围，不需要额外授权。
只有在后续综合/实现报 License 错误时，我们再来处理授权问题。

### 步骤 3：配置环境
安装完成后：
1. 确认这两个入口存在：
   E:\fpga\env\Xilinx\Vivado\2022.1\bin\vivado.bat
   E:\fpga\env\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat
   （如果实际版本目录名不同，以实际为准并告诉我真实路径）
2. 确认 xc7z020clg400-1 器件库已安装
3. 在 E:\fpga\env\ 下写一个 enable_xilinx.ps1，把两个工具加入当前会话 PATH，
   方便后续调用（不要改系统级环境变量，除非我明确同意）

### 步骤 4：验证安装（自动完成，做完汇报）
1. 运行 vivado -version，确认输出 2022.1
2. 运行 vitis_hls -version，确认输出 2022.1
3. 跑 HLS C 仿真（该 Tcl 用 [info script] 自解析路径，不需要改路径）：
   & 'E:\fpga\env\Xilinx\Vitis_HLS\2022.1\bin\vitis_hls.bat' -f 'E:\fpga\project\FPGA2.0\hls_verification\run_optimized_ip_csim.tcl'
   预期：All optimized HLS IP C tests passed，0 error
4. 跑 Vivado 工程验证（同样自解析路径）：
   & 'E:\fpga\env\Xilinx\Vivado\2022.1\bin\vivado.bat' -mode batch -source 'E:\fpga\project\FPGA2.0\vivado_optimization\verify_prepared_project.tcl'
   预期：validate_bd_design 无红色报错，LOCKED_IP_COUNT=0，
   六条 ADDRESS_SEGMENT 地址与下面这张表一致：

   frame_diff 0x40000000 / morphology 0x40010000 / rgb2gray 0x40020000 /
   threshold 0x40030000 / AXI GPIO 0x40040000 / AXI DMA 0x41E00000

5. 跑 E:\fpga\project\check_env.ps1，确认第 5 节"Xilinx 工具链"两项由 TODO 变成 OK

### 步骤 5：汇报
把下面这些如实汇报给我，不要美化：
- 安装包是否成功解压，实际安装器入口是什么
- 实际安装目录和工具版本
- HLS CSim 的完整结论（通过/失败，失败把关键报错原文给我）
- Vivado 工程验证的完整结论，六条地址是否匹配
- 实际占用磁盘空间
- check_env.ps1 的最新结果
- 任何警告、报错、或你不确定的地方

## 四、门禁（必须遵守）

- 运行 HLS 综合（csynth）、Vivado 综合/实现、生成 bitstream 之前，必须分别再问我确认
- 加载 overlay、连接板卡、驱动硬件之前必须问我
- 不要为了"让流程跑通"而修改工程源码、Block Design、AXI 地址或分辨率
- 不要重新生成 bitstream 覆盖 optimized_overlay 下已验证的文件
  （那两个文件 SHA-256 与队友实机验收版本完全一致，是唯一的已验证产物）
- 如果工具不可用或某步失败，如实标为待办，不要假装成功

## 五、参考文档

- E:\fpga\project\复现指南.md —— 本机复现指南（含完整 7 步流程）
- E:\fpga\project\check_env.ps1 —— 环境自检脚本
- E:\fpga\project\FPGA2.0\00_交付包使用说明.md —— 交付包总览
- E:\fpga\project\FPGA2.0\项目交接文档.md —— 原始接口与地址定义
- E:\fpga\project\FPGA2.0\PYNQ上板测试清单.md —— 上板五里程碑

## 六、第一轮只做这些

第一轮不要执行任何安装或解压动作。请先：
1. 读 E:\fpga\project\复现指南.md 和本提示词
2. 只读确认 E:\vivado 下的分卷、密码文件、教程 PDF 都在
3. 只读确认 E:\fpga\env\Xilinx 可写、E: 剩余空间足够
4. 告诉我：你打算用哪种解压方案（7-Zip 还是拼接+WinRAR）、预计空间与耗时、需要我确认什么
然后停下来等我确认。
```

---

## 附：本提示词依据的实测结论

| 项目 | 实测值 |
|---|---|
| 分卷数量 | 8 |
| 总分卷大小 | 73.81 GB |
| 单卷大小 | 10,000,000,000 字节（前 7 卷）；第 8 卷 9,253,114,183 字节 |
| zip 首签名 | `50 4B 03 04`（合法 zip） |
| general purpose flag | `0x0001`（bit0 = 已加密） |
| 压缩方法 | `8`（deflate，传统 ZipCrypto，非 AES） |
| 解压密码 | `AriesOpenFPGA` |
| 包内顶层目录 | `Xilinx_Unified_2022.1_0420_0327/` |
| E: 可用空间 | 848.8 GB |
| 预计总占用 | 拼接 73.81 GB + 解压约 75 GB + 安装约 30~40 GB ≈ 185 GB |
| 本机解压工具 | WinRAR 有，7-Zip 无，bsdtar 有 |
