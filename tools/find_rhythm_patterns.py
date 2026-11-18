"""Find two-person patterns where each person keeps their own rhythm.

Each beat, each person either rests (-), rolls one lane, or rolls two lanes
together. They do not have to take turns. Every ball rolls at the same speed;
a ball that arrives before it is needed waits in a hand, and a person can hold
at most two balls. Each hand always rolls the ball that has waited longest.

Rules: each lane is only ever rolled from one end; every lane is used; both
people roll the same number of balls per loop; the pattern has at least one
pair and at least one single roll; it is not a shorter pattern repeated.
Patterns that only differ by starting beat, by being upside down or by being a
mirror image are counted once.
"""
import itertools, sys
from collections import defaultdict

def show_row(row):
    return " ".join("-" if not a else str(a[0]) if len(a) == 1 else f"[{a[0]}{a[1]}]" for a in row)

def ball_counts(R, L, max_travel=6, max_balls=9):
    """For each travel time D (in beats), the ball count that works, and whether any ball has to wait."""
    P = len(R)
    out = {}
    def cum(row, t):                       # balls thrown up to and including beat t
        full, rem = divmod(t, P)
        per = sum(len(a) for a in row)
        return full * per + sum(len(row[i]) for i in range(rem + 1))
    for D in range(1, max_travel + 1):
        stock = []
        ok, waits = True, False
        for me, other in ((L, R), (R, L)):
            c = max(cum(me, t) - cum(other, t - D) for t in range(P, 2 * P))
            for t in range(P, 2 * P):
                held = c + cum(other, t - D) - cum(me, t - 1)
                if held > 2: ok = False
                if held > len(me[t % P]): waits = True
            stock.append(c)
        if not ok: continue
        # stock[i] already counts every ball that person has been sent and not yet rolled back, including the ones
        # still on their way, so the two stocks together are all the balls
        n = stock[0] + stock[1]
        if 1 <= n <= max_balls:
            out[n] = (D, waits)
    return out

def valid(R, L, k):
    P = len(R)
    if sum(len(a) for a in R) != sum(len(a) for a in L): return False
    acts = [a for a in R + L if a]
    if not acts: return False
    kinds = {len(a) for a in acts}
    if kinds != {1, 2}: return False
    if {x for a in acts for x in a} != set(range(1, k + 1)): return False
    for r in range(1, P):
        if P % r == 0 and R[r:] + R[:r] == R and L[r:] + L[:r] == L: return False
    return True

def images(R, L, k):
    out = []
    for a, b in ((R, L), (L, R)):
        for flip in (False, True):
            x, y = a, b
            if flip:
                f = lambda row: tuple(tuple(sorted(k + 1 - v for v in act)) for act in row)
                x, y = f(x), f(y)
            for r in range(len(x)):
                out.append((x[r:] + x[:r], y[r:] + y[:r]))
    return out

def search(k, P):
    found = {}
    lanes = list(range(1, k + 1))
    for size in range(1, k):
        for mine in itertools.combinations(lanes, size):
            theirs = tuple(x for x in lanes if x not in mine)
            def acts(ls):
                return [()] + [(a,) for a in ls] + list(itertools.combinations(ls, 2))
            for R in itertools.product(acts(mine), repeat=P):
                rolls = sum(len(a) for a in R)
                if not rolls: continue
                for L in itertools.product(acts(theirs), repeat=P):
                    if sum(len(a) for a in L) != rolls or not valid(R, L, k): continue
                    canon = min(images(R, L, k))
                    if canon in found: continue
                    counts = ball_counts(*canon)
                    if counts: found[canon] = counts
    return found

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k, P in ((3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4)):
        found = search(k, P)
        waiting = {c: v for c, v in found.items() if any(w for d, w in v.values())}
        print(f"\n{k} lanes, {P} beats: {len(found)} patterns work, {len(waiting)} of them have balls waiting in a hand")
        for (R, L), counts in sorted(waiting.items())[:10]:
            cs = ", ".join(f"{n}{'*' if w else ''}" for n, (d, w) in sorted(counts.items()))
            print(f"   Right: {show_row(R):<16} Left: {show_row(L):<16} balls: {cs}")


def steady(row):
    """A person only rests on the beat after rolling a pair, and always rests then."""
    P = len(row)
    for i, a in enumerate(row):
        if len(a) == 2 and row[(i + 1) % P] != (): return False
        if a == () and len(row[i - 1]) != 2: return False
    return True

def text(R, L):
    row = lambda r: "".join("-" if not a else str(a[0]) if len(a) == 1 else f"[{a[0]}{a[1]}]" for a in r)
    return row(R) + "|" + row(L)

def display(R, L, k):
    """The same pattern written to start on lane 1 with the first person, where possible."""
    def key(im):
        a, b = im
        return (1 not in {x for act in a for x in act}, a[0] == (), 1 not in a[0], text(a, b))
    return min(images(R, L, k), key=key)

def symmetric(R, L, k):
    ims = images(R, L, k)
    P = len(R)
    return any(im == (R, L) for i, im in enumerate(ims) if i >= P)      # the first P images are plain rotations

def embed(path="index.html"):
    """Rewrite the own-rhythm lists inside index.html and the expected ball counts used by the tests."""
    import json, re
    everything, expected, groups = {}, {}, []
    picked = {}
    for k, P in ((3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4)):
        rows = []
        for (R, L), counts in search(k, P).items():
            if not (steady(R) and steady(L)): continue
            d = display(R, L, k)
            t = text(*d)
            expected[t] = {str(n): v[0] for n, v in counts.items()}
            rows.append((not symmetric(R, L, k), 5 not in counts, t))
        rows.sort()
        everything.setdefault(str(k), {})[str(P)] = " ".join(sorted(r[2] for r in rows))
        picked[(k, P)] = [r[2] for r in rows]
    groups.append({"group": "3 lanes", "items": picked[(3, 2)] + picked[(3, 3)] + picked[(3, 4)]})
    groups.append({"group": "4 lanes, 2 beats", "items": picked[(4, 2)]})
    groups.append({"group": "4 lanes, 3 beats", "items": picked[(4, 3)][:6]})
    groups.append({"group": "4 lanes, 4 beats", "items": picked[(4, 4)][:6]})
    # Lanes that change direction (rolled from both ends), added by hand 2026-11-17 and checked in the app's engine.
    # Waves: one person rolls every lane in turn, the other starts as the first ball arrives and sends them all back.
    # Only these go on the All patterns wall, not every reversing pattern the search could find.
    waves = {k: "".join(map(str, range(1, k + 1))) + "-" * k + "|" + "-" * k + "".join(map(str, range(1, k + 1))) for k in (3, 4, 5)}   # the 6-lane one was dropped at the user's request
    both_ways = {"3": ["111[12]|3[23]33", "-11[12]|3[23]-3"], "4": ["1234|3412", "1324|2413", "1243|4312", "-124|-431"]}
    # The waves (Snakes) and the user's Funnel are written this way but live in 2 people + Reverses, not Mixed
    # (user, 2026-11-17): they go in ROW_REV_WALL for that mode's wall, and stay in the expected counts for the tests.
    fold = "[15][24]3---|---[15][24]3"
    for k, w in waves.items():
        expected[w] = {str(k): k}
    expected[fold] = {"5": 3}
    row_rev_wall = {"3": {"6": waves[3]}, "4": {"8": waves[4]}, "5": {"10": waves[5] + " " + fold}}
    for k, ps in both_ways.items():
        everything[k]["4"] = everything[k]["4"] + " " + " ".join(ps)
    expected.update({"111[12]|3[23]33": {"3": 1, "5": 2}, "-11[12]|3[23]-3": {"4": 2},
                     "1234|3412": {"2": 1, "4": 2}, "1324|2413": {"2": 1, "4": 2}, "1243|4312": {"2": 1, "4": 2}, "-124|-431": {"2": 1, "4": 2}})
    # The list only shows the named patterns (user, 2026-11-17), one group per number of lanes; the rest stay on the wall.
    groups = [
        {"group": "3 lanes", "items": ["[13]-|22", "11|-[23]", "111[12]|3[23]33"]},
        {"group": "4 lanes", "items": ["12|-[34]", "13|-[24]", "[14]-|23", "1[12]-|4[34]-", "111|-2[34]"]},
    ]
    on_wall = {p for d in everything.values() for v in d.values() for p in v.split()}
    assert all(p in on_wall for g in groups for p in g["items"]), [p for g in groups for p in g["items"] if p not in on_wall]
    top = ["[13]-|22", "111|-2[34]", "111[12]|3[23]33", "1[12]-|4[34]-"]   # the user's picks, 2026-11-17
    assert all(any(p in g["items"] for g in groups) for p in top), top
    block = ('<script id="mixed-patterns">\nconst MIX_LIST = ' + json.dumps(groups, separators=(",", ":")) +
             ';\nconst MIX_TOP = ' + json.dumps(top) + ';\nconst ALL_MIX = ' + json.dumps(everything, separators=(",", ":")) +
             ';\nconst ROW_REV_WALL = ' + json.dumps(row_rev_wall, separators=(",", ":")) + ';\n</script>')
    html = open(path, encoding="utf-8").read()
    html, n = re.subn(r'<script id="mixed-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    assert n == 1
    open(path, "w", encoding="utf-8").write(html)
    json.dump(expected, open("tests/rhythm-counts.json", "w"), separators=(",", ":"))
    print("rhythm:", {k: {b: len(v.split()) for b, v in d.items()} for k, d in everything.items()})
    print("top:", top)
    for g in groups: print(g["group"], g["items"])

if __name__ == "__main__" and "--embed" in sys.argv:
    embed()
