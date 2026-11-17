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

if __name__ == "__main__":
    for k, P in ((3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4)):
        found = search(k, P)
        waiting = {c: v for c, v in found.items() if any(w for d, w in v.values())}
        print(f"\n{k} lanes, {P} beats: {len(found)} patterns work, {len(waiting)} of them have balls waiting in a hand")
        for (R, L), counts in sorted(waiting.items())[:10]:
            cs = ", ".join(f"{n}{'*' if w else ''}" for n, (d, w) in sorted(counts.items()))
            print(f"   Right: {show_row(R):<16} Left: {show_row(L):<16} balls: {cs}")
