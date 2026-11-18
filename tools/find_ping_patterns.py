"""Ping Pong patterns: one person, a hand at each end, three balls.

A hand places its ball a little way up a lane just after the ball coming towards it has rolled past, then jumps
back and grabs that ball before it reaches the end, so a lane can be rolled both ways, even one lane on its own.
The hands take turns; a ball rolled on beat i is grabbed by the other hand and rolled again on beat i + 3, so that
hand carries it from lane seq[i] to lane seq[i + 3]. The grab has to be quick, so each roll is in the same lane as
the roll before it or the lane next to it (user, 2026-11-18).

Rules for the list: each roll is in the same lane as the one before or next to it; every lane 1..K is used; some lane is rolled by both hands (otherwise it is an ordinary
pattern); no hand move (hand, from lane, to lane) happens twice; not a shorter pattern repeated. Patterns that
only differ by starting roll, by being upside down, by being a mirror image or by running backwards count once.
"""
import itertools, sys

def period(seq):
    return len(seq) if len(seq) % 2 == 0 else 2 * len(seq)

def valid(seq, k):
    L = len(seq)
    if any(abs(seq[i] - seq[(i + 1) % L]) > 1 for i in range(L)):
        return False
    if set(seq) != set(range(1, k + 1)):
        return False
    if any(L % d == 0 and seq == seq[d:] + seq[:d] for d in range(1, L)):
        return False
    P = period(seq)
    hands = {}
    for i in range(P):
        hands.setdefault(seq[i % L], set()).add(i % 2)
    if not any(len(h) == 2 for h in hands.values()):
        return False
    moves = [((i + 1) % 2, seq[i % L], seq[(i + 3) % L]) for i in range(P)]
    return len(set(moves)) == len(moves)

def images(seq, k):
    out = []
    for base in (seq, tuple(reversed(seq))):
        for s in (base, tuple(k + 1 - x for x in base)):
            out += [s[r:] + s[:r] for r in range(len(s))]
    return out

def search(k, L):
    found = {}
    for seq in itertools.product(range(1, k + 1), repeat=L):
        if seq[0] != 1 or not valid(seq, k):
            continue
        canon = min(images(seq, k))
        if canon not in found:
            found[canon] = min((t for t in images(seq, k) if t[0] == 1))
    return sorted("".join(map(str, s)) for s in found.values())

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k in range(1, 5):
        for L in range(1, 9):
            r = search(k, L)
            if r:
                print(k, "lanes", L, "rolls:", len(r), " ".join(r[:30]))

if __name__ == "__main__" and "--embed" in sys.argv:
    import json, re
    # the list and the wall both have everything of up to 8 rolls (there are only a few)
    groups, wall = [], {}
    for k in range(1, 5):
        items = []
        for L in range(1, 9):
            r = search(k, L)
            if r:
                wall.setdefault(str(k), {})[str(L)] = " ".join(r)
                items += r
        if items:
            groups.append({"group": str(k) + (" lane" if k == 1 else " lanes"), "items": items})
    block = ('<script id="ping-patterns">\nconst PING_LIST = ' + json.dumps(groups, separators=(",", ":")) +
             ';\nconst ALL_PING = ' + json.dumps(wall, separators=(",", ":")) + ';\n</script>')
    html = open("index.html", encoding="utf-8").read()
    if '<script id="ping-patterns">' in html:
        html = re.sub(r'<script id="ping-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    else:
        html = html.replace('<script id="mixed-patterns">', block + '\n<script id="mixed-patterns">', 1)
    open("index.html", "w", encoding="utf-8").write(html)
    print(sum(len(g["items"]) for g in groups), "in the list,", sum(len(v.split()) for d in wall.values() for v in d.values()), "on the wall")
