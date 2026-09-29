"""Check the direct-batch schedule against the historical probe ranges.

This models ownership and buffer bounds; it does not compile Ascend C or time an NPU.
"""

from itertools import product


def ceil16(value):
    return (value + 15) // 16 * 16


def check_case(case, b, m, n, k, workers, ub):
    mp, np = ceil16(m), ceil16(n)
    assert k % 8 == 0
    assert mp >= m and np >= n
    assert workers <= b
    if case in (4, 5):
        # One AIV loads every valid row; the second still consumes the Cube flag.
        cbuf = mp * np * 4
        live = cbuf + 2 * mp * 4 + 32 + 512 + 1024
        assert live < ub
        rows = (m, 0)
    else:
        # Two VECIN slots, one VECOUT slot and four row scratch slots.
        live = 2 * mp * np * 4 + 5 * mp * 4 + 1024
        assert live < ub
        rows = (m, 0)
    assert sum(rows) == m
    assert all(0 <= count <= mp for count in rows)
    assert all(0 < min(64, n - offset) <= 64 for offset in range(0, n, 64))
    owners = [0] * b
    for worker in range(workers):
        for batch in range(worker, b, workers):
            owners[batch] += 1
    assert owners == [1] * b


def main():
    probes = {
        4: ((4, 7), (8, 15), (16, 31), (128, 248)),
        5: ((8, 15), (16, 31), (32, 63), (128, 248)),
        7: ((16, 31), (32, 63), (128, 255), (256, 504)),
    }
    checked = 0
    for case, limits in probes.items():
        samples = [[lo, (lo + hi) // 2, hi] for lo, hi in limits]
        for b, m, n, k in product(*samples):
            k = k // 8 * 8
            for cores in (1, 2, 4, 8, 20, 32):
                check_case(case, b, m, n, k, min(b, cores), 192 * 1024)
                checked += 1
    print(f"direct-batch ownership and buffer bounds: {checked} configurations PASS")


if __name__ == "__main__":
    main()
