#!/usr/bin/env python3
"""Execute actual C9 producer and resource selector; not CANN or timing evidence.

MTE2 and MMAD can be deferred. MTE1 is synchronous; native TQue release
semantics and cross-core hardware timing require official device validation.
"""
from pathlib import Path
import hashlib, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / 'kernel.asc').read_text()
parent = subprocess.check_output(['git', 'show', '0d4bd04:kernel.asc'], cwd=ROOT, text=True)
zero = src[src.index('template<typename T>\n__aicore__ inline void ManualZeroNZTail'):src.index('// One Cube owns one complete small batch.')]
a = src.index('template<typename T,bool TX1,bool PAD_MN>\n__aicore__ inline void Case9CopyAPackage')
b = src.index('template <typename T, bool PAD_MN>', a)
copies = src[a:b]
a = src.index('void bmmms_case9_packages(')
a = src.index('    AscendC::SetAtomicNone();', a)
b = src.index('\n#else\n    AscendC::TQue', a)
body = src[a:b]
producer = '''template<class T,bool PAD_MN>
void RunCase9(AscendC::TPipe& pipe,AscendC::GlobalTensor<T> a,AscendC::GlobalTensor<T> b,
 AscendC::GlobalTensor<float> ring,Schedule s,uint32_t worker,uint32_t bPackK){
 constexpr bool TX1=false,TX2=true,RESIDENT_A=true;
 const uint32_t aPackK=bPackK,width=s.baseN*s.window,slotSize=s.baseM*width;
 const int64_t tasks=s.b*s.mTiles*s.nSplit;uint32_t sequence=0;
''' + body + '\n}\n'
fixture = (ROOT / 'tests/cpu/fullm_transpose_model.cpp.in').read_text().split('void Run(Schedule s,bool neg)')[0]
fixture = fixture.replace('window=1;', 'window=1,kChunk=128;')
fixture = fixture.replace('MTE2_MTE1};', 'MTE2_MTE1,MTE1_MTE2};').replace('next[5]', 'next[6]')
fixture = fixture.replace('id>=4 && id<6', 'id>=2 && id<4').replace('st.cross[id-4]', 'st.cross[id-2]')
fixture = fixture.replace('namespace AscendC {', 'namespace AscendC {\nvoid SetAtomicNone(){}\nvoid SetLoadDataBoundary(uint64_t){}\nvoid SetLoadDataPaddingValue(uint64_t){}')
a = fixture.index('void LoadData(LocalTensor<half>')
b = fixture.index('struct MmadParams', a)
# Independent mapping: logical M,K in A1 NZ -> L0A ZZ for non-transposed A.
fixture = fixture[:a] + r'''
void LoadData(LocalTensor<half> dst,LocalTensor<half> src,LoadData3DParamsV2<half> p){
 assert(!p.enTranspose&&dst.mem->pos==TPosition::A2&&src.mem->pos==TPosition::A1&&!src.mem->pending);
 assert(p.l1H==1&&p.l1W%16==0&&p.channelSize%16==0&&p.strideH==1&&p.strideW==1&&p.filterH==1&&p.filterW==1);
 assert(p.dilationFilterH==1&&p.dilationFilterW==1&&p.mStartPt==0&&p.kStartPt%16==0);
 uint32_t rows=p.mExtension,count=p.kExtension;
 assert(rows==p.l1W&&count%16==0&&p.kStartPt+count<=p.channelSize);
 for(uint32_t m=0;m<rows;++m)for(uint32_t k=0;k<count;++k){
  uint32_t logicalK=p.kStartPt+k;
  dst.at(((m/16)*(count/16)+k/16)*256+(m%16)*16+k%16)=
   src.at((logicalK/16)*p.l1W*16+m*16+logicalK%16);
 }
 st.aL0+=uint64_t(rows)*count;++st.aLoads;
}
''' + fixture[b:]
fixture = fixture.replace('template<AscendC::HardEvent E>void Fence(){}', '''template<AscendC::HardEvent E>void Fence(){
 if(E==AscendC::HardEvent::MTE2_MTE1)while(!AscendC::dma.empty())AscendC::Flush(AscendC::dma.front().mem);
}''')
fixture = fixture.replace('// INSERT_HELPERS', zero + copies + producer)
main = (ROOT / 'tests/cpu/c9_packages_model.cpp.in').read_text()
model = fixture + main

# Read live operands only when M events force completion; catches premature
# overwrites of double-buffered A2/B2 and C before M_FIX.
delayed_model = model.replace('namespace AscendC {', 'std::deque<std::function<void()>> mac;\nnamespace AscendC {', 1)
delayed_model = delayed_model.replace(
 'template<HardEvent E>void SetFlag(int i){assert(st.events[std::make_pair(int(E),i)]++==0);}',
 'template<HardEvent E>void SetFlag(int i){auto f=[=]{assert(st.events[std::make_pair(int(E),i)]++==0);};if(E==HardEvent::M_MTE1)mac.push_back(f);else f();}')
delayed_model = delayed_model.replace('    assert(st.events[std::make_pair(int(E),i)]--==1);',
 '    if(E==HardEvent::M_MTE1)while(st.events[std::make_pair(int(E),i)]==0){assert(!mac.empty());auto f=mac.front();mac.pop_front();f();}\n    assert(st.events[std::make_pair(int(E),i)]--==1);')
a = delayed_model.index('template<class T>void Mmad(')
b = delayed_model.index('struct FixpipeParamsV220', a)
mm = delayed_model[a:b].replace('    for(uint32_t m=0;m<p.m;++m)', '    mac.push_back([=]{\n    for(uint32_t m=0;m<p.m;++m)', 1)
mm = mm.rsplit('}\n', 1)[0] + '    });\n}\n'
delayed_model = delayed_model[:a] + mm + delayed_model[b:]
delayed_model = delayed_model.replace('template<AscendC::HardEvent E>void Fence(){',
 'template<AscendC::HardEvent E>void Fence(){\n if(E==AscendC::HardEvent::M_FIX)while(!mac.empty()){auto f=mac.front();mac.pop_front();f();}')
delayed_model = delayed_model.replace('assert(AscendC::dma.empty());', 'assert(mac.empty());assert(AscendC::dma.empty());')

# All old implementations and MakePlan remain identical. Strip only the three
# inserted regions; this also checks unrelated launch paths were preserved.
old = src
a = old.index('// Resident A and larger B packages');b = old.index('// Isolated case12', a)
old = old[:a] + old[b:]
a = old.index('struct Case9PackagePlan');b = old.index('using CacheKey =', a)
old = old[:a] + old[b:]
a = old.index('    if(p.schedule.dual==20 && s.dtype==1');b = old.index('    if(p.schedule.dual==20) {', a)
old = old[:a] + old[b:]
old = old.replace('const bool middle9=s.dtype==1 && !s.tx1 && s.tx2 && s.m>=2048 && s.m<4096 && s.n>=1024 && s.n<2048 && s.k>=1024 && s.k<2048;', 'const bool middle9=s.dtype==1 && !s.tx1 && s.tx2 && NearMeasured(s.m,3072) && NearMeasured(s.n,1536) && NearMeasured(s.k,1536);')
assert old == parent, 'changes outside isolated C9 regions'

shapes = src[src.index('struct Shape {'):src.index('template <AscendC::HardEvent')]
host = src[src.index('struct Plan {'):src.index('using CacheKey =')]
hostmain = (ROOT / 'tests/cpu/c9_packages_host.cpp.in').read_text()
stub = (ROOT / 'tests/cpu/planner_stub.hpp').read_text().replace('struct TCubeTiling {', 'struct TCubeTiling { int stepKa=1,stepKb=1;')
hostmodel = stub + shapes + host + hostmain

# Execute the actual inline C9 Vector window against delayed copies and
# destructive producer reuse once both AIVs return the window credit.
a = src.index('void bmmms_case9_packages(')
a = src.index('\n#else\n    AscendC::TQue', src.index('    AscendC::SetAtomicNone();', a))
a = src.index('            const uint32_t slot=sequence&1;', a)
b = src.index('            AscendC::CrossCoreSetFlag<2,PIPE_MTE2>(2+slot);', a)
b = src.index('\n', b)
window = src[a:b].replace('            const uint32_t tiles=end-nt<s.window?end-nt:s.window;\n', '')
consumer = '''__aicore__ inline void ManualFullMConsumeWindow(
 AscendC::TQue<AscendC::TPosition::VECIN,2>& cq,AscendC::GlobalTensor<float> ring,const Schedule& s,
 uint32_t slotSize,uint32_t rowStart,uint32_t rows,uint32_t nt,uint32_t tiles,uint32_t sequence,
 AscendC::LocalTensor<float> maxima,AscendC::LocalTensor<float> row){
 const uint32_t width=s.baseN*s.window;
''' + window + '\n}\n'
consumer_model = (ROOT/'tests/cpu/fullk_window_consumer_model.cpp.in').read_text()
consumer_model = consumer_model.replace('flag==4+st.slot', 'flag==2+st.slot')
consumer_model = consumer_model.replace(' assert(!pad.pad&&!dst.mem->pending);', ' assert(pad.pad&&!dst.mem->pending);')
consumer_model = consumer_model.replace('p.dstStride==(BN-cols)/8', 'p.dstStride==(BN-((cols+7)/8*8))/8')
consumer_model = consumer_model.replace(' const size_t expected=', ' assert(pad.left==0&&pad.right==(cols+7)/8*8-cols&&pad.value==-std::numeric_limits<float>::infinity());\n const size_t expected=')
consumer_model = consumer_model.replace('dst.mem->pending=false;',
 'for(uint32_t r=0;r<p.blockCount;++r)for(uint32_t j=cols;j<cols+pad.right;++j)dst.At(r*BN+j)=pad.value;\n  dst.mem->pending=false;')
consumer_model = consumer_model.replace('}\n}\n// INSERT_CONSUMER', '''}
struct BinaryRepeatParams{uint32_t d,s1,s2,dr,s1r,s2r;};
void Max(LocalTensor<float> dst,LocalTensor<float> a,LocalTensor<float> b,uint64_t mask,uint32_t reps,BinaryRepeatParams p){
 assert(p.d==1&&p.s1==1&&p.s2==1&&p.dr==8&&p.s1r==8&&p.s2r==8);
 for(uint32_t r=0;r<reps;++r)Max(dst[r*64],a[r*64],b[r*64],mask);
}
}
// INSERT_CONSUMER''')
consumer_model = consumer_model.replace('// INSERT_CONSUMER', consumer)

def main():
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler
    print('kernel SHA256:', hashlib.sha256(src.encode()).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory(prefix='bmmms-c9-packages-') as d:
        for name, code, flags in [('producer', model, []), ('delayed-mmad', delayed_model, []), ('consumer', consumer_model, []),
                                  ('host', hostmodel, []), ('host-tuning', hostmodel, ['-DBMMMS_TUNING'])]:
            cpp, exe = Path(d)/(name+'.cpp'), Path(d)/name
            cpp.write_text(code)
            subprocess.run([compiler, '-std=c++17', '-O2', *flags, str(cpp), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)
    print('MTE1 synchronous; native queues, CANN9 compile, NPU precision/latency PENDING.')

if __name__ == '__main__':
    main()
