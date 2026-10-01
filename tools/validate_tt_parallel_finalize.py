#!/usr/bin/env python3
"""Run actual distributed Max-then-Sum helper with threads and delayed DMA.

Models queue/event memory ownership, not hardware precision or latency.
"""
from pathlib import Path
import shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1];src=(root/'kernel.asc').read_text()
a=src.index('// All worker partials are ready');b=src.index('// Consume wide GM windows',a)
model=(root/'tests/cpu/fullm_parallel_finalize_model.cpp.in').read_text().replace('// INSERT_FINALIZER',src[a:b])
compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-tt-merge-') as d:
 cpp,exe=Path(d)/'merge.cpp',Path(d)/'merge';cpp.write_text(model)
 subprocess.run([compiler,'-std=c++17','-O2','-pthread',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('Installed CANN9/NPU pipeline/precision/performance PENDING.')
