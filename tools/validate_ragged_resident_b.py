"""Independent CPU check of the ragged full-B reuse geometry.

This checks logical values, K/N padding and worker ownership. It does not
compile Ascend C or validate its DMA and event instructions.
"""

from random import Random


def ceil16(x):
    return (x + 15) // 16 * 16


def check(n, k, workers, negative):
    rng = Random(1000 + 17 * n + k + workers + negative)
    b = [[-rng.randint(1, 3) if negative else rng.randint(-3, 3)
          for _ in range(n)] for _ in range(k)]
    packed = [[0] * ceil16(n) for _ in range(ceil16(k))]
    for ki in range(k):
        packed[ki][:n] = b[ki]

    seen = [0] * 64
    streamed = [0.0] * workers
    for worker in range(workers):
        # 64 tiles model the competition M=8192, baseM=128 path.
        for mt in range(worker, 64, workers):
            seen[mt] += 1
        if worker < 4:
            q = [rng.randint(1, 3) if negative else rng.randint(-3, 3)
                 for _ in range(k)]
            q.extend([0] * (ceil16(k) - k))
            reference = max(sum(q[ki] * b[ki][col] for ki in range(k))
                            for col in range(n))
            obtained = max(sum(q[ki] * packed[ki][col]
                               for k0 in range(0, ceil16(k), 128)
                               for ki in range(k0, min(k0 + 128, ceil16(k))))
                           for col in range(n))
            assert obtained == reference, (n, k, workers, worker)
            if negative:
                assert obtained < 0
            streamed[worker] += obtained

    assert seen == [1] * 64
    assert len(streamed) == workers
    return 4


def main():
    rows = 0
    for n in (64, 65, 96, 127):
        for k in (128, 136, 192, 248):
            for workers in (16, 20, 32):
                for negative in (False, True):
                    rows += check(n, k, workers, negative)
    print(f"ragged B padding/reuse: {rows} sampled rows PASS")


if __name__ == "__main__":
    main()
