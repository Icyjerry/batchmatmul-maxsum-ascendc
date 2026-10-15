#!/usr/bin/env python3
"""Check the actual two-line handshake and its happens-before requirement."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
source = (root / 'kernel.asc').read_text()
old = subprocess.check_output(['git', 'show', 'e2f1b63:kernel.asc'], cwd=root, text=True)
start = source.index('__schedmode__(1)__global__ __mix__(1,1)void bmmms_manual_split_tt(')
stop = source.index('inline void CheckAcl(', start)
body = source[start:stop]
send = 'AscendC::CrossCoreSetFlag<2,PIPE_FIX>(0);\n'
wait = 'AscendC::CrossCoreWaitFlag<2>(0);\n'
assert body.count(send) == body.count(wait) == 1
assert body.index('Fence<AscendC::HardEvent::FIX_M>();') < body.index(send) < body.index('#else')
assert body.index('#else') < body.index(wait) < body.index('AscendC::SyncAll<true>();') < body.index('FinalizeSplitKND<PACKED_FINAL>')
assert source[:start] + body.replace(send, '').replace(wait, '') + source[stop:] == old
for name in ['CMakeLists.txt', 'main.asc', 'run.sh', 'data_utils.h', 'scripts/BatchMatmulMaxSum.py', 'scripts/gen_data.py', 'scripts/verify_result.py']:
    assert (root / name).read_bytes() == subprocess.check_output(['git', 'show', '1734f16:' + name], cwd=root)


def before_read(workers, tasks, mode):
    deps = {}
    for worker in range(workers):
        owned = list(range(worker, tasks, workers))
        # Each Cube's own loop drains its Fixpipe writes before the completion flag.
        for idx, task in enumerate(owned):
            deps[f'fix{task}'] = {f'fix{owned[idx-1]}'} if idx else set()
        deps[f'ready{worker}'] = {f'fix{owned[-1]}'} if mode == 'fixed' else set()
        deps[f'aiv{worker}'] = {f'ready{worker}'} if mode != 'old' else set()
    deps['read'] = {f'aiv{x}' for x in range(workers)}  # existing AIV-only barrier
    def ancestors(event):
        out = set()
        for dep in deps[event]:
            out.add(dep)
            out.update(ancestors(dep))
        return out
    return ancestors('read')


for workers in [1, 2, 3, 4, 8]:
    for tasks in [8, 16, 32]:
        writes = {f'fix{x}' for x in range(tasks)}
        assert writes <= before_read(workers, tasks, 'fixed')
        assert not writes <= before_read(workers, tasks, 'old')
        assert not writes <= before_read(workers, tasks, 'flag_before_fix')
print('Actual handshake location/whole inverse/protected7 PASS; 15 task-owner graphs require all Fix writes before finalizer; old/misordered flags rejected')
print('DAG semantics model only: native CANN compile, full FP64 precision and repeated launch validation remain independent gates.')
