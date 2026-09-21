#!/usr/bin/env python3
"""Compile the actual batch traversal headers; check exactly one writer per y."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=(ROOT/'kernel.asc').read_text()
    functions=[]
    for name in ('FinalizeRows','FinalizeSplitKND','bmmms_gemv_vector'):
        # Skip forward declarations (only FinalizeRows has one).
        match=re.search(r'void '+name+r'\([^;{]+\)\s*\{', source)
        start=match.start(); end=source.index('\n}\n',start)
        block=source[start:end]
        # Balanced parentheses tolerate casts inside the actual loop header.
        loop_start=block.index('for',block.index('for (int64_t b0') if 'for (int64_t b0' in block else block.index('for(int64_t b0'))
        pos=block.index('(',loop_start); depth=1; stop=pos+1
        while depth:
            if block[stop]=='(': depth+=1
            elif block[stop]==')': depth-=1
            stop+=1
        loop=block[loop_start:stop]
        decl=''
        if name=='FinalizeRows': decl=re.search(r'    const int64_t finalWorkers[^;]+;',block).group(0)
        if name=='FinalizeSplitKND': decl=re.search(r'    const int64_t firstBatch[^;]+;',block).group(0)
        functions.append('void Check'+name+'(Schedule s,int worker,std::vector<int>& counts){\n'+decl+'\n'+loop+'''
{for(int64_t b=b0;b<std::min<int64_t>(s.b,b0+8);++b) ++counts.at(b);}}
''')
    code='''#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <vector>
struct Schedule{int64_t b;uint32_t workers,dual;};
int currentBlock=0;
namespace AscendC{int GetBlockIdx(){return currentBlock;}}
'''+''.join(functions)+'''
int main(){
 uint64_t cases=0,oldMissing=0,oldDuplicate=0;
 for(int b=1;b<=64;++b)for(int workers=1;workers<=64;++workers)for(int kind=0;kind<3;++kind)
 for(int dual:{0,1,2,3,14}){
  if(kind!=0 && dual!=1)continue;
  Schedule s{b,uint32_t(workers),uint32_t(dual)};
  int aivs=kind==2?workers:(kind==1 || dual)?2*workers:workers;
  std::vector<int> now(b),old(b);
  for(int v=0;v<aivs;++v){
   currentBlock=v;
   if(kind==0)CheckFinalizeRows(s,v,now);
   if(kind==1)CheckFinalizeSplitKND(s,v,now);
   if(kind==2)Checkbmmms_gemv_vector(s,v,now);
   if(kind==0) {for(int start=v*8;start<b;start+=workers*8)
       for(int j=start;j<std::min(b,start+8);++j)++old[j];}
   else if(v*8<b)for(int j=v*8;j<std::min(b,v*8+8);++j)++old[j];
  }
  assert(std::all_of(now.begin(),now.end(),[](int c){return c==1;}));
  oldMissing+=std::find(old.begin(),old.end(),0)!=old.end();
  oldDuplicate+=std::any_of(old.begin(),old.end(),[](int c){return c>1;});
  ++cases;
 }
 std::cout<<"Finalizers: "<<cases<<" configurations, unique complete output coverage PASS; old missing="
          <<oldMissing<<", old duplicate="<<oldDuplicate<<"\\n";
}
'''
    # These are loop/address checks; neither buffer barriers nor arithmetic is emulated.
    with tempfile.TemporaryDirectory(prefix='bmmms-finalizers-') as tmp:
        cpp=Path(tmp)/'model.cpp';exe=Path(tmp)/'model';cpp.write_text(code)
        subprocess.run([shutil.which('clang++') or 'c++','-std=c++14','-O2',str(cpp),'-o',str(exe)],check=True,timeout=60)
        subprocess.run([str(exe)],check=True,timeout=60)


if __name__=='__main__':main()
