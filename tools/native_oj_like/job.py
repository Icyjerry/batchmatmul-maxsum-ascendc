#!/usr/bin/env python3
"""Serialize complete device jobs; collector uses all default metrics, no filter."""
import argparse,fcntl,json,os,shlex,subprocess,time,uuid
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def serial(root,name):
 root=Path(root);root.mkdir(parents=True,exist_ok=True);ticket={'id':str(uuid.uuid4()),'pid':os.getpid(),'name':name,'time':time.time()}
 def update(fn):
  with (root/'state.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);p=root/'npu_test_state.json'
   state=json.loads(p.read_text()) if p.exists() else {'active':None,'pending':[]}
   fn(state);tmp=root/f'state-{os.getpid()}.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(p)
 update(lambda s:s['pending'].append(ticket))
 with (root/'npu.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  def active(s):s['pending']=[x for x in s['pending'] if x['id']!=ticket['id']];s['active']=ticket
  update(active)
  try:yield
  finally:
   def done(s):
    if s['active'] and s['active']['id']==ticket['id']:s['active']=None
    s['pending']=[x for x in s['pending'] if x['id']!=ticket['id']]
   update(done)

def main():
 p=argparse.ArgumentParser();p.add_argument('--lib',required=True);p.add_argument('--case',required=True);p.add_argument('--inputs',required=True)
 p.add_argument('--frame');p.add_argument('--output',required=True);p.add_argument('--python',required=True);p.add_argument('--queue',required=True);p.add_argument('--mode',choices=['plan','correctness','profile'],required=True)
 a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
 cmd=[a.python,str(Path(__file__).with_name('driver.py')),'--lib',str(Path(a.lib).resolve()),'--case',str(Path(a.case).resolve()),'--inputs',str(Path(a.inputs).resolve()),'--output',str(out/'application')]
 if a.frame:cmd+=['--frame',str(Path(a.frame).resolve())]
 if a.mode=='plan':cmd+=['--plan-only']
 elif a.mode=='profile':cmd+=['--calls','5'];cmd=['msprof','op','--application='+shlex.join(cmd),'--output='+str(out/'profiler'),'--warm-up=5','--launch-count=5000','--replay-mode=kernel']
 (out/'command.json').write_text(json.dumps(cmd,indent=2))
 with serial(a.queue,a.mode+':'+str(out)),(out/'job.log').open('w') as log:
  result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
 (out/'exit.json').write_text(json.dumps({'exit':result.returncode}))
 if result.returncode:print((out/'job.log').read_text()[-6000:]);raise SystemExit(result.returncode)
 if a.mode=='profile':
  identity=out/'application/identity.json'
  assert identity.exists(),'collector returned0 without application identity'
  record=json.loads(identity.read_text());assert record['calls']==5 and len(record['validation'])==5
  from analyze import analyze
  analyze(out)
 print('Completed',a.mode,'reports at',out,flush=True)
if __name__=='__main__':main()
