"""Small independent checks for worked Codeforces crossover examples."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product
from random import Random


def check_bridge_sweep(rng):
    from heapq import heappop, heappush
    for _ in range(300):
        needs = [sorted(rng.sample(range(1, 7), 2)) for _ in range(rng.randint(1, 4))]
        lengths = [rng.randint(1, 6) for _ in range(rng.randint(1, 6))]
        expected = any(all(lo <= x <= hi for (lo, hi), x in zip(needs, picks))
                       for picks in permutations(lengths, len(needs)))
        waiting = []
        order = sorted(needs)
        i = filled = 0
        for x in sorted(lengths):
            while i < len(order) and order[i][0] <= x:
                heappush(waiting, order[i][1])
                i += 1
            if waiting:
                if heappop(waiting) < x:
                    break
                filled += 1
        assert expected == (filled == len(needs))


def check_checkpoint_segments():
    """Compare the aggregate with direct linear equations at all stations."""
    checks = 0
    for n in range(1, 5):
        for probs in product([Fraction(1, 3), Fraction(1, 2), Fraction(1)], repeat=n):
            for mask in range(1 << (n - 1)):
                starts = [0] + [i for i in range(1, n) if mask >> (i - 1) & 1] + [n]
                expected = Fraction()
                for start, end in zip(starts, starts[1:]):
                    prob, attempts = Fraction(1), Fraction()
                    for p in probs[start:end]:
                        attempts += prob
                        prob *= p
                    expected += attempts / prob
                rows = [[Fraction(int(i == j)) for j in range(n)] + [Fraction(1)] for i in range(n)]
                for i, p in enumerate(probs):
                    checkpoint = max(s for s in starts if s <= i)
                    rows[i][checkpoint] -= 1 - p
                    if i + 1 < n:
                        rows[i][i + 1] -= p
                for col in range(n):
                    pivot = next(i for i in range(col, n) if rows[i][col])
                    rows[col], rows[pivot] = rows[pivot], rows[col]
                    scale = rows[col][col]
                    rows[col] = [v / scale for v in rows[col]]
                    for i in range(n):
                        if i != col:
                            scale = rows[i][col]
                            rows[i] = [a - scale*b for a, b in zip(rows[i], rows[col])]
                assert rows[0][-1] == expected
                checks += 1
    return checks


def check_pile_parity():
    def mex(items):
        n = 0
        while n in items:
            n += 1
        return n

    def fast(n, k):
        if k % 2 == 0:
            return (0, 1, 2)[n] if n <= 2 else int(n % 2 == 0)
        if n < 5:
            return (0, 1, 0, 1, 2)[n]
        return 0 if n % 2 else 1 + (fast(n // 2, k) == 1)

    checks = 0
    for k in range(1, 8):
        table = [0]
        for n in range(1, 401):
            moves = [table[n - 1]]
            if n % 2 == 0:
                split = 0
                for _ in range(k):
                    split ^= table[n // 2]
                moves.append(split)
            table.append(mex(moves))
            assert table[n] == fast(n, k)
            checks += 1
    return checks


def check_numeric_cuts(rng):
    for _ in range(500):
        digits = "".join(str(rng.randrange(5)) for _ in range(rng.randint(1, 8)))
        low, high = sorted(rng.sample(range(46), 2))
        n = len(digits)
        expected = 0
        for mask in range(1 << (n - 1)):
            points = [0] + [i for i in range(1, n) if mask >> (i - 1) & 1] + [n]
            chunks = [digits[a:b] for a, b in zip(points, points[1:])]
            expected += all(str(int(c)) == c and low <= int(c) <= high for c in chunks)
        ways = [0]*(n+2)
        ways[0] = 1
        ways[1] = -1
        running = 0
        ls, rs = str(low), str(high)
        for i in range(n):
            running += ways[i]
            if digits[i] == "0":
                a, b = i+1, i+1 if low == 0 else i
            else:
                a, b = i + len(ls), min(n, i + len(rs))
                if a <= n and digits[i:a] < ls:
                    a += 1
                if b-i == len(rs) and digits[i:b] > rs:
                    b -= 1
            if a <= b:
                ways[a] += running
                ways[b+1] -= running
        assert expected == running + ways[n]


def robust_color_count(n, edges):
    """For a tiny graph, enumerate every possible two-color assignment."""
    return any(all(colors[u] != colors[v] for u, v in edges) for colors in product(range(2), repeat=n))


def check_parity_cuts(rng):
    for _ in range(400):
        n = rng.randint(2, 8)
        edges = [e for e in combinations(range(n), 2) if rng.random() < 0.36]
        adj = [[] for _ in range(n)]
        for i, (u, v) in enumerate(edges):
            adj[u].append((v, i))
            adj[v].append((u, i))
        parent = [-1]*n
        depth = [-1]*n
        tree = set()
        def dfs(v):
            for u, i in adj[v]:
                if depth[u] < 0:
                    depth[u] = depth[v]+1
                    parent[u] = i
                    tree.add(i)
                    dfs(u)
        for v in range(n):
            if depth[v] < 0:
                depth[v] = 0
                dfs(v)
        bad = set()
        bad_cross, good_cross = Counter(), Counter()
        for i, (u,v) in enumerate(edges):
            if i in tree:
                continue
            if depth[u] < depth[v]:
                u,v=v,u
            dest = good_cross
            if (depth[u]-depth[v]) % 2 == 0:
                bad.add(i)
                dest = bad_cross
            while u != v:
                e = parent[u]
                assert e >= 0
                dest[e] += 1
                a,b = edges[e]
                u = b if a == u else a
        found = {i for i in range(len(edges)) if not bad or
                 (i in tree and bad_cross[i] == len(bad) and good_cross[i] == 0) or
                 (i in bad and len(bad) == 1)}
        expected = {i for i in range(len(edges)) if robust_color_count(n, edges[:i]+edges[i+1:])}
        assert found == expected


if __name__ == "__main__":
    rng = Random(20261123)
    check_bridge_sweep(rng)
    check_numeric_cuts(rng)
    check_parity_cuts(rng)
    report = {"interval assignments": 300, "decimal cuts": 500, "odd-cycle repairs": 400,
              "checkpoint systems": check_checkpoint_segments(), "identical pile splits": check_pile_parity()}
    print(report)
    print(sum(report.values()), "checks passed")
