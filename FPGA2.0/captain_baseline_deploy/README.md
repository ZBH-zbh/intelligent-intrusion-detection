# 队长原版部署包

此目录只包含队长已经跑通的基线产物，不包含优化 bitstream。

上传位置：

| 本目录文件 | PYNQ 目标路径 |
|---|---|
| `design_1_wrapper.bit` | `/home/xilinx/design_1_wrapper.bit` |
| `design_1_wrapper.hwh` | `/home/xilinx/design_1_wrapper.hwh` |
| `pl_motion_detection_buzzer.py` | `/home/xilinx/jupyter_notebooks/pl_motion_detection_buzzer.py` |
| `test_buzzer.py` | `/home/xilinx/jupyter_notebooks/test_buzzer.py` |
| `pl_motion_detection_smooth.py` | `/home/xilinx/jupyter_notebooks/pl_motion_detection_smooth.py`，备用 |

BIT/HWH 必须保持同名。主脚本已经固定从 `/home/xilinx/design_1_wrapper.bit` 加载队长基线。

## SHA-256

```text
CE606CF8DCF112E893E28A2FA0CF9837A380F876164D7BC1A35C68D75CD0F28E  design_1_wrapper.bit
04C235AD5094E0621B40074DECC3CDAA01C10B2D98436B37E649B1ACEE5FDF95  design_1_wrapper.hwh
496828BBFFB282717CA9C5011A3310ABE7881B8764F4477255188A85015A4F5E  pl_motion_detection_buzzer.py
2FE0DE1ED5CA5BAB72C6A51A0692A892328FD42425F9BA8D21EED1B3582BC20B  test_buzzer.py
6E72A754CEB63B46E8276FEEF0829AF6C4DAC4BCD5BC730BACE4A547BB565E63  pl_motion_detection_smooth.py
```

加载 overlay、测试蜂鸣器和摄像头前仍需确认硬件连接。当前本机尚未发现可达的板卡 IP。
