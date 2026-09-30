#!/usr/bin/env python3
"""Run unmodified public Matmul tiling C++ with minimal platform/log/layout shims.

This is source-level evidence for public 8.3.T9.0.B066, not a CANN9 compile,
installed CANN tiler, hardware model, or performance test. Uses illustrative
910B memories; stubs only external support headers, never tiling arithmetic.
"""
from pathlib import Path
import re, subprocess
import argparse, tempfile
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,required=True,help='Official ascendc-api-adv checkout; not installed CANN')
args=parser.parse_args()
src=args.source.resolve()
revision=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
expected='c7dfa2d901a314e1ae69e9cef850057593f2a58b'
if revision!=expected: raise SystemExit('Expected public source revision '+expected+', got '+revision)
tmp=tempfile.TemporaryDirectory(prefix='bmmms-public-tiler-')
out=Path(tmp.name)
def put(name,text):
    p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
fields=re.findall(r'TILING_DATA_FIELD_DEF\((\w+), (\w+)\)',(src/'lib/matmul/matmul_tilingdata.h').read_text())
raw='struct TCubeTiling {\n'+''.join(f'{t} {n}=0;\n' for t,n in fields)+'};\n'
put('kernel_tiling/kernel_tiling.h','#pragma once\n#include <cstdint>\n'+raw)
put('register/tilingdata_base.h','''#pragma once
#include <cstdint>
#include <cstring>
#define BEGIN_TILING_DATA_DEF(name) struct name {
#define TILING_DATA_FIELD_DEF(type,name) type name=0; type get_##name() const {return name;} void set_##name(type v){name=v;}
#define END_TILING_DATA_DEF void SaveToBuffer(void* dst,size_t bytes) const {if(bytes>=sizeof(*this))std::memcpy(dst,this,sizeof(*this));} }
#define REGISTER_TILING_DATA_CLASS(a,b)
''')
put('tiling/platform/platform_ascendc.h','''#pragma once
#include <cstdint>
namespace platform_ascendc {
enum class SocVersion{ASCEND910,ASCEND310P,ASCEND910B,ASCEND310B,ASCEND910_95};
enum class CoreMemType{L1,L0_C,UB,L0_A,L0_B};
struct PlatformAscendC {
SocVersion GetSocVersion() const {return SocVersion::ASCEND910B;}
void GetCoreMemSize(CoreMemType t,uint64_t& n) const {n=t==CoreMemType::L1?512*1024:t==CoreMemType::L0_C?128*1024:t==CoreMemType::UB?192*1024:64*1024;}
};}
''')
put('impl/host_log.h','''#pragma once
#include <cassert>
#define TILING_LOG_INFO(...)
#define TILING_LOG_DEBUG(...)
#define TILING_LOG_WARNING(...)
#define TILING_LOG_ERROR(...)
#define ASCENDC_HOST_ASSERT(cond,ret,...) do {assert(cond);} while(0)
''')
put('securec.h','''#pragma once
#include <cstring>
using errno_t=int;
constexpr int EOK=0;
inline errno_t memcpy_s(void* d,size_t capacity,const void* s,size_t n){if(n>capacity)return 1;std::memcpy(d,s,n);return 0;}
''')
put('probe.cpp','''#include <iostream>
#include "lib/matmul/matmul_tiling.h"
int main(){
using namespace matmul_tiling;
PlatformInfo hw{platform_ascendc::SocVersion::ASCEND910B,512*1024,128*1024,192*1024,64*1024,64*1024};
std::cout<<"singleM,config,K,singleN,result,baseK,stepM,stepN,stepKa,stepKb,depthA1,depthB1,dbL0A,dbL0B\\n";
for(int type:{0,1})for(int k:{1024,1536,2048,3072,4096})for(int n:{128,256,512,1024})for(int m:{128,256}) {
MatmulApiTiling q(hw);q.SetAType(TPosition::GM,CubeFormat::ND,DataType::DT_BF16,true);
q.SetBType(TPosition::GM,CubeFormat::ND,DataType::DT_BF16,true);q.SetCType(TPosition::GM,CubeFormat::ND,DataType::DT_FLOAT);
q.SetBias(false);q.SetMatmulConfigParams(type);q.SetOrgShape(1536,3072,k);q.SetShape(m,n,k);
q.SetBufferSpace(512*1024,128*1024,110*1024);q.SetFixSplit(128,128,-1);
optiling::TCubeTiling t;auto ok=q.GetTiling(t);
std::cout<<m<<","<<type<<","<<k<<","<<n<<","<<ok<<","<<t.get_baseK()<<","<<t.get_stepM()<<","<<t.get_stepN()<<","<<t.get_stepKa()<<","<<t.get_stepKb()<<","<<t.get_depthA1()<<","<<t.get_depthB1()<<","<<t.get_dbL0A()<<","<<t.get_dbL0B()<<"\\n";
}}
''')
files=['matmul_tiling.cpp','matmul_tiling_base.cpp','matmul_tiling_algorithm.cpp','math_util.cpp']
cmd=['clang++','-std=c++17','-O2','-include','map','-I'+str(out),'-I'+str(src),str(out/'probe.cpp')]+[str(src/'impl/matmul/tiling'/f) for f in files]+['-o',str(out/'probe')]
subprocess.run(cmd,check=True)
subprocess.run([str(out/'probe')],check=True)
tmp.cleanup()
