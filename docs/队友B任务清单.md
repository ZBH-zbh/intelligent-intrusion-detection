# 队友 B 任务清单（Python / OpenCV / PS 应用）

## 角色定位

负责 PS（ARM 处理系统）端开发，包括 Python 应用、OpenCV 图像处理、摄像头采集、调用 PL 加速、UI 显示、入侵报警逻辑，以及性能对比实验。

---

## 第 1 周：基础入门

### 任务 B1：搭建本地 Python + OpenCV 环境

- **目标**：在自己电脑上能运行 OpenCV
- **安装内容**：
  ```bash
  pip install opencv-python opencv-contrib-python numpy matplotlib jupyter
  ```
- **交付物**：一段能读取图片并显示成功的 Python 代码
- **截止时间**：第 1 周末
- **验收标准**：`import cv2` 不报错，能显示图片

### 任务 B2：学习 OpenCV 基础操作

- **目标**：掌握以下函数
  - `cv2.imread` / `cv2.imshow`
  - `cv2.cvtColor`（BGR ↔ 灰度 ↔ RGB）
  - `cv2.threshold`（二值化）
  - `cv2.morphologyEx`（开运算/闭运算）
  - `cv2.findContours`（轮廓检测）
  - `cv2.boundingRect`（外接矩形）
  - `cv2.rectangle`（画框）
- **交付物**：`ps/notebooks/opencv_basics.ipynb`
- **截止时间**：第 1 周末
- **验收标准**：能独立完成一张图片的灰度化、二值化、画框

### 任务 B3：在本地实现纯软件帧差法

- **目标**：用电脑摄像头或一个视频文件跑通运动检测
- **功能要求**：
  - 读取视频流
  - 帧差法检测运动
  - 二值化 + 形态学去噪
  - 轮廓检测 + 画框
- **交付物**：`ps/notebooks/software_frame_diff.ipynb`
- **截止时间**：第 1 周末
- **验收标准**：在本地能看到运动目标被绿色框标记

---

## 第 2 周：PYNQ 摄像头与显示

### 任务 B4：在 PYNQ 上读取 USB 摄像头

- **目标**：摄像头到货后，能在 PYNQ 的 Jupyter 里采集画面
- **测试代码**：
  ```python
  import cv2
  cap = cv2.VideoCapture(0)
  ret, frame = cap.read()
  print(frame.shape)
  ```
- **交付物**：`ps/notebooks/camera_test.ipynb`
- **截止时间**：第 2 周初
- **验收标准**：能在 Jupyter 里打印出画面尺寸，如 `(480, 640, 3)`

### 任务 B5：在 Jupyter 中实时显示视频

- **目标**：把本地帧差法 demo 搬到 PYNQ Jupyter 里
- **显示方式**：用 matplotlib 或 IPython.display
- **交付物**：`ps/notebooks/live_display.ipynb`
- **截止时间**：第 2 周中
- **验收标准**：能在 Jupyter 里实时看到摄像头画面

### 任务 B6：实现画框与目标计数

- **目标**：在检测到运动目标后，在原图上画框并显示数量
- **功能**：
  - 过滤小面积噪声
  - 每个目标画一个矩形框
  - 在画面左上角显示 `Targets: X`
- **交付物**：`ps/notebooks/draw_bbox_count.ipynb`
- **截止时间**：第 2 周末
- **验收标准**：画面中有几个人动，就显示几个框

---

## 第 3 周：调用 PL 与应用逻辑

### 任务 B7：学习 PYNQ Overlay 调用

- **目标**：理解怎么用 Python 配置 PL 寄存器
- **学习内容**：
  - `from pynq import Overlay`
  - `ol.ip_dict`
  - `ip.write(offset, value)`
  - `ip.read(offset)`
- **交付物**：一段能读写 AXI-Lite 寄存器的测试代码
- **截止时间**：第 3 周初
- **验收标准**：能向队长解释 MMIO 读写原理

### 任务 B8：把视频帧发送给 PL 处理

- **目标**：用 Python 把摄像头采集的帧传给 FPGA
- **方式**：根据 `docs/接口协议.md` 中的方案 A 或方案 B
- **交付物**：`ps/notebooks/pl_frame_process.ipynb`
- **截止时间**：第 3 周中
- **验收标准**：PL 返回的结果能被 PS 正确读取

### 任务 B9：实现入侵判断逻辑

- **目标**：判断运动目标是否进入警戒区域
- **输入**：
  - 目标 bounding box（x, y, w, h）
  - 警戒区域（alarm_zone_x, y, w, h）
- **输出**：报警状态 0/1
- **交付物**：入侵判断函数
- **截止时间**：第 3 周中
- **验收标准**：目标进入区域时 alarm_status = 1

### 任务 B10：接入 Grove Buzzer 报警

- **目标**：入侵时蜂鸣器响
- **控制方式**：通过 Grove Base Shield 的 GPIO
- **参考**：PYNQ GPIO 控制
- **交付物**：`ps/src/alarm.py`
- **截止时间**：第 3 周末
- **验收标准**：alarm_status = 1 时蜂鸣器发声

### 任务 B11：整合完整应用

- **目标**：把所有功能串起来
- **流程**：
  1. 采集视频
  2. 传给 PL 或用纯软件处理
  3. 获取目标坐标
  4. 画框 + 计数
  5. 入侵判断
  6. 触发报警
  7. Jupyter 显示
- **交付物**：`ps/notebooks/main_app.ipynb`
- **截止时间**：第 3 周末
- **验收标准**：系统能稳定运行，检测到入侵时蜂鸣器响

---

## 第 4 周：对比实验与文档

### 任务 B12：实现 PS 纯软件版本

- **目标**：保留一套完整的纯软件实现作为基准
- **交付物**：`ps/notebooks/software_only.ipynb`
- **截止时间**：第 4 周初
- **验收标准**：不加载任何 overlay 也能跑运动检测

### 任务 B13：做 PS 纯软件 vs PL 加速性能对比

- **目标**：量化 FPGA 加速效果
- **对比指标**：
  - 帧率 FPS
  - CPU 占用率
  - 端到端延迟
- **交付物**：`docs/性能对比报告.md`
- **截止时间**：第 4 周中
- **验收标准**：有数据、有图表、有结论

### 任务 B14：整理 Python 端文档

- **目标**：写清楚 PS 端代码结构和使用方法
- **交付物**：
  - `docs/Python应用说明.md`
  - `docs/使用手册.md`
- **截止时间**：第 4 周末
- **验收标准**：别人能根据文档跑通 Python 应用

---

## 关键技能要求

- Python 基础
- OpenCV 图像处理
- Jupyter Notebook
- PYNQ Overlay 调用
- 基础 GPIO 控制

## 需要阅读的文档

- `docs/需求分析.md`
- `docs/接口协议.md`
- `docs/开发计划.md`
- PYNQ 官方文档
- OpenCV Python 教程
