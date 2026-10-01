#!/usr/bin/env python3
"""Actual lean C7 consumer and byte-for-byte scope proof versus passed parent.

The CPU fixture queues MTE2/V/MTE3 separately with event dependencies. Cube
and companion AIV readiness/credits are abstracted, not a native protocol
simulation. Integer-valued FP32 reductions do not test native FP rounding.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    src = (ROOT / 'kernel.asc').read_text()
    parent = subprocess.check_output(['git', 'show', 'd793083:kernel.asc'], cwd=ROOT, text=True)
    a = src.index('// One full C per small TF batch:')
    b = src.index('// The basic-API path owns all local events;', a)
    helper = src[a:b]
    call = '''    if constexpr(SMALL_FULL_INPUTS) {
        RunSmallFullInputsVector(pipe,ring,output,s,worker,sub);
        return;
    }
'''
    assert src.count(call) == 1
    restored = (src[:a] + src[b:]).replace(call, '')
    assert restored == parent, 'unrelated Cube/host/launch/Vector/C9/TT/workspace change'
    fixture = (ROOT / 'tests/cpu/c7_lean_vector_model.cpp.in').read_text()
    model = fixture.replace('// INSERT_CONSUMER', helper)
    compiler = shutil.which('clang++') or shutil.which('c++')
    print('kernel SHA256:', hashlib.sha256(src.encode()).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory(prefix='bmmms-c7-lean-') as tmp:
        def run(name, code, negative=False):
            cpp, exe = Path(tmp)/(name+'.cpp'), Path(tmp)/name
            cpp.write_text(code)
            subprocess.run([compiler, '-std=c++17', '-O2', str(cpp), '-o', str(exe)], check=True)
            result = subprocess.run([str(exe)], capture_output=negative)
            assert (result.returncode != 0) if negative else (result.returncode == 0)
        run('consumer', model)
        for fence in ['V_MTE2', 'MTE2_V', 'V_MTE3', 'MTE3_V']:
            unsafe = model.replace('        Fence<AscendC::HardEvent::'+fence+'>();', '')
            assert unsafe != model
            run('missing-'+fence.lower(), unsafe, True)
            print('Missing '+fence+' correctly rejected PASS', flush=True)
        unsafe = model.replace('uint64_t(cols),rows,1,1,s.baseN/8,', 'uint64_t(64),rows,1,1,s.baseN/8,')
        assert unsafe != model
        run('unmasked-n', unsafe, True)
        print('Unmasked N tail correctly rejected PASS', flush=True)
        unsafe_helper = helper.replace('''        AscendC::DataCopyPad(c,ring[slot*oneC],cp,pad);
        // This MTE2 signal follows the last GM read, independent of V/MTE3.
        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4+slot);''', '''        AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(4+slot);
        AscendC::DataCopyPad(c,ring[slot*oneC],cp,pad);''')
        assert unsafe_helper != helper
        run('early-credit', fixture.replace('// INSERT_CONSUMER', unsafe_helper), True)
        print('Credit before last GM read correctly rejected PASS', flush=True)
    print('Remove only new helper/call restores the complete passed parent byte-for-byte.')
    print('Cube/host capacity/grid/workspace/C9/TT unchanged. CANN9/NPU precision/latency PENDING.')

if __name__ == '__main__':
    main()
