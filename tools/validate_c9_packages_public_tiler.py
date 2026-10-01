#!/usr/bin/env python3
"""Run actual C9 selector with fixed public 8.3 tiler, not installed CANN9."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ns = {'__file__': str(ROOT/'tools/validate_c9_packages.py'), '__name__': 'c9_import'}
exec((ROOT/'tools/validate_c9_packages.py').read_text(), ns)
env = {}
bootstrap = (ROOT/'tools/inspect_public_matmul_tiling.py').read_text()
exec(bootstrap[:bootstrap.index("put('probe.cpp',")], env)
put, src, out = env['put'], env['src'], env['out']
put('tiling/platform/platform_ascendc.h', '''#pragma once
#include <cstdint>
namespace platform_ascendc {
enum class SocVersion{ASCEND910,ASCEND310P,ASCEND910B,ASCEND310B,ASCEND910_95};
enum class CoreMemType{L1,L0_C,UB,L0_A,L0_B};
struct PlatformAscendC {
 int aic=20,aiv=40;uint64_t l1=524288,l0c=131072,ub=196608,l0a=65536,l0b=65536;
 static PlatformAscendC* GetInstance(){static PlatformAscendC p;return &p;}
 SocVersion GetSocVersion()const{return SocVersion::ASCEND910B;}
 int GetCoreNumAic(){return aic;}int GetCoreNumAiv(){return aiv;}
 uint64_t GetLibApiWorkSpaceSize(){return 16*1024*1024;}
 void GetCoreMemSize(CoreMemType t,uint64_t& n)const{
  n=t==CoreMemType::L1?l1:t==CoreMemType::L0_C?l0c:t==CoreMemType::UB?ub:t==CoreMemType::L0_A?l0a:l0b;}
};using PlatformAscendCManager=PlatformAscendC;
}
''')
put('kernel_tiling/kernel_tiling.h', '#pragma once\n#include <cstdint>\n'+env['raw']+'namespace AscendC{namespace tiling{using TCubeTiling=::TCubeTiling;}}\n')
code = '''#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>
#include "lib/matmul/matmul_tiling.h"
inline int64_t Ceil(int64_t n,int64_t d){return (n+d-1)/d;}
''' + ns['shapes'] + ns['host'] + ns['hostmain']
code = code.replace('hw->l0)', 'hw->l0c)').replace('&hw->l0,', '&hw->l0c,')
put('probe.cpp', code)
files = ['matmul_tiling.cpp', 'matmul_tiling_base.cpp', 'matmul_tiling_algorithm.cpp', 'math_util.cpp']
for flags in ([], ['-DBMMMS_TUNING']):
    exe = out/('tuning' if flags else 'prod')
    subprocess.run(['clang++', '-std=c++17', '-O2', '-include', 'map', *flags,
                    '-I'+str(out), '-I'+str(src), str(out/'probe.cpp')]
                   + [str(src/'impl/matmul/tiling'/f) for f in files] + ['-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
env['tmp'].cleanup()
