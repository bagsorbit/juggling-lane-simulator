"""Ping Pong patterns: one person, a hand at each end, three balls.

Every roll takes one beat, so only one ball is ever rolling and a lane can be rolled both ways, even one lane on
its own. The hands take turns; a ball rolled on beat i is caught by the other hand and rolled again on beat i + 3,
so that hand carries it from lane seq[i] to lane seq[i + 3].

Rules for the list: every lane 1..K is used; some lane is rolled by both hands (otherwise it is an ordinary
pattern); no hand move (hand, from lane, to lane) happens twice; not a shorter pattern repeated. Patterns that
only differ by starting roll, by being upside down, by being a mirror image or by running backwards count once.
"""
import itertools, sys

def period(seq):
    return len(seq) if len(seq) % 2 == 0 else 2 * len(seq)

def valid(seq, k):
    L = len(seq)
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
        for L in range(1, 7):
            r = search(k, L)
            if r:
                print(k, "lanes", L, "rolls:", len(r), " ".join(r[:30]))

if __name__ == "__main__" and "--embed" in sys.argv:
    import json, re
    # the list: everything of up to 5 rolls, plus the two 2-lane ones of 6; the wall has everything of up to 6
    groups, wall = [], {}
    for k in range(1, 5):
        items = []
        for L in range(1, 7):
            r = search(k, L)
            if r:
                wall.setdefault(str(k), {})[str(L)] = " ".join(r)
                if L <= 5 or k == 2:
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
    from notation import round_brackets
    open("index.html", "w", encoding="utf-8").write(round_brackets(html))
    print(sum(len(g["items"]) for g in groups), "in the list,", sum(len(v.split()) for d in wall.values() for v in d.values()), "on the wall")
