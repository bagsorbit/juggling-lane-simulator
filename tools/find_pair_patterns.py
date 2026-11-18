"""Find two-person patterns where each person rolls two balls at once.

Written with brackets: [14][23] means the right person rolls lanes 1 and 4
together, then the left person rolls lanes 2 and 3 together. The order inside
the brackets says which ball goes where: the first ball of one bracket becomes
the first ball of the next, so each position in the brackets traces its own path.

Rules: the two ends take turns; each lane is only ever rolled from one end;
every lane is used; within one path no hand move happens twice; the pattern is
not a shorter pattern repeated. Patterns that only differ by starting bracket,
by being upside down, by being a mirror image, or by which ball is written
first are counted once.
"""
import itertools, sys
from collections import defaultdict

def show(seq):
    return "".join(f"[{a}{b}]" for a, b in seq)

def valid(seq, k):
    n = len(seq)
    side, used = {}, set()
    for i, br in enumerate(seq):
        if br[0] == br[1]:
            return False
        for lane in br:
            used.add(lane)
            if side.setdefault(lane, i % 2) != i % 2:
                return False
    if used != set(range(1, k + 1)):
        return False
    for s in (0, 1):
        moves = {(seq[i][s], seq[(i + 1) % n][s]) for i in range(n)}
        if len(moves) != n:
            return False
    for r in range(2, n, 2):
        if n % r == 0 and seq[r:] + seq[:r] == seq:
            return False
    return True

def images(seq, k):
    n = len(seq)
    out = []
    for flip in (False, True):
        for swap in (False, True):
            s = seq
            if flip: s = tuple((k + 1 - a, k + 1 - b) for a, b in s)
            if swap: s = tuple((b, a) for a, b in s)
            for r in range(n):
                out.append(s[r:] + s[:r])
    return out

def paths(seq):
    """The two paths, each as a plain one-person pattern."""
    return ["".join(str(br[s]) for br in seq) for s in (0, 1)]

def loops(seq):
    """How many separate loops the balls make when there is one pair."""
    n = len(seq)
    seen, count = set(), 0
    for start in ((0, 0), (0, 1)):
        if start in seen: continue
        count += 1
        i, s = start
        while (i, s) not in seen:
            seen.add((i, s)); i = (i + 1) % n
    return count

def search(k, max_brackets):
    found = {}
    lanes = range(1, k + 1)
    brackets = [(a, b) for a in lanes for b in lanes if a != b]
    for n in range(2, max_brackets + 1, 2):
        for rest in itertools.product(brackets, repeat=n - 1):
            for first in ((1, b) for b in lanes if b != 1):
                seq = (first,) + rest
                if not valid(seq, k): continue
                ims = images(seq, k)
                canon = min(ims)
                if canon in found: continue
                found[canon] = min(s for s in ims if s[0][0] == 1)
    return found

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k, mx in ((4, 6), (5, 4), (6, 4)):
        found = search(k, mx)
        by_len = defaultdict(list)
        for d in found.values():
            by_len[len(d)].append(d)
        for n in sorted(by_len):
            rows = sorted(by_len[n])
            print(f"\n{k} lanes, {n} brackets ({2 * n} rolls): {len(rows)} patterns")
            if len(rows) <= 40:
                for d in rows:
                    p = paths(d)
                    twin = p[1] in [p[0][r:] + p[0][:r] for r in range(len(p[0]))]
                    print(f"  {show(d):<26} paths {p[0]} and {p[1]}{'  (same path, out of step)' if twin else ''}")


NAMES = {"[13][24][31][42]": "Scarf Sync", "[14][23][41][32]": "Mobius Sync", "[12][34][21][43]": "Loop de Loop Sync",
         "[12][34]": "Paired Loops", "[14][32]": "Criss Cross", "[14][23][14][32]": "Hot Cross Buns"}

def embed(path="index.html"):
    """Rewrite the two-person pair lists inside index.html."""
    import json, re
    four = defaultdict(list)
    for d in search(4, 6).values():
        four[len(d)].append(show(d))
    five = defaultdict(list)
    for d in search(5, 4).values():
        five[len(d)].append(show(d))
    short = [{"group": f"Two at once, {2 * n} rolls", "items": [[NAMES.get(t, ""), t] for t in sorted(v)]} for n, v in sorted(four.items())]
    everything = {"4": {str(2 * n): " ".join(sorted(v)) for n, v in sorted(four.items())},
                  "5": {str(2 * n): " ".join(sorted(v)) for n, v in sorted(five.items())}}
    block = ('<script id="pair-patterns">\nconst PAIR_LIST = ' + json.dumps(short, separators=(",", ":")) +
             ';\nconst ALL_PAIRS = ' + json.dumps(everything, separators=(",", ":")) + ';\n</script>')
    html = open(path, encoding="utf-8").read()
    html, n = re.subn(r'<script id="pair-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    assert n == 1
    open(path, "w", encoding="utf-8").write(html)
    print("pairs:", {k: {b: len(v.split()) for b, v in d.items()} for k, d in everything.items()})

if __name__ == "__main__" and "--embed" in sys.argv:
    embed()
