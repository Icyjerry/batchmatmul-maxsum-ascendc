#!/usr/bin/env python3
"""Recompute supplied records; never runs a device probe or discovers hidden data."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'docs/teammate_probe'


def table(text, section, header):
    chunk = text[text.index(section):]
    chunk = chunk[chunk.index(header):].split('\n\n', 1)[0]
    rows = [[float(x.strip()) for x in line.strip('|').split('|')]
            for line in chunk.splitlines() if re.match(r'^\| \d+ \|', line)]
    assert [r[0] for r in rows] == list(range(1, 16))
    return rows


def main():
    manifest = json.loads((DATA / 'source_manifest.json').read_text())
    for local, member in [('source_probe_data.md', 'docs/02-probe-data.md'),
                          ('source_case_paths.json', 'docs/case_paths.json')]:
        assert hashlib.sha256((DATA / local).read_bytes()).hexdigest() == manifest['members'][member]
    text = (DATA / 'source_probe_data.md').read_text()
    baseline = [r[1] for r in table(text, '## 6.', '| point | our')]
    mnk = [r[1:] for r in table(text, '## 7.', '| point | s6')]
    later = [r[1:] for r in table(text, '## 8.', '| pt | s9')]
    paths = json.loads((DATA / 'source_case_paths.json').read_text())
    assert len(paths) == 45
    rows, residuals, conflicts = [], [], []
    for i, (base, axes, times) in enumerate(zip(baseline, mnk, later)):
        coarse = [(times[0] - base) / 15] + [(t - base) / 15 for t in axes]
        attr = (times[4] - times[3]) / 15
        residuals += [abs(x - round(x)) for x in coarse + [attr]]
        ranges = [(2 ** round(x), min(8192, 2 ** (round(x) + 1) - 1)) for x in coarse]
        # Fine-M is conditional on the supplied BASE=64, STEP=5 build attribution.
        if i + 1 in (14, 15):
            assert round((times[2] - times[1]) / 15) == 0
            ranges[1] = (max(64, ranges[1][0]), min(68, ranges[1][1]))
        lo, hi = ranges[3]
        ranges[3] = ((lo + 7) // 8 * 8, hi // 8 * 8)
        packed = round(attr)
        dtype, tx1, tx2 = ('bf16' if packed & 4 else 'fp16'), (packed >> 1) & 1, packed & 1
        supplied_attrs = sorted({(p['dt'], p['tx1'], p['tx2']) for p in paths if p['case'] == i + 1})
        if supplied_attrs != [(dtype, tx1, tx2)]:
            conflicts.append({'case': i + 1, 'decoded': [dtype, tx1, tx2], 'old_paths': supplied_attrs})
        rows.append([i + 1] + [v for pair in ranges for v in pair] +
                    [dtype, tx1, tx2, times[6], 'CONFLICT' if i + 1 == 10 else 'conditional'])

    report = {
        'archive_sha256': manifest['archive_sha256'],
        'evidence': 'arithmetic on teammate transcription; original submission/build ledger absent',
        'max_rung_residual_BMNK_and_attributes': round(max(residuals), 6),
        'section15_sum_us': round(sum(t[6] for t in later), 2),
        'attribute_conflicts': conflicts,
        'old_proxy_K_not_multiple_of_8': [[p['case'], p['which'], p['K']] for p in paths if p['K'] % 8],
        'old_proxy_M_outside_refined_range': [[p['case'], p['which'], p['M']] for p in paths
                                             if p['case'] in (14, 15) and not 64 <= p['M'] <= 68],
    }
    assert max(residuals) < 0.15
    assert len(report['old_proxy_K_not_multiple_of_8']) == 14
    assert [c['case'] for c in conflicts] == [10]
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['case', 'B_lo', 'B_hi', 'M_lo', 'M_hi', 'N_lo', 'N_hi', 'K_lo', 'K_hi',
                     'decoded_dtype', 'tx1', 'tx2', 'historical_sec15_us', 'attribution_status'])
    writer.writerows(rows)
    (DATA / 'hypothesis_ranges.csv').write_text(stream.getvalue())
    # Local validation inputs only: legal interior/endpoints, not claimed OJ shapes.
    proxies = []
    for row in rows:
        case = row[0]
        bounds = list(zip(row[1:9:2], row[2:9:2]))
        attrs = [(row[9], row[10], row[11])]
        if case == 10:
            attrs.append(('fp16', 1, 1))
        shapes = []
        for index in (0, 1, 2):
            shape = [lo if index == 0 else hi if index == 2 else (lo + hi) // 2
                     for lo, hi in bounds]
            shape[3] = shape[3] // 8 * 8
            shapes.append(shape)
        if case in (14, 15):
            shapes.append([1, 65, bounds[2][0], bounds[3][0]])
        for shape in shapes:
            b, m, n, k = shape
            assert k % 8 == 0 and max(b*m*k, b*k*n) <= 2**26
            for dtype, tx1, tx2 in attrs:
                proxy = [case, *shape, dtype, tx1, tx2]
                if proxy not in proxies:
                    proxies.append(proxy)
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['hypothesis_case', 'B', 'M', 'N', 'K', 'dtype', 'tx1', 'tx2'])
    writer.writerows(proxies)
    (DATA / 'local_validation_inputs.csv').write_text(stream.getvalue())
    report['legal_local_validation_inputs'] = len(proxies)
    (DATA / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
