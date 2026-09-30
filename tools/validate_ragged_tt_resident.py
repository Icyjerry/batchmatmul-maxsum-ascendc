#!/usr/bin/env python3
"""Extract the resident TT loaders and host route; CPU semantics, not CANN."""
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'kernel.asc').read_text()
shapes = source[source.index('struct Shape {'):source.index('template <AscendC::HardEvent')]
host = source[source.index('struct Plan {'):source.index('using CacheKey =')]
host_model = (root / 'tests/cpu/planner_stub.hpp').read_text() + shapes + host + r'''
int main() {
    auto* hw=platform_ascendc::PlatformAscendCManager::GetInstance();
    unsigned selected=0;
    for(int cores: {1,8,20,24,32}) for(int m: {1024,1025,1537,2047})
    for(int n: {1024,1025,1537,4095}) for(int k: {1024,1032,1536,1784,2040,2048}) {
        hw->aic=cores;hw->aiv=2*cores;
        Shape s{1,m,n,k,2,1,1};auto p=MakePlan(s,cores);const auto& d=p.schedule;
        if(m%16==0 && n%16==0 && k%16==0) {assert(d.dual!=26);continue;}
        if(d.dual!=26)std::cerr << "unselected " << cores << ": " << m << ',' << n << ',' << k << " dual=" << d.dual << '\n';
        assert(d.dual==26 && d.kSplit==1 && d.kChunk==128);++selected;
        assert(d.baseM==64 || d.baseM==128);assert(d.baseN==128);
        assert(d.mTiles==Ceil(m,d.baseM) && d.nTiles==Ceil(n,128));
        assert(d.nSplit>=1 && d.nTiles>=2*d.nSplit);
        assert(d.workers==std::min<int64_t>(cores,d.mTiles*d.nSplit));
        assert(d.workers==p.cubeBlocks && d.window==1 && !d.earlySum && !d.tree);
        assert(uint64_t(d.baseM)*Ceil(k,16)*16*2+128*128*4+1024+4096<=hw->l1);
        assert(uint64_t(d.baseM)*128*4<=hw->l0a && 128*128*4<=hw->l0b);
        assert(uint64_t(d.baseM)*128*8<=hw->l0);
        auto partial=uint64_t(d.mTiles)*d.baseM*d.nSplit*4;
        assert(p.totalBytes==p.systemBytes+Ceil(partial,512)*512+
            uint64_t(d.workers)*2*d.baseM*d.baseN*4);
        // Independent ownership check: every valid (m, N tile) pair exactly once.
        std::vector<int> seen(m*d.nTiles,0);
        for(unsigned w=0;w<d.workers;++w)
        for(unsigned t=w;t<d.mTiles*d.nSplit;t+=d.workers) {
            unsigned ns=t%d.nSplit,mt=t/d.nSplit;
            for(unsigned r=mt*d.baseM;r<std::min<unsigned>(m,(mt+1)*d.baseM);++r)
            for(unsigned nt=ns*d.nTiles/d.nSplit;nt<(ns+1)*d.nTiles/d.nSplit;++nt)
                assert(++seen[r*d.nTiles+nt]==1);
        }
        for(int x:seen)assert(x==1);
    }
    hw->aic=20;hw->aiv=40;
    const Shape target{1,1025,1537,1032,2,1,1};
    assert(MakePlan(target,20).schedule.dual==26);
    for(Shape s: {Shape{2,1025,1537,1032,2,1,1},Shape{1,1025,1537,1032,1,1,1},
        Shape{1,1025,1537,1032,2,0,1},Shape{1,1025,1537,1032,2,1,0},
        Shape{1,1025,1537,2056,2,1,1}})assert(MakePlan(s,20).schedule.dual!=26);
    for(auto mem: {&hw->l1,&hw->l0a,&hw->l0b,&hw->l0,&hw->ub}) {
        auto old=*mem;*mem=8192;assert(MakePlan(target,20).schedule.dual!=26);*mem=old;
    }
#ifdef BMMMS_TUNING
    for(auto pin: {&Tune().bm,&Tune().bn,&Tune().window,&Tune().ns,&Tune().workers,
                  &Tune().dual,&Tune().ks,&Tune().tree,&Tune().early}) {
        Tune()=TuneConfig{};*pin=1;assert(MakePlan(target,20).schedule.dual!=26);
    }
#endif
    std::cout << "resident TT host route/ownership/resource checks: " << selected << " selected\n";
}
'''

# Reuse the explicit NZ/ZZ mocks; extract the actual producer helpers and A copy.
mock = (root / 'tests/cpu/panel_model.cpp.in').read_text()
mock = mock[:mock.index('struct Schedule {')] + shapes + mock[mock.index('struct Expected {'):mock.index('// INSERT_HELPERS')]
mock = mock.replace('int16_t A(int64_t b,int64_t m,int64_t k){return int((b*13+m*7+k*3)%7)-3;}',
    'bool negativeA=false;\nint16_t A(int64_t b,int64_t m,int64_t k){return negativeA?1+(b*13+m*7+k*3)%3:int((b*13+m*7+k*3)%7)-3;}')
zero = source[source.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):source.index('// One Cube owns one complete small batch.')]
copy = source[source.index('template<typename T,bool TX1,bool TX2,bool PAD_MN=false,bool SKIP_B=false>'):source.index('__aicore__ inline void ManualCopyC')]
load = source[source.index('template<typename T>\n__aicore__ inline void ManualLoadResidentTT'):source.index('// The basic-API path owns all local events;')]
manual = source[source.index('void bmmms_manual('):]
resident_copy = manual[manual.index('resident=residentBuf.Get<T>();'):manual.index('        for(uint32_t nt=begin;nt<end;++nt)')]
resident_copy = resident_copy[:resident_copy.rfind('        }')]
physical_model = mock + zero + copy + load + r'''
void Check(unsigned m,unsigned n,unsigned k,unsigned m0,unsigned n0,unsigned bm) {
    using T=int16_t;
    constexpr bool TX1=true,RESIDENT_PAD=true;
    Schedule s{};s.b=1;s.m=m;s.n=n;s.k=k;s.baseM=bm;s.baseN=128;
    const unsigned batch=0,bk=128,kp=(k+15)/16*16;
    const unsigned validRows=std::min(bm,m-m0),rows=(validRows+15)/16*16;
    const unsigned validCols=std::min(128U,n-n0),cols=(validCols+15)/16*16;
    st=State{};st.s=s;
    std::vector<int16_t> av(m*k),bv(n*k);
    for(unsigned r=0;r<m;++r)for(unsigned q=0;q<k;++q)av[q*m+r]=A(0,r,q);
    for(unsigned c=0;c<n;++c)for(unsigned q=0;q<k;++q)bv[c*k+q]=B(0,q,c);
    AscendC::GlobalTensor<int16_t> a{&av,0,true},b{&bv,0,false};
    AscendC::TPipe pipe;AscendC::TBuf<AscendC::TPosition::A1> residentBuf;
    AscendC::TBuf<AscendC::TPosition::A2> ab;AscendC::TBuf<AscendC::TPosition::B2> bb;
    AscendC::TQue<AscendC::TPosition::A1,2> aq;AscendC::TQue<AscendC::TPosition::B1,2> bq;
    pipe.InitBuffer(residentBuf,bm*kp*2);pipe.InitBuffer(ab,bm*bk*2);
    pipe.InitBuffer(bb,128*bk*2);pipe.InitBuffer(aq,2,512);pipe.InitBuffer(bq,2,128*bk*2);
    AscendC::LocalTensor<int16_t> resident;
''' + resident_copy + r'''
    // Read the same resident operand twice to check reuse and both K tails.
    std::vector<float> c(rows*cols,0);
    for(unsigned repeat=0;repeat<2;++repeat) {
        std::fill(c.begin(),c.end(),0);
        for(unsigned k0=0;k0<k;k0+=bk) {
            const unsigned count=(std::min(bk,k-k0)+15)/16*16;
            auto a2=ab.Get<int16_t>(),b2=bb.Get<int16_t>();
            ManualLoadResidentTT(a2,resident,rows,kp,k0,count);
            ManualCopyK<int16_t,true,true,true>(aq,bq,a,b,s,bk,validRows,validCols,0,m0,n0,k0,true);
            auto b1=bq.DeQue<int16_t>();AscendC::LoadData2DParams lp;
            lp.ifTranspose=false;lp.repeatTimes=count*cols/256;lp.srcStride=1;lp.dstGap=0;
            AscendC::LoadData(b2,b1,lp);bq.FreeTensor(b1);
            for(unsigned r=0;r<rows;++r)for(unsigned q=0;q<count;++q) {
                auto ai=((r/16)*(count/16)+q/16)*256+(r%16)*16+q%16;
                auto gold=(r<validRows && k0+q<k)?A(0,m0+r,k0+q):0;
                assert(a2.at(ai)==gold);
            }
            for(unsigned col=0;col<cols;++col)for(unsigned q=0;q<count;++q) {
                auto bi=((q/16)*(cols/16)+col/16)*256+(col%16)*16+q%16;
                auto gold=(col<validCols && k0+q<k)?B(0,k0+q,n0+col):0;
                assert(b2.at(bi)==gold);
            }
            // Execute physical dot products for small cases, independent golden below.
            if(m<=65 && n<=129)for(unsigned r=0;r<rows;++r)for(unsigned col=0;col<cols;++col)
                for(unsigned q=0;q<count;++q) {
                    auto ai=((r/16)*(count/16)+q/16)*256+r%16*16+q%16;
                    auto bi=((q/16)*(cols/16)+col/16)*256+col%16*16+q%16;
                    c[r*cols+col]+=float(a2.at(ai))*float(b2.at(bi));
                }
        }
        if(m<=65 && n<=129) {
            float y=0,goldenY=0;
            for(unsigned r=0;r<validRows;++r) {
                float mx=-1e30f,gmx=-1e30f;
                for(unsigned col=0;col<validCols;++col) {
                    float gold=0;for(unsigned q=0;q<k;++q)gold+=float(A(0,m0+r,q))*float(B(0,q,n0+col));
                    assert(c[r*cols+col]==gold);mx=std::max(mx,c[r*cols+col]);gmx=std::max(gmx,gold);
                }
                y+=mx;goldenY+=gmx;
            }
            assert(y==goldenY);if(negativeA)assert(y<0);
        }
    }
    assert(st.aCopies==1 && st.aReads==validRows*k);
}
int main() {
    unsigned cases=0;
    for(unsigned bm: {64U,128U})for(unsigned m: {17U,65U,1025U,1537U})
    for(unsigned n: {17U,129U,1537U})for(unsigned k: {40U,136U,1032U,1536U,2040U,2048U}) {
        if(bm*((k+15)/16*16)*2+128*128*4+1024>512*1024)continue;
        const unsigned m0=(m-1)/bm*bm,n0=(n-1)/128*128;
        Check(m,n,k,m0,n0,bm);++cases;
        if(m0 || n0) {Check(m,n,k,0,0,bm);++cases;}
    }
    // Execute negative-only dot products through the extracted loaders as well.
    negativeA=true;
    for(unsigned n: {1U,15U,17U,31U,127U}) {
        Check(17,n,136,0,0,64);++cases;
    }
    std::cout << "resident TT physical NZ/ZZ/ZN and reused C oracle: " << cases << " cases\n";
}
'''
compiler = shutil.which('clang++') or shutil.which('c++')
assert compiler
with tempfile.TemporaryDirectory(prefix='bmmms-resident-tt-') as tmp:
    for name, model, flags in [('host', host_model, []), ('host-tuning', host_model, ['-DBMMMS_TUNING']),
                               ('physical', physical_model, [])]:
        cpp, exe = Path(tmp) / (name + '.cpp'), Path(tmp) / name
        cpp.write_text(model)
        subprocess.run([compiler, '-std=c++17', '-O2', *flags, str(cpp), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
