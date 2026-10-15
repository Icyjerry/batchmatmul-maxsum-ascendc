#!/usr/bin/env python3
"""Execute extracted compact-NZ descriptor/reduction; layout model is not SDK proof."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text();parent=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],cwd=R,text=True)
start=s.index('bool DIRECT_BATCH=false,bool SINGLE_AIV=false,bool COMPACT_NZ=false>');end=s.index('template<typename T>__aicore__ inline void TallTransposeCopyPanel',start);body=s[start:end]
x=body.index('if constexpr(COMPACT_NZ){fp.mSize=');y=body.index('}else AscendC::Fixpipe(ring,c,fp);',x);fix=body[x+len('if constexpr(COMPACT_NZ){'):y]
x=body.index('if constexpr(COMPACT_NZ){const uint32_t plane=');y=body.index('}else SmallRowMaxLaneFold',x);reduce=body[x+len('if constexpr(COMPACT_NZ){'):y]
# Remove only the explicit new alternatives; default false code must be the parent.
legacy=body.replace('bool SINGLE_AIV=false,bool COMPACT_NZ=false','bool SINGLE_AIV=false',1)
legacy=legacy.replace('static_assert(!COMPACT_NZ||(DIRECT_BATCH&&SINGLE_AIV&&!TX1&&TX2&&MP==32&&NP==80&&KP==192),"compact NZ requires the full-K C6 frame");\n','',1)
legacy=legacy.replace('if constexpr(STREAM_C){\nif constexpr(COMPACT_NZ)AscendC::SetMMColumnMajor();else AscendC::SetMMRowMajor();}','if constexpr(STREAM_C)AscendC::SetMMRowMajor();',1)
legacy=legacy.replace('if constexpr(COMPACT_NZ){'+fix+'}else AscendC::Fixpipe(ring,c,fp);','AscendC::Fixpipe(ring,c,fp);',1)
legacy=legacy.replace('if constexpr(COMPACT_NZ){'+reduce+'}else SmallRowMaxLaneFold(c,row,rows,s.n,np);','SmallRowMaxLaneFold(c,row,rows,s.n,np);',1)
legacy=legacy.replace('SingleTileDirectFence<DIRECT_BATCH,AscendC::HardEvent::MTE2_V>();\nSmallRowMaxLaneFold','SingleTileDirectFence<DIRECT_BATCH,AscendC::HardEvent::MTE2_V>();SmallRowMaxLaneFold',1)
legacy=legacy.replace('bool DIRECT_BATCH=false,bool COMPACT_NZ=false>','bool DIRECT_BATCH=false>',1).replace('DIRECT_BATCH,true,COMPACT_NZ>','DIRECT_BATCH,true>',1)
inv=s[:start]+legacy+s[end:];a=inv.index('inline bool UseSmallC6CompactNZ(');b=inv.index('inline bool UseSmallC5Direct',a);inv=inv[:a]+inv[b:]
call='''if(UseSmallC6CompactNZ(s,p)){
bmmms_single_tile_direct_batch_mix11<T,false,true,32,80,192,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);
return;}
'''
assert inv.count(call)==1;inv=inv.replace(call,'',1);assert inv==parent,'default path or unrelated source changed'
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=R)
PRE=r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <vector>
#include <iostream>
#include <cmath>
#define PIPE_V 0
namespace AscendC{
struct Data{std::vector<float>v;Data(unsigned n):v(n,9876543){}};
struct Tensor{Data*p;unsigned off=0;Tensor operator[](unsigned n)const{return{p,off+n};}float get(unsigned i)const{assert(off+i<p->v.size());return p->v[off+i];}void set(unsigned i,float v)const{assert(off+i<p->v.size());p->v[off+i]=v;}};
struct BinaryRepeatParams{unsigned db,ab,bb,dr,ar,br;};
enum class ReduceOrder{ORDER_ONLY_VALUE};
constexpr int CFG_NZ=0;
struct FixpipeParamsV220{unsigned nSize=80,mSize=32,srcStride=32,dstStride=80;};
template<class T,class U,int cfg>void Fixpipe(Tensor dst,Tensor src,FixpipeParamsV220 p){assert(cfg==CFG_NZ&&p.nSize==80&&p.mSize==23&&p.srcStride==32&&p.dstStride==46);for(unsigned g=0;g<p.nSize/16;++g)for(unsigned r=0;r<p.mSize;++r)for(unsigned lane=0;lane<16;++lane)dst.set(g*p.dstStride*8+r*16+lane,src.get(g*p.srcStride*16+r*16+lane));}
template<int>void PipeBarrier(){}
void Max(Tensor dst,Tensor a,Tensor b,unsigned n){for(unsigned i=0;i<n;++i)dst.set(i,std::max(a.get(i),b.get(i)));}
void Max(Tensor dst,Tensor a,Tensor b,uint64_t mask,unsigned repeat,BinaryRepeatParams p){assert(p.db==1&&p.ab==1&&p.bb==1);for(unsigned r=0;r<repeat;++r)for(unsigned i=0;i<mask;++i)dst.set(r*p.dr*8+i,std::max(a.get(r*p.ar*8+i),b.get(r*p.br*8+i)));}
void WholeReduceMax(Tensor dst,Tensor src,uint64_t mask,unsigned repeat,unsigned drep,unsigned sblk,unsigned srep,ReduceOrder){assert(sblk==1);for(unsigned r=0;r<repeat;++r){float v=-INFINITY;for(unsigned i=0;i<mask;++i)v=std::max(v,src.get(r*srep*8+i));dst.set(r*drep,v);}}
void WholeReduceSum(Tensor dst,Tensor src,uint64_t mask,unsigned repeat,unsigned drep,unsigned sblk,unsigned srep){assert(sblk==1);for(unsigned r=0;r<repeat;++r){float v=0;for(unsigned i=0;i<mask;++i)v+=src.get(r*srep*8+i);dst.set(r*drep,v);}}
}
struct Shape{unsigned m=23,n=73,k=192;}s;
int main(){using namespace AscendC;unsigned pairs=0;
for(unsigned seed=0;seed<3;++seed)for(bool neg:{false,true})for(unsigned batch=0;batch<13;++batch){
 Data co(2560),gm(5120+8),local(2560+8),rowdata(64),sumdata(8);Tensor ring{&gm},c{&co},row{&rowdata},sum{&sumdata};FixpipeParamsV220 fp;
 std::vector<float>ref(23,-INFINITY);
 for(unsigned m=0;m<32;++m)for(unsigned n=0;n<80;++n){float dot=0;for(unsigned k=0;k<192;++k){float a=(neg||m==0)?float(1+(batch*5+m*3+k+seed)%5):float(int((batch*5+m*3+k+seed)%7)-3);float b=neg?-(n==72?1.0f:float(2+(batch*2+n*7+k*3+seed)%7)):(n==72?15.0f:float(int((batch*2+n*7+k*3+seed)%11)-5));dot+=a*b;}if(m<23&&n<73)ref[m]=std::max(ref[m],dot);if(n>=73)dot=9876543;co.v[(n/16)*32*16+m*16+n%16]=dot;}
'''
MID=r'''
 for(unsigned i=1840;i<gm.v.size();++i)assert(gm.v[i]==9876543);
 for(unsigned i=0;i<1840;++i)local.v[i]=gm.v[i];
 c={&local};const uint32_t rows=s.m;
'''
END=r'''
 AscendC::WholeReduceSum(sum,row,uint64_t(rows),1,1,1,1);
 float expected=0;for(unsigned m=0;m<23;++m){assert(row.get(m)==ref[m]);expected+=ref[m];}assert(sum.get(0)==expected);if(neg)assert(expected<0);
 for(unsigned i=1840;i<local.v.size();++i)assert(local.v[i]==9876543);++pairs;
 }std::cout<<pairs<<" full K192 batch pairs, mixed/all-negative, compact producer and actual NZ reduction PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c6-compact-nz-') as tmp:
 d=Path(tmp)
 def run(fx,rd,name):
  f=d/(name+'.cpp');exe=d/name;f.write_text(PRE+fx+MID+rd+END);subprocess.run(['c++','-std=c++17','-O2',str(f),'-o',str(exe)],check=True);return subprocess.run([str(exe)],capture_output=True)
 result=run(fix,reduce,'good');assert result.returncode==0,result.stderr.decode();print(result.stdout.decode(),end='')
 for name,fx,rd in [('wrong_dst_units',fix.replace('s.m*2','s.m*16'),reduce),('wrong_src_pitch',fix.replace('fp.mSize=s.m;','fp.mSize=s.m;fp.srcStride=s.m;'),reduce),('wrong_plane',fix,reduce.replace('plane=rows*16','plane=32*16')),('include_invalid_tail',fix,reduce.replace('s.n-64','16')),('omit_last_valid_doc',fix,reduce.replace('s.n-64','s.n-65'))]:
  assert (fx,rd)!=(fix,reduce);assert run(fx,rd,name).returncode!=0,name
print('Default inverse/protected7/five fault controls PASS; SDK NZ layout, unitFlag and BF16 hardware remain native gates')
