#!/usr/bin/env python3
"""Check dispatch precedence with real host code and a permissive CPU tiler."""
from pathlib import Path
import hashlib
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'kernel.asc').read_text()
# Read the shipped defaults, rather than silently overriding the production mode.
macros = source[source.index('#ifndef BMMMS_CUBE_PANEL'):source.index('// Experimental aligned')]
code = ((ROOT / 'tests/cpu/planner_stub.hpp').read_text() + macros
        + source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
        + source[source.index('struct Plan {'):source.index('using CacheKey =')]
        + r'''
void Reject(Shape s) {
    bool rejected=false;
    try { MakePlan(s,20); } catch(const std::exception&) { rejected=true; }
    assert(rejected);Tune()=TuneConfig{};
}
int main() {
    auto base=MakePlan({1,1536,1536,1536,1,1,1},20).schedule;
    if(BMMMS_CUBE_PANEL==0)assert(base.dual==1 && base.window==4 && base.nSplit==3 && !base.panelK);
    auto onePair=MakePlan({16,128,256,128,1,1,0},20).schedule;
    assert(!onePair.panelResident);
    if(BMMMS_CUBE_PANEL)assert(onePair.panelK==128 && onePair.panelGroup==2);
    for(int layout=0;layout<4;++layout) {
        Shape s{1,64,8192,128,2,layout/2,layout%2};
        // Individual pins must also override the profile, without a dual pin.
        for(int which=0;which<4;++which) {
            Tune()=TuneConfig{};
            if(which==0)Tune().bm=32;if(which==1)Tune().bn=64;
            if(which==2)Tune().ns=2;if(which==3)Tune().window=1;
            auto d=MakePlan(s,20).schedule;
            assert(!d.panelK);
            assert(which!=0 || d.baseM==32);assert(which!=1 || d.baseN==64);
            assert(which!=2 || d.nSplit==2);assert(which!=3 || d.window==1);
        }
        Tune().bm=32;Tune().bn=64;Tune().ns=2;Tune().window=1;
        auto d=MakePlan(s,20).schedule;
        assert(d.baseM==32 && d.baseN==64 && d.nSplit==2 && d.window==1 && !d.panelK);
    }
    Tune()=TuneConfig{};Tune().ks=2;
    auto split=MakePlan({1,64,96,8192,1,1,1},20).schedule;
    assert(split.kSplit==2 && split.baseM==64 && split.baseN==96);
    Tune().bm=32;Reject({1,64,96,8192,1,1,1}); // split-K may not truncate M
    Tune().bm=17;Reject({1,64,8192,128,2,0,1}); // no silent tile fallback
    Tune().bn=512;Reject({1,64,8192,128,2,0,1});
    Tune().ns=10000;Reject({1,64,8192,128,2,0,1}); // no silent clamping
    Tune().dual=3;Tune().window=2;Reject({16,128,256,128,1,1,0});
    Tune().window=1;Reject({1,1,1,32,1,0,0}); // ignored pin on vector early return
    std::cout<<"panel="<<BMMMS_CUBE_PANEL<<": profile precedence, incompatible pins, one-pair residency PASS\n";
}
''')
print('CPU planner only; CANN tiler and NPU performance PENDING.', flush=True)
print('kernel SHA256:', hashlib.sha256(source.encode()).hexdigest(), flush=True)
with tempfile.TemporaryDirectory(prefix='bmmms-dispatch-') as directory:
    root = Path(directory)
    cpp, exe = root / 'model.cpp', root / 'model'
    cpp.write_text(code)
    for flags in ([], ['-DBMMMS_CUBE_PANEL=2'], ['-DBMMMS_CUBE_PANEL=3']):
        subprocess.run(['clang++', '-std=c++14', '-O2', '-DBMMMS_TUNING',
                        '-DBMMMS_ADAPTIVE_SPLITK=1', '-DBMMMS_BALANCED_NSPLIT=1',
                        *flags, str(cpp), '-o', str(exe)], check=True, timeout=60)
        subprocess.run([str(exe)], check=True, timeout=60)

# Check actual preprocessor isolation on both sides of the MIX kernel.
manual = source[source.index('void bmmms_manual('):source.index('// Optional MDL package-copy')]
for mode in (0, 3):
    for cube in (False, True):
        flags = ['-D__DAV_CUBE__'] if cube else []
        result = subprocess.run(['clang++', '-E', '-P', '-x', 'c++',
                                 f'-DBMMMS_CUBE_PANEL={mode}', *flags, '-'],
                                input=manual, text=True, capture_output=True,
                                check=True, timeout=30).stdout
        if mode == 0:
            assert 'if(s.panelK)' not in result and 'RunPanelCube<' not in result
        elif cube:
            assert result.count('RunPanelCube<') == 2
        else:
            assert 'ReduceDualTile(c,maxima,row,rows,cols,s.baseN)' in result
print('Production preprocessing: experimental AIC/AIV dispatch absent at panel=0 PASS')
