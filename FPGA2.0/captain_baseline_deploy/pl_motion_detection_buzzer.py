"""
PYNQ-Z2 智能入侵检测系统 - 流畅显示 + 优化画框 + 报警区域 + Grove Buzzer 版本

前提：Vivado Block Design 中已经加入 AXI GPIO，并把它的一根输出引脚接到
Grove Base Shield 的某个 G 端口信号线上（默认按 G1=D2=AR2=U13）。
生成新的 bitstream 后，把这个脚本和 .bit/.hwh 一起传到 PYNQ 运行。
"""

from pynq import Overlay, allocate, MMIO
import cv2
import numpy as np
import time
import ipywidgets as widgets
from IPython.display import display

# ====================== 配置参数 ======================
BITSTREAM = "/home/xilinx/design_1_wrapper.bit"
WIDTH = 320
HEIGHT = 240
THRESH = 30                 # PL 二值化阈值
MIN_CONTOUR_AREA = 300      # 最小目标面积
MAX_CONTOUR_AREA = 50000    # 最大目标面积（过滤整个画面抖动）
ALARM_ZONE = (85, 45, 150, 150)  # 警戒区域 (x, y, w, h)，画面中心

# AXI-Lite 基地址
DMA_BASE_ADDR = 0x41E00000
FRAME_DIFF_BASE = 0x40000000
MORPHOLOGY_BASE = 0x40010000
RGB2GRAY_BASE = 0x40020000
THRESHOLD_BASE = 0x40030000

# 新增的 AXI GPIO 基地址（在 Vivado Address Editor 里手动指定为 0x40040000）
BUZZER_BASE = 0x40040000

# 蜂鸣器使能开关：如果还没生成带 GPIO 的 bitstream，可以设 False 先跑图像部分
USE_BUZZER = True

# 蜂鸣器报警频率（Hz），即每秒响/停几次
BUZZER_BEEP_HZ = 4

# 寄存器偏移
AP_CTRL = 0x00
WIDTH_REG = 0x10
HEIGHT_REG = 0x18
THRESH_REG = 0x20

# AXI GPIO 数据寄存器偏移
GPIO_DATA_REG = 0x00


# ====================== AXI DMA MMIO 驱动 ======================
class SimpleAxiDMA:
    def __init__(self, base_addr, addr_range=0x10000):
        self.mmio = MMIO(base_addr, addr_range)
        self.mmio.write(0x00, 0x04)
        self.mmio.write(0x30, 0x04)
        time.sleep(0.01)
        self.mmio.write(0x00, 0x01)
        self.mmio.write(0x30, 0x01)

    def transfer(self, src_buf, dst_buf, length):
        self.mmio.write(0x48, dst_buf.physical_address)
        self.mmio.write(0x58, length)
        self.mmio.write(0x18, src_buf.physical_address)
        self.mmio.write(0x28, length)
        while not (self.mmio.read(0x04) & 0x02):
            pass
        while not (self.mmio.read(0x34) & 0x02):
            pass


# ====================== 蜂鸣器控制 ======================
class BuzzerGPIO:
    """用 MMIO 控制 AXI GPIO 的一位输出。"""

    def __init__(self, base_addr, enable=True):
        self.enable = enable
        self.mmio = None
        if not enable:
            print("Buzzer disabled (USE_BUZZER=False)")
            return
        try:
            self.mmio = MMIO(base_addr, 0x10000)
            # AXI GPIO 默认是输入，需要把 bit0 设为输出：GPIO_TRI 偏移 0x04，写 0 表示输出
            self.mmio.write(0x04, 0xFFFFFFFE)
            self.off()
            print(f"Buzzer GPIO initialized at 0x{base_addr:08X}")
        except Exception as e:
            print(f"Buzzer GPIO init failed: {e}")
            self.enable = False

    def _write(self, value):
        if self.mmio is not None:
            self.mmio.write(GPIO_DATA_REG, value & 0x1)

    def on(self):
        self._write(1)

    def off(self):
        self._write(0)

    def update(self, alarm_status):
        """根据报警状态更新蜂鸣器：报警时按 BUZZER_BEEP_HZ 频率间歇响。"""
        if not self.enable or self.mmio is None:
            return
        if alarm_status:
            # 用时间取相位，实现周期性 beep，不需要额外线程
            beep_phase = int(time.time() * BUZZER_BEEP_HZ) & 1
            self._write(beep_phase)
        else:
            self.off()


# ====================== 辅助函数 ======================

def pack_rgb32(frame_rgb):
    """RGB 打包成 32 位 0x00RRGGBB"""
    flat = frame_rgb.reshape(-1, 3).astype(np.uint32)
    return (flat[:, 0] << 16) | (flat[:, 1] << 8) | flat[:, 2]


def process_mask(raw_mask):
    """
    对 PL 返回的二值掩码做后处理：
    - 闭运算连接断裂区域
    - 开运算去除小噪点
    """
    mask = raw_mask.copy()
    kernel_close = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    kernel_open = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    return mask


def merge_nearby_boxes(boxes, distance_thresh=30):
    """合并距离较近或重叠的边界框，避免一个目标被分成多个框。"""
    if not boxes:
        return []

    boxes = sorted(boxes, key=lambda b: b[0])
    merged = [list(boxes[0])]

    for x, y, w, h in boxes[1:]:
        px, py, pw, ph = merged[-1]
        px2, py2 = px + pw, py + ph
        x2, y2 = x + w, y + h

        overlap_x = not (x2 + distance_thresh < px or x - distance_thresh > px2)
        overlap_y = not (y2 + distance_thresh < py or y - distance_thresh > py2)

        if overlap_x and overlap_y:
            nx = min(px, x)
            ny = min(py, y)
            nx2 = max(px2, x2)
            ny2 = max(py2, y2)
            merged[-1] = [nx, ny, nx2 - nx, ny2 - ny]
        else:
            merged.append([x, y, w, h])

    return [tuple(b) for b in merged]


def detect_targets(mask):
    """在二值掩码上检测运动目标，返回合并后的边界框列表。"""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    raw_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if MIN_CONTOUR_AREA <= area <= MAX_CONTOUR_AREA:
            raw_boxes.append(cv2.boundingRect(cnt))

    return merge_nearby_boxes(raw_boxes)


def check_alarm(targets, zone=ALARM_ZONE):
    """判断是否有目标边界框与警戒区域重叠。"""
    zx, zy, zw, zh = zone
    zx2, zy2 = zx + zw, zy + zh
    for x, y, w, h in targets:
        x2, y2 = x + w, y + h
        if x < zx2 and x2 > zx and y < zy2 and y2 > zy:
            return True
    return False


def draw_overlay(frame, targets, fps, alarm_status):
    """在原始帧上画警戒区、目标框、计数、FPS、报警状态。"""
    ax, ay, aw, ah = ALARM_ZONE
    zone_color = (0, 0, 255) if alarm_status else (255, 0, 0)
    cv2.rectangle(frame, (ax, ay), (ax + aw, ay + ah), zone_color, 2)

    for x, y, w, h in targets:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.putText(frame, f"Targets: {len(targets)}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    status_text = "ALARM!" if alarm_status else "Normal"
    status_color = (0, 0, 255) if alarm_status else (0, 255, 0)
    cv2.putText(frame, status_text, (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

    return frame


# ====================== 主流程 ======================

def main():
    print("Loading bitstream...")
    ol = Overlay(BITSTREAM)
    ol.download()
    print("Bitstream loaded")

    dma = SimpleAxiDMA(DMA_BASE_ADDR)
    rgb2gray = MMIO(RGB2GRAY_BASE, 0x10000)
    frame_diff = MMIO(FRAME_DIFF_BASE, 0x10000)
    threshold = MMIO(THRESHOLD_BASE, 0x10000)
    morphology = MMIO(MORPHOLOGY_BASE, 0x10000)

    for ip in [rgb2gray, frame_diff, threshold, morphology]:
        ip.write(WIDTH_REG, WIDTH)
        ip.write(HEIGHT_REG, HEIGHT)
    threshold.write(THRESH_REG, THRESH)

    in_buf = allocate(shape=(HEIGHT * WIDTH,), dtype=np.uint32)
    out_buf = allocate(shape=(HEIGHT * WIDTH,), dtype=np.uint32)

    buzzer = BuzzerGPIO(BUZZER_BASE, enable=USE_BUZZER)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    image_widget = widgets.Image(format='jpeg', width=640, height=480)
    display(image_widget)

    count = 0
    start = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            in_buf[:] = pack_rgb32(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            for ip in [rgb2gray, frame_diff, threshold, morphology]:
                ip.write(AP_CTRL, 0x01)
            dma.transfer(in_buf, out_buf, WIDTH * HEIGHT * 4)

            # PS 后处理
            raw_mask = (out_buf & 0xFF).reshape((HEIGHT, WIDTH)).astype(np.uint8)
            mask = process_mask(raw_mask)
            targets = detect_targets(mask)
            alarm_status = check_alarm(targets)

            # 蜂鸣器联动
            buzzer.update(alarm_status)

            count += 1
            fps = count / (time.time() - start)

            vis = draw_overlay(frame.copy(), targets, fps, alarm_status)
            _, buf = cv2.imencode('.jpg', vis)
            image_widget.value = buf.tobytes()

    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        buzzer.off()
        cap.release()
        in_buf.freebuffer()
        out_buf.freebuffer()
        print("Resources released")


if __name__ == "__main__":
    main()
