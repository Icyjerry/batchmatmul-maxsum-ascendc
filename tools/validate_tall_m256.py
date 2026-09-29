"""Model the historical tall/narrow case's 128- and 256-row task geometry.

The device tiler, basic MMAD instructions and latency still require CANNJudge.
"""

import math


def ceil16(x):
    return (x + 15) // 16 * 16


def check(n, k, workers):
    m = 8192
    bn = ceil16(n)
    assert k % 8 == 0 and 128 <= k < 256
    scores = []
    for bm in (128, 256):
        tasks = m // bm
        owners = [0] * tasks
        partials = [None] * (tasks * 2)
        for worker in range(min(workers, tasks)):
            for task in range(worker, tasks, min(workers, tasks)):
                owners[task] += 1
                for sub in (0, 1):
                    start = task * bm + sub * (bm // 2)
                    values = [-float((row * 17 + n * 11) % 101 + 1)
                              for row in range(start, start + bm // 2)]
                    partials[task * 2 + sub] = math.fsum(values)
        assert owners == [1] * tasks and all(v is not None for v in partials)
        scores.append(math.fsum(partials))
        # Explicit live buffers: two A1/B1 and A2/B2 panels, one L0C tile,
        # two half-row VECIN buffers plus early-sum finalizer allocations.
        a = 2 * bm * 64 * 2
        b = 2 * bn * 64 * 2
        tile = bm * bn
        l0c = (2 if tile * 8 <= 131072 else 1) * tile * 4
        ub = bm * bn * 4 + 5 * bm * 4 + 5440
        assert a <= 64 * 1024 and b <= 64 * 1024
        assert a + b + 512 <= 512 * 1024
        assert l0c <= 128 * 1024 and ub < 192 * 1024
    assert scores[0] == scores[1]
    assert math.ceil(32 / workers) <= math.ceil(64 / workers)


def main():
    count = 0
    for n in (64, 65, 80, 96, 112, 127):
        for k in (128, 136, 192, 248):
            for workers in (1, 2, 4, 8, 20, 32):
                check(n, k, workers)
                count += 1
    print(f"tall manual 256-row geometry and buffers: {count} configurations PASS")


if __name__ == "__main__":
    main()
