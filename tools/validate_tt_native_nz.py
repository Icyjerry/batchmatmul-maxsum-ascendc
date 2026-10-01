#!/usr/bin/env python3
"""Actual manual Cube NZ ring and Vector slab/tree Max, bounded CPU models.

Reuse passing B-stream engine models. No CANN/NPU/timing/FP16 precision claim.
"""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile

ROOT=Path(__file__).resolve().parents[1]
base=(ROOT/'tools/validate_tt_b_stream.py').read_text().rsplit('\ndef main():',1)[0]
old=next(line for line in base.splitlines() if line.startswith('text=text[:a]+'))
base=base.replace(old,'text=text[:a]+text[b:]')
base=base.replace('exec(text,ns)', '''text=text.replace("src.index('// All N-tile partials are ready')", "src.index('// Native C0/NZ ring:')")
exec(text,ns)''',1)
ns={'__file__':str(ROOT/'tools/validate_tt_b_stream.py')}
exec(base,ns)
src=ns['src']
parent=subprocess.check_output(['git','show','e1b3634:kernel.asc'],cwd=ROOT,text=True)

def producer(code):
    code=code.replace('namespace AscendC {','namespace AscendC {\nconstexpr int CFG_NZ=1;',1)
    old='void Fixpipe(GlobalTensor<float> dst,LocalTensor<float> src,FixpipeParamsV220 p){'
    assert code.count(old)==1
    code=code.replace(old,'template<class D=float,class S=float,auto CFG=0>\nvoid Fixpipe(GlobalTensor<D> dst,LocalTensor<S> src,FixpipeParamsV220 p){')
    code=code.replace('assert(p.srcStride==p.mSize && p.dstStride==st.s.baseN*st.s.window);',
       'assert(p.srcStride==p.mSize);if constexpr(CFG==CFG_NZ)assert(p.dstStride==st.s.baseM*2);else assert(p.dstStride==st.s.baseN*st.s.window);')
    code=code.replace('dst.at(m*p.dstStride+n)=v;',
       'dst.at(CFG==CFG_NZ?(n/16)*p.dstStride*8+m*16+n%16:m*p.dstStride+n)=v;')
    return code

models=[(name,producer(ns[key])) for name,key in [('producer','model'),('delayed-engines','delayed_model'),
        ('eager-mte2','eager_model'),('legacy-producer','legacy_model')]]

a=src.index('// Native C0/NZ ring:');b=src.index('// All N-tile partials',a)
consumer=src[a:b]
cm=(ROOT/'tests/cpu/fullk_window_consumer_model.cpp.in').read_text()
a=cm.index('void DataCopyPad(');b=cm.index('template<int Mode>void CrossCoreWaitFlag',a)
cm=cm[:a]+r'''
void DataCopyPad(LocalTensor<float> dst,GlobalTensor<float> src,DataCopyExtParams p,DataCopyPadExtParams<float> pad){
 assert(!pad.pad&&!dst.mem->pending);const uint32_t BM=st.s.baseM,BN=st.s.baseN;
 const uint32_t cols=std::min(BN,uint32_t(st.s.n)-(st.nt+st.copies)*BN),groups=(cols+15)/16;
 assert(p.blockCount==groups&&p.blockLen==st.rows*16*4&&p.srcStride==(BM-st.rows)*16*4&&p.dstStride==0);
 const size_t expected=st.slot*st.slotSize+st.copies*BM*BN+st.sub*(BM/2)*16;
 assert(src.offset==expected);++st.copies;dst.mem->pending=true;
 st.dma.push_back([=]{
  assert(st.releases[0]!=1||st.releases[1]!=1);
  for(uint32_t g=0;g<groups;++g)for(uint32_t r=0;r<st.rows;++r)for(uint32_t lane=0;lane<16;++lane)
   dst.At(g*st.rows*16+r*16+lane)=src.At(g*BM*16+r*16+lane);
  dst.mem->pending=false;
 });
}
''' + cm[b:]
cm=cm.replace('rs==st.s.baseN/8','rs==2')
cm=cm.replace('ManualFullMConsumeWindow(', 'ManualFullMConsumeNZWindow(')
cm=cm.replace('   ring[st.slot*slotSize+r*BN*W+c]=Value(r,nt*BN+c,neg);',
 '   ring[st.slot*slotSize+(c/BN)*BM*BN+((c%BN)/16)*BM*16+r*16+c%16]=Value(r,nt*BN+c,neg);')
needle='}\n}\n// INSERT_CONSUMER'
assert cm.count(needle)==1
cm=cm.replace(needle,r'''}
struct BinaryRepeatParams{uint32_t d,s1,s2,dr,s1r,s2r;};
void Max(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint64_t mask,uint32_t reps,BinaryRepeatParams p){
 assert(p.d==1&&p.s1==1&&p.s2==1&&p.dr==8&&p.s1r==8&&p.s2r==8);
 for(uint32_t r=0;r<reps;++r)Max(dst[r*64],a[r*64],b[r*64],mask);
}
void Duplicate(LocalTensor<float> dst,float v,uint64_t masks[2],uint32_t reps,uint32_t block,uint32_t stride){
 assert(masks[0]==0&&block==1&&stride==2);
 for(uint32_t r=0;r<reps;++r)for(uint32_t j=0;j<64;++j)if(masks[1]&(uint64_t(1)<<j))dst.At(r*16+j)=v;
}
}
// INSERT_CONSUMER''')
cm=cm.replace('// INSERT_CONSUMER',consumer)
cm=cm.replace('extracted wide-window consumer cases:', 'actual NZ slab/tree consumer cases:')

# Prove changes are restricted to native manual copyout/consumer dispatch/helper.
old=src
a=old.index('// Native C0/NZ ring:');b=old.index('// All N-tile partials',a);old=old[:a]+old[b:]
dispatch='''                if constexpr(TILE_STREAM)
                    ManualFullMConsumeNZWindow(cq,ring,s,slotSize,rowStart,rows,nt,tiles,sequence,maxima,row);
                else ManualFullMConsumeWindow(cq,ring,s,slotSize,rowStart,rows,nt,tiles,sequence,maxima,row);'''
assert old.count(dispatch)==1
old=old.replace(dispatch,'                ManualFullMConsumeWindow(cq,ring,s,slotSize,rowStart,rows,nt,tiles,sequence,maxima,row);')
a=old.index('            fp.nSize=cols;fp.mSize=rows;fp.srcStride=rows;\n            if constexpr(TILE_STREAM)')
b=old.index('            AscendC::SetFlag<AscendC::HardEvent::FIX_M>(cFree[cs]);',a)
old=old[:a]+'''            fp.nSize=cols;fp.mSize=rows;fp.srcStride=rows;fp.dstStride=span*bn;
            AscendC::Fixpipe(ring[slot*slotSize+pairIndex*bn],cAll[cs*oneC],fp);
'''+old[b:]
assert old==parent,'changes beyond native NZ ring/consumer'

def main():
    compiler=shutil.which('clang++') or shutil.which('c++');assert compiler
    print('kernel SHA256:',hashlib.sha256(src.encode()).hexdigest(),flush=True)
    with tempfile.TemporaryDirectory(prefix='bmmms-native-nz-') as d:
        for name,code in models+[('consumer',cm)]:
            cpp,exe=Path(d)/(name+'.cpp'),Path(d)/name;cpp.write_text(code)
            subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
        unsafe=cm.replace('            AscendC::Duplicate(c[(groups-1)*groupStride],-__builtin_inff(),masks,rows,1,2);',
                          '// Negative control: remove invalid-column masking.')
        assert unsafe!=cm
        cpp,exe=Path(d)/'missing-n-mask.cpp',Path(d)/'missing-n-mask';cpp.write_text(unsafe)
        subprocess.run([compiler,'-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        result=subprocess.run([str(exe)],capture_output=True,text=True)
        assert result.returncode!=0 and 'Assertion failed' in result.stderr,'NZ N-tail negative control must fail'
        print('Unmasked poisoned N tail correctly rejected PASS')
    print('Host/workspace/UB/compute/C9 unchanged; CANN9/NPU precision/latency PENDING.')

if __name__=='__main__':main()
