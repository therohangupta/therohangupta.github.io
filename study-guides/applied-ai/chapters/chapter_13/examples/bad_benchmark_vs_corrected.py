#!/usr/bin/env python3
"""Bad vs corrected benchmark shape.

This file does not require CUDA. It shows the measurement structure you should use
when timing asynchronous accelerator work.
"""

from time import perf_counter, sleep


def fake_gpu_launch():
    # A real CUDA op would often enqueue work and return before completion.
    return "launched"


def fake_synchronize():
    # A real benchmark would call torch.cuda.synchronize().
    sleep(0.01)


start = perf_counter()
fake_gpu_launch()
print(f"bad timing only measures launch path: {(perf_counter() - start) * 1000:.2f} ms")

fake_synchronize()
start = perf_counter()
fake_gpu_launch()
fake_synchronize()
print(f"corrected timing includes completion: {(perf_counter() - start) * 1000:.2f} ms")
