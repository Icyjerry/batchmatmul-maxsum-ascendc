#!/usr/bin/env python3
"""Extract real current/baseline consumers and model queue/address/flag semantics."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '35a86eb'


def main():
    raw = (ROOT / 'kernel.asc').read_bytes()
    source = raw.decode()
    baseline = subprocess.check_output(['git', 'show', f'{BASELINE}:kernel.asc'], cwd=ROOT).decode()
    print('CPU model only; CANN compile, hardware ordering and latency remain PENDING.', flush=True)
    print('kernel SHA256:', hashlib.sha256(raw).hexdigest(), flush=True)
    start = source.index('__aicore__ inline void CopyDualTile(')
    end = source.index('template <typename T, bool TX1, bool TX2>\n__schedmode__(1)', start)
    helpers = source[start:end]
    start = baseline.index('            const uint32_t slot=sequence&1;', baseline.index(
        'uint32_t totalWindows=0;', baseline.index('void bmmms_dual(')))
    end = baseline.index('\n        }\n        if(s.earlySum', start)
    old_body = baseline[start:end]
    assert baseline.count(old_body) == 2
    declaration = helpers[helpers.index('template <typename MM>'):helpers.index('\n{', helpers.index('template <typename MM>'))]
    reference = declaration.replace('ConsumeDualWindow', 'ReferenceConsume') + '''
{
    const uint32_t width=s.baseN*s.window;
    const uint32_t slotSize=s.baseM*width;
''' + old_body + '\n}\n'
    call = 'ConsumeDualWindow(mm,cq,ring,s,maxima,row,rowStart,rows,nt,end,sequence,totalWindows);'
    assert source.count(call) == 2
    # Host plan, allocation, Cube code and all unrelated kernels must be identical.
    stripped = source.replace(source[source.index('// Consumer pipeline experiment:'):source.index('// Experimental aligned dual=1 scheduling.')], '')
    stripped = stripped.replace('// The queue already owns two UB tiles. Prefetching does not change its budget.\n'+helpers, '')
    stripped = stripped.replace('            '+call, old_body)
    assert stripped == baseline, 'Changes beyond the two consumers require a new validation plan'
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler, 'C++14 compiler required'
    template = (ROOT / 'tests/cpu/dual_pipeline_model.cpp.in').read_text()
    code = template.replace('// BMMMS_INSERT_HELPERS', helpers).replace('// BMMMS_INSERT_REFERENCE', reference)
    with tempfile.TemporaryDirectory(prefix='bmmms-pipeline-') as directory:
        cpp = Path(directory) / 'model.cpp'
        cpp.write_text(code)
        for mode in (0, 1, 2):
            exe = Path(directory) / f'model-{mode}'
            subprocess.run([compiler, '-std=c++14', '-O2', f'-DBMMMS_DUAL_PIPELINE={mode}', str(cpp), '-o', str(exe)], check=True, timeout=60)
            subprocess.run([str(exe)], check=True, timeout=60)
    subprocess.run([shutil.which('python3'), str(ROOT / 'tests/cpu/dual_pipeline_protocol.py')], check=True, timeout=60)
    print('PASS: CPU model and surgical source comparison; no device-performance claim.')


if __name__ == '__main__':
    main()
