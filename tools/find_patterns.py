"""Find every lane pattern up to a beat limit.

Rules: hands alternate, so each lane is only ever rolled by one hand;
no hand move (lane -> next lane) is used twice in one loop; every lane is used.
Patterns that are the same after a change of starting beat, an upside-down
flip or a left-right mirror are counted once.
"""
import itertools, sys
from collections import defaultdict

def valid(seq, k):
    n = len(seq)
    if n % 2: return False
    side = {}
    for i, lane in enumerate(seq):
        if side.setdefault(lane, i % 2) != i % 2: return False
    if set(seq) != set(range(1, k + 1)): return False
    moves = [(seq[i], seq[(i + 1) % n]) for i in range(n)]
    return len(set(moves)) == n

def images(seq, k):
    n = len(seq)
    out = []
    for base in (seq, tuple(reversed(seq))):
        for s in (base, tuple(k + 1 - x for x in base)):
            for r in range(n):
                out.append(s[r:] + s[:r])
    return out

def canon(seq, k):
    return min(images(seq, k))

def display(seq, k):
    """Smallest equivalent form that starts on lane 1."""
    return min(s for s in images(seq, k) if s[0] == 1)

def diagram(seq, k):
    n = len(seq)
    best = None
    for flip in (False, True):
        for rev in (False, True):
            m = []
            for i in range(n):
                a, b = seq[i], seq[(i + 1) % n]
                if rev: a, b = b, a
                if flip: a, b = k + 1 - a, k + 1 - b
                m.append((a, b))
            m = tuple(sorted(m))
            if best is None or m < best: best = m
    return best

def search(k, max_beats):
    found = {}
    for n in range(2, max_beats + 1, 2):
        for rest in itertools.product(range(1, k + 1), repeat=n - 1):
            seq = (1,) + rest
            if valid(seq, k):
                found.setdefault(canon(seq, k), display(seq, k))
    return found

if __name__ == "__main__":
    max_beats = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    for k in range(2, 7):
        found = search(k, max_beats)
        groups = defaultdict(list)
        for c, d in found.items():
            groups[diagram(d, k)].append("".join(map(str, d)))
        print(f"{k} lanes, up to {max_beats} beats: {len(groups)} diagrams, {len(found)} hand orders")
        for g in sorted(groups.values(), key=lambda v: (len(v[0]), sorted(v)[0])):
            print("   ", " / ".join(sorted(g)))


def embed(path="index.html", max_beats=8):
    """Rewrite the list of every pattern inside index.html (the "All patterns" pop-up)."""
    import json, re
    data = {}
    named = set(re.findall(r"\['[^']+', '(\d+)'\]", open(path, encoding="utf-8").read()))
    for k in range(2, 7):
        by_beats = defaultdict(list)
        for d in search(k, max_beats).values():
            # where a pattern has a name in the list, show it spelled the way the list spells it
            same = {"".join(map(str, im)) for im in images(d, k)}
            text = min(same & named) if same & named else "".join(map(str, d))
            by_beats[str(len(d))].append(text)
        data[str(k)] = {b: " ".join(sorted(v)) for b, v in sorted(by_beats.items())}
    html = open(path, encoding="utf-8").read()
    block = '<script id="all-patterns">\nconst ALL_PATTERNS = ' + json.dumps(data, separators=(",", ":")) + ';\n</script>'
    html, n = re.subn(r'<script id="all-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    assert n == 1
    open(path, "w", encoding="utf-8").write(html)
    print({k: {b: len(v.split()) for b, v in d.items()} for k, d in data.items()})
