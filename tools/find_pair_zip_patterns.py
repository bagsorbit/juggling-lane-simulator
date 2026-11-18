"""Two-person zip passes two at once: patterns with [zz].

Written like the pair patterns: [12][zz] means the right person rolls lanes 1 and 2
together, then the left person hands both balls back across the middle at once.
Each position in the brackets traces its own path, which is an ordinary zip pattern
(z = a pass to the other person). The two paths must have the same timing, so each
pair of balls moves together, and where they share a lane a ball on one path must
never catch up with a ball on the other.

Rules for the search: an even number of brackets; at least one [zz]; each lane is
only rolled from one end; every lane 1..K is used; on each path no hand move happens
twice; not a shorter pattern repeated. Patterns that only differ by starting bracket,
by being upside down, or by which ball is written first are counted once.

The list holds a "Sync" version of each named one-person zip pattern: the pattern
itself as the first path, and the same pattern on other lanes as the second.
"""
import itertools, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from find_zip_patterns import timing, Z

BALLS = (1, 2, 3, 4)            # balls on each path, so 2 to 8 in all

def show(seq):
    return "".join("[zz]" if x == Z else f"[{x[0]}{x[1]}]" for x in seq)

def paths(seq):
    return [tuple(Z if x == Z else x[s] for x in seq) for s in (0, 1)]

def counts(seq):
    """Ball counts (in all) that work."""
    s0, s1 = paths(seq)
    n = len(seq)
    out = []
    for m in BALLS:
        v = timing(s0, m)
        if not v or timing(s1, m) != v:
            continue
        ok = True
        for i in range(n):
            for j in range(n):
                if i == j or s0[i] == Z or s0[i] != s1[j]:
                    continue
                lo, hi = min(i, j), max(i, j)
                gap = hi - lo
                if not (v[lo] - v[hi] < gap and v[hi] - v[lo] < n - gap):
                    ok = False
        if ok:
            out.append(2 * m)
    return out

def sides_ok(seq):
    side = {}
    for i, x in enumerate(seq):
        if x == Z:
            continue
        for lane in x:
            if side.setdefault(lane, i % 2) != i % 2:
                return False
    return True

def search(k, n):
    lanes = range(1, k + 1)
    brs = [Z] + [(a, b) for a in lanes for b in lanes if a != b]
    found = {}
    for seq in itertools.product(brs, repeat=n):
        if seq[0] == Z or Z not in seq or not sides_ok(seq):
            continue
        if {l for x in seq if x != Z for l in x} != set(lanes):
            continue
        if any(len({(s[i], s[(i + 1) % n], i % 2) for i in range(n)}) != n for s in paths(seq)):
            continue
        if any(n % r == 0 and seq[r:] + seq[:r] == seq for r in range(2, n, 2)):
            continue
        ims = []
        for flip in (False, True):
            for swap in (False, True):
                t = tuple(x if x == Z else ((k + 1 - x[0], k + 1 - x[1]) if flip else x) for x in seq)
                t = tuple(x if x == Z else ((x[1], x[0]) if swap else x) for x in t)
                ims += [t[r:] + t[:r] for r in range(0, n, 2)]
        canon = min(ims, key=lambda t: tuple((9, 9) if x == Z else x for x in t))
        if canon in found:
            continue
        c = counts(seq)
        if c:
            found[canon] = (min((t for t in ims if t[0] != Z), key=lambda t: tuple((9, 9) if x == Z else x for x in t)), c)
    return found

def sync(text):
    """The best two-at-once version of a one-person zip pattern: the pattern on the first path,
    the same pattern on other lanes on the second (as few lanes as possible, then the most balls)."""
    s0 = tuple(Z if c == "z" else int(c) for c in text)
    k = max(s0)
    for total in range(max(k, 2), 7):                   # as few lanes as possible
        best = None
        for f in itertools.permutations(range(1, total + 1), k):
            if any(f[l - 1] == l for l in range(1, k + 1)):
                continue                                   # each ball of a pair in its own lane
            s1 = tuple(Z if x == Z else f[x - 1] for x in s0)
            seq = tuple(Z if a == Z else (a, b) for a, b in zip(s0, s1))
            if not sides_ok(seq) or {l for x in seq if x != Z for l in x} != set(range(1, total + 1)):
                continue
            c = counts(seq)
            if c and (best is None or (max(c), len(c)) > (max(best[1]), len(best[1]))):
                best = (seq, c)
        if best:
            return best
    return None

SOURCES = ["1z", "121z", "1z2z", "12zz", "12z21z", "123z", "12z3", "13z2", "1z2z3z", "121z13", "12z213",
           "12321z", "1232z2", "13z21z", "1z2z3z4z", "12134z", "12143z", "1213z4", "13234z", "14z3241z"]

if __name__ == "__main__" and "--embed" not in sys.argv:
    for t in SOURCES:
        b = sync(t)
        print(f"{t:<10}", (show(b[0]), b[1]) if b else "none")
    for k, n in ((2, 2), (2, 4), (3, 4), (4, 4), (2, 6), (3, 6), (4, 6)):
        print(k, "lanes", n, "brackets:", len(search(k, n)))

if __name__ == "__main__" and "--embed" in sys.argv:
    import json, re
    picks = []
    for t in SOURCES:
        b = sync(t)
        if b:
            picks.append([t, show(b[0])])
    wall = {}
    for k, n in ((2, 2), (2, 4), (3, 4), (4, 4), (2, 6), (3, 6), (4, 6)):
        found = search(k, n)
        if found:
            wall.setdefault(str(k), {})[str(2 * n)] = " ".join(sorted(show(d) for d, c in found.values()))
    for src, p in picks:                                   # the Sync versions go on the wall too
        k = str(max(int(c) for c in p if c.isdigit()))
        n = str(2 * p.count("["))
        have = wall.setdefault(k, {}).get(n, "")
        if p not in have.split():
            wall[k][n] = (have + " " + p).strip()
    # half-zips (one ball of a pair rolls while the other is handed across), named by the user 2026-11-17.
    # Only these go on the wall: the full search finds about 1,800, too many to show.
    half = ["[1z][z2]", "[13][2z][13][z2]", "[1z][2z][z3][z2]", "[1z][z2][4z][z3]"]
    for p in half:
        k, n = str(max(int(c) for c in p if c.isdigit())), str(2 * p.count("["))
        wall.setdefault(k, {})[n] = (wall[k].get(n, "") + " " + p).strip()
    block = ('<script id="pair-zip-patterns">\nconst PAIR_ZIP_LIST = ' + json.dumps(picks, separators=(",", ":")) +
             ';\nconst HALF_ZIP_LIST = ' + json.dumps(half) + ';\nconst ALL_PAIR_ZIPS = ' + json.dumps(wall, separators=(",", ":")) + ';\n</script>')
    html = open("index.html", encoding="utf-8").read()
    if '<script id="pair-zip-patterns">' in html:
        html = re.sub(r'<script id="pair-zip-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    else:
        html = html.replace('<script id="zip2-patterns">', block + '\n<script id="zip2-patterns">', 1)
    open("index.html", "w", encoding="utf-8").write(html)
    print(len(picks), "in the list,", sum(len(v.split()) for d in wall.values() for v in d.values()), "on the wall")
    for src, p in picks:
        print(f"  {src:<10} {p}")
