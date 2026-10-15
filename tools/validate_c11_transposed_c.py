#!/usr/bin/env python3
"""Execute actual C^T copy and vertical max blocks with arbitrary completed C tiles."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text();old=subprocess.check_output(['git','show','a11e2d9:kernel.asc'],cwd=R,text=True)
a=s.index('template<typename T,bool TX1,bool TX2,bool TRANSPOSE_C=false>');b=s.index('template<bool PACKED=false>\n__aicore__ inline void FinalizeSplitKND',a);body=s[a:b]
pa=old.index('template<typename T,bool TX1,bool TX2>\n__schedmode__(1)__global__ __mix__(1,2)void bmmms_dual_mdl');pb=old.index('template<bool PACKED=false>\n__aicore__ inline void FinalizeSplitKND',pa);parent=old[pa:pb]
start=body.index('a.SetGlobalBuffer(');end=body.index('partials.SetGlobalBuffer',start);buffers=body[start:end]
start=body.index('mm.SetOrgShape(s.n,s.m');end=body.index('}else{mm.SetOrgShape(s.m',start);producer=body[start:end]
start=body.index('AscendC::DataCopyExtParams cp{static_cast<uint16_t>(cols),rows*4,');end=body.index('}else{const uint32_t padded=',start);copy=body[start:end]
start=body.index('for(uint32_t active=s.baseN;active>1;active/=2)');end=body.index('}else{for(uint32_t col=0;',start);reduce=body[start:end]
assert body[body.index('AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(2+slot);'):]==parent[parent.index('AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(2+slot);'):], 'credits/task outputs/finalizer escaped scope'
legacy=body.replace('template<typename T,bool TX1,bool TX2,bool TRANSPOSE_C=false>','template<typename T,bool TX1,bool TX2>',1)
legacy=legacy.replace('static_assert(!TRANSPOSE_C||(TX1&&TX2),"transposed MDL swaps TT operands into NN");\n','',1)
for x,y in [('TRANSPOSE_C?false:TX1','TX1'),('TRANSPOSE_C?false:TX2','TX2'),('TRANSPOSE_C?x2:x1','x1'),('TRANSPOSE_C?x1:x2','x2')]:legacy=legacy.replace(x,y,1)
for first,last,oldfirst in [('if constexpr(TRANSPOSE_C){\nmm.SetOrgShape','mm.template IterateAll<false>(ring[slot*slotSize]);','mm.SetOrgShape(s.m,s.n'),('if constexpr(TRANSPOSE_C){\nAscendC::DataCopyExtParams cp','cq.EnQue(c);','const uint32_t padded='),('if constexpr(TRANSPOSE_C){\nfor(uint32_t active=','cq.FreeTensor(c);','for(uint32_t col=0;')]:
 x=legacy.index(first);y=legacy.index(last,x);u=parent.index(oldfirst);v=parent.index(last,u);legacy=legacy[:x]+parent[u:v]+legacy[y:]
assert legacy==parent,'default false code changed outside selected true branches'
inv=s[:a]+legacy+s[b:];g=inv.index('inline bool MakeTTMdlTranspose(');h=inv.index('using CacheKey=',g);inv=inv[:g]+inv[h:]
call='''if(s.tx1&&s.tx2){
AscendC::tiling::TCubeTiling transposed;
if(MakeTTMdlTranspose(s,p,transposed))
bmmms_dual_mdl<T,true,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,workspace,transposed,p.schedule);
else bmmms_dual_mdl<T,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,workspace,p.cube,p.schedule);
}'''
assert call in inv;inv=inv.replace(call,'if(s.tx1&&s.tx2)bmmms_dual_mdl<T,true,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,workspace,p.cube,p.schedule);',1);assert inv==old
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name],cwd=R)
PRE=r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <vector>
#include <cmath>
#include <iostream>
#define PIPE_V 0
namespace AscendC {
template<int>void PipeBarrier(){}
struct Store{std::vector<float>v;Store(unsigned n):v(n,-9876543){}};
template<class T>struct LocalTensor{Store*p;unsigned off=0;LocalTensor operator[](unsigned n)const{return{p,off+n};}
 T get(unsigned i)const{assert(off+i<p->v.size());return p->v[off+i];}void set(unsigned i,T x)const{assert(off+i<p->v.size());p->v[off+i]=x;}};
struct Global{Store*p;unsigned off=0;Global operator[](unsigned n)const{return{p,off+n};}};
struct DataCopyExtParams{unsigned blockCount,blockLen,srcStride,dstStride,unused;};
template<class T>struct DataCopyPadExtParams{bool padded;unsigned left,right;T value;};
void DataCopyPad(LocalTensor<float>dst,Global src,DataCopyExtParams p,DataCopyPadExtParams<float>pad){
 assert(!pad.padded&&!pad.left&&!pad.right&&p.blockCount==128&&p.blockLen==512&&p.srcStride==512&&!p.dstStride);
 for(unsigned row=0;row<p.blockCount;++row)for(unsigned col=0;col<p.blockLen/4;++col){unsigned from=src.off+row*(p.blockLen+p.srcStride)/4+col;assert(from<src.p->v.size());dst.set(row*p.blockLen/4+col,src.p->v[from]);}}
void Max(LocalTensor<float>dst,LocalTensor<float>a,LocalTensor<float>b,unsigned n){for(unsigned i=0;i<n;++i)dst.set(i,std::max(a.get(i),b.get(i)));}
}
struct Schedule{unsigned b=1,m=1536,n=2048,k=2048,baseM=256,baseN=128;};
using T=uint16_t;T*physicalX1;T*physicalX2;
#define __gm__
struct Tensor{T*physical=nullptr;unsigned off=0;void SetGlobalBuffer(T*p){physical=p;}Tensor operator[](unsigned n)const{return{physical,off+n};}};
struct Matmul{unsigned oa,on,ak,bk,pitch,ap,bp,rm,rn,rk;void SetOrgShape(unsigned m,unsigned n,unsigned k,unsigned kb,unsigned p){oa=m;on=n;ak=k;bk=kb;pitch=p;}
 void SetTensorA(Tensor a,bool t){assert(!t&&a.physical==physicalX2);ap=a.off;}void SetTensorB(Tensor b,bool t){assert(!t&&b.physical==physicalX1);bp=b.off;}
 void SetTail(unsigned m,unsigned n,unsigned k){rm=m;rn=n;rk=k;}};
float value(unsigned q,unsigned d,unsigned seed,bool negative){float bias=(q%53)*100, v=(q*7+d*17+seed*11)%127;return negative?-bias-1-v:bias+v-63;}
int main(){using namespace AscendC;constexpr bool TRANSPOSE_C=true;T input1[1],input2[1];void*x1=input1;void*x2=input2;physicalX1=input1;physicalX2=input2;Schedule s;Tensor a,b;Matmul mm;unsigned batch=0,rows=256,cols=128,slotSize=32768,p=0;
 for(unsigned seed=0;seed<3;++seed)for(bool negative:{false,true}){
 std::vector<float>maximaAll(1536,-INFINITY),reference(1536,-INFINITY);
 for(unsigned mt=0;mt<6;++mt)for(unsigned nt=0;nt<16;++nt){unsigned m0=mt*256,n0=nt*128,slot=nt%2;rows=256;
'''
POST=r'''
 assert(mm.oa==s.n&&mm.on==s.m&&mm.ak==s.k&&mm.bk==s.k&&mm.pitch==256&&mm.rm==128&&mm.rn==256&&mm.rk==s.k&&mm.ap==n0*s.k&&mm.bp==m0);
 rows=128;
 for(unsigned k=0;k<2048;++k){assert(mm.ap+k>=n0*2048&&mm.ap+k<(n0+128)*2048);assert(mm.bp+k*1536<1536*2048);}
 Store gm(2*slotSize),local(16384+8),maxbuf(128);Global ring{&gm};LocalTensor<float>c{&local},maxima{&maxbuf};
 for(unsigned doc=0;doc<128;++doc)for(unsigned query=0;query<256;++query)gm.v[slot*slotSize+doc*256+query]=value(m0+query,n0+doc,seed,negative);
 for(unsigned sub=0;sub<2;++sub){unsigned rowStart=sub*128;for(unsigned q=0;q<128;++q)maxbuf.v[q]=maximaAll[m0+rowStart+q];
'''
END=r'''
 for(unsigned q=0;q<128;++q){maximaAll[m0+rowStart+q]=maxbuf.v[q];for(unsigned d=0;d<128;++d)reference[m0+rowStart+q]=std::max(reference[m0+rowStart+q],value(m0+rowStart+q,n0+d,seed,negative));assert(maximaAll[m0+rowStart+q]==reference[m0+rowStart+q]);}
 for(unsigned i=16384;i<16392;++i)assert(local.v[i]==-9876543);
 }}
 float score=0,ref=0;for(unsigned q=0;q<1536;++q){score+=maximaAll[q];ref+=reference[q];}assert(score==ref);if(negative)assert(score<0);
 }
 std::cout<<"Actual swapped-operand descriptor / transposed GM copy / vertical max PASS:6 complete M1536 N2048 similarity matrices,192 AIV tiles each, negative maxima, source bounds and local guards\n";
}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c11-transpose-') as tmp:
 d=Path(tmp)
 def run(cp,rd,name,buf=buffers):
  f=d/(name+'.cpp');exe=d/name;f.write_text(PRE+buf+producer+POST+cp+rd+END);subprocess.run(['c++','-std=c++17','-O2',str(f),'-o',str(exe)],check=True);return subprocess.run([str(exe)],capture_output=True)
 r=run(copy,reduce,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,cp,rd in [('wrong_query_half',copy.replace('+rowStart],cp,pad)','],cp,pad)'),reduce),('wrong_vertical_stride',copy.replace('(s.baseM-rows)*4','0'),reduce),('missing_last_docs',copy,reduce.replace('active=s.baseN','active=s.baseN/2'))]:
  assert (cp,rd)!=(copy,reduce);assert run(cp,rd,name).returncode!=0,name
 assert run(copy,reduce,'wrong_operand_pointer',buffers.replace('TRANSPOSE_C?x2:x1','TRANSPOSE_C?x1:x2')).returncode!=0
print('Scope/protected7/unchanged credits and finalizer/four negative controls PASS; FP16/BF16 matmul, hardware synchronization, actual selector/tiling and performance are native gates.')
