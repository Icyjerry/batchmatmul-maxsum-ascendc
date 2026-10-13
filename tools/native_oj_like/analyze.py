#!/usr/bin/env python3
"""Reject partial collection; preserve all five reports and source identities."""
import argparse,csv,json,statistics,math
from pathlib import Path

def analyze(root):
 root=Path(root);identity=json.loads((root/'application/identity.json').read_text())
 assert identity['calls']==5 and len(identity['validation'])==5
 basics=list((root/'profiler').rglob('OpBasicInfo_*.csv'));assert len(basics)==5,(len(basics),'expected exactly5 completeTask reports')
 samples=[]
 for p in basics:
  rows=list(csv.DictReader(p.open()));assert len(rows)==1
  row=rows[0];assert int(row['Device Id'])==identity['case']['device']
  capture=identity['case'].get('capture')
  if capture:
   assert row['Op Type']==capture['op_type'] and int(row['Block Dim'])==capture['block_dim']
   assert row['Mix Block Dim']=='NA' if capture['op_type']=='vector' and capture['mix_block_dim']==0 else int(row['Mix Block Dim'])==capture['mix_block_dim']
   aic,aiv=capture['aic'],capture['aiv'];family=capture['family']
  else:
   aic=identity['normal_plan']['cube_blocks'];aiv=aic*(1 if identity['normal_plan']['tall_single'] else 2)
   assert row['Op Type']=='mix' and int(row['Block Dim'])==aic and int(row['Mix Block Dim'])==aiv
   family='bmmms_tall_single_frame' if identity['normal_plan']['tall_single'] else 'bmmms_manual_case12_packed'
  name=row['Op Name'];assert family in name,name
  duration=float(row['Task Duration(us)']);assert math.isfinite(duration) and duration>0
  reports={q.name.split('_20')[0]:q for q in p.parent.glob('*.csv')}
  expected={'OpBasicInfo','PipeUtilization','ArithmeticUtilization','L2Cache','Memory','ResourceConflictRatio','MemoryL0','MemoryUB'}
  assert set(reports)==expected,(reports.keys(),expected)
  pmu=list(csv.DictReader(reports['ArithmeticUtilization'].open()));cube=[x for x in pmu if x['sub_block_id'].startswith('cube')]
  vec=[x for x in pmu if x['sub_block_id'].startswith('vector')]
  assert len(cube)==aic and len(vec)==aiv,(len(cube),len(vec))
  samples.append({'index':int(p.parent.name),'task_duration_us':duration,'symbol':name,'block_dim':int(row['Block Dim']),'mix_block_dim':row['Mix Block Dim'] if row['Mix Block Dim']=='NA' else int(row['Mix Block Dim']), 'current_freq':row['Current Freq'],'rated_freq':row['Rated Freq'],'cube_instructions':[int(x['aic_cube_total_instr_number']) for x in cube],'path':str(p)})
 samples.sort(key=lambda x:x['index']);assert [x['index'] for x in samples]==list(range(5))
 result={'identity':identity,'samples':samples,'median_us':statistics.median(x['task_duration_us'] for x in samples),'complete':True}
 (root/'summary.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root');a=p.parse_args();r=analyze(a.root);print(json.dumps({'samples':[x['task_duration_us'] for x in r['samples']],'median_us':r['median_us'],'cube_instructions':[x['cube_instructions'] for x in r['samples']]},indent=2))
