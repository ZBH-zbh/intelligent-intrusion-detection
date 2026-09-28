# OpenCV 纯软件版说明

## 1. 文件

| 文件 | 作用 |
|---|---|
| `motion_common.py` | PL/软件共用的掩码后处理、轮廓、合框、报警和绘制逻辑 |
| `opencv_software_motion.py` | OpenCV 纯软件实时运动检测程序 |
| `tests/test_opencv_software.py` | 不依赖摄像头的自动测试 |

## 2. 算法口径

纯软件版固定使用 320×240、阈值 30，流程为：

```text
BGR -> OpenCV 灰度 -> 相邻帧绝对差 -> threshold(>30)
    -> 模拟当前 PL 的 3×3 腐蚀
    -> 7×7 闭运算 -> 3×3 开运算
    -> 轮廓 -> 面积过滤 -> 合框 -> 警戒区判断
```

第一帧只用于建立上一帧背景，返回空掩码。正式对比也必须先用相同第一帧分别初始化软件状态和 PL 的帧缓存，然后从下一帧开始计数。

当前 HLS 灰度公式与 `cv2.cvtColor(..., COLOR_BGR2GRAY)` 存在最多约 1～2 个灰度级的舍入差异。测试代码保留了 HLS 整数公式参考实现，阶段 4 会量化该差异对阈值掩码的影响。

## 3. Windows 本地运行

先执行无摄像头自测：

```powershell
D:\FPGA2.0\.venv\Scripts\python.exe D:\FPGA2.0\opencv_software_motion.py --self-test
```

运行全部自动测试：

```powershell
D:\FPGA2.0\.venv\Scripts\python.exe -m unittest discover -s D:\FPGA2.0\tests -v
```

使用摄像头窗口运行，按 `q` 退出：

```powershell
D:\FPGA2.0\.venv\Scripts\python.exe D:\FPGA2.0\opencv_software_motion.py --source 0 --display window
```

读取视频文件但不显示：

```powershell
D:\FPGA2.0\.venv\Scripts\python.exe D:\FPGA2.0\opencv_software_motion.py --source D:\FPGA2.0\sample.mp4 --display none
```

## 4. PYNQ Jupyter 运行

板卡恢复连接后，把 `motion_common.py` 和 `opencv_software_motion.py` 上传到同一目录，在 Notebook 中执行：

```python
%run /home/xilinx/jupyter_notebooks/opencv_software_motion.py --source 0 --display jupyter
```

该版本不加载 overlay，也不驱动物理蜂鸣器；报警状态会显示在画面上。这样可保证它是 PS/OpenCV 纯软件基准。

## 5. 注意事项

- 当前实时脚本显示的 FPS 用于运行观察，不作为最终比赛数据。
- 正式 FPS、CPU 和一致性数据由阶段 4 的统一 benchmark 工具生成。
- 目前未修改队长的 PL 脚本，公共逻辑将在确认后接入新的优化版 PL 脚本。

## 6. 本地基准流程验证

```powershell
D:\FPGA2.0\.venv\Scripts\python.exe D:\FPGA2.0\benchmark_motion.py --source synthetic --warmup 20 --frames 200 --repeats 3 --min-seconds 1.0 --output-root D:\FPGA2.0\results
```

该命令比较 OpenCV 标准灰度和当前 HLS 整数灰度参考，验证 FPS、CPU、掩码、bbox
和报警指标的采集流程。它不调用 FPGA，结果不能当作 PL 加速数据。

板卡连接后的真实 PL 对比使用 `D:\FPGA2.0\pynq_compare_motion.py`，具体步骤见
`D:\FPGA2.0\PYNQ上板测试清单.md`。
