#!/usr/bin/env python3
"""Extract and execute new Cube producer; does not compile with CANN."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    raw = (ROOT / 'kernel.asc').read_bytes()
    source = raw.decode()
    zero = source[source.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):
                  source.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false>')]
    panel = source[source.index('// Copy one physical ND rectangle'):
                   source.index('// The basic-API path owns all local events')]
    code = (ROOT / 'tests/cpu/panel_model.cpp.in').read_text().replace('// INSERT_HELPERS', zero + panel)
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler
    print('CPU physical block model only. CANN/NPU/real event timing PENDING.', flush=True)
    print('kernel SHA256:', hashlib.sha256(raw).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory(prefix='bmmms-panel-') as directory:
        cpp, exe = Path(directory) / 'model.cpp', Path(directory) / 'model'
        cpp.write_text(code)
        subprocess.run([compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', str(cpp), '-o', str(exe)], check=True, timeout=60)
        subprocess.run([str(exe)], check=True, timeout=60)


if __name__ == '__main__':
    main()
