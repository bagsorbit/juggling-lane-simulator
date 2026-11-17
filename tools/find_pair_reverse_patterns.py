"""Two-person pair patterns in which lanes change direction.

Written with brackets, like the pair patterns: [12][34][56] means the right
person rolls lanes 1 and 2 together, then the left person rolls 3 and 4, then the
right person 5 and 6. With an odd number of brackets the second time round each
bracket is rolled by the other person, so every lane changes direction.

Each position in the brackets traces its own path (a "track"), which is an
ordinary reversing pattern with half the balls. Rules: an odd number of brackets;
every lane 1..K is used; the two tracks use different lanes (so balls on one
track never meet balls on the other); each track follows the one-person reversing
rules (no hand move twice, not a shorter pattern repeated, balls never meet
head-on); the pattern works with at least 2 balls. Patterns that only differ by
starting bracket, by being upside down, by being a mirror image, by running
backwards or by which ball is written first are counted once.
"""
import itertools, sys
from collections import defaultdict
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from find_reverse_patterns import works, valid as track_valid, MAX_BALLS

def show(seq):
    return "".join(f"[{a}{b}]" for a, b in seq)

def relabel(track):
    m = {l: i + 1 for i, l in enumerate(sorted(set(track)))}
    return tuple(m[x] for x in track), len(m)

def valid(seq, k):
    t0, t1 = tuple(b[0] for b in seq), tuple(b[1] for b in seq)
    if set(t0) & set(t1) or set(t0) | set(t1) != set(range(1, k + 1)):
        return False
    return all(track_valid(*relabel(t)) for t in (t0, t1))

def counts(seq):
    t0, t1 = tuple(b[0] for b in seq), tuple(b[1] for b in seq)
    return [2 * m for m in range(1, MAX_BALLS // 2 + 1) if works(t0, m) and works(t1, m)]

def images(seq, k):
    out = []
    for base in (seq, tuple(reversed(seq))):
        for s in (base, tuple((k + 1 - a, k + 1 - b) for a, b in base)):
            for sw in (s, tuple((b, a) for a, b in s)):
                for r in range(len(sw)):
                    out.append(sw[r:] + sw[:r])
    return out

def search(k, lengths=(3, 5)):
    found = {}
    pairs = [(a, b) for a in range(1, k + 1) for b in range(1, k + 1) if a != b]
    for L in lengths:
        for seq in itertools.product(pairs, repeat=L):
            if 1 not in seq[0] or not valid(seq, k):
                continue
            ims = images(seq, k)
            canon = min(ims)
            if canon in found:
                continue
            c = counts(seq)
            if c:
                found[canon] = (min(ims, key=lambda s: (s[0][0] != 1, s)), c)
    return found

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k in (4, 5, 6):
        res = search(k, (3, 5) if k < 6 else (3,))
        by = defaultdict(list)
        for disp, c in res.values():
            by[len(disp)].append((show(disp), c))
        for L in sorted(by):
            print(f"{k} lanes, {L} brackets: {len(by[L])}")
            for t, c in sorted(by[L])[:40]:
                print("  ", t, c)

if __name__ == "__main__" and "--embed" in sys.argv:
    import json, re
    found = search(6, (3,))
    every = " ".join(sorted(show(d) for d, c in found.values()))
    picks = ["[12][34][56]", "[12][34][65]", "[14][25][36]", "[13][25][46]",
             "[16][25][34]", "[16][25][43]", "[16][34][52]", "[16][43][52]"]
    assert all(p in every.split() for p in picks), picks
    block = ('<script id="rev-pair-patterns">\nconst REV_PAIR_LIST = ' +
             json.dumps([{"group": "Two at once, 6 lanes", "items": picks}], separators=(",", ":")) +
             ';\nconst ALL_REV_PAIRS = ' + json.dumps({"6": {"3": every}}, separators=(",", ":")) + ';\n</script>')
    html = open("index.html", encoding="utf-8").read()
    if '<script id="rev-pair-patterns">' in html:
        html = re.sub(r'<script id="rev-pair-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    else:
        html = html.replace('<script id="reverse-patterns">', block + '\n<script id="reverse-patterns">', 1)
    open("index.html", "w", encoding="utf-8").write(html)
    print(len(every.split()), "on the wall,", len(picks), "in the list")
