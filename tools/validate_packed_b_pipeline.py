#!/usr/bin/env python3
"""Execute actual B packing source with deferred DMA and queue ownership checks."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
source=(root/'kernel.asc').read_text()
helper=source[source.index('template<typename T>\n__aicore__ inline int64_t ManualPackBInput('):
              source.index('// Isolated case12 packed-B kernel')]
start=source.index('        const uint32_t packRows=',source.index('void bmmms_manual_case12_packed('))
end=source.index('        // The signal is issued only after every packed panel',start)
body=source[start:end]
model=(root/'tests/cpu/packed_b_pipeline_model.cpp.in').read_text().replace('// @HELPER@',helper).replace('// @PACK@',body)
parent=subprocess.check_output(['git','show','3e9b090:kernel.asc'],text=True)
restored=source[:source.index('#ifndef BMMMS_PACK_B_PIPELINE')]+source[source.index('// Isolated case12 packed-B kernel'):]
restored=re.sub(r'#if BMMMS_PACK_B_PIPELINE\n.*?\n#else\n(.*?)\n#endif',r'\1',restored,flags=re.S)
assert restored==parent, 'mutation outside packing stage'
compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-packed-b-') as directory:
    cpp=Path(directory)/'model.cpp';cpp.write_text(model)
    for mode in (0,1):
        exe=Path(directory)/f'pack{mode}'
        subprocess.run([compiler,'-std=c++17','-O2',f'-DBMMMS_PACK_B_PIPELINE={mode}',str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
print('Host, Cube, reduction, flags, resources and non-pack code match passing parent exactly')
