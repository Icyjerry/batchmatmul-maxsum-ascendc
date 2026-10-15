#!/usr/bin/env python3
"""Execute extracted flattened offset/Gather code; casts and arithmetic stay parent."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text();old=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],cwd=R,text=True)
a=s.index('__aicore__ inline void TinyFlatGather48(');b=s.index('template<typename T,bool TX1,bool TX2,uint32_t KCONST=0,bool FLAT_GATHER=false>',a);helper=s[a:b]
a=s.index('auto rowOffsets=idx[192],offsets=idx[320];');b=s.index('}else{for(uint32_t bi=0;',a);flat=s[a:b]
inv=s.replace(helper,'',1).replace('uint32_t KCONST=0,bool FLAT_GATHER=false>','uint32_t KCONST=0>')
inv=inv.replace('static_assert(!FLAT_GATHER||KCONST==48,"flat gather requires full K48");\n','',1).replace('3*64*4+(FLAT_GATHER?3008:0)','3*64*4',1)
start=inv.index('if constexpr(FLAT_GATHER){');stop=inv.index('auto prod=products.ReinterpretCast<float>()',start)
pstart=old.index('for(uint32_t bi=0;bi<s.b;++bi){\nif constexpr(TX1)for(uint32_t m=0;');pstop=old.index('auto prod=products.ReinterpretCast<float>()',pstart)
inv=inv[:start]+old[pstart:pstop]+inv[stop:]
inv=inv.replace('TinyCompute<T,TX1,TX2,KCONST,FLAT_GATHER>','TinyCompute<T,TX1,TX2,KCONST>',1)
a=inv.index('template<bool TX1,bool TX2>\ninline bool UseTinyFlatGather48(');b=inv.index('template<typename T,bool TX1,bool TX2,uint32_t KCONST,bool GROUPED>',a);inv=inv[:a]+inv[b:]
hook='''if constexpr(GROUPED&&KCONST==48)if(UseTinyFlatGather48<TX1,TX2>(s,group,blocks)){
bmmms_tiny_grouped<T,TX1,TX2,KCONST,true><<<blocks,nullptr,stream>>>(x1,x2,y,s,group);return;}
'''
assert hook in inv;inv=inv.replace(hook,'',1);assert inv==old,'unrelated source or default path changed'
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=R)
PRE=r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <vector>
#include <iostream>
#include <cmath>
#define __aicore__
#define PIPE_V 0
namespace AscendC{
struct Store{std::vector<double>v;Store(unsigned n):v(n,9876543){}};
template<class T>struct LocalTensor{Store*p;unsigned off=0;LocalTensor operator[](unsigned n)const{return{p,off+n};}T get(unsigned i)const{assert(off+i<p->v.size());return T(p->v[off+i]);}void set(unsigned i,T v)const{assert(off+i<p->v.size());p->v[off+i]=v;}template<class U>LocalTensor<U>ReinterpretCast()const{return{p,off};}};
struct BinaryRepeatParams{unsigned db,ab,bb,dr,ar,br;};struct BrcbRepeatParams{unsigned block,repeat;};
template<int>void PipeBarrier(){}
void Brcb(LocalTensor<int32_t>dst,LocalTensor<int32_t>src,uint8_t repeats,BrcbRepeatParams p){assert(p.block==1&&p.repeat==8);for(unsigned r=0;r<repeats;++r)for(unsigned a=0;a<8;++a)for(unsigned lane=0;lane<8;++lane)dst.set(r*64+a*8+lane,src.get(r*8+a));}
void Muls(LocalTensor<int32_t>dst,LocalTensor<int32_t>src,int32_t factor,unsigned count){for(unsigned i=0;i<count;++i)dst.set(i,src.get(i)*factor);}
void Add(LocalTensor<int32_t>dst,LocalTensor<int32_t>a,LocalTensor<int32_t>b,uint64_t mask,unsigned repeat,BinaryRepeatParams p){for(unsigned r=0;r<repeat;++r)for(unsigned i=0;i<mask;++i)dst.set(r*p.dr*8+(i/8)*p.db*8+i%8,a.get(r*p.ar*8+(i/8)*p.ab*8+i%8)+b.get(r*p.br*8+(i/8)*p.bb*8+i%8));}
void Gather(LocalTensor<float>dst,LocalTensor<float>src,LocalTensor<uint32_t>offset,unsigned base,unsigned count){for(unsigned i=0;i<count;++i){auto address=offset.get(i);assert(address%4==0);dst.set(i,src.get(base/4+address/4));}}
}
'''
MAIN=r'''
struct Shape{unsigned m=7,n=13,k=48;}s;
float x(unsigned batch,unsigned m,unsigned k,unsigned seed,bool negative){return negative?float(1+(batch*17+m*13+k*3+seed)%5):float(int((batch*17+m*13+k*3+seed)%7)-3);}
float z(unsigned batch,unsigned n,unsigned k,unsigned seed,bool negative){return negative?-float(1+(batch*11+n*7+k*17+seed)%7):float(int((batch*11+n*7+k*17+seed)%13)-6);}
template<bool TX1,bool TX2>void test(unsigned seed,unsigned batch,bool negative){using namespace AscendC;Store index(944+8),rawa(336),rawb(624),ca(336+8),cb(624+8);LocalTensor<int32_t>idx{&index},ia=idx[64],ib=idx[128];LocalTensor<float>rawAf{&rawa},rawBf{&rawb},fa{&ca},fb{&cb};
for(unsigned k=0;k<48;++k){idx.set(k,k);ia.set(k,k*7*4);ib.set(k,k*13*4);}
for(unsigned m=0;m<7;++m)for(unsigned k=0;k<48;++k){auto v=x(batch,m,k,seed,negative);rawa.v[TX1?k*7+m:m*48+k]=v;if(!TX1)ca.v[m*48+k]=v;}
for(unsigned n=0;n<13;++n)for(unsigned k=0;k<48;++k){auto v=z(batch,n,k,seed,negative);rawb.v[TX2?n*48+k:k*13+n]=v;if(TX2)cb.v[n*48+k]=v;}
'''
END=r'''
for(unsigned m=0;m<7;++m)for(unsigned k=0;k<48;++k)assert(fa.get(m*48+k)==x(batch,m,k,seed,negative));
for(unsigned n=0;n<13;++n)for(unsigned k=0;k<48;++k)assert(fb.get(n*48+k)==z(batch,n,k,seed,negative));
float score=0,ref=0;for(unsigned m=0;m<7;++m){float maximum=-INFINITY,expected=-INFINITY;for(unsigned n=0;n<13;++n){float dot=0,golden=0;for(unsigned k=0;k<48;++k){dot+=fa.get(m*48+k)*fb.get(n*48+k);golden+=x(batch,m,k,seed,negative)*z(batch,n,k,seed,negative);}assert(dot==golden);maximum=std::max(maximum,dot);expected=std::max(expected,golden);}score+=maximum;ref+=expected;}assert(score==ref);if(negative)assert(score<0);
for(unsigned i=944;i<952;++i)assert(index.v[i]==9876543);for(unsigned i=336;i<344;++i)assert(ca.v[i]==9876543);for(unsigned i=624;i<632;++i)assert(cb.v[i]==9876543);
}
int main(){for(unsigned seed=0;seed<4;++seed)for(unsigned b=0;b<2;++b)for(bool negative:{false,true}){test<false,false>(seed,b,negative);test<true,false>(seed,b,negative);test<true,true>(seed,b,negative);}std::cout<<"48 full-K48 batch/layout pairs: actual Brcb/Add/Gather addresses, canonical operands, fullM7N13 math, negative max and UB guards PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c3-flat-') as tmp:
 d=Path(tmp)
 def run(h,f,name):
  src=d/(name+'.cpp');exe=d/name;src.write_text(PRE+h+MAIN+f+END);subprocess.run(['c++','-std=c++17','-O2',str(src),'-o',str(exe)],check=True);return subprocess.run([str(exe)],capture_output=True)
 r=run(helper,flat,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,h,f in [('wrong_row_stride',helper.replace('{1,0,1,6,1,0}','{1,0,1,6,0,0}'),flat),('wrong_k_repeat',helper.replace('{1,0,1,6,1,0}','{1,0,1,6,1,1}'),flat),('incomplete_K',helper.replace('rows*48','rows*47'),flat),('wrong_byte_units',helper,flat.replace('int32_t(4)','int32_t(1)')),('incomplete_row_offsets',helper,flat.replace('uint8_t(2)','uint8_t(1)'))]:
  assert (h,f)!=(helper,flat);assert run(h,f,name).returncode!=0,name
print('Default inverse/protected7/five negative controls PASS; actual BF16/casts/Vector subpipeline/speed remain native gates')
