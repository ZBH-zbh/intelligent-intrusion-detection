# PYNQ-Z2 PL v2 部署说明（PL 完成 close+open）

本目录新增 `pl_motion_detection_v2.py` 与 `pynq_compare_motion_v2.py`，配合 `intrusion_detection_v2.bit` / `intrusion_detection_v2.hwh` 使用。

## 需要上传到 `/home/xilinx/` 的文件

- `intrusion_detection_v2.bit`
- `intrusion_detection_v2.hwh`
- `pl_motion_detection_v2.py`
- `pynq_compare_motion_v2.py`
- `motion_common.py`
- `opencv_software_motion.py`
- `benchmark_motion.py`

`pl_motion_detection_optimized.py` 等旧文件可保留作为对照。

## 生成 bitstream 后的检查

在 Vivado 实现完成后：

```bash
cd /home/xilinx
sha256sum intrusion_detection_v2.bit intrusion_detection_v2.hwh
```

当前版本哈希值（Vivado 2022.1，xc7z020clg400-1）：

```text
7a9bbf08ba8b47d8c88bfa31e7774bd921ffad8363113b52ac042e4fb20d01a7  intrusion_detection_v2.bit
7cad032bf51c358cd46c32c34623989249f5e7df62eaef1b4639d4bacdb4d03f  intrusion_detection_v2.hwh
```

## 实时运行

```python
%run /home/xilinx/pl_motion_detection_v2.py
```

## 正式无显示对比（PL v2 vs OpenCV 纯软件）

```bash
cd /home/xilinx
python3 pynq_compare_motion_v2.py \
  --bitstream /home/xilinx/intrusion_detection_v2.bit \
  --source synthetic \
  --warmup 20 --frames 200 --repeats 3 --min-seconds 5 \
  --opencv-threads 1 --dma-poll-sleep-us 100 \
  --output-root /home/xilinx/pynq_results_v2
```

## PL v2 地址映射

| 模块 | 基地址 | 配置 |
|---|---|---|
| frame_diff | 0x40000000 | width/height |
| morphology_ex_0 | 0x40010000 | op=1, kernel=7（dilate） |
| rgb2gray | 0x40020000 | width/height |
| threshold | 0x40030000 | width/height/thresh |
| axi_gpio | 0x40040000 | 蜂鸣器 |
| morphology_ex_1 | 0x40050000 | op=0, kernel=7（erode） |
| morphology_ex_2 | 0x40060000 | op=0, kernel=3（erode） |
| morphology_ex_3 | 0x40070000 | op=1, kernel=3（dilate） |
| axi_dma | 0x41E00000 | DMA 控制 |

## 回退

若 PL v2 上板异常，可继续使用旧的 `intrusion_detection_optimized.bit` 与 `pl_motion_detection_optimized.py`。
