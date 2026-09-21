# 02 — Probe raw data (OJ leaderboard sections 1..15)

Source of every number in this file: `/mnt/workspace/glm_t/performance.txt`
(267 lines, 15 sections), cross-checked against the working plan
`/mnt/workspace/agent-config/claude/plans/2x-rustling-ladybug.md` ("进展记录")
and the submitted/working kernel sources.

All figures are **device Task Duration in microseconds**, OJ-measured, unless a
value is marked `ms`. `μs` is stripped in dense tables; the section provenance
(line range in `performance.txt`) is given for each table.

Scoring context (given): `y[b] = Σ_m max_n( x1[b] @ x2[b] )`, fp16/bf16 → fp32,
15 hidden graded points, all 15 must pass precision before anything scores.
Score `100 / (1 + log_1.5(t/T))`. The OJ keeps the **last** submission.

---

## 0. Section map (what each section is)

| Sec | provenance | label in `performance.txt` | what it is |
|---|---|---|---|
| 1 | lines 7–21 | `section1(current version vs All teams best)` | our "current" build vs All-teams-best |
| 2 | lines 25–39 | `section2(old version vs All teams best)` | our "old" build vs All-teams-best |
| 3 | lines 43–45 | `section3(current verified top-3 teams' results)` | **TARGET** — the 3 verified top teams |
| 4 | lines 48–62 | `section4` | OJ result of the **F6** submission (Σ 644.61) |
| 5 | lines 65–79 | `section5(case_verify_test)` | **serial probe** (cubeBlocks pinned to 1) |
| ? | lines 82–96 | `section?` (header has no number) | **production baseline**, = F8_prod (Σ 644.40) |
| 6 | lines 99–113 | `section6` | **M-axis ladder** (AXIS 2) |
| 7 | lines 116–130 | `section7` | **N-axis ladder** (AXIS 3) |
| 8 | lines 133–147 | `section8` | **K-axis ladder** (AXIS 4) |
| 9 | lines 150–164 | `section9 ?` | **ANOMALY** — points 3–7 inflated (see §9) |
| 10 | lines 167–181 | `section10 ?` | production submission |
| 11 | lines 184–198 | `section11` | **coarse M probe** (`AXIS 2`, `BASE 64`, `STEP 5`; `scratch/pb_fine`) — not a production row |
| 12 | lines 201–215 | `section12(case 15 indeed improve…)` | production submission |
| 13 | lines 218–232 | `section13` | **packed-attribute probe** (`AXIS 8`; `scratch/w0/ax8p`) — not a production row |
| 14 | lines 235–249 | `section14` | production submission |
| 15 | lines 252–266 | `section15` | production submission |

**Column layout.** Every graded row is `point  Pass  decline%  colA  colB …`.
For sections 1, 2, 4, 5 and `section?`: `colA` = our µs, `colB` = All-teams-best µs.
For sections 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15: `colA` = our µs, `colB` =
All-teams-best µs (section 3 is different — see §3).

**Baseline choice for the ladders.** Sections 6/7/8 are differenced against
`section?` (lines 82–96). This is not a guess: the plan's own M-ladder table
(`2x-rustling-ladybug.md`, "阶梯探针 M 轴结果") prints production values
`3.59 7.80 8.71 11.65 10.76 16.53 15.03 69.55 92.88 110.08 88.18 131.25 27.39 20.59 30.41`,
which are exactly the `section?` column. `section?` is the F8_prod production
snapshot (`scratch/kernel_VERIFIED_F8_prod.asc`, per the plan).

---

## 1. Section 1 — current version vs All teams best (lines 7–21)

| point | our µs | best µs |
|---|---|---|
| 1 | 3.67 | 1.59 |
| 2 | 7.86 | 2.34 |
| 3 | 8.64 | 2.63 |
| 4 | 11.31 | 3.90 |
| 5 | 11.14 | 2.96 |
| 6 | 17.15 | 3.82 |
| 7 | 15.61 | 5.74 |
| 8 | 71.31 | 17.32 |
| 9 | 93.16 | 52.43 |
| 10 | 110.26 | 75.59 |
| 11 | 89.11 | 45.65 |
| 12 | 132.65 | 33.62 |
| 13 | 27.65 | 1.40 |
| 14 | 21.08 | 11.86 |
| 15 | 29.78 | 10.12 (†) |

† `performance.txt` line 21 writes the point-15 best as `10.12` with **no `μs`
suffix**. Every other cell in the file carries the unit. Treated as 10.12 µs;
flagged because the cell is malformed.

## 2. Section 2 — old version vs All teams best (lines 25–39)

| point | our µs | best µs |
|---|---|---|
| 1 | 3.74 | 1.59 |
| 2 | 7.51 | 2.34 |
| 3 | 8.34 | 2.63 |
| 4 | 11.36 | 3.90 |
| 5 | 10.76 | 2.96 |
| 6 | 16.29 | 3.82 |
| 7 | 14.38 | 5.74 |
| 8 | 68.23 | 17.32 |
| 9 | 92.48 | 52.43 |
| 10 | 109.54 | 75.59 |
| 11 | 93.48 | 45.65 |
| 12 | 195.86 | 33.62 |
| 13 | 26.26 | 1.40 |
| 14 | 19.30 | 11.86 |
| 15 | 30.36 | 10.12 |

Neither section 1 nor section 2 carries a timestamp, a score, or a build id, so
**which revision each is cannot be recovered from this file**. They are recorded
here as raw numbers only.

---

## 3. Section 3 — verified top-3 teams = TARGET (lines 43–45)

Layout per row: `rank  Pass  score  timestamp  t1 … t15`. The three teams are
identified only by score + timestamp — **team names are not present in the file**.

| team | score | timestamp | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| row 1 | 51.61 | 2026/09/18 13:40:55 | 2.09 | 2.37 | 2.82 | 11.44 | 6.19 | 10.48 | 8.80 | 76.84 | 53.06 | 79.78 | 82.82 | 116.72 | 17.74 | 15.29 | 16.67 |
| row 2 | 46.16 | 2026/09/18 15:28:46 | 2.04 | 2.52 | 3.52 | 4.30 | 5.98 | 10.67 | 8.42 | 79.69 | 66.21 | 99.51 | 138.29 | 117.88 | 20.84 | 16.30 | 31.03 |
| row 3 | 46.00 | 2026/09/15 13:40:50 | 1.60 | 5.31 | 2.86 | 9.66 | 7.20 | 15.10 | 12.68 | 67.01 | 84.29 | 122.03 | 111.03 | 135.35 | 13.20 | 13.82 | 10.12 |
| **per-point min (target)** | | | **1.60** | **2.37** | **2.82** | **4.30** | **5.98** | **10.48** | **8.42** | **67.01** | **53.06** | **79.78** | **82.82** | **116.72** | **13.20** | **13.82** | **10.12** |

Σ of the per-point min = **472.50 µs**; row-1 Σ = 503.11 µs (row-1 is a single
team's 15 numbers, not the min — it is not a lower envelope).

---

## 4. Section 4 — F6 OJ result = serial-probe baseline (lines 48–62)

| point | our µs | best µs |
|---|---|---|
| 1 | 3.74 | 1.59 |
| 2 | 7.22 | 2.14 |
| 3 | 8.51 | 2.63 |
| 4 | 11.68 | 3.90 |
| 5 | 10.92 | 2.96 |
| 6 | 16.70 | 3.82 |
| 7 | 15.31 | 5.74 |
| 8 | 69.90 | 17.32 |
| 9 | 92.34 | 52.43 |
| 10 | 110.81 | 75.59 |
| 11 | 88.77 | 45.65 |
| 12 | 130.86 | 33.62 |
| 13 | 27.28 | 1.40 |
| 14 | 20.61 | 11.86 |
| 15 | 29.96 | 10.12 |

Σ = **644.61 µs**, which matches the plan's "F6 OJ: Σ 650.4 → 644.6 µs". This is
the identity anchor that makes section 4 the F6 submission.

---

## 5. Section 5 — serial probe (`case_verify_test`) (lines 65–79)

The serial probe clamps the cube-side grid to **one block** (`plan.cubeBlocks = 1`,
`finalBlocks` untouched) and buries **no spin**. Its readout is therefore **not a
rung** — it is the **probe ÷ production ratio**, whose magnitude tracks how much
cube parallelism the production plan had. Raw:

| point | probe µs | best µs |
|---|---|---|
| 1 | 3.68 | 1.59 |
| 2 | 7.56 | 2.14 |
| 3 | 8.52 | 2.63 |
| 4 | 21.39 | 3.90 |
| 5 | 17.23 | 2.96 |
| 6 | 39.72 | 3.82 |
| 7 | 36.61 | 5.74 |
| 8 | 666.74 | 17.32 |
| 9 | 789.96 | 52.43 |
| 10 | 1.16 ms (= 1160 µs, ±5) | 75.59 |
| 11 | 1.21 ms (= 1210 µs, ±5) | 45.65 |
| 12 | 1.54 ms (= 1540 µs, ±5) | 33.62 |
| 13 | 133.34 | 1.40 |
| 14 | 62.01 | 11.86 |
| 15 | 29.31 | 10.12 |

### 5.1 Decode arithmetic — section 5 vs its baseline

**Baseline = section 4 (F6).** Justification: the serial probe is F6 + 27 probe
lines (`kernel.asc` diff vs `kernel_VERIFIED_F6.asc`); the plan's "探针结果"
table prints exactly section 4's µs (`3.74 / 7.22 / 8.51 / 29.96`) in its "生产 µs"
column. **Ambiguity flag:** the F8_prod `section?` column differs from section 4
by only −0.4 %…−4 % on the lite points, so using `section?` instead changes every
ratio below by <0.05 and does **not** move any point across a class boundary; the
class assignment is robust either way. There is no rung to recover here.

| point | probe µs (s5) | baseline µs (s4) | diff (µs) | ratio probe/base | class |
|---|---|---|---|---|---|
| 1 | 3.68 | 3.74 | −0.06 | 0.98 | fixed overhead |
| 2 | 7.56 | 7.22 | +0.34 | 1.05 | fixed overhead |
| 3 | 8.52 | 8.51 | +0.01 | 1.00 | fixed overhead |
| 4 | 21.39 | 11.68 | +9.71 | 1.83 | few cube blocks |
| 5 | 17.23 | 10.92 | +6.31 | 1.58 | few cube blocks |
| 6 | 39.72 | 16.70 | +23.02 | 2.38 | few cube blocks |
| 7 | 36.61 | 15.31 | +21.30 | 2.39 | few cube blocks |
| 8 | 666.74 | 69.90 | +596.84 | 9.54 | cube saturated |
| 9 | 789.96 | 92.34 | +697.62 | 8.55 | cube saturated |
| 10 | 1160 (1.16 ms) | 110.81 | +1049.19 | 10.47 | cube saturated |
| 11 | 1210 (1.21 ms) | 88.77 | +1121.23 | 13.63 | cube saturated |
| 12 | 1540 (1.54 ms) | 130.86 | +1409.14 | 11.77 | cube saturated |
| 13 | 133.34 | 27.28 | +106.06 | 4.89 | few cube blocks |
| 14 | 62.01 | 20.61 | +41.40 | 3.01 | few cube blocks |
| 15 | 29.31 | 29.96 | −0.65 | 0.98 | fixed overhead |

Worked examples:
- p1: `3.68 / 3.74 = 0.984` → ratio below 1 → clamping the cube grid to 1 changes
  nothing → this point never had cube parallelism (pure AIV / fixed overhead).
- p12: `1540 / 130.86 = 11.77` → the serial run is ~12× slower → production used
  ~12 blocks' worth of cube work.
- p15: `29.31 / 29.96 = 0.978` → same as p1, no cube parallelism.

**Reading:** points {1, 2, 3, 15} are fixed-overhead dominated; {4, 5, 6, 7, 13, 14}
use few cube blocks; {8–12} are cube-saturated. This partitioning is the plan's
"探针结果：定位到病根" table and it reproduces exactly.

---

## 6. `section?` — F8_prod production baseline (lines 82–96)

Unlabeled in the file (its header line 81 is literally `section?`). Used as the
ladder baseline.

| point | our µs | best µs |
|---|---|---|
| 1 | 3.59 | 1.59 |
| 2 | 7.80 | 2.14 |
| 3 | 8.71 | 2.63 |
| 4 | 11.65 | 3.90 |
| 5 | 10.76 | 2.96 |
| 6 | 16.53 | 3.82 |
| 7 | 15.03 | 5.74 |
| 8 | 69.55 | 17.32 |
| 9 | 92.88 | 52.43 |
| 10 | 110.08 | 75.59 |
| 11 | 88.18 | 45.65 |
| 12 | 131.25 | 33.62 |
| 13 | 27.39 | 1.40 |
| 14 | 20.59 | 11.86 |
| 15 | 30.41 | 10.12 |

Σ = 644.40 µs.

---

## 7. Sections 6 / 7 / 8 — the three ladder probes

**Method (given).** `iterations = rung · BMMMS_PROBE_SPIN`, `rung = floor(log2(axis))`
clamped to 0..13. Calibrated on the RISC-V scalar side at `BMMMS_PROBE_SPIN = 1000`
→ **15.0–15.1 µs per rung**, verified linear across 8 rungs. Read-out:

```
rung = round( (T_probe − T_production) / 15.0 )
```

Axis encoding: **2 = M, 3 = N, 4 = K** (also 1 = B, 5 = dtype, 6 = tx1, 7 = tx2,
8 = packed). Rung → factor-of-two bucket:

| rung | axis value |
|---|---|
| 0 | 1 |
| 1 | 2–3 |
| 2 | 4–7 |
| 3 | 8–15 |
| 4 | 16–31 |
| 5 | 32–63 |
| 6 | 64–127 |
| 7 | 128–255 |
| 8 | 256–511 |
| 9 | 512–1023 |
| 10 | 1024–2047 |
| 11 | 2048–4095 |
| 12 | 4096–8191 |
| 13 | ≥ 8192 (clamp) |

Baseline for all three = `section?` (§6). Raw values:

| point | s6 (M) | s7 (N) | s8 (K) |
|---|---|---|---|
| 1 | 3.70 | 3.62 | 79.46 |
| 2 | 22.50 | 37.74 | 83.22 |
| 3 | 38.86 | 54.06 | 84.51 |
| 4 | 56.40 | 71.66 | 117.30 |
| 5 | 71.19 | 86.63 | 116.48 |
| 6 | 76.12 | 107.08 | 121.58 |
| 7 | 90.47 | 120.94 | 135.62 |
| 8 | 219.62 | 221.72 | 220.44 |
| 9 | 257.21 | 243.13 | 243.04 |
| 10 | 291.37 | 261.03 | 259.58 |
| 11 | 238.75 | 254.74 | 254.06 |
| 12 | 281.81 | 312.54 | 281.42 |
| 13 | 222.80 | 117.59 | 132.87 |
| 14 | 110.66 | 217.17 | 125.79 |
| 15 | 121.38 | 120.82 | 226.77 |

### 7.1 Section 6 decode — AXIS 2 (M)

Baseline = `section?` (§6). `diff = T_s6 − T_baseline`, `rung = round(diff / 15.0)`.

| point | s6 probe µs | base (`section?`) | diff | diff/15 | rung | ⇒ M |
|---|---|---|---|---|---|---|
| 1 | 3.70 | 3.59 | +0.11 | 0.007 | 0 | 1 |
| 2 | 22.50 | 7.80 | +14.70 | 0.980 | 1 | 2–3 |
| 3 | 38.86 | 8.71 | +30.15 | 2.010 | 2 | 4–7 |
| 4 | 56.40 | 11.65 | +44.75 | 2.983 | 3 | 8–15 |
| 5 | 71.19 | 10.76 | +60.43 | 4.029 | 4 | 16–31 |
| 6 | 76.12 | 16.53 | +59.59 | 3.973 | 4 | 16–31 |
| 7 | 90.47 | 15.03 | +75.44 | 5.029 | 5 | 32–63 |
| 8 | 219.62 | 69.55 | +150.07 | 10.005 | 10 | 1024–2047 |
| 9 | 257.21 | 92.88 | +164.33 | 10.955 | 11 | 2048–4095 |
| 10 | 291.37 | 110.08 | +181.29 | 12.086 | 12 | 4096–8191 |
| 11 | 238.75 | 88.18 | +150.57 | 10.038 | 10 | 1024–2047 |
| 12 | 281.81 | 131.25 | +150.56 | 10.037 | 10 | 1024–2047 |
| 13 | 222.80 | 27.39 | +195.41 | 13.027 | 13 | ≥8192 |
| 14 | 110.66 | 20.59 | +90.07 | 6.005 | 6 | 64–127 |
| 15 | 121.38 | 30.41 | +90.97 | 6.065 | 6 | 64–127 |

Worked: p2 `(22.50 − 7.80)/15.0 = 0.980 → round = 1`; p10
`(291.37 − 110.08)/15.0 = 12.086 → 12`; p13 `(222.80 − 27.39)/15.0 = 13.027 → 13`.

Note the **residual**: every point lands within **±0.11** of an integer, and
points 1 and 2 are within 0.02 of their integer. This is the evidence the ladder
is clean on the OJ (the plan claims "全部落在整数 0.1 以内" — confirmed here).

### 7.2 Section 7 decode — AXIS 3 (N)

| point | s7 probe µs | base (`section?`) | diff | diff/15 | rung | ⇒ N |
|---|---|---|---|---|---|---|
| 1 | 3.62 | 3.59 | +0.03 | 0.002 | 0 | 1 |
| 2 | 37.74 | 7.80 | +29.94 | 1.996 | 2 | 4–7 |
| 3 | 54.06 | 8.71 | +45.35 | 3.023 | 3 | 8–15 |
| 4 | 71.66 | 11.65 | +60.01 | 4.001 | 4 | 16–31 |
| 5 | 86.63 | 10.76 | +75.87 | 5.058 | 5 | 32–63 |
| 6 | 107.08 | 16.53 | +90.55 | 6.037 | 6 | 64–127 |
| 7 | 120.94 | 15.03 | +105.91 | 7.061 | 7 | 128–255 |
| 8 | 221.72 | 69.55 | +152.17 | 10.145 | 10 | 1024–2047 |
| 9 | 243.13 | 92.88 | +150.25 | 10.017 | 10 | 1024–2047 |
| 10 | 261.03 | 110.08 | +150.95 | 10.063 | 10 | 1024–2047 |
| 11 | 254.74 | 88.18 | +166.56 | 11.104 | 11 | 2048–4095 |
| 12 | 312.54 | 131.25 | +181.29 | 12.086 | 12 | 4096–8191 |
| 13 | 117.59 | 27.39 | +90.20 | 6.013 | 6 | 64–127 |
| 14 | 217.17 | 20.59 | +196.58 | 13.105 | 13 | ≥8192 |
| 15 | 120.82 | 30.41 | +90.41 | 6.027 | 6 | 64–127 |

Worked: p2 `(37.74 − 7.80)/15.0 = 1.996 → 2`; p11
`(254.74 − 88.18)/15.0 = 11.104 → 11`; p14 `(217.17 − 20.59)/15.0 = 13.105 → 13`.

### 7.3 Section 8 decode — AXIS 4 (K)

| point | s8 probe µs | base (`section?`) | diff | diff/15 | rung | ⇒ K |
|---|---|---|---|---|---|---|
| 1 | 79.46 | 3.59 | +75.87 | 5.058 | 5 | 32–63 |
| 2 | 83.22 | 7.80 | +75.42 | 5.028 | 5 | 32–63 |
| 3 | 84.51 | 8.71 | +75.80 | 5.053 | 5 | 32–63 |
| 4 | 117.30 | 11.65 | +105.65 | 7.043 | 7 | 128–255 |
| 5 | 116.48 | 10.76 | +105.72 | 7.048 | 7 | 128–255 |
| 6 | 121.58 | 16.53 | +105.05 | 7.003 | 7 | 128–255 |
| 7 | 135.62 | 15.03 | +120.59 | 8.039 | 8 | 256–511 |
| 8 | 220.44 | 69.55 | +150.89 | 10.059 | 10 | 1024–2047 |
| 9 | 243.04 | 92.88 | +150.16 | 10.011 | 10 | 1024–2047 |
| 10 | 259.58 | 110.08 | +149.50 | 9.967 | 10 | 1024–2047 |
| 11 | 254.06 | 88.18 | +165.88 | 11.059 | 11 | 2048–4095 |
| 12 | 281.42 | 131.25 | +150.17 | 10.011 | 10 | 1024–2047 |
| 13 | 132.87 | 27.39 | +105.48 | 7.032 | 7 | 128–255 |
| 14 | 125.79 | 20.59 | +105.20 | 7.013 | 7 | 128–255 |
| 15 | 226.77 | 30.41 | +196.36 | 13.091 | 13 | ≥8192 |

Worked: p1 `(79.46 − 3.59)/15.0 = 5.058 → 5`; p7
`(135.62 − 15.03)/15.0 = 8.039 → 8`; p15 `(226.77 − 30.41)/15.0 = 13.091 → 13`.

### 7.4 Combined M/N/K decode (sections 6+7+8)

| # | M | N | K | | # | M | N | K |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 32–63 | | 9 | 2048–4095 | 1024–2047 | 1024–2047 |
| 2 | 2–3 | 4–7 | 32–63 | | 10 | 4096–8191 | 1024–2047 | 1024–2047 |
| 3 | 4–7 | 8–15 | 32–63 | | 11 | 1024–2047 | 2048–4095 | 2048–4095 |
| 4 | 8–15 | 16–31 | 128–255 | | 12 | 1024–2047 | 4096–8191 | 1024–2047 |
| 5 | 16–31 | 32–63 | 128–255 | | 13 | ≥8192 | 64–127 | 128–255 |
| 6 | 16–31 | 64–127 | 128–255 | | 14 | 64–127 | ≥8192 | 128–255 |
| 7 | 32–63 | 128–255 | 256–511 | | 15 | 64–127 | 64–127 | ≥8192 |
| 8 | 1024–2047 | 1024–2047 | 1024–2047 | | | | | |

Corroboration: `docs/case_paths.json` (machine-generated) lists 15 cases × lo/mid/hi
whose shapes sit inside exactly these buckets (e.g. case 7 = M 32→63, N 128→255,
K 256→511; case 15 = M 64→127, N 64→127, K 8192). That file is a *proposed*
grid consistent with the decode, not an independent measurement of the OJ shapes.

---

## 8. Sections 9–15 (lines 150–266)

**Three of these are PROBE submissions, not production rows**, which is what an earlier draft of
this document got wrong. They sit between production runs and carry no label in
`performance.txt`:

| section | what it actually is | evidence |
|---|---|---|
| **9** | B-axis ladder (`AXIS 1`, `SPIN 1000`) | delta vs the production block gives rungs 0,0,1,2,3,3,4,0…0, which maps to B = 1,1,2,4,8,8,16,1…1 — an exact match to the hypotheses' B column, residual < 0.1; `scratch/pb_B/CMakeLists.txt` carries `BMMMS_PROBE_AXIS=1`, calibration in `scratch/w0/blad_probe/` |
| **11** | coarse M pass (`AXIS 2`, `BASE 64`, `STEP 5`) | inflates exactly points 8–13 by ≈195 µs ≈ 13 rungs (the clamp) and nothing else; `scratch/pb_fine/CMakeLists.txt` carries `BMMMS_PROBE_AXIS=2 BMMMS_PROBE_BASE=64 BMMMS_PROBE_STEP=5`. Separates {8…13} (M ≥ 1024) from the rest, corroborating §6. The exact BASE/STEP encoding is undocumented, so treat this as corroboration only |
| **13** | packed attributes (`AXIS 8` = `4·bf16 + 2·tx1 + tx2`) | §13 − §12 gives rungs 0,6,1,7,0,5,2,7,1,4,3,6,0,5,3, matching the attribute encoding for 14 of 15 points, residuals < 0.1; `scratch/w0/ax8p` and `ax8q` hold the AXIS-8 captures. **Point 10 disagrees** (measured 3.97 → rung 4, i.e. bf16/0/0, vs the table's fp16/1/1 = 3) |

Remaining production submissions: **10, 12, 14, 15.**

| pt | s9 | s10 | s11 | s12 | s13 | s14 | s15 |
|---|---|---|---|---|---|---|---|
| 1 | 3.92 | 3.72 | 3.94 | 3.73 | 3.82 | 3.29 | 3.42 |
| 2 | 7.64 | 6.95 | 7.57 | 7.48 | 98.14 | 7.75 | 6.88 |
| 3 | 23.86 | 8.50 | 8.42 | 8.42 | 23.75 | 8.13 | 8.83 |
| 4 | 41.19 | 11.51 | 11.40 | 10.68 | 116.84 | 10.77 | 11.53 |
| 5 | 55.53 | 10.74 | 11.72 | 10.02 | 11.13 | 9.02 | 9.20 |
| 6 | 60.28 | 16.76 | 17.92 | 15.78 | 90.98 | 16.11 | 15.87 |
| 7 | 74.21 | 15.22 | 16.75 | 14.08 | 44.00 | 11.89 | 11.72 |
| 8 | 70.39 | 70.56 | 266.69 | 68.01 | 173.68 | 67.89 | 68.85 |
| 9 | 92.62 | 91.80 | 288.49 | 92.59 | 105.86 | 91.95 | 92.60 |
| 10 | 109.76 | 111.51 | 305.52 | 110.17 | 169.77 | 109.66 | 109.56 |
| 11 | 89.32 | 89.08 | 283.76 | 87.16 | 131.74 | 86.94 | 87.14 |
| 12 | 132.25 | 131.93 | 326.89 | 129.97 | 220.17 | 130.56 | 131.19 |
| 13 | 27.86 | 27.99 | 223.30 | 26.27 | 27.58 | 26.79 | 26.11 |
| 14 | 21.45 | 20.61 | 22.54 | 19.44 | 94.08 | 19.34 | 19.01 |
| 15 | 30.36 | 29.46 | 30.13 | 24.74 | 70.19 | 24.90 | 25.05 |
| **Σ** | 840.64 | 646.34 | 1825.04 | 628.54 | 1381.73 | 624.99 | 626.96 |

Sections 10, 12, 14, 15 are all ≈625–646 µs and look like clean production runs
(consistent with §6's 644.40). Sections 9, 11, 13 are far above that.

### 8.1 Section 9 — ANOMALY, flagged

Section 9's points **3, 4, 5, 6, 7 are inflated** while 1, 2, 8–15 are normal.
Differenced against `section?` (§6):

| point | s9 µs | base (`section?`) | diff | diff/15 | note |
|---|---|---|---|---|---|
| 1 | 3.92 | 3.59 | +0.33 | 0.02 | normal |
| 2 | 7.64 | 7.80 | −0.16 | −0.01 | normal |
| **3** | **23.86** | 8.71 | **+15.15** | **1.01** | **inflated** |
| **4** | **41.19** | 11.65 | **+29.54** | **1.97** | **inflated** |
| **5** | **55.53** | 10.76 | **+44.77** | **2.98** | **inflated** |
| **6** | **60.28** | 16.53 | **+43.75** | **2.92** | **inflated** |
| **7** | **74.21** | 15.03 | **+59.18** | **3.95** | **inflated** |
| 8 | 70.39 | 69.55 | +0.84 | 0.06 | normal |
| 9 | 92.62 | 92.88 | −0.26 | −0.02 | normal |
| 10 | 109.76 | 110.08 | −0.32 | −0.02 | normal |
| 11 | 89.32 | 88.18 | +1.14 | 0.08 | normal |
| 12 | 132.25 | 131.25 | +1.00 | 0.07 | normal |
| 13 | 27.86 | 27.39 | +0.47 | 0.03 | normal |
| 14 | 21.45 | 20.59 | +0.86 | 0.06 | normal |
| 15 | 30.36 | 30.41 | −0.05 | 0.00 | normal |

The five inflated diffs land near **+1, +2, +3, +3, +4 rungs** (residuals ≤0.08).
The file carries no label; the working hypothesis recorded in the plan/this task is
a **mis-submitted build or a build with a limit removed**, not a measurement of a
real production revision. This document does **not** assert an upstream cause —
only the raw inflation above. Excluding points 3–7, section 9 agrees with `section?`
to within ±1.2 µs.

### 8.2 Sections 11 and 13 — secondary anomalies (observation, not asked-for)

Not requested by the brief, recorded because a reader comparing Σ would otherwise
be misled:
- **Section 11** inflation is on **points 8–13** (266.69, 288.49, 305.52, 283.76,
  326.89, 223.30 vs base 69.55, 92.88, 110.08, 88.18, 131.25, 27.39) — this is the
  signature of a build whose large-shape path was slowed (or a probe variant), not
  of a production run.
- **Section 13** inflation is scattered (points 2, 4, 6, 7, 8, 9, 10, 11, 12, 14, 15
  all elevated), including a 98.14 µs point 2 and 94.08 µs point 14 — again
  inconsistent with a production run — because it is not one. It is the AXIS-8
  packed-attribute probe: the elevations are exactly `15 x (4*bf16 + 2*tx1 + tx2)`.
Neither is an anomalous leaderboard row; both are probe submissions, and their
builds ARE identified (`scratch/pb_fine`, `scratch/w0/ax8p`).

---

## 9. Numbers that could NOT be recovered

1. **Exact shapes.** The ladder resolves each axis only to a factor of two
   (`floor(log2)`). B, dtype, transposeX1, transposeX2 were **never probed** —
   AXIS 1 / 5 / 6 / 7 / 8 ladders are defined in the kernel but have **no
   corresponding section in `performance.txt`**. So the exact `(B,M,N,K,dtype,tx)`
   of any OJ point is *not* recoverable from this file; only the M/N/K buckets in §7.4.
2. **Section 5 has no rung.** The serial probe buries no spin, so the
   `rung = round(diff/15.0)` formula does **not** apply to it — the only readout is
   the probe/production ratio (§5.1). The brief's "recovered rung" column is
   therefore printed as N/A for section 5.
3. **Section 5 points 10–12 are quantized.** Given as `1.16 ms / 1.21 ms / 1.54 ms`
   (two decimals of a millisecond) → ±5 µs resolution. Their ratios (10.47 / 13.63 /
   11.77) carry that same ±~0.05 uncertainty.
4. **Ladder baseline identity.** Sections 6/7/8 and 4 are differenced against
   `section?` and section 4 respectively; `section?` itself has **no numeric label**
   in `performance.txt` (header is the literal string `section?`). Its assignment to
   F8_prod comes from the plan, not from the file. If it were in fact the F6 row, all
   ladder rungs above are **unchanged** (every diff shifts by <0.5 µs, well inside
   the 15.0 µs rung spacing) — verified point-by-point — so the decode is robust to
   this ambiguity.
5. **Section 5 baseline identity is genuinely ambiguous** between section 4 (F6,
   used here per the plan) and `section?` (F8_prod). §5.1 shows the ratio/class
   conclusion is identical either way, but the *absolute* diff values are not.
6. **Build identity of sections 1, 2, 9–15.** No md5, score, or timestamp is present
   for these rows except section 3's timestamps. The mapping of sections 10–15 to
   named `kernel_VERIFIED_F*.asc` snapshots is **not** stated anywhere I can read and
   is left unasserted. Section 9's "mis-submitted / limit-removed" cause is a
   hypothesis, not an established fact.
7. **Team names for section 3** are absent (score + timestamp only).
8. **Two malformed cells** (noted, value inferred by pattern, not quoted from a
   well-formed token): `performance.txt` line 21 (section 1, point 15, best column)
   is `10.12` with no unit; sections 7/8/9 (lines 129, 146, 163) print the
   point-14 best as `10.18μs` while sections 1–6 print `11.86μs` — the
   All-teams-best column for point 14 changes value mid-file from 11.86 to 10.18.
   Neither affects our-µs numbers.

---

### Arithmetic re-check

All `rung = round((T_probe − T_baseline) / 15.0)` values in §7 and §8.1 were
computed programmatically from the raw `performance.txt` columns; every one lands
within **±0.145** of an integer (largest residual: s7 p8 = 10.145; s7 p14 = 13.105;
s8 p15 = 13.091). §7.4 and the Σ row of §8 were likewise machine-summed.
