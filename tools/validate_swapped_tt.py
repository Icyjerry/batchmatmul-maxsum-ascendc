"""Independent small-input oracle for the TT column-Max task layout.

This checks address ownership and Max(N)->Sum(M), not Ascend instructions or speed.
"""

import math
import random


BM = BN = 128


def check_case(batches, m, n, k, split, workers, negative):
    rng = random.Random((batches, m, n, k, split, workers, negative).__hash__())
    x1 = [[[rng.randint(1, 3) if negative else rng.randint(-3, 3)
            for _ in range(m)] for _ in range(k)] for _ in range(batches)]
    x2 = [[[rng.randint(-3, -1) if negative else rng.randint(-3, 3)
            for _ in range(k)] for _ in range(n)] for _ in range(batches)]
    logical_x1 = [[[x1[b][kk][col] for kk in range(k)]
                   for col in range(m)] for b in range(batches)]
    logical_x2 = [[[x2[b][row][kk] for row in range(n)]
                   for kk in range(k)] for b in range(batches)]
    expected = [sum(max(sum(logical_x1[b][col][kk] * logical_x2[b][kk][row]
                            for kk in range(k)) for row in range(n))
                    for col in range(m)) for b in range(batches)]
    d = [[[sum(x2[b][row][kk] * x1[b][kk][col] for kk in range(k))
           for col in range(m)] for row in range(n)] for b in range(batches)]

    row_tiles = math.ceil(n / BM)
    col_tiles = math.ceil(m / BN)
    assert 1 <= split <= row_tiles
    partial = [None] * (batches * split * 2 * col_tiles * BN)
    tasks = batches * col_tiles * split
    seen_tasks = set()
    for worker in range(workers):
        for task in range(worker, tasks, workers):
            assert task not in seen_tasks
            seen_tasks.add(task)
            ns = task % split
            col_tile = (task // split) % col_tiles
            batch = task // (split * col_tiles)
            start = ns * row_tiles // split
            stop = (ns + 1) * row_tiles // split
            for sub in range(2):
                maxima = [-math.inf] * BN
                for tile in range(start, stop):
                    first = tile * BM + sub * (BM // 2)
                    rows = min(BM // 2, max(0, n - first))
                    for col in range(min(BN, m - col_tile * BN)):
                        lanes = [d[batch][first + row][col_tile * BN + col]
                                 for row in range(rows)]
                        lanes.extend([-math.inf] * (BM // 2 - rows))
                        span = BM // 4
                        while span:
                            for row in range(span):
                                lanes[row] = max(lanes[row], lanes[row + span])
                            span //= 2
                        maxima[col] = max(maxima[col], lanes[0])
                base = ((batch * (split * 2) + ns * 2 + sub) * col_tiles + col_tile) * BN
                for col, value in enumerate(maxima):
                    assert partial[base + col] is None
                    partial[base + col] = value
    assert len(seen_tasks) == tasks and all(value is not None for value in partial)
    got = []
    for batch in range(batches):
        score = 0
        for col in range(m):
            col_tile, offset = divmod(col, BN)
            score += max(partial[((batch * (split * 2) + lane) * col_tiles + col_tile)
                                 * BN + offset] for lane in range(split * 2))
        got.append(score)
    assert got == expected, (batches, m, n, split, workers, negative, got, expected)


def main():
    shapes = [(1, 1), (31, 31), (64, 64), (65, 65), (127, 127),
              (128, 128), (129, 129), (129, 1), (1, 129),
              (65, 129), (129, 65), (17, 145), (145, 17), (145, 145)]
    cases = 0
    for m, n in shapes:
        for batches in (1, 2):
            for negative in (False, True):
                for workers in (1, 3, 7):
                    for split in range(1, math.ceil(n / BM) + 1):
                        check_case(batches, m, n, 8, split, workers, negative)
                        cases += 1
    print(f"TT swapped task/column reduction: {cases} cases passed")


if __name__ == "__main__":
    main()
