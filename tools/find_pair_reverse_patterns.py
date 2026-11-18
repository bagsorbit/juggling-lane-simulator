"""Two-person pair patterns in which lanes change direction.

Written with brackets, like the pair patterns: [12][34][56] means the right
person rolls lanes 1 and 2 together, then the left person rolls 3 and 4, then the
right person 5 and 6. With an odd number of brackets the second time round each
bracket is rolled by the other person, so every lane changes direction. With an
even number, lanes change direction where the same lane turns up at both ends, as
in [12][34][34][12]: two pairs going back and forth, each on its own two lanes.

Each position in the brackets traces its own path (a "track"), which is an
ordinary reversing pattern with half the balls. Rules: some lane is rolled from both ends;
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
                # with an even number of brackets, shifting by one changes who rolls what (and, when both
                # people roll at once, which brackets go together), so only shift by whole rounds of two
                for r in range(0, len(sw), 1 if len(sw) % 2 else 2):
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
    # even numbers of brackets: lanes reverse where a lane turns up at both ends. On 4 and 5 lanes only the 4-bracket
    # ones that take 4 balls are kept (the rest only work with 2). Each 4-lane one is two pairs going back and forth on
    # their own lanes; the ball order inside the brackets makes no difference there, so one of each is listed.
    even = {k: sorted(show(d) for d, c in search(k, (4,)).values() if max(c) >= 4) for k in (4, 5)}
    picks4 = ["[12][34][34][12]", "[13][24][24][13]", "[14][23][23][14]"]
    assert all(p in even[4] for p in picks4), (picks4, even[4])
    # Double loops that change direction, asked for by the user: each ball goes out on one lane and back on the other,
    # then round the other way. They repeat a hand move (each person rolls the same pair twice running), so the search's
    # no-repeat rule leaves them out; they were checked in the app's engine with 2 and 4 balls.
    loops = ["[12][34][12][34][34][12][34][12]", "[13][24][13][24][24][13][24][13]", "[14][23][14][23][23][14][23][14]"]
    # the list keeps only the user's named ones (2026-11-17); everything above stays on the wall
    groups = [{"group": "Two at once, 4 lanes", "items": ["[12][34][34][12]", "[13][24][24][13]", "[14][23][14][23][23][14][23][14]"]},
              {"group": "Two at once, 6 lanes", "items": ["[12][34][56]", "[13][25][46]", "[16][25][43]"]}]
    # Hot Dog Sync and Space Invader Sync: the one-person pattern on lanes 1-3, mirrored on 4-6 (kept by the user, 2026-11-17)
    syncs = ["[16][25][16][34][25][34]", "[16][25][34][16][34][25]"]
    assert all(max(counts(tuple((int(p[i]), int(p[i + 1])) for i in range(1, len(p), 4)))) == 6 for p in syncs)
    groups[1]["items"] += syncs
    # Twin Dogs: the two paths share lanes (allowed since 2026-11-17, kept by the user)
    even[4] = sorted(set(even[4]) | {"[14][23][23][41]", "[14][23][32][14]"})   # Twin Dogs, Quarter Pounder
    wall = {"4": {"4": " ".join(even[4]), "8": " ".join(loops)}, "5": {"4": " ".join(even[5])}, "6": {"3": every, "6": " ".join(syncs)}}
    block = ('<script id="rev-pair-patterns">\nconst REV_PAIR_LIST = ' +
             json.dumps(groups, separators=(",", ":")) +
             ';\nconst ALL_REV_PAIRS = ' + json.dumps(wall, separators=(",", ":")) + ';\n</script>')
    html = open("index.html", encoding="utf-8").read()
    if '<script id="rev-pair-patterns">' in html:
        html = re.sub(r'<script id="rev-pair-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    else:
        html = html.replace('<script id="reverse-patterns">', block + '\n<script id="reverse-patterns">', 1)
    open("index.html", "w", encoding="utf-8").write(html)
    print(sum(len(v.split()) for d in wall.values() for v in d.values()), "on the wall,", sum(len(g["items"]) for g in groups), "in the list")
