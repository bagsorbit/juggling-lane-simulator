"""Two-person patterns with zips (single rolls, people take turns).

Beats alternate between the two people; each person uses their hands in turn.
- a lane number: a roll to the other person (odd number of beats, at least 3 with 2+ balls)
- z: pass zip, handed to the other person in the middle, rolled on the next beat (1)
- s: self zip, handed to that person's own other hand, rolled on their next turn (2)
Same shape rules as solo zips: every lane 1..K used, a lane is always rolled from the
same end, no move happens twice in a loop, most even timing kept.
"""
import itertools, sys
from collections import defaultdict

Z, S = 0, -1
VAL = {Z: 1, S: 2}
def show(seq): return "".join("z" if x == Z else "s" if x == S else str(x) for x in seq)
def key(seq): return tuple(9 if x == Z else 8 if x == S else x for x in seq)

def valid_shape(seq, k):
    n = len(seq); side = {}
    for i, x in enumerate(seq):
        if x > 0 and side.setdefault(x, i % 2) != i % 2: return False
    if set(x for x in seq if x > 0) != set(range(1, k + 1)): return False
    moves = {(seq[i], seq[(i + 1) % n], i % 2) if min(seq[i], seq[(i + 1) % n]) <= 0 else (seq[i], seq[(i + 1) % n]) for i in range(n)}
    return len(moves) == n

def images(seq, k):
    out = []
    for s in (seq, tuple(x if x <= 0 else k + 1 - x for x in seq)):
        for r in range(len(s)): out.append(s[r:] + s[:r])
    return out

def timing(seq, balls):
    n = len(seq); low = 1 if balls == 1 else 3; cap = 2 * n + balls
    rolls = [i for i in range(n) if seq[i] > 0]
    vals = [VAL.get(x) if x <= 0 else None for x in seq]
    used = set()
    for i in range(n):
        if seq[i] <= 0:
            s = (i + vals[i]) % n
            if s in used: return None
            used.add(s)
    best = [None, None]
    def lane_ok(i):
        for j in rolls:
            if j == i or vals[j] is None or seq[j] != seq[i]: continue
            a, b = (i, j) if i < j else (j, i); gap = b - a
            if not (vals[a] - vals[b] < gap and vals[b] - vals[a] < n - gap): return False
        return True
    def go(idx, left):
        if idx == len(rolls):
            if left == 0 and rolls:
                rv = [vals[i] for i in rolls]
                score = (max(rv) - min(rv), sum(v * v for v in rv), tuple(vals))
                if best[0] is None or score < best[0]: best[0], best[1] = score, tuple(vals)
            return
        i = rolls[idx]; remaining = len(rolls) - idx - 1
        for v in range(low, cap + 1, 2):
            if left - v < remaining * low: break
            slot = (i + v) % n
            if slot in used: continue
            vals[i] = v
            if lane_ok(i):
                used.add(slot); go(idx + 1, left - v); used.discard(slot)
            vals[i] = None
    go(0, balls * n - sum(VAL[x] for x in seq if x <= 0))
    return best[1]

def symmetric(seq, k):
    """The two people do the same thing: shifting one beat over and turning the board round gives the same pattern."""
    n = len(seq); flip = tuple(x if x <= 0 else k + 1 - x for x in seq)
    return any(seq[r:] + seq[:r] == flip for r in range(1, n, 2))

def search(k, max_beats=8, balls=range(2, 10)):
    found = {}
    for n in range(2, max_beats + 1, 2):
        for rest in itertools.product(list(range(1, k + 1)) + [Z, S], repeat=n - 1):
            seq = (1,) + rest
            if S not in seq or not valid_shape(seq, k): continue
            ims = images(seq, k); canon = min(ims, key=key)
            if canon in found: continue
            disp = min((s for s in ims if s[0] == 1), key=key)
            found[canon] = (disp, {b: timing(disp, b) for b in balls})
    return found

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k in range(1, 5):
        res = search(k)
        cnt = defaultdict(int)
        for disp, tm in res.values():
            kind = "self+pass" if Z in disp else "self only"
            if any(tm.values()): cnt[kind] += 1
        print(k, dict(cnt))


def spread(seq, vals):
    r = [vals[i] for i in range(len(seq)) if seq[i] > 0]
    return max(r) - min(r)

def pick():
    """The listed selection. Self zips: both people self zip, no pass zips, evenly timed rolls.
    Self and pass zips: each person does both, evenly timed, plus Scarf and Mobius with zips added."""
    self_only, both = defaultdict(list), []
    for k in range(1, 5):
        for disp, tm in sorted(search(k).values(), key=lambda r: (len(r[0]), key(r[0]))):
            even = [b for b, v in tm.items() if v and 3 <= b <= 6 and spread(disp, v) == 0]
            if Z not in disp and S in disp[0::2] and S in disp[1::2] and even:
                self_only[k].append(show(disp))
            if all(x in disp[p::2] for x in (Z, S) for p in (0, 1)) and even:
                both.append(show(disp))
    both += ["1234zzss", "1243zzss"]
    return self_only, both

if __name__ == "__main__" and "--embed" in sys.argv:
    import json, re
    self_only, both = pick()
    html = open("index.html", encoding="utf-8").read()
    # the list keeps only the named ones (2026-11-17); the page groups them by lanes along with the pass zips
    found = {p for v in self_only.values() for p in v} | set(both)
    keep = ["1zs2zs", "1z3zs2zs", "12s21s", "12s43s", "1s34s2"]
    assert all(p in found for p in keep), [p for p in keep if p not in found]
    groups = ["14z3241z"] + keep
    # every pattern the search finds, for the All patterns page: {lanes: {beats: "p p p"}}
    walls = {"self": defaultdict(dict), "both": defaultdict(dict)}
    for k in range(1, 5):
        by = defaultdict(list)
        for disp, tm in search(k).values():
            if any(tm.values()): by[("both" if Z in disp else "self", len(disp))].append(disp)
        for (kind, n), v in sorted(by.items()):
            walls[kind][str(k)][str(n)] = " ".join(show(d) for d in sorted(v, key=key))
    block = ('<script id="zip2-patterns">\nconst ZIP2_LIST = ' + json.dumps(groups, separators=(",", ":")) +
             ';\nconst ALL_ZIPS2_SELF = ' + json.dumps(walls["self"], separators=(",", ":")) +
             ';\nconst ALL_ZIPS2_BOTH = ' + json.dumps(walls["both"], separators=(",", ":")) + ';\n</script>')
    if '<script id="zip2-patterns">' in html:
        html = re.sub(r'<script id="zip2-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    else:
        html = html.replace('<script id="zip-patterns">', block + '\n<script id="zip-patterns">', 1)
    open("index.html", "w", encoding="utf-8").write(html)
    print({kind: sum(len(x.split()) for d in w.values() for x in d.values()) for kind, w in walls.items()})
