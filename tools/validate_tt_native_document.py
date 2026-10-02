#!/usr/bin/env python3
"""Extracted TT swapped operands: physical CPU address/event models, not NPU timing."""
from pathlib import Path
import hashlib,shutil,subprocess,tempfile
from validate_c7_manual_frame import span,source
from validate_tt_manual_frame import cube as old_cube,vector as old_vector
ROOT=Path(__file__).resolve().parents[1]
BASE=source('1734f16')
ENTRY=span(BASE,'// Same TT tile/package stream','// All N-tile partials are ready')

def scope(s):
 entry=span(s,'// TT operands are swapped:','// All N-tile partials are ready')
 host=span(s,'// Resource-selected TT document frame','using CacheKey =')
 call='''    const auto ttDocument=MakeTTDocumentFrame(s,p);
    if(ttDocument.workers) {
        bmmms_tt_native_document<T><<<p.cubeBlocks,nullptr,stream>>>(x1,x2,partial,y,ttDocument);
        return;
    }
'''
 assert s.count(call)==1 and s.replace(entry,'',1).replace(host,'',1).replace(call,'',1)==BASE
 return entry,host

def cube(s,entry):
 f=old_cube(BASE,ENTRY).split('void Run(uint32_t M,uint32_t N,uint32_t K,uint32_t BM')[0]
 f=f.replace(ENTRY,entry)
 f=f.replace('if(p==TPosition::B1){mem=', 'if(p==TPosition::A1&&start){mem=')
 f=f.replace('srcDValue,dstNzC0Stride,dstNzNStride;','srcDValue,dstNzC0Stride,dstNzNStride,srcNdMatrixStride=0,dstNzMatrixStride=0;')
 a=f.index('template<class T>void DataCopy(LocalTensor<T> dst,GlobalTensor<T> src,Nd2NzParams p)');b=f.index('struct LoadData2DParams',a)
 f=f[:a]+'''template<class T>void DataCopy(LocalTensor<T> dst,GlobalTensor<T> src,Nd2NzParams p){
 assert(p.ndNum>=1&&p.ndNum<=4095&&p.nValue>=1&&p.dValue>=1);
 assert(p.dstNzNStride>=1&&p.dstNzC0Stride>=1);
 assert(!dst.mem->pending);dst.mem->pending=true;
 dma.push_back({dst.mem,[=]{
  for(uint32_t matrix=0;matrix<p.ndNum;++matrix)
  for(uint32_t r=0;r<p.nValue;++r)for(uint32_t c=0;c<(p.dValue+15)/16*16;++c){
   size_t di=matrix*p.dstNzMatrixStride+(c/16)*p.dstNzC0Stride*16+r*p.dstNzNStride*16+c%16;
   size_t si=matrix*p.srcNdMatrixStride+r*p.srcDValue+c;
   dst.at(di)=c<p.dValue?src.at(si):0;
  }
 }});
 (src.isA?st.aReads:st.bReads)+=uint64_t(p.ndNum)*p.nValue*p.dValue;
 ++(src.isA?st.aCopies:st.bCopies);
}
'''+f[b:]
 a=f.index('void LoadData(LocalTensor<half>');b=f.index('struct MmadParams',a)
 f=f[:a]+'''// Independent NC1HWC0 -> im2col -> ZZ / ZN mapping, per CANN900 Load3D.
void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 assert(!p.enTranspose&&p.channelSize%16==0&&p.channelSize>0);
 assert(p.filterH==1&&p.filterW>=1&&p.filterW<=255&&p.strideH==1&&p.strideW==1);
 assert(p.dilationFilterH==1&&p.dilationFilterW==1);
 assert(p.mStartPt%16==0&&p.kStartPt%16==0&&p.mExtension%16==0&&p.kExtension%16==0);
 assert((dst.mem->pos==TPosition::A2&&src.mem->pos==TPosition::A1)||
        (dst.mem->pos==TPosition::B2&&src.mem->pos==TPosition::B1));
 mte1.push_back([=]{
  assert(!src.mem->pending);
  const uint32_t outW=p.l1W-p.filterW+1,outH=p.l1H;
  assert(p.mStartPt+p.mExtension<=outW*outH);
  assert(p.kStartPt+p.kExtension<=p.channelSize*p.filterW);
  for(uint32_t r=0;r<p.mExtension;++r)for(uint32_t c=0;c<p.kExtension;++c){
   uint32_t mo=p.mStartPt+r,ko=p.kStartPt+c;
   uint32_t oh=mo/outW,ow=mo%outW,ci=(ko/(p.filterW*16))*16+ko%16,fw=(ko/16)%p.filterW;
   size_t si=((ci/16)*p.l1H*p.l1W+oh*p.l1W+ow+fw)*16+ci%16;
   size_t di=((r/16)*(p.kExtension/16)+c/16)*256;
   di+=dst.mem->pos==TPosition::A2?(r%16)*16+c%16:(c%16)*16+r%16;
   dst.at(di)=src.at(si);
  }
 });
 (dst.mem->pos==TPosition::A2?st.aL0:st.bL0)+=uint64_t(p.mExtension)*p.kExtension;
 ++(dst.mem->pos==TPosition::A2?st.aLoads:st.bLoads);
}
'''+f[b:]
 f=f.replace('p.dstStride==st.s.baseN*st.s.window','p.dstStride==st.s.baseM')
 f=f.replace('if(m<e.rows && n<e.cols)for(uint32_t k=0;k<st.s.k;++k)gold+=float(A(e.b,e.m+m,k))*float(B(e.b,k,e.n+n));',
 'if(n<e.rows && m<e.cols)for(uint32_t k=0;k<st.s.k;++k)gold+=float(A(e.b,e.m+n,k))*float(B(e.b,k,e.n+m));')
 f=f.replace('if(m<e.rows && n<e.cols) {','if(n<e.rows && m<e.cols) {').replace('e.m+m,e.ns','e.m+n,e.ns')
 footer=(ROOT/'tests/cpu/tt_manual_frame_cube.cpp.in').read_text().split('int main()')[0]
 footer=footer.replace('uint32_t workers,bool neg)', 'uint32_t workers,uint32_t NS,bool neg)')
 footer=footer.replace('TTFrameShape q{M,N,K,BM,BN,PK,nt,workers};','TTDocumentShape q{M,N,K,BM,BN,PK,NS,workers};')
 footer=footer.replace('Schedule s{1,M,N,K,BM,BN,mt,nt,nt,workers,0,0};','Schedule s{1,M,N,K,BM,BN,mt,nt,NS,workers,0,0};')
 footer=footer.replace('prefix=(nt*mt*BM+127)/128*128','prefix=(NS*mt*BM+127)/128*128')
 footer=footer.replace('uint32_t begin=w*mt*nt/workers,end=(w+1)*mt*nt/workers,acopies=0;',
 '''uint32_t gb=w*mt*NS/workers,ge=(w+1)*mt*NS/workers;
  uint32_t begin=(gb/NS)*nt+(gb%NS)*nt/NS,end=(ge/NS)*nt+(ge%NS)*nt/NS,acopies=0;''')
 footer=footer.replace('bmmms_tt_manual_frame<int16_t>','bmmms_tt_native_document<int16_t>')
 f+=footer+(ROOT/'tests/cpu/tt_native_document_cube.cpp.in').read_text()
 return f

def vector(s,entry):
 f=old_vector(BASE,ENTRY).split('void Run(uint32_t M,uint32_t N,uint32_t BM')[0]
 oldheader=ENTRY[:ENTRY.index('template<typename T>')]
 oldkernel=ENTRY[ENTRY.index('template<typename T>\n__schedmode__(1)'):]
 header=entry[:entry.index('template<typename T>')]
 kernel=entry[entry.index('template<typename T>\n__schedmode__(1)'):]
 assert oldheader in f and oldkernel in f
 f=f.replace(oldheader,header).replace(oldkernel,kernel)
 # The ordinal of a Cube tile depends on the parent N-shard assignment.
 f=f.replace('uint32_t total=(s.mp/s.bm)*s.nt,begin=(st.block/2)*total/s.workers,end=(st.block/2+1)*total/s.workers;',
 '''uint32_t total=(s.mp/s.bm)*s.ns,gb=(st.block/2)*total/s.workers,ge=(st.block/2+1)*total/s.workers;
 uint32_t begin=(gb/s.ns)*s.nt+(gb%s.ns)*s.nt/s.ns,end=(ge/s.ns)*s.nt+(ge%s.ns)*s.nt/s.ns;''')
 f=f.replace('st.ring[flag*s.bm*s.np+r*s.np+n]', 'st.ring[flag*s.bm*s.np+n*s.bm+r]')
 a=f.index(' auto s=shared->s;uint32_t sub=',f.index('void DataCopyPad(LocalTensor<float>'));b=f.index('\n}\ntemplate<class T>void DataCopy',a)
 f=f[:a]+''' auto s=shared->s;uint32_t start=(st.block%2)*(s.bm/2),total=(s.mp/s.bm)*s.ns;
 uint32_t gb=(st.block/2)*total/s.workers;
 uint32_t first=(gb/s.ns)*s.nt+(gb%s.ns)*s.nt/s.ns,task=first+st.issued-1,m0=(task/s.nt)*s.bm,nt=task%s.nt;
 uint32_t hm=s.bm/2,rows=start+m0>=s.m?0:std::min(s.m-m0-start,hm),cols=std::min(s.n-nt*s.np,s.np),padded=(rows+7)/8*8;
 int gen=st.issued-1;uint32_t slot=gen&1;
 assert(src.kind==GlobalTensor<float>::RING&&src.offset==slot*s.bm*s.np+start);
 assert(p.blockCount==cols&&p.blockLen==rows*4&&p.srcStride==(s.bm-rows)*4&&p.dstStride==(hm-padded)/8);
 assert(pad.pad&&pad.left==0&&pad.right==padded-rows&&pad.value==-std::numeric_limits<float>::infinity());
 assert(dst.offset==slot*hm*s.np);++st.copies;
 st.Push(PIPE_MTE2,[=]{assert(st.ringGen[slot]==gen&&"GM released before DMA");
  for(uint32_t n=0;n<cols;++n)for(uint32_t m=0;m<padded;++m){
   dst.At(n*hm+m)=m<rows?src.At(n*s.bm+m):pad.value;dst.Gen(n*hm+m)=gen;
  }
 });'''+f[b:]
 a=f.index(' auto s=shared->s;uint32_t worker=',f.index('void DataCopy(GlobalTensor<float>'));b=f.index('\n}\nvoid DataCopy(LocalTensor<float>',a)
 f=f[:a]+''' auto s=shared->s;uint32_t worker=st.block/2,sub=st.block%2,total=(s.mp/s.bm)*s.ns;
 uint32_t gb=worker*total/s.workers,ge=(worker+1)*total/s.workers,group=gb+st.stores++;
 assert(group<ge);uint32_t mt=group/s.ns,ns=group%s.ns;int gen=st.issued-1;
 assert(dst.kind==GlobalTensor<float>::PARTS&&dst.offset==ns*s.mp+mt*s.bm+sub*s.bm/2&&count==s.bm/2);
 assert(src.offset==s.bm*s.np+((group-gb)&1)*s.bm/2);
 st.Push(PIPE_MTE3,[=]{for(uint32_t i=0;i<count;++i){
  uint32_t start=mt*s.bm+sub*s.bm/2,rows=start>=s.m?0:std::min(s.bm/2,s.m-start);
  int initial=gen-int((ns+1)*s.nt/s.ns-ns*s.nt/s.ns);
  assert(src.Gen(i)==(i<rows?gen:initial)&&"row overwritten before store or V completion");
  dst.At(i)=src.At(i);assert(shared->written[dst.offset+i].fetch_add(1,std::memory_order_release)==0);
 }});'''+f[b:]
 f=f.replace('issued=0,copies=0','issued=0,stores=0,copies=0')
 a=f.index('void Duplicate(LocalTensor<float> dst,float v,uint32_t count)');b=f.index('void Max(',a)
 f=f[:a]+'''void Duplicate(LocalTensor<float> dst,float v,uint32_t count){
 int gen=st.issued-1;
 st.Push(PIPE_V,[=]{for(uint32_t i=0;i<count;++i){dst.At(i)=v;dst.Gen(i)=gen;}});
}
void Duplicate(LocalTensor<float> dst,float v,uint64_t mask,uint8_t reps,uint16_t bs,uint8_t rs){
 assert(mask>=1&&mask<=64&&reps>0&&bs==1&&rs==shared->s.bm/16);int gen=st.issued-1;
 st.Push(PIPE_V,[=]{for(uint32_t r=0;r<reps;++r)for(uint32_t i=0;i<mask;++i){dst.At(r*rs*8+i)=v;dst.Gen(r*rs*8+i)=gen;}});
}
'''+f[b:]
 # A row is deliberately retained across complete-K N tiles, unlike the parent one-tile row.
 f=f.replace('assert(a.Gen(i)>=0&&b.Gen(i)==gen);', 'assert(a.Gen(i)>=-1&&b.Gen(i)==gen);')
 f+=(ROOT/'tests/cpu/tt_native_document_vector.cpp.in').read_text()
 return f

def host(s,entry,h):
 from validate_tt_manual_frame import ROOT as oldroot
 stub=(ROOT/'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {','struct TCubeTiling {int stepKa=1,stepKb=1;')
 shapes=span(s,'struct Shape {','template <AscendC::HardEvent')
 plans=span(s,'struct Plan {','// Select only an already complete TF batch')
 header=entry[:entry.index('template<typename T>')]
 return '#include <cstring>\n'+stub+shapes+header+plans+h+(ROOT/'tests/cpu/tt_native_document_host.cpp.in').read_text()

def main():
 s=(ROOT/'kernel.asc').read_text();entry,h=scope(s)
 print('Exact scope: baseline restored by removing three additions; SHA',hashlib.sha256(s.encode()).hexdigest(),flush=True)
 compiler=shutil.which('clang++') or shutil.which('c++')
 with tempfile.TemporaryDirectory(prefix='bmmms-tt-doc-') as tmp:
  def run(name,code,bad=False,flags=()):
   cpp,exe=Path(tmp)/(name+'.cpp'),Path(tmp)/name;cpp.write_text(code)
   subprocess.run([compiler,'-std=c++17','-O2','-pthread',*flags,str(cpp),'-o',str(exe)],check=True)
   r=subprocess.run([str(exe)],capture_output=bad,timeout=180)
   if bad:assert r.returncode!=0,'negative control missed: '+name
   else:r.check_returncode()
  c=cube(s,entry);run('cube',c)
  for name,old,new in [
   ('doc-reader','    AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(slot);',''),
   ('query-reader','            AscendC::WaitFlag<AscendC::HardEvent::MTE1_MTE2>(2);',''),
   ('l0-reader','            AscendC::WaitFlag<AscendC::HardEvent::M_MTE1>(bs);',''),
   ('c0-reader','            if(k0==0)AscendC::WaitFlag<AscendC::HardEvent::FIX_M>(cs);',''),
   ('doc-row-stride','cp.dstNzMatrixStride=s.packageK','cp.dstNzMatrixStride=16'),
   ('doc-pad','if(missing)AscendC::InitConstValue','if(false)AscendC::InitConstValue')]:
   unsafe=c.replace(old,new);assert unsafe!=c;run('no-'+name,unsafe,True)
  v=vector(s,entry);run('vector',v)
  for name,old,new in [
   ('c-ready','            AscendC::WaitFlag<AscendC::HardEvent::MTE2_V>(slot);',''),
   ('row-reader','        AscendC::WaitFlag<AscendC::HardEvent::MTE3_V>(rs);',''),
   ('barrier','    AscendC::SyncAll<true>();',''),
   ('n-pad','if(cols<s.bn)AscendC::Duplicate','if(false)AscendC::Duplicate'),
   ('n-tree','step=s.bn/2','step=s.bn/4'),
   ('m-tail','full=s.m/64,tail=s.m%64','full=(s.m+63)/64,tail=0')]:
   unsafe=v.replace(old,new);assert unsafe!=v;run('no-'+name,unsafe,True)
  print('Six Cube / six AIV negative controls rejected PASS',flush=True)
  h=host(s,entry,h);run('host',h);run('host-tuning',h,flags=['-DBMMMS_TUNING'])
 print('CPU integer models PASS, native CANN9/FP16/BF16/latency PENDING. No hardware timing simulation.')
if __name__=='__main__':main()
