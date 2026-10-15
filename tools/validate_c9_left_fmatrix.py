#!/usr/bin/env python3
"""Execute actual A Load3D helper against persistent FMatrix, all captured C9 tiles."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'kernel.asc').read_text()
a=s.index('constexpr AscendC::IsResetLoad3dConfig RESIDENT_NN_KEEP_LOAD3D=');b=s.index('template<typename T,bool TX2=true>',a);helper=s[a:b]
a=s.index('if constexpr(SPLIT_FMATRIX){const uint8_t zeroPad[4]={0,0,0,0};');b=s.index('\n}for(uint32_t nt=',a);setup=s[a:b]
assert 'AscendC::SetLoadDataPaddingValue(uint64_t(0));' in s[s.index('void bmmms_manual('):s.index('RunManualFullMCube<T,TILE_STREAM',s.index('void bmmms_manual('))]
old_assert='static_assert(!SPLIT_FMATRIX||(!TX1&&!TX2&&TILE_STREAM&&PARTITION_STREAM&&!WIDE_K),\n"Split FMatrix uses the complete original NN partition stream");'
new_assert='static_assert(!SPLIT_FMATRIX||(!TX1&&TILE_STREAM&&PARTITION_STREAM&&!WIDE_K),\n"Cached FMatrix uses the complete non-transposed A partition stream");'
inv=s.replace(new_assert,old_assert,1);a=inv.index('inline bool UseC9LeftFmatrix(');b=inv.index('using CacheKey=',a);inv=inv[:a]+inv[b:]
hook='''if(UseC9LeftFmatrix(s,p)){
bmmms_manual<T,false,true,true,false,false,false,false,true,true,true,false,false,false,true><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,p.schedule);return;}
'''
assert hook in inv;inv=inv.replace(hook,'',1);assert inv==subprocess.check_output(['git','show','a11e2d9:kernel.asc'],text=True)
for name in ['CMakeLists.txt','main.asc','run.sh','data_utils.h','scripts/BatchMatmulMaxSum.py','scripts/gen_data.py','scripts/verify_result.py']:
 assert (R/name).read_bytes()==subprocess.check_output(['git','show','1734f16:'+name])
# With TX2=true the existing B branch executes only Load2D and cannot reset FMatrix.
a=s.index('if constexpr(TX2){AscendC::LoadData2DParams lp;',s.index('void RunManualFullMCube'));b=s.index('\n}else{',a)
assert 'SetFmatrix' not in s[a:b] and 'LoadData(b2,b1,lp)' in s[a:b]
PRE=r'''
#include <vector>
#include <cassert>
#include <cstdint>
#include <iostream>
#define __aicore__
using half=uint32_t;
unsigned width=999,padding=999,matrixSets=0,paddingSets=0,loads=0,globalM=0,expectK=0;uint64_t checks=0;
namespace AscendC {
struct IsResetLoad3dConfig{bool isSetFMatrix,isSetPadding;constexpr IsResetLoad3dConfig(bool a,bool b):isSetFMatrix(a),isSetPadding(b){}};
constexpr IsResetLoad3dConfig defaultConfig{true,true};enum class FmatrixMode{FMATRIX_LEFT,FMATRIX_RIGHT};
void SetFmatrix(unsigned h,unsigned w,const uint8_t*p,FmatrixMode mode=FmatrixMode::FMATRIX_LEFT){assert(h==1&&mode==FmatrixMode::FMATRIX_LEFT);for(unsigned i=0;i<4;++i)assert(p[i]==0);width=w;++matrixSets;}
template<class T>struct LocalTensor{std::vector<T>*p;unsigned off=0;template<class U>LocalTensor<U>ReinterpretCast(){return{p,off};}};
template<class T>struct LoadData3DParamsV2{unsigned l1H=0,l1W=0,channelSize=0,strideH=0,strideW=0,filterH=0,filterW=0,dilationFilterH=0,dilationFilterW=0,mStartPt=0,kStartPt=0,mExtension=0,kExtension=0;bool enTranspose=false,fMatrixCtrl=false;uint8_t padList[4]={0};T padValue=0;};
template<class T,const IsResetLoad3dConfig&C=defaultConfig>void LoadData(LocalTensor<T>dst,LocalTensor<T>src,LoadData3DParamsV2<half>p){
if constexpr(C.isSetFMatrix)SetFmatrix(p.l1H,p.l1W,p.padList);if constexpr(C.isSetPadding){padding=p.padValue;++paddingSets;}
assert(width==128&&padding==0&&p.l1H==1&&p.l1W==128&&p.channelSize==1280&&!p.enTranspose&&!p.fMatrixCtrl&&p.mStartPt==0&&p.kStartPt==expectK&&p.mExtension==128&&p.kExtension==128);
assert(p.strideH==1&&p.strideW==1&&p.filterH==1&&p.filterW==1&&p.dilationFilterH==1&&p.dilationFilterW==1);
for(unsigned m=0;m<128;++m)for(unsigned k=0;k<128;++k){unsigned from=src.off+((expectK+k)/16*width+m)*16+(expectK+k)%16;unsigned to=dst.off+(m/16*8+k/16)*256+(m%16)*16+k%16;assert(from<src.p->size()&&to<dst.p->size());(*dst.p)[to]=(*src.p)[from];assert((*dst.p)[to]==(globalM+m)*1280+expectK+k);++checks;}++loads;
}
}
void setup(unsigned rows){constexpr bool SPLIT_FMATRIX=true;
'''
END=r'''
int main(){for(bool reuse:{false,true}){width=padding=999;matrixSets=paddingSets=loads=0;checks=0;padding=0; // original entry initializes padding before Cube helper
for(unsigned core=0;core<20;++core){int cached=-1;std::vector<half>a(128*1280),out(128*128+8,9876543);AscendC::LocalTensor<half>src{&a,0},dst{&out,0};
for(unsigned task=80*core/20;task<80*(core+1)/20;++task){unsigned mt=task/5,ns=task%5;globalM=mt*128;if(cached!=int(mt)){cached=mt;for(unsigned m=0;m<128;++m)for(unsigned k=0;k<1280;++k)a[(k/16*128+m)*16+k%16]=(globalM+m)*1280+k;if(reuse)setup(128);}
for(unsigned nt=ns*12/5;nt<(ns+1)*12/5;++nt)for(expectK=0;expectK<1280;expectK+=128){if(reuse)ManualTransposeFullM<half,false,true>(dst,src,1280,128,128,expectK);else ManualTransposeFullM<half,false,false>(dst,src,1280,128,128,expectK);}
}for(unsigned i=128*128;i<out.size();++i)assert(out[i]==9876543);}
assert(loads==1920&&checks==31457280);assert(matrixSets==(reuse?32:1920));assert(paddingSets==(reuse?0:1920));}
std::cout<<"Actual helper:62914560 source/destination tag checks, all1920 K panels old/new, FMatrix setups1920->32, original padding initialization and L0 guards PASS\n";}
'''
with tempfile.TemporaryDirectory(prefix='bmmms-c9-left-') as tmp:
 d=Path(tmp)
 def run(h,p,name):
  src=d/(name+'.cpp');e=d/name;src.write_text(PRE+p+'\n}\n'+h+END);subprocess.run(['c++','-std=c++17','-O2',str(src),'-o',str(e)],check=True);return subprocess.run([str(e)],capture_output=True)
 r=run(helper,setup,'good');assert r.returncode==0,r.stderr.decode();print(r.stdout.decode(),end='')
 for name,h,p in [('missing_setup',helper,''),('wrong_width',helper,setup.replace('1,rows,zeroPad','1,rows/2,zeroPad')),('wrong_K_offset',helper.replace('panel.kStartPt=TX1?0:k0','panel.kStartPt=TX1?0:0'),setup),('resetting_instead_of_reuse',helper.replace('RESIDENT_NN_KEEP_LOAD3D={false,false}','RESIDENT_NN_KEEP_LOAD3D={true,true}'),setup)]:
  assert h!=helper or p!=setup;assert run(h,p,name).returncode!=0,name
print('Four controls/full parent inverse/protected7/NT B2D config preservation PASS; integer tags do not prove native time or SIMD synchronization')
