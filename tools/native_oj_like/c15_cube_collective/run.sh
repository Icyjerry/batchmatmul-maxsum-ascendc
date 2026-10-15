#!/usr/bin/env bash
# Run the one frozen C15 candidate, once, through the existing native harness.
set -eo pipefail
bundle_dir="$(cd "$(dirname "$0")" && pwd)"
task_root="${1:?usage: run.sh /workspace/bmmms-codex}"
source /usr/local/Ascend/cann-9.0.0/set_env.sh
export LD_LIBRARY_PATH="/usr/local/Ascend/driver/lib64/common:/usr/local/Ascend/driver/lib64/driver:${LD_LIBRARY_PATH:-}"
set -u
python_bin="$task_root/test-venv/bin/python"
build_dir="$task_root/native_oj_like/build-c15-cube-collective"
for mode in correctness alternating profile; do
  test ! -e "$task_root/results/c15-cube-collective-$mode" || { echo "Existing result: inspect that job instead of restarting it"; exit 1; }
done
"$python_bin" - "$bundle_dir" "$task_root" <<'PY'
from pathlib import Path
import hashlib,json,sys
bundle=Path(sys.argv[1]);root=Path(sys.argv[2])
manifest=json.loads((bundle/'manifest.json').read_text())
for name,expected in manifest['files'].items():
 assert hashlib.sha256((bundle/name).read_bytes()).hexdigest()==expected,name
assert manifest['kernel_sha256']=='ca66a5417b3ba41d6dd86231e4f3e36fb28dc6ca7df9feb854c1218bee872583'
assert json.loads((root/'native_oj_like/c15.complete_frame.json').read_text())==json.loads((bundle/'frame.json').read_text())
assert json.loads((root/'native_oj_like/c15.json').read_text())==json.loads((bundle/'native_oj_like/c15.json').read_text())
assert json.loads((root/'native_oj_like/c15_input_sequence.json').read_text())==[str(root/'inputs/c15'),str(root/'inputs/c15-negative'),str(root/'inputs/c15')]
for name in ['c15','c15-negative']:
 ref=json.loads((root/'inputs'/name/'reference.json').read_text());assert ref['full_math']
 for filename,expected in zip(['x1.b16','x2.b16'],manifest['input_sha256'][name]):
  assert hashlib.sha256((root/'inputs'/name/filename).read_bytes()).hexdigest()==expected
 assert hashlib.sha256((root/'inputs'/name/'golden.f32').read_bytes()).hexdigest()==manifest['golden_sha256'][name]
print('Frozen source, harness, full reviewed frame and both input sets verified')
PY
cmake -S "$bundle_dir/native_oj_like" -B "$build_dir" -DKERNEL_DIR="$bundle_dir/source" > "$bundle_dir/build.log" 2>&1
cmake --build "$build_dir" -j2 >> "$bundle_dir/build.log" 2>&1
"$python_bin" - "$bundle_dir" "$build_dir" <<'PY'
from pathlib import Path
import hashlib,json,sys
bundle=Path(sys.argv[1]);dso=Path(sys.argv[2])/'libnative_bmmms.so';kernel=bundle/'source/kernel.asc'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
identity={'kernel_path':str(kernel),'kernel_sha256':sha(kernel),'dso_sha256':sha(dso),'wrapper_sha256':sha(bundle/'native_oj_like/library.asc'),'cann':'9.0.0','arch':'dav-2201'}
Path(str(dso)+'.identity.json').write_text(json.dumps(identity,indent=2));print(json.dumps(identity,indent=2))
PY
for mode in correctness alternating profile; do
  job_mode="$mode"
  sequence_args=()
  if test "$mode" = alternating; then
    job_mode=correctness
    sequence_args=(--input-sequence "$task_root/native_oj_like/c15_input_sequence.json")
  fi
  "$python_bin" "$bundle_dir/native_oj_like/job.py" --lib "$build_dir/libnative_bmmms.so" --case "$bundle_dir/native_oj_like/c15.json" --inputs "$task_root/inputs/c15" --frame "$bundle_dir/frame.json" --output "$task_root/results/c15-cube-collective-$mode" --python "$python_bin" --queue "$task_root" --mode "$job_mode" "${sequence_args[@]}"
done
"$python_bin" - "$task_root/results/c15-cube-collective-profile/summary.json" <<'PY'
from pathlib import Path
import json,sys
s=json.loads(Path(sys.argv[1]).read_text());assert s['complete']
for row in s['samples']:
 assert 'bmmms_manual_split_tt' in row['symbol'] and 'Lb1ELb1E' in row['symbol']
 assert row['block_dim']==8 and row['mix_block_dim']==8 and row['cube_instructions']==[8]*8
values=[row['task_duration_us'] for row in s['samples']]
print(json.dumps({'times':values,'median_us':s['median_us'],'old_parent_median_us':10.940437,'row_only_median_us':10.260410,'passes_performance_gate':s['median_us']<=9.8463933 and max(values)<10.540421,'formal15':'NOT SUBMITTED'},indent=2))
PY
