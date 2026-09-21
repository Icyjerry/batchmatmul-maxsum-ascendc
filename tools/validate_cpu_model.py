#!/usr/bin/env python3
"""Reproduce CPU-only v1 checks; this does not compile or run an NPU kernel."""

from collections import Counter
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def check_schedules(source):
    expected = "const int64_t finalWorkers = static_cast<int64_t>(s.workers) * (s.dual ? 2 : 1);"
    if expected not in source or "b0 < s.b; b0 += finalWorkers * 8" not in source:
        raise RuntimeError("FinalizeRows changed; update the schedule model before reporting a pass")
    checked = old_duplicates = 0
    for dual in (0, 1, 2, 3, 4, 6, 7):
        for workers in range(1, 65):
            aivs = workers * (2 if dual else 1)
            for batches in range(1, 65):
                old, new = Counter(), Counter()
                for core in range(aivs):
                    for start in range(core * 8, batches, workers * 8):
                        old.update(range(start, min(start + 8, batches)))
                    for start in range(core * 8, batches, aivs * 8):
                        new.update(range(start, min(start + 8, batches)))
                assert len(new) == batches and all(v == 1 for v in new.values())
                old_duplicates += any(v != 1 for v in old.values())
                checked += 1
    print(f"FinalizeRows: {checked} schedules passed; old duplicate-writer cases: {old_duplicates}")


def check_budget(source):
    for term in (
        "uint64_t(bm / 2) * 64 * 4",
        "d.kSplit == 1 && d.baseN >= 64 && s.n / d.nSplit > 64",
        "32 + finalBytes + deferredBytes",
    ):
        if term not in source:
            raise RuntimeError("UB/dispatch code changed; update the budget model before reporting a pass")
    checked = largest_actual = largest_budget = 0
    for bm in (16, 32, 64, 128):
        for bn in (16, 32, 64, 128, 256):
            for n in (1, 31, 63, 64, 65, 127, 128, 129, 255, 256, 257, 511, 513, 8192):
                for splits in range(1, (n + bn - 1) // bn + 1):
                    enabled = bn >= 64 and n // splits > 64
                    reserved = bm // 2 * 64 * 4 if bn >= 64 and n > 64 else 0
                    allocated = bm // 2 * 64 * 4 if enabled else 0
                    assert allocated <= reserved
                    final = 3 * 1024 * 4 + 64
                    actual = bm * bn * 4 + 3 * bm * 4 + 32 + allocated + final
                    budget = bm * bn * 4 + 18 * bm * 4 + 32 + reserved + final
                    assert actual <= budget
                    if enabled:
                        assert bm // 2 <= 255 and bn // 8 <= 255
                        largest_actual = max(largest_actual, actual)
                        largest_budget = max(largest_budget, budget)
                    checked += 1
    print(f"UB/dispatch: {checked} combinations passed; max modeled live bytes={largest_actual}, budget={largest_budget}")


def main():
    raw = (ROOT / "kernel.asc").read_bytes()
    source = raw.decode().replace("\r\n", "\n")
    print("CPU models only; no CANN compilation, synchronization check, or NPU benchmark.", flush=True)
    print("kernel SHA256:", hashlib.sha256(raw).hexdigest(), flush=True)
    if "class DeferredRowMax {" not in source:
        raise SystemExit("NOT APPLICABLE: this CPU model targets experiment-v1 / experiment/v2-dual1-nsplit; current user-best kernel is not validated by it.")
    start = source.index("class DeferredRowMax {")
    end = source.index("\n};", start) + 3
    helper = source[start:end]
    template = (ROOT / "tests/cpu/deferred_model.cpp.in").read_text()
    marker = "// BMMMS_INSERT_LIVE_HELPER"
    assert template.count(marker) == 1
    compiler = shutil.which("clang++") or shutil.which("c++")
    if not compiler:
        raise RuntimeError("A C++14 compiler (clang++ or c++) is required")
    with tempfile.TemporaryDirectory(prefix="bmmms-cpu-") as directory:
        cpp = Path(directory) / "model.cpp"
        exe = Path(directory) / "model"
        cpp.write_text(template.replace(marker, helper))
        subprocess.run([compiler, "-std=c++14", "-O2", str(cpp), "-o", str(exe)], check=True, timeout=60)
        subprocess.run([str(exe)], check=True, timeout=60)
    check_schedules(source)
    check_budget(source)
    print("PASS: CPU helper, schedule, and budget models. NPU validation remains pending.")


if __name__ == "__main__":
    main()
