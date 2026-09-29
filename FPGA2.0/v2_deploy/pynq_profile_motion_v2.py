"""Profile the PS-side stages for the PL v2 pipeline (close+open in PL)."""

import argparse
import json
from pathlib import Path
import statistics
import time

import cv2
import numpy as np
import psutil

from benchmark_motion import generate_synthetic_frames
from motion_common import (
    HEIGHT,
    WIDTH,
    check_alarm,
    detect_targets,
)
from pl_motion_detection_v2 import (
    DMA_BASE_ADDR,
    FRAME_DIFF_BASE,
    RGB2GRAY_BASE,
    THRESHOLD_BASE,
    AP_CTRL,
    SimpleAxiDMA,
    configure_ip,
)
from pynq import MMIO, Overlay


def summarize(samples):
    values = np.asarray(samples, dtype=np.float64)
    return {
        "mean_ms": statistics.fmean(samples),
        "p50_ms": float(np.percentile(values, 50)),
        "p95_ms": float(np.percentile(values, 95)),
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Profile PS-side stages for the PL v2 motion detector"
    )
    parser.add_argument("--bitstream", default="./intrusion_detection_v2.bit")
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--frames", type=int, default=200)
    parser.add_argument("--poll-sleep-us", type=float, default=100.0)
    parser.add_argument("--output", default="profile_results_v2.json")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.warmup < 1 or args.frames < 1 or args.poll_sleep_us < 0:
        raise ValueError(
            "warmup and frames must be positive; poll sleep must not be negative"
        )

    try:
        from pynq import allocate
    except ImportError as exc:
        raise RuntimeError("This profiler must run on a PYNQ image") from exc

    print(f"Loading overlay {args.bitstream} ...")
    overlay = Overlay(args.bitstream)
    overlay.download()
    print("Overlay loaded")

    frames = generate_synthetic_frames(args.warmup + args.frames)
    pixel_count = WIDTH * HEIGHT
    transfer_bytes = pixel_count * np.dtype(np.uint32).itemsize

    input_buffer = None
    output_buffer = None
    stages = {
        "pack_rgb32": [],
        "start_hls_ips": [],
        "input_flush": [],
        "dma_registers": [],
        "dma_wait": [],
        "output_invalidate": [],
        "extract_mask": [],
        "contours_alarm": [],
        "frame_total": [],
    }

    try:
        dma = SimpleAxiDMA(
            DMA_BASE_ADDR, poll_sleep_seconds=args.poll_sleep_us / 1_000_000.0
        )
        rgb2gray = MMIO(RGB2GRAY_BASE, 0x10000)
        frame_diff = MMIO(FRAME_DIFF_BASE, 0x10000)
        threshold = MMIO(THRESHOLD_BASE, 0x10000)
        morph_instances = []
        configure_ip(rgb2gray, frame_diff, threshold, morph_instances)

        input_buffer = allocate(shape=(pixel_count,), dtype=np.uint32)
        output_buffer = allocate(
            shape=(pixel_count,), dtype=np.uint32, cacheable=True
        )
        input_bytes = input_buffer.view(np.uint8).reshape(HEIGHT, WIDTH, 4)
        input_bytes[:, :, 3] = 0
        output_bytes = output_buffer.view(np.uint8).reshape(HEIGHT, WIDTH, 4)
        raw_mask = np.empty((HEIGHT, WIDTH), dtype=np.uint8)

        all_ips = [rgb2gray, frame_diff, threshold, *morph_instances]

        process = psutil.Process()
        process_before = None
        measured_wall_started = None

        for index, frame in enumerate(frames):
            if index == args.warmup:
                process_before = process.cpu_times()
                measured_wall_started = time.perf_counter()

            frame_started = time.perf_counter()

            started = time.perf_counter()
            cv2.mixChannels([frame], [input_bytes], [0, 0, 1, 1, 2, 2])
            pack_done = time.perf_counter()

            for ip in all_ips:
                ip.write(AP_CTRL, 0x01)
            ips_started = time.perf_counter()

            if hasattr(input_buffer, "flush"):
                input_buffer.flush()
            flush_done = time.perf_counter()

            dma.mmio.write(dma.MM2S_DMASR, dma.IRQ_CLEAR_MASK)
            dma.mmio.write(dma.S2MM_DMASR, dma.IRQ_CLEAR_MASK)
            dma.mmio.write(dma.S2MM_DA, output_buffer.physical_address)
            dma.mmio.write(dma.S2MM_LENGTH, transfer_bytes)
            dma.mmio.write(dma.MM2S_SA, input_buffer.physical_address)
            dma.mmio.write(dma.MM2S_LENGTH, transfer_bytes)
            registers_done = time.perf_counter()

            dma._wait_for_idle()
            wait_done = time.perf_counter()

            if hasattr(output_buffer, "invalidate"):
                output_buffer.invalidate()
            invalidate_done = time.perf_counter()

            cv2.mixChannels([output_bytes], [raw_mask], [0, 0])
            extract_done = time.perf_counter()

            targets = detect_targets(raw_mask)
            check_alarm(targets)
            frame_done = time.perf_counter()

            if index >= args.warmup:
                stages["pack_rgb32"].append((pack_done - started) * 1000.0)
                stages["start_hls_ips"].append(
                    (ips_started - pack_done) * 1000.0
                )
                stages["input_flush"].append(
                    (flush_done - ips_started) * 1000.0
                )
                stages["dma_registers"].append(
                    (registers_done - flush_done) * 1000.0
                )
                stages["dma_wait"].append(
                    (wait_done - registers_done) * 1000.0
                )
                stages["output_invalidate"].append(
                    (invalidate_done - wait_done) * 1000.0
                )
                stages["extract_mask"].append(
                    (extract_done - invalidate_done) * 1000.0
                )
                stages["contours_alarm"].append(
                    (frame_done - extract_done) * 1000.0
                )
                stages["frame_total"].append(
                    (frame_done - frame_started) * 1000.0
                )

        measured_wall_seconds = time.perf_counter() - measured_wall_started
        process_after = process.cpu_times()
        process_seconds = (
            process_after.user
            + process_after.system
            - process_before.user
            - process_before.system
        )
    finally:
        if input_buffer is not None:
            input_buffer.freebuffer()
        if output_buffer is not None:
            output_buffer.freebuffer()

    summary = {name: summarize(values) for name, values in stages.items()}
    total_mean = summary["frame_total"]["mean_ms"]
    for name, values in summary.items():
        values["percent_of_frame"] = 100.0 * values["mean_ms"] / total_mean

    payload = {
        "notice": "PL v2 profiler: morphology close+open runs in PL.",
        "bitstream": args.bitstream,
        "warmup_frames": args.warmup,
        "measured_frames": args.frames,
        "poll_sleep_us": args.poll_sleep_us,
        "process_cpu_one_core_percent": (
            100.0 * process_seconds / measured_wall_seconds
        ),
        "process_cpu_total_capacity_percent": (
            100.0
            * process_seconds
            / measured_wall_seconds
            / (psutil.cpu_count(logical=True) or 1)
        ),
        "fps_from_mean_latency": 1000.0 / total_mean,
        "stages": summary,
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("stage                     mean_ms     p50_ms     p95_ms   percent")
    for name, values in summary.items():
        print(
            "{:<24} {:>9.3f} {:>10.3f} {:>10.3f} {:>8.2f}%".format(
                name,
                values["mean_ms"],
                values["p50_ms"],
                values["p95_ms"],
                values["percent_of_frame"],
            )
        )
    print(
        "fps_from_mean_latency={:.2f}".format(payload["fps_from_mean_latency"])
    )
    print(
        "process_cpu_one_core_percent={:.2f}".format(
            payload["process_cpu_one_core_percent"]
        )
    )
    print(
        "process_cpu_total_capacity_percent={:.2f}".format(
            payload["process_cpu_total_capacity_percent"]
        )
    )
    print("results={}".format(output.resolve()))


if __name__ == "__main__":
    main()
