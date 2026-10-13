#!/usr/bin/env python3
"""Actual unchanged run_kernel via DSO; external full-storage golden verification."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from pathlib import Path
import numpy as np

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(code,what):
 if code!=0:raise RuntimeError(f'{what}: error {code}')
def main():
 p=argparse.ArgumentParser();p.add_argument('--lib',required=True);p.add_argument('--case',required=True)
 p.add_argument('--inputs',required=True);p.add_argument('--output',required=True);p.add_argument('--calls',type=int,default=1)
 p.add_argument('--frame');p.add_argument('--plan-only',action='store_true');a=p.parse_args();case=json.loads(Path(a.case).read_text())
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);inputs=Path(a.inputs)
 B,M,N,K=case['shape'];dt=case['dtype'];tx1,tx2=case['transpose'];limit=case['core_limit'];dev=case['device']
 manifest=json.loads(Path(a.lib+'.identity.json').read_text());assert manifest['dso_sha256']==sha(a.lib)
 assert manifest['kernel_sha256']==sha(manifest['kernel_path'])
 lib=c.CDLL(a.lib);acl=c.CDLL('libascendcl.so');acl.aclrtGetSocName.restype=c.c_char_p
 acl.aclrtMalloc.argtypes=[c.POINTER(c.c_void_p),c.c_size_t,c.c_int]
 acl.aclrtMemcpy.argtypes=[c.c_void_p,c.c_size_t,c.c_void_p,c.c_size_t,c.c_int]
 acl.aclrtCreateStream.argtypes=[c.POINTER(c.c_void_p)]
 acl.aclrtSynchronizeStreamWithTimeout.argtypes=[c.c_void_p,c.c_int]
 acl.aclrtDestroyStream.argtypes=[c.c_void_p];acl.aclrtFree.argtypes=[c.c_void_p]
 lib.native_plan.argtypes=[c.c_int64]*4+[c.c_int]*3+[c.c_int64,c.c_void_p,c.c_size_t]
 lib.native_call.argtypes=[c.c_void_p]*4+[c.c_int64]*4+[c.c_int]*3+[c.c_int64]
 lib.release_kernel_resources.argtypes=[c.c_void_p]
 stream=c.c_void_p();buffers=[];initialized=False;selected=False
 check(acl.aclInit(None),'aclInit');initialized=True
 try:
  check(acl.aclrtSetDevice(dev),'setDevice');selected=True
  assert acl.aclrtGetSocName().decode()==case['expected_soc']
  mapping=subprocess.check_output(['npu-smi','info','-m'],text=True)
  found=[line.split() for line in mapping.splitlines() if line.split() and line.split()[0].isdigit()]
  assert any(row[0]==str(case['smi_card']) and row[1]==str(case['smi_chip']) and row[2]==str(dev) and row[3]==str(case['expected_physical']) for row in found),mapping
  plan=c.create_string_buffer(32768);args=(B,M,N,K,dt,tx1,tx2,limit)
  check(lib.native_plan(*args,plan,len(plan)),'normalPlan');frame=json.loads(plan.value)
  identity={'build':manifest,'dso_sha256':sha(a.lib),'case':case,'normal_plan':frame,'soc':acl.aclrtGetSocName().decode(),'npu_mapping':mapping}
  (out/'identity.json').write_text(json.dumps(identity,indent=2))
  if a.plan_only:print(json.dumps(identity,indent=2));return
  assert a.frame and frame==json.loads(Path(a.frame).read_text()),'normal plan differs from reviewed complete frame'
  expected=np.fromfile(inputs/'golden.f32',dtype='<f4');assert expected.size==B
  raw=[(inputs/n).read_bytes() for n in ['x1.b16','x2.b16']]
  assert len(raw[0])==B*M*K*2 and len(raw[1])==B*N*K*2
  ref=json.loads((inputs/'reference.json').read_text());assert ref['case']==case and ref['full_math']
  assert ref['input_sha256']==[hashlib.sha256(x).hexdigest() for x in raw]
  identity['input_sha256']=[hashlib.sha256(x).hexdigest() for x in raw];identity['golden_sha256']=sha(inputs/'golden.f32')
  for v in raw:
   ptr=c.c_void_p();check(acl.aclrtMalloc(c.byref(ptr),len(v),0),'input malloc');buffers.append(ptr)
   src=c.create_string_buffer(v);check(acl.aclrtMemcpy(ptr,len(v),src,len(v),1),'H2D')
  guard=np.full(B+16,0x5ab6d3c2,dtype='<u4');y=c.c_void_p()
  check(acl.aclrtMalloc(c.byref(y),guard.nbytes,0),'output malloc');buffers.append(y)
  check(acl.aclrtCreateStream(c.byref(stream)),'createStream');results=[]
  for i in range(a.calls):
   check(acl.aclrtMemcpy(y,guard.nbytes,c.c_void_p(guard.ctypes.data),guard.nbytes,1),'output guard reset')
   check(lib.native_call(buffers[0],buffers[1],y,stream,*args),'run_kernel')
   check(acl.aclrtSynchronizeStreamWithTimeout(stream,60000),'synchronize')
   got=np.empty_like(guard);check(acl.aclrtMemcpy(c.c_void_p(got.ctypes.data),got.nbytes,y,got.nbytes,2),'output D2H')
   assert np.array_equal(got[B:],guard[B:]),'output canary modified'
   value=got[:B].view('<f4');assert np.all(np.isfinite(value))
   error=np.abs(value.astype(np.float64)-expected.astype(np.float64));relative=error/np.maximum(np.abs(expected.astype(np.float64)),1e-30)
   assert np.allclose(value,expected,rtol=1e-4,atol=1e-4),(value,expected,error,relative)
   (out/f'y_{i}.f32').write_bytes(value.tobytes())
   results.append({'call':i,'y':value.tolist(),'max_abs_error':float(error.max()),'max_relative_error':float(relative.max())})
  for ptr,v in zip(buffers,raw):
   read=c.create_string_buffer(len(v));check(acl.aclrtMemcpy(read,len(v),ptr,len(v),2),'input D2H');assert read.raw==v,'input modified'
  identity['validation']=results;identity['calls']=a.calls
  (out/'identity.json').write_text(json.dumps(identity,indent=2));print(json.dumps({'calls':a.calls,'validation':results}),flush=True)
 finally:
  if stream.value:lib.release_kernel_resources(stream);acl.aclrtDestroyStream(stream)
  for ptr in buffers:acl.aclrtFree(ptr)
  if selected:acl.aclrtResetDevice(dev)
  if initialized:acl.aclFinalize()
if __name__=='__main__':main()
