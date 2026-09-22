// Deliberately not a CANN emulator. Only supports execution of host control flow.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <map>
#include <mutex>
#include <stdexcept>
#include <tuple>
#include <vector>
inline int64_t Ceil(int64_t n,int64_t d){assert(d>0);return (n+d-1)/d;}
namespace AscendC { namespace tiling {
struct TCubeTiling {uint32_t baseM=0,baseN=0,baseK=0,stepM=0,stepN=0,usedCoreNum=0;};
}}
namespace platform_ascendc {
enum class CoreMemType {UB,L1,L0_C};
struct PlatformAscendCManager {
    int aic=20,aiv=40;uint64_t ub=192*1024,l1=512*1024,l0=128*1024,system=16*1024*1024;
    static PlatformAscendCManager* GetInstance(){static PlatformAscendCManager p;return &p;}
    int GetCoreNumAic(){return aic;} int GetCoreNumAiv(){return aiv;}
    void GetCoreMemSize(CoreMemType kind,uint64_t& value){value=kind==CoreMemType::UB?ub:kind==CoreMemType::L1?l1:l0;}
    uint64_t GetLibApiWorkSpaceSize(){return system;}
};
}
namespace matmul_tiling {
enum class TPosition {GM,VECIN};enum class CubeFormat{ND,NZ};enum class DataType{DT_FLOAT16,DT_BF16,DT_FLOAT};
struct MatmulApiTiling {
    uint32_t m=0,n=0; static bool rejectFirst;
    explicit MatmulApiTiling(platform_ascendc::PlatformAscendCManager&){}
    void SetAType(TPosition,CubeFormat,DataType,bool){} void SetBType(TPosition,CubeFormat,DataType,bool){}
    void SetCType(TPosition,CubeFormat,DataType){} void SetBias(bool){}
    void SetOrgShape(int64_t,int64_t,int64_t){} void SetShape(int64_t,int64_t,int64_t){}
    void SetBufferSpace(uint64_t,uint64_t,uint64_t){}
    int SetFixSplit(int bm,int bn,int){m=bm;n=bn;return 0;}
    int GetTiling(AscendC::tiling::TCubeTiling& t){
        if(rejectFirst){rejectFirst=false;return -1;}
        t.baseM=m;t.baseN=n;t.baseK=32;return 0;
    }
};
bool MatmulApiTiling::rejectFirst=false;
}
