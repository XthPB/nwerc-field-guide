"""Reference implementations for the advanced DP workshops. Python 3.9+."""
from bisect import bisect_left
from collections import deque
from math import isqrt


def grid_sum_possible(grid, target=0):
    """Full rectangular grid of +1 and -1, with down/right moves."""
    low, high = [float("inf")] * len(grid[0]), [-float("inf")] * len(grid[0])
    low[0] = high[0] = 0
    for row in grid:
        for j, cost in enumerate(row):
            low[j] = cost + min(low[j], low[j-1] if j else float("inf"))
            high[j] = cost + max(high[j], high[j-1] if j else -float("inf"))
    return low[-1] <= target <= high[-1] and (target - low[-1]) % 2 == 0


def suffix_score(word, values=(1, 10, 100, 1000, 10000)):
    """word contains zero-based indices into strictly increasing positive values."""
    states = {(-1, 0): 0}
    for old in reversed(word):
        following = {}
        for (largest, used), score in states.items():
            for new, value in enumerate(values):
                changes = used + (new != old)
                if changes > 1:
                    continue
                key = max(largest, new), changes
                candidate = score + (value if new >= largest else -value)
                following[key] = max(following.get(key, -float("inf")), candidate)
        states = following
    return max(states.values())


def unmerge(output):
    """Recover two equal-length queues for a permutation, or return None."""
    if len(output) % 2:
        return None
    target = len(output) // 2
    starts = []
    for i, value in enumerate(output):
        if not starts or value > output[starts[-1]]:
            starts.append(i)
    starts.append(len(output))
    parent = {0: None}
    for block, (left, right) in enumerate(zip(starts, starts[1:])):
        length = right - left
        for total in range(target, length - 1, -1):
            if total not in parent and total - length in parent:
                parent[total] = block, total - length
    if target not in parent:
        return None
    chosen = set()
    while target:
        block, target = parent[target]
        chosen.add(block)
    a, b = [], []
    for block, (left, right) in enumerate(zip(starts, starts[1:])):
        (a if block in chosen else b).extend(output[left:right])
    return a, b


def shift_tables(bits=60, exponents=None):
    """Capped pair table and its suffix minima. Production bounds use bits=60."""
    exact = {(0, 0): 0}
    for k in (range(1, bits + 1) if exponents is None else exponents):
        following = exact.copy()
        for (a, b), cost in exact.items():
            for cell in ((min(bits, a+k), b), (a, min(bits, b+k))):
                following[cell] = min(following.get(cell, float("inf")), cost + (1 << k))
        exact = following
    suffix = [[exact.get((i,j), float("inf")) for j in range(bits+1)] for i in range(bits+1)]
    for i in range(bits, -1, -1):
        for j in range(bits, -1, -1):
            if i < bits:
                suffix[i][j] = min(suffix[i][j], suffix[i+1][j])
            if j < bits:
                suffix[i][j] = min(suffix[i][j], suffix[i][j+1])
    return exact, suffix


def equalization_cost(x, y, tables):
    exact, suffix = tables
    result = suffix[x.bit_length()][y.bit_length()]
    a = b = 0
    while x and y:
        if x == y:
            result = min(result, exact.get((a, b), float("inf")))
            x >>= 1
            y >>= 1
            a += 1
            b += 1
        elif x > y:
            x >>= 1
            a += 1
        else:
            y >>= 1
            b += 1
    return result


def preorder_count(labels, mod=998244353):
    """labels in heap order on a perfect binary tree."""
    types, ways, dictionary = [0] * (len(labels)+1), [1] * (len(labels)+1), {}
    for i in range(len(labels), 0, -1):
        left = right = 0
        if 2*i <= len(labels):
            left, right = types[2*i], types[2*i+1]
            ways[i] = ways[2*i] * ways[2*i+1] * (1 + (left != right)) % mod
        code = (labels[i-1], min(left, right), max(left, right))
        types[i] = dictionary.setdefault(code, len(dictionary)+1)
    return ways[1]


def tile_triples(counts):
    states = {(0,0): 0}
    for available in [*counts, 0, 0]:
        following = {}
        for (a,b), score in states.items():
            for c in range(3):
                spare = available - a - b - c
                if spare >= 0:
                    key = b, c
                    following[key] = max(following.get(key, -1), score + c + spare//3)
        states = following
    return states[0,0]


def expected_squared(cells, mod=998244353):
    """cells are (label,x,y). Return expectations in input order, in the prime field."""
    from itertools import groupby
    values = [0] * len(cells)
    count = sx = sy = squared = futures = 0
    order = sorted(range(len(cells)), key=lambda i: cells[i][0])
    for _, group in groupby(order, key=lambda i: cells[i][0]):
        indices = list(group)
        inv = pow(count, -1, mod) if count else 0
        for i in indices:
            _, x, y = cells[i]
            if count:
                values[i] = ((x*x+y*y) + (futures+squared-2*x*sx-2*y*sy)*inv) % mod
        for i in indices:
            _, x, y = cells[i]
            count += 1
            sx += x
            sy += y
            squared += x*x + y*y
            futures += values[i]
    return values


def road_table(period, clock=60):
    """The clock must be divisible by the period, which is at least two."""
    return tuple(1 + (t % period == 0) for t in range(clock))


def join_roads(left, right):
    size = len(left)
    return tuple(delay + right[(time + delay) % size] for time, delay in enumerate(left))


def xor_block_bests(values):
    """Root maximum (allowing an empty subarray) for all global XOR permutations."""
    def combine(a, b):
        total_a, pre_a, suf_a, best_a = a
        total_b, pre_b, suf_b, best_b = b
        return (total_a+total_b, max(pre_a, total_a+pre_b),
                max(suf_b, total_b+suf_a), max(best_a, best_b, suf_a+pre_b))
    def build(lo, hi):
        if hi-lo == 1:
            x = values[lo]
            return [(x, max(0,x), max(0,x), max(0,x))]
        mid = (lo+hi)//2
        left, right = build(lo, mid), build(mid, hi)
        return ([combine(a,b) for a,b in zip(left,right)] +
                [combine(b,a) for a,b in zip(left,right)])
    assert values and len(values) & (len(values)-1) == 0
    return [summary[-1] for summary in build(0, len(values))]


def lis_edits(array, queries):
    """Each (zero-based position, replacement) refers to the original array."""
    groups = [[] for _ in array]
    for q, (i, x) in enumerate(queries):
        groups[i].append((q, x))
    def side(indices, direction):
        tails = []
        lengths, inserts = [0] * len(array), [0] * len(queries)
        for i in indices:
            for q, x in groups[i]:
                inserts[q] = bisect_left(tails, direction*x)
            value = direction * array[i]
            j = bisect_left(tails, value)
            lengths[i] = j + 1
            if j == len(tails):
                tails.append(value)
            else:
                tails[j] = value
        return lengths, inserts
    left, prefix = side(range(len(array)), 1)
    right, suffix = side(reversed(range(len(array))), -1)
    best = max(left)
    layers = [0] * (best+1)
    for l, r in zip(left, right):
        if l+r-1 == best:
            layers[l] += 1
    answers = []
    for q, (i, _) in enumerate(queries):
        mandatory = left[i]+right[i]-1 == best and layers[left[i]] == 1
        answers.append(max(best-mandatory, prefix[q]+1+suffix[q]))
    return answers


def zoning_profit(n, cap, rules):
    """Rules (l,r,threshold,fee) have zero-based inclusive endpoints."""
    old = [[0]*n for _ in range(n)]
    for h in range(1, cap+1):
        pref = [[0]*(n+1) for _ in range(n+1)]
        for l,r,threshold,fee in rules:
            if h > threshold:
                pref[l+1][r+1] += fee
        for i in range(1, n+1):
            for j in range(1, n+1):
                pref[i][j] += pref[i-1][j] + pref[i][j-1] - pref[i-1][j-1]
        cur = [row.copy() for row in old]
        for width in range(1, n+1):
            for l in range(n+1-width):
                r = l+width-1
                for p in range(l, r+1):
                    fee = pref[p+1][r+1]-pref[l][r+1]-pref[p+1][p]+pref[l][p]
                    left = cur[l][p-1] if l<p else 0
                    right = cur[p+1][r] if p<r else 0
                    cur[l][r] = max(cur[l][r], left+right+h*h-fee)
        old = cur
    return old[0][n-1]


def wildcard_score(text, patterns, alphabet):
    """Letters at '?' positions are distinct. patterns holds (word, weight) pairs."""
    size = len(alphabet)
    index = {letter:i for i,letter in enumerate(alphabet)}
    go, failure, gain = [[-1]*size], [0], [0]
    for word, weight in patterns:
        state = 0
        for letter in word:
            c = index[letter]
            if go[state][c] == -1:
                go[state][c] = len(go)
                go.append([-1]*size)
                failure.append(0)
                gain.append(0)
            state = go[state][c]
        gain[state] += weight
    queue = deque()
    for c in range(size):
        child = go[0][c]
        if child == -1:
            go[0][c] = 0
        else:
            queue.append(child)
    while queue:
        u = queue.popleft()
        gain[u] += gain[failure[u]]
        for c in range(size):
            v = go[u][c]
            if v == -1:
                go[u][c] = go[failure[u]][c]
            else:
                failure[v] = go[failure[u]][c]
                queue.append(v)
    def read(state, block):
        score = 0
        for letter in block:
            state = go[state][index[letter]]
            score += gain[state]
        return state, score
    prefix, *blocks = text.split("?")
    start, score = read(0, prefix)
    states = {(0,start): score}
    for block in blocks:
        jump = [read(u, block) for u in range(len(go))]
        following = {}
        for (mask, state), score in states.items():
            for c in range(size):
                if mask >> c & 1:
                    continue
                after = go[state][c]
                target, extra = jump[after]
                key = mask | 1 << c, target
                following[key] = max(following.get(key, -float("inf")), score+gain[after]+extra)
        states = following
    return max(states.values())


def isolated_partitions(values, k, mod=998244353):
    """Sqrt decomposition with local suffix histograms of ±1 markers."""
    n = len(values)
    width = isqrt(n) + 1
    blocks = (n+width-1)//width
    markers, weight = [0]*n, [0]*(n+1)
    weight[0] = 1
    sums = [0]*blocks
    prefix = [[0]*(2*width+1) for _ in range(blocks)]
    def rebuild(b):
        hist = [0]*(2*width+1)
        total = 0
        for j in reversed(range(b*width, min(n,(b+1)*width))):
            total += markers[j]
            hist[width+total] += weight[j]
        for j in range(1,len(hist)):
            hist[j] = (hist[j]+hist[j-1]) % mod
        sums[b], prefix[b] = total, hist
    last_two = {}
    for r,x in enumerate(values):
        last, previous = last_two.get(x, (-1,-1))
        touched = {r//width}
        for j, v in ((previous,0),(last,-1),(r,1)):
            if j>=0:
                markers[j] = v
                touched.add(j//width)
        for b in touched:
            rebuild(b)
        total = ways = 0
        for b in reversed(range(r//width+1)):
            bound = k - total
            if bound >= -width:
                ways += prefix[b][min(width,bound)+width]
            total += sums[b]
        weight[r+1] = ways % mod
        last_two[x] = r, last
    return weight[n]


def truth_merge(left, right, operators, mod=1000000007):
    """Combine distributions over truth masks using AND and/or OR."""
    size = len(left)
    def transform(arr, op, inverse):
        arr = arr.copy()
        bit = 1
        while bit < size:
            for mask in range(size):
                target = bool(mask & bit) if op == "|" else not (mask & bit)
                if target:
                    delta = arr[mask ^ bit]
                    arr[mask] = (arr[mask] + (-delta if inverse else delta)) % mod
            bit <<= 1
        return arr
    result = [0]*size
    for op in operators:
        a, b = transform(left,op,False), transform(right,op,False)
        exact = transform([x*y % mod for x,y in zip(a,b)], op, True)
        result = [(x+y)%mod for x,y in zip(result,exact)]
    return result
