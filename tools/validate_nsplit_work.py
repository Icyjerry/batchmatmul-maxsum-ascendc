#!/usr/bin/env python3
"""Compile the actual N-split selector against a tile-enumeration oracle (CPU)."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    raw = (ROOT / 'kernel.asc').read_bytes()
    source = raw.decode()
    helpers = source[source.index('struct NPartitionCost'):source.index('inline uint32_t PanelKCapacity(')]
    start = source.index('#if BMMMS_BALANCED_NSPLIT\n')
    end = source.index('    d.window = std::min<uint32_t>', start)
    integration = source[start:end]
    device = source[source.index('void bmmms_dual('):source.index('// ND2NZ clears')]
    for expression in ['task+=s.workers', 'ns=task%s.nSplit',
                       'begin=ns*s.nTiles/s.nSplit,end=(ns+1)*s.nTiles/s.nSplit',
                       'nt+=s.window']:
        assert expression in device, 'Model needs review: device schedule changed'
    code = '''#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
#include <cmath>
inline int64_t Ceil(int64_t n,int64_t d){return (n+d-1)/d;}
''' + helpers + '''
struct Shape {int64_t b=1,m=1536,n=1536,k=1536;};
struct Schedule {int balance=1,dual=1,kSplit=1,baseM=128,baseN=128;
    uint32_t mTiles=12,nTiles=12,nSplit=2,window=8;};
struct Profile {int dual=0;};
enum {FORCED_NONE=0};
struct Pins {int bm=0,bn=0,window=0,ks=0,workers=0;};
Pins pins;
Pins& Tune(){return pins;}
uint32_t Apply(Shape s={},Schedule d={},Profile caseProfile={},
               bool forcedPinned=false,bool splitPinned=false) {
    int64_t capacity=40,tuneCores=20;
''' + integration + '''
    return d.nSplit;
}
// Independent oracle: visit every N tile, assign it to a split interval, then
// round-robin whole (row,split) tasks to workers. Count actual window starts.
NPartitionCost Oracle(int rows,int n,int window,int ns,int cores) {
    int workers=std::min(rows*ns,cores),width=std::min(window,int(Ceil(n,ns)));
    std::vector<int64_t> tiles(workers),windows(workers);
    for(int row=0;row<rows;++row) for(int col=0;col<n;++col) {
        int split=0;
        while(col >= (split+1)*n/ns) ++split;
        int worker=(row*ns+split)%workers;
        ++tiles[worker];
        if((col-split*n/ns)%width==0) ++windows[worker];
    }
    return {*std::max_element(tiles.begin(),tiles.end()),
            *std::max_element(windows.begin(),windows.end())};
}
int main(){
    int checked=0,changed=0;
    for(int rows:{1,2,3,5,8,9,12,16,20,24,31,32,48,64,96,128,256,512})
    for(int n=8;n<=16;++n) for(int window:{1,2,4,8})
    for(int cores:{1,2,4,8,12,16,20,24,32,40,48,64}) {
        std::vector<NPartitionCost> expected(n+1);
        for(int ns=1;ns<=n;++ns) {
            expected[ns]=Oracle(rows,n,window,ns,cores);
            auto got=NPartitionWork(rows,n,window,ns,cores);
            assert(got.tiles==expected[ns].tiles && got.windows==expected[ns].windows);
        }
        for(int current:{1,2,3,5,n}) {
            auto before=expected[current],best=before;
            int oracle=current;
            for(int ns=1;ns<=n;++ns) {
                auto c=expected[ns];
                if(c.windows>before.windows) continue;
                if(c.tiles<best.tiles || (c.tiles==best.tiles &&
                    (c.windows<best.windows || (c.windows==best.windows && ns<oracle)))) {
                    best=c;oracle=ns;
                }
            }
            if(best.tiles*4>before.tiles*3) oracle=current;
            int selected=SelectBalancedNSplit(rows,n,window,current,cores);
            assert(selected==oracle && selected>=1 && selected<=n);
            if(selected!=current) {
                assert(expected[selected].tiles*4<=before.tiles*3);
                assert(expected[selected].windows<=before.windows);
                ++changed;
            }
            ++checked;
        }
    }
    // All finite C entries are negative here: zero-init or omission fails.
    int reduced=0;
    for(int n=1024;n<=2048;n+=128) for(int ns=1;ns<=n/128;++ns) {
        for(int row=0;row<17;++row) {
            float merged=-INFINITY,direct=-INFINITY;
            std::vector<int> visited(n);
            for(int split=0;split<ns;++split) {
                float partial=-INFINITY;
                int begin=split*(n/128)/ns*128,end=(split+1)*(n/128)/ns*128;
                for(int col=begin;col<end;++col) {
                    float value=-float(1+(col*73+row*19)%997);
                    partial=std::max(partial,value);++visited[col];
                }
                merged=std::max(merged,partial);
            }
            for(int col=0;col<n;++col) {
                assert(visited[col]==1);
                direct=std::max(direct,-float(1+(col*73+row*19)%997));
            }
            assert(merged==direct);++reduced;
        }
    }
    assert(SelectBalancedNSplit(12,12,8,2,20)==3);
    assert(SelectBalancedNSplit(24,12,8,1,20)==3);
    assert(Apply()==(BMMMS_BALANCED_NSPLIT?3:2));
    // Every integration exclusion must preserve the supplied plan.
    for(int flag=0;flag<14;++flag) {
        Shape s;Schedule d;Profile p;bool forced=false,split=false;
        switch(flag){
        case 0: s.m=1537;break; case 1:s.n=1537;break;
        case 2:s.k=2048;break;case 3:s.k=1016;break;
        case 4:d.dual=2;break;case 5:d.kSplit=4;break;
        case 6:d.baseN=256;break;case 7:d.baseM=64;break;
        case 8:p.dual=1;break;case 9:forced=true;break;
        case 10:split=true;break;case 11:d.balance=0;break;
        case 12:s.n=2176;break;case 13:s.m=896;break;}
        assert(Apply(s,d,p,forced,split)==2);
    }
#ifdef BMMMS_TUNING
    for(int field=0;field<5;++field){
        pins=Pins{};
        switch(field){case 0:pins.bm=128;break;case 1:pins.bn=128;break;
        case 2:pins.window=8;break;case 3:pins.ks=1;break;case 4:pins.workers=20;break;}
        assert(Apply()==2);
    }
#endif
    std::cout<<checked<<" schedules; "<<changed<<" work reductions; "
             <<reduced<<" partitioned negative rows; integration gates PASS\\n";
}
'''
    print('CPU scheduling/partition model only. CANN/NPU PENDING.', flush=True)
    print('kernel SHA256:', hashlib.sha256(raw).hexdigest(), flush=True)
    compiler = shutil.which('clang++') or shutil.which('c++')
    assert compiler
    with tempfile.TemporaryDirectory(prefix='bmmms-nsplit-') as tmp:
        cpp, exe = Path(tmp) / 'model.cpp', Path(tmp) / 'model'
        cpp.write_text(code)
        for flags in [['-DBMMMS_BALANCED_NSPLIT=0'], ['-DBMMMS_BALANCED_NSPLIT=1'],
                      ['-DBMMMS_BALANCED_NSPLIT=1', '-DBMMMS_TUNING']]:
            print(' '.join(flags), flush=True)
            subprocess.run([compiler, '-std=c++14', '-O2', *flags, str(cpp), '-o', str(exe)], check=True, timeout=60)
            subprocess.run([str(exe)], check=True, timeout=60)


if __name__ == '__main__':
    main()
