"""Find two-person patterns that mix single rolls and pairs, such as [13]21[24].

The two people take strict turns. A turn is one lane, or two lanes in brackets
rolled together. Both people roll the same number of balls per loop. Each lane is
only ever rolled from one end and every lane is used. No turn-to-turn step
happens twice, and the pattern is not a shorter one repeated.

Timing works like zips: every roll gets a number of beats until that ball is
rolled again (odd, because it changes ends; at least 3 unless everything is 1).
Each turn must receive exactly as many balls as it rolls, and a ball can never
overtake another in the same lane. The two balls of a pair must take the same
number of beats, because they are rolled together at one speed. The most even
timing is kept.

Patterns that only differ by starting turn, by being upside down or by being a
mirror image are counted once.
"""
import itertools, sys, math
from collections import defaultdict

def show(seq):
    return "".join(str(t[0]) if len(t) == 1 else f"[{t[0]}{t[1]}]" for t in seq)

def timing(seq, balls):
    L = len(seq)
    sites = [(t, s) for t in range(L) for s in range(len(seq[t]))]
    R = len(sites)
    total = balls * L
    avg = total / R
    low = 1 if avg <= 1 else 3
    cap = 2 * L + math.ceil(avg) + 2
    need = [len(t) for t in seq]
    got = [0] * L
    vals = [None] * R
    best = [None, None]

    def lane_ok(i):
        ti, si = sites[i]
        for j in range(R):
            if j == i or vals[j] is None: continue
            tj, sj = sites[j]
            if seq[tj][sj] != seq[ti][si]: continue
            (a, va), (b, vb) = sorted(((ti, vals[i]), (tj, vals[j])))
            gap = b - a
            if not (va - vb < gap and vb - va < L - gap): return False
        return True

    def go(i, left):
        if i == R:
            if left == 0:
                score = (max(vals) - min(vals), sum(v * v for v in vals), tuple(vals))
                if best[0] is None or score < best[0]:
                    best[0], best[1] = score, tuple(vals)
            return
        t, s = sites[i]
        rest = R - i - 1
        # the two balls of a pair are rolled together, so they must take the same time
        for v in ([vals[i - 1]] if s == 1 else range(low, cap + 1, 2)):
            if left - v < rest * low: break
            lt = (t + v) % L
            if got[lt] >= need[lt]: continue
            vals[i] = v
            if lane_ok(i):
                got[lt] += 1
                go(i + 1, left - v)
                got[lt] -= 1
            vals[i] = None

    go(0, total)
    return best[1]

def valid(seq, k):
    L = len(seq)
    side, used = {}, set()
    rolls = [0, 0]
    kinds = set()
    for i, turn in enumerate(seq):
        kinds.add(len(turn)); rolls[i % 2] += len(turn)
        for lane in turn:
            used.add(lane)
            if side.setdefault(lane, i % 2) != i % 2: return False
    if rolls[0] != rolls[1] or kinds != {1, 2} or used != set(range(1, k + 1)): return False
    if len({(seq[i], seq[(i + 1) % L]) for i in range(L)}) != L: return False
    for r in range(2, L, 2):
        if L % r == 0 and seq[r:] + seq[:r] == seq: return False
    return True

def images(seq, k):
    out = []
    for s in (seq, tuple(tuple(k + 1 - x for x in t) for t in seq)):
        for r in range(len(s)):
            out.append(s[r:] + s[:r])
    return out

def symmetric(seq, k):
    """True if the pattern looks the same upside down (allowing a different starting turn)."""
    flipped = tuple(tuple(k + 1 - x for x in t) for t in seq)
    same = lambda a, b: all(sorted(x) == sorted(y) for x, y in zip(a, b))
    return any(same(flipped[r:] + flipped[:r], seq) for r in range(len(seq)))

def search(k, max_rolls=8, ball_counts=range(1, 9)):
    lanes = range(1, k + 1)
    turns = [(a,) for a in lanes] + [(a, b) for a in lanes for b in lanes if a != b]
    found = {}
    def build(seq, rolls):
        if len(seq) % 2 == 0 and len(seq) >= 2 and valid(seq, k):
            ims = images(seq, k)
            canon = min(ims)
            if canon not in found:
                disp = min(ims, key=lambda s: (s[0][0] != 1, 1 not in s[0], s))   # start on lane 1 where possible
                tm = {b: timing(disp, b) for b in ball_counts}
                found[canon] = (disp, {b: v for b, v in tm.items() if v})
        if len(seq) >= 8: return
        for t in turns:
            if rolls + len(t) > max_rolls: continue
            ok = True
            for lane in t:
                for i, old in enumerate(seq):
                    if lane in old and i % 2 != len(seq) % 2: ok = False
            if ok: build(seq + (t,), rolls + len(t))
    for t in turns:
        if 1 in t: build((t,), len(t))
    return found

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k in (3, 4):
        found = search(k)
        playable = {c: v for c, v in found.items() if v[1]}
        by = defaultdict(list)
        for d, tm in playable.values():
            by[(sum(len(t) for t in d), len(d))].append((show(d), tm))
        print(f"\n{k} lanes: {len(found)} patterns, {len(playable)} of them have a timing that works")
        for key in sorted(by):
            rows = sorted(by[key])
            print(f"  {key[0]} rolls in {key[1]} turns: {len(rows)}")
            if len(rows) <= 12:
                for text, tm in rows:
                    print("     ", text.ljust(18), "  ".join(f"{b}: {''.join(map(str, v))}" for b, v in tm.items()))


def embed(path="index.html"):
    """Rewrite the mixed-pattern lists inside index.html and the expected timings used by the tests."""
    import json, re
    found = search(4)
    by = defaultdict(list)
    expected = {}
    for d, tm in found.values():
        by[sum(len(t) for t in d)].append(show(d))
        expected[show(d)] = {str(b): list(v) for b, v in tm.items()}
    everything = {"4": {str(r): " ".join(sorted(v)) for r, v in sorted(by.items())}}
    sym = sorted(show(d) for d, tm in found.values() if symmetric(d, 4))
    short = [{"group": "Symmetric, 4 or 8 balls", "items": sym}]
    top = [sym[i] for i in (0, 3, 6, 8, 12)]
    block = ('<script id="mixed-patterns">\nconst MIX_LIST = ' + json.dumps(short, separators=(",", ":")) +
             ';\nconst MIX_TOP = ' + json.dumps(top) + ';\nconst ALL_MIX = ' + json.dumps(everything, separators=(",", ":")) + ';\n</script>')
    html = open(path, encoding="utf-8").read()
    html, n = re.subn(r'<script id="mixed-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    assert n == 1
    open(path, "w", encoding="utf-8").write(html)
    json.dump(expected, open("tests/mixed-timings.json", "w"), separators=(",", ":"))
    print("mixed:", {r: len(v.split()) for r, v in everything["4"].items()}, "symmetric:", len(sym), "top:", top)

if __name__ == "__main__" and "--embed" in sys.argv:
    embed()
