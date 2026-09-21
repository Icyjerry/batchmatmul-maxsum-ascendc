"""Abstract one-AIC/two-AIV ring protocol; not a hardware synchronization test."""
import random


def validate_protocol():
    checked = 0
    for mode in range(3):
        for windows in range(10):
            for seed in range(128):
                rng = random.Random(seed * 31 + windows * 3 + mode)
                # Initial releases for both ring slots and two wrapper start credits.
                release = [[1, 1], [1, 1]]
                starts = [min(2, windows)] * 2
                ready = [[], []]
                aic = 0
                seq = [0, 0]
                phase = [0, 0]
                read_done = [set(), set()]
                written = [-1, -1]
                reductions = [[], []]
                # Phases: wait, read completion, then release/start/reduce (mode 2)
                # or reduce/release/start (modes 0/1), then advance. Actual source
                # queues/addresses are checked separately by the extracted C++ test.
                while aic < windows or seq != [windows, windows]:
                    runnable = []
                    slot = aic % 2
                    if aic < windows and all(release[v][slot] and starts[v] for v in range(2)):
                        runnable.append(2)
                    for v in range(2):
                        if seq[v] < windows and (phase[v] != 0 or ready[v]):
                            runnable.append(v)
                    assert runnable, ('deadlock', mode, windows, seed, aic, seq, phase)
                    actor = rng.choice(runnable)
                    if actor == 2:
                        if written[slot] >= 0:
                            assert all(written[slot] in read_done[v] for v in range(2)), 'premature overwrite'
                        written[slot] = aic
                        for v in range(2):
                            release[v][slot] -= 1
                            starts[v] -= 1
                            ready[v].append(aic)
                        aic += 1
                        continue
                    v = actor
                    q = seq[v]
                    ph = phase[v]
                    if ph == 0:
                        assert ready[v].pop(0) == q and written[q % 2] == q
                    elif ph == 1:
                        assert written[q % 2] == q
                        read_done[v].add(q)  # also covers an empty AIV half: no reads
                    else:
                        actions = ('release', 'start', 'reduce') if mode == 2 else ('reduce', 'release', 'start')
                        action = actions[ph - 2]
                        if action == 'release':
                            assert q in read_done[v]
                            release[v][q % 2] += 1
                            assert release[v][q % 2] <= 1
                        elif action == 'start':
                            if q + 2 < windows:
                                starts[v] += 1
                                assert starts[v] <= 2
                        else:
                            reductions[v].append(q)
                    phase[v] += 1
                    if phase[v] == 5:
                        phase[v] = 0
                        seq[v] += 1
                assert starts == [0, 0] and ready == [[], []]
                assert reductions == [list(range(windows)), list(range(windows))]
                # Final AIC waits consume exactly one remaining release per slot,
                # including initial credit for an unused slot (zero/one window).
                assert release == [[1, 1], [1, 1]]
                checked += 1
    print(f'Abstract AIC/two-AIV protocol: {checked} randomized interleavings PASS; no deadlock/early overwrite, exact final credits.')


if __name__ == '__main__':
    validate_protocol()
