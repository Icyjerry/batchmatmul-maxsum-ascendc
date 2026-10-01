#!/usr/bin/env python3
"""Execute actual persistent Vector tasks and sparse finalizer with delayed DMA.

Synthetic full-K C values isolate the Max/partial/barrier flow. Cube arithmetic
is covered separately; this does not measure hardware precision or latency.
"""
from pathlib import Path
import shutil, subprocess, tempfile

root = Path(__file__).resolve().parents[1]
src = (root / 'kernel.asc').read_text()
tasks = src[src.index('struct ManualTaskRange'):src.index('template<typename T,bool TILE_STREAM=false>')]
consumer = src[src.index('// Consume wide GM windows'):src.index('__aicore__ inline void ManualCopyC(')]
finalizer = src[src.index('// All worker partials are ready'):src.index('// Consume wide GM windows')]
model = (root / 'tests/cpu/tt_worker_max_model.cpp.in').read_text()
model = model.replace('// INSERT_CONSUMER', tasks + consumer).replace('// INSERT_FINALIZER', finalizer)
legacy_consumer = consumer[:consumer.index('// Retain the N maximum')]
legacy_model = (root / 'tests/cpu/fullk_window_consumer_model.cpp.in').read_text().replace('// INSERT_CONSUMER', legacy_consumer)
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-worker-max-') as directory:
    for name, code in [('worker-max', model), ('window-regression', legacy_model)]:
        cpp, exe = Path(directory) / (name + '.cpp'), Path(directory) / name
        cpp.write_text(code)
        subprocess.run([compiler, '-std=c++17', '-O2', '-pthread', str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
print('Installed CANN9/NPU precision/performance PENDING; CPU source models only.')
