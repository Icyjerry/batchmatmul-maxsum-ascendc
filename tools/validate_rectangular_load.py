#!/usr/bin/env python3
"""Execute actual six changed load blocks in a bounded CPU layout model."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'kernel.asc').read_text()
helper = source[source.index('template<typename T>\n__aicore__ inline void ManualLoadRectangle('):
                source.index('// One Cube owns one complete small batch.')]
blocks = re.findall(r'#if BMMMS_RECT_LOAD3D\n(.*?)\n#else\n(.*?)\n#endif', source, re.S)
assert len(blocks) == 6
assert blocks[2] == blocks[4] and blocks[3] == blocks[5]
functions = []
names = ('directA', 'directB', 'manualA', 'manualB', 'packedA', 'packedB')
for name, (new, old) in zip(names, blocks):
    functions.append('''
void %s(AscendC::LocalTensor<int16_t> a2, AscendC::LocalTensor<int16_t> a1,
        uint32_t rows,uint32_t count,uint32_t sourceCols,uint32_t k0,bool residentA,unsigned tree){
    auto b1=a1,b2=a2;
    const uint32_t mp=rows,kp=count,np=sourceCols,cols=sourceCols;
    struct {uint32_t k,tree;} s{sourceCols,tree};
    AscendC::LoadData2DParams lp;lp.ifTranspose=%s;
#if BMMMS_RECT_LOAD3D
%s
#else
%s
#endif
}
''' % (name, 'true' if name.endswith('B') else 'false', new, old))
model = (root / 'tests/cpu/rectangular_load_model.cpp.in').read_text()
model = model.replace('// @HELPER@', helper).replace('// @BLOCKS@', '\n'.join(functions))
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-rect-load-') as directory:
    cpp = Path(directory) / 'model.cpp'
    cpp.write_text(model)
    for mode in (0, 1):
        exe = Path(directory) / f'load{mode}'
        subprocess.run([compiler, '-std=c++17', '-O2', f'-DBMMMS_RECT_LOAD3D={mode}',
                        str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)

# Remove our helper and alternatives; unrelated regions must match the parent.
parent = subprocess.check_output(['git', 'show', '909294b:kernel.asc'], text=True)
restored = source[:source.index('#ifndef BMMMS_RECT_LOAD3D')] + source[source.index('// One Cube owns one complete small batch.'):]
restored = re.sub(r'#if BMMMS_RECT_LOAD3D\n.*?\n#else\n(.*?)\n#endif', r'\1', restored, flags=re.S)
normalize = lambda text: re.sub(r'\s+', '', text)
# Compare unaffected prefix/suffix and every other function without relying on brace equivalence.
start = '// Isolated case6 fast path'
end = 'template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>'
for current, expected in zip((restored.split(start)[0], restored.split(end)[1]),
                             (parent.split(start)[0], parent.split(end)[1])):
    assert normalize(current) == normalize(expected), 'unrelated kernel mutation'
print('Actual six load blocks, macro 0/1, physical layout/bounds; unaffected kernel regions PASS')
