"""Find patterns in which lanes change direction.

A lane may be rolled from either end, as long as it is empty whenever it is
rolled the other way. Patterns can have an odd number of rolls: the hands still
take turns, so the second time round each lane is rolled by the other hand.

Rules: every lane is used; no hand move (lane -> next lane, by the same hand)
happens twice; the pattern is not a shorter one repeated; it works with at
least one ball count from 1 to 9. Patterns that only differ by starting roll,
by being upside down, by being a mirror image or by running backwards are
counted once.
"""
import itertools, sys
from collections import defaultdict

MAX_BALLS = 9

def works(seq, n):
    """True if no two balls ever meet head-on in a lane with n balls."""
    L = len(seq)
    for i in range(2 * L):
        for j in range(i + 1, i + 2 * n + 3):
            if seq[i % L] != seq[j % L] or (i - j) % 2 == 0:
                continue
            gap = (j - i) if n % 2 else 2 * (j // 2 - i // 2)
            if gap < n:
                return False
    return True

def reverses(seq):
    L = len(seq)
    side = {}
    for i in range(2 * L):
        if side.setdefault(seq[i % L], i % 2) != i % 2:
            return True
    return False

def valid(seq, k):
    L = len(seq)
    if set(seq) != set(range(1, k + 1)) or not reverses(seq):
        return False
    P = L if L % 2 == 0 else 2 * L
    if len({(seq[i % L], seq[(i + 1) % L], i % 2) for i in range(P)}) != P:
        return False
    for r in range(1, L):
        if L % r == 0 and seq[r:] + seq[:r] == seq and (r % 2 == 0 or L % 2 == 1 and False):
            return False
    for r in range(1, L):                      # a shorter pattern repeated
        if L % r == 0 and seq == seq[:r] * (L // r) and (r % 2 == L % 2 or r % 2 == 1):
            return False
    return True

def images(seq, k):
    L = len(seq)
    out = []
    for base in (seq, tuple(reversed(seq))):
        for s in (base, tuple(k + 1 - x for x in base)):
            for r in range(L):
                out.append(s[r:] + s[:r])
    return out

def search(k, max_len):
    found = {}
    for L in range(1, max_len + 1):
        for seq in itertools.product(range(1, k + 1), repeat=L):
            if seq[0] != 1 or not valid(seq, k):
                continue
            ims = images(seq, k)
            canon = min(ims)
            if canon in found:
                continue
            counts = [n for n in range(1, MAX_BALLS + 1) if works(seq, n)]
            if counts:
                found[canon] = (min(s for s in ims if s[0] == 1), counts)
    return found

def text(seq):
    return "".join(map(str, seq))

if __name__ == "__main__" and "--embed" not in sys.argv:
    for k in range(1, 5):
        found = search(k, 8)
        by_len = defaultdict(list)
        for d, counts in found.values():
            by_len[len(d)].append((d, counts))
        for L in sorted(by_len):
            rows = sorted(by_len[L])
            many = [r for r in rows if max(r[1]) >= 3]
            print(f"{k} lanes, {L} rolls: {len(rows)} patterns, {len(many)} of them work with 3 or more balls")
            if len(many) <= 14:
                for d, counts in many:
                    print(f"    {text(d):<9} balls: {' '.join(map(str, counts))}")


def embed(path="index.html"):
    """Rewrite the reversing-lane lists inside index.html and the expected ball counts used by the tests."""
    import json, re
    everything, expected = {}, {}
    for k, mx in ((3, 8), (4, 8), (5, 7)):
        by_len = defaultdict(list)
        for d, counts in search(k, mx).values():
            if len(d) <= 6:
                expected[text(d)] = counts
            if max(counts) >= 3:
                by_len[len(d)].append(text(d))
        everything[str(k)] = {str(L): " ".join(sorted(v)) for L, v in sorted(by_len.items())}
    for k in (1, 2):
        for d, counts in search(k, 6).values():
            expected[text(d)] = counts
    short = [
        {"group": "3 lanes", "items": ["123", "121323", "123132"]},
        # added by hand (2026-11-19): one person with the hands reaching across, or not taking turns (rows; see index.html)
        {"group": "Waves, hands reaching across", "items": ["123---|---123", "1234----|----1234", "12345-----|-----12345"]},
        {"group": "3 lanes, hands not taking turns", "items": ["3-31-3--|-2--2-21", "3-32-3--|-1--1-12"]},
        {"group": "4 lanes, hands not taking turns", "items": ["3--31-34--|-24--2--21", "4-32-3--|-1--1-12", "3-31-3--|-4--2-21"]},
        {"group": "5 lanes", "items": ["12345", "123145", "123543"]},   # trimmed at the user's request (2026-11-17); the rest stay on All patterns
        {"group": "6 lanes", "items": ["123456214365"]},                # Hex Double Helix, picked 2026-11-19
    ]
    block = ('<script id="reverse-patterns">\nconst REV_LIST = ' + json.dumps(short, separators=(",", ":")) +
             ';\nconst ALL_REVS = ' + json.dumps(everything, separators=(",", ":")) + ';\n</script>')
    html = open(path, encoding="utf-8").read()
    html, n = re.subn(r'<script id="reverse-patterns">.*?</script>', lambda m: block, html, flags=re.S)
    assert n == 1
    open(path, "w", encoding="utf-8").write(html)
    json.dump(expected, open("tests/reverse-counts.json", "w"), separators=(",", ":"))
    print("reverses:", {k: {b: len(v.split()) for b, v in d.items()} for k, d in everything.items()}, "expected:", len(expected))

if __name__ == "__main__" and "--embed" in sys.argv:
    embed()
