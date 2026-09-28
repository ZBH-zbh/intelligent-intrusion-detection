"""
单独测试 Grove Buzzer 的 AXI GPIO 控制。
用法：先加载带 AXI GPIO 的 bitstream，然后运行本脚本，蜂鸣器会响 5 声。
"""

from pynq import Overlay, MMIO
import time

BITSTREAM = "/home/xilinx/design_1_wrapper.bit"
BUZZER_BASE = 0x40040000

print("Loading bitstream...")
ol = Overlay(BITSTREAM)
ol.download()
print("Bitstream loaded")

buzzer = MMIO(BUZZER_BASE, 0x10000)
# 把 bit0 配置为输出（GPIO_TRI 偏移 0x04，写 0 表示输出）
buzzer.write(0x04, 0xFFFFFFFE)
buzzer.write(0x00, 0)

print("Beeping 5 times...")
for i in range(5):
    buzzer.write(0x00, 1)
    time.sleep(0.2)
    buzzer.write(0x00, 0)
    time.sleep(0.2)
    print(f"  beep {i+1}/5")

print("Done")
