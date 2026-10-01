#!/usr/bin/env python3
"""Check actual large B1 ND2NZ stages against old K panels and raw ZN oracle."""
from pathlib import Path
import shutil, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
src=(root/'kernel.asc').read_text()
prefix=(root/'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('// INSERT_HELPERS')[0]
zero=src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
read=src[src.index('template<typename T,int DEPTH>\n__aicore__ inline void ManualFullMReadB'):src.index('struct ManualTaskRange')]
code=prefix+zero+read+(root/'tests/cpu/tt_b_stage_layout_model.cpp.in').read_text()
compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-b-stage-layout-') as directory:
    cpp,exe=Path(directory)/'layout.cpp',Path(directory)/'layout';cpp.write_text(code)
    subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('Physical layout/source model only; installed CANN/NPU PENDING.')
