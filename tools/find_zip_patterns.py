"""Find every pattern that uses zips, and work out its timing.

A zip (written z) is a handoff: instead of rolling, the hand passes its ball
straight to the other hand, which rolls it on the very next beat.

Rules used here
- One person, hands take turns, odd ball counts only (1, 3, 5).
- Each lane is only ever rolled by one hand; every lane 1..K is used.
- No hand move happens twice in a loop, so each hand zips at most once.
- Timing: every beat one ball is thrown. A zipped ball is thrown again 1 beat
  later. A rolled ball is thrown again an odd number of beats later (odd because
  it has changed sides), at least 3 beats when there is more than one ball.
  Two balls can never be due at the same beat, and a ball can never overtake
  another one in the same lane. Among all timings that work, the most even one
  is kept (smallest gap between the longest and shortest roll).
- Patterns that only differ by starting beat, by being upside down, or by being
  a mirror image are counted once. (Running a pattern backwards is NOT counted
  as the same here, because with zips it changes the timing.)
"""
import itertools, sys
from collections import defaultdict

Z = 0  # how a zip is stored

def show(seq):
    return "".join("z" if x == Z else str(x) for x in seq)

def key(seq):
    return tuple(9 if x == Z else x for x in seq)   # sorts zips after lanes

def valid_shape(seq, k):
    n = len(seq)
    side = {}
    zips = [0, 0]
    for i, x in enumerate(seq):
        if x == Z:
            zips[i % 2] += 1
        elif side.setdefault(x, i % 2) != i % 2:
            return False
    if max(zips) > 1 or sum(zips) == 0:
        return False
    if set(seq) - {Z} != set(range(1, k + 1)):
        return False
    moves = {(seq[i], seq[(i + 1) % n], i % 2) if Z in (seq[i], seq[(i + 1) % n]) else (seq[i], seq[(i + 1) % n]) for i in range(n)}
    return len(moves) == n

def images(seq, k):
    n = len(seq)
    out = []
    for s in (seq, tuple(x if x == Z else k + 1 - x for x in seq)):
        for r in range(n):
            out.append(s[r:] + s[:r])
    return out

def timing(seq, balls):
    """Most even beat counts for each throw, or None if the pattern can't be done with this many balls."""
    n = len(seq)
    total = balls * n
    low = 1 if balls == 1 else 3
    cap = 2 * n + balls
    rolls = [i for i in range(n) if seq[i] != Z]
    best = [None, None]
    vals = [1 if x == Z else None for x in seq]
    used = set((i + 1) % n for i in range(n) if seq[i] == Z)
    if len(used) != n - len(rolls):
        return None
    fixed = n - len(rolls)

    def lane_ok(i):
        for j in rolls:
            if j == i or vals[j] is None or seq[j] != seq[i]:
                continue
            a, b = (i, j) if i < j else (j, i)
            gap = b - a
            if not (vals[a] - vals[b] < gap and vals[b] - vals[a] < n - gap):
                return False
        return True

    def go(idx, left):
        if idx == len(rolls):
            if left == 0:
                rv = [vals[i] for i in rolls]
                score = (max(rv) - min(rv), sum(v * v for v in rv), tuple(vals))
                if best[0] is None or score < best[0]:
                    best[0], best[1] = score, tuple(vals)
            return
        i = rolls[idx]
        remaining = len(rolls) - idx - 1
        for v in range(low, cap + 1, 2):
            if left - v < remaining * low:
                break
            slot = (i + v) % n
            if slot in used:
                continue
            vals[i] = v
            if lane_ok(i):
                used.add(slot)
                go(idx + 1, left - v)
                used.discard(slot)
            vals[i] = None

    go(0, total - fixed)
    return best[1]

def search(k, max_beats=8, ball_counts=(1, 3, 5)):
    found = {}
    for n in range(2, max_beats + 1, 2):
        for rest in itertools.product(list(range(1, k + 1)) + [Z], repeat=n - 1):
            seq = (1,) + rest
            if not valid_shape(seq, k):
                continue
            ims = images(seq, k)
            canon = min(ims, key=key)
            if canon in found:
                continue
            disp = min((s for s in ims if s[0] == 1), key=key)
            found[canon] = (disp, {b: timing(disp, b) for b in ball_counts})
    return found

if __name__ == "__main__":
    out = []
    grand = 0
    for k in range(1, 5):
        found = search(k)
        by_len = defaultdict(list)
        for disp, tm in found.values():
            by_len[len(disp)].append((disp, tm))
        for n in sorted(by_len):
            rows = sorted(by_len[n], key=lambda r: key(r[0]))
            three = sum(1 for _, tm in rows if tm[3])
            five = sum(1 for _, tm in rows if tm[5])
            grand += len(rows)
            out.append(f"\n{k} lane{'s' if k > 1 else ''}, {n} beats: {len(rows)} patterns ({three} work with 3 balls, {five} with 5)")
            for disp, tm in rows:
                parts = [f"{b}: {' '.join(map(str, tm[b]))}" if tm[b] else f"{b}: no" for b in (3, 5)]
                out.append(f"  {show(disp):<9} " + "   ".join(parts))
    text = f"{grand} zip patterns in all (every one works with 1 ball)\nThe numbers after each pattern are how many beats later each ball is thrown again.\n" + "\n".join(out)
    open("zip-patterns.txt", "w").write(text + "\n")
    print("\n".join(l for l in text.split("\n") if not l.startswith("  ")))
