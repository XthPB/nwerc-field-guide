"""Small-instance oracles for worked hard Codeforces lessons. Run with Python 3.9+."""
from collections import Counter, deque
from itertools import combinations, permutations, product
from math import gcd
from random import Random


def check_permutation_slack():
    def enlarge(groups, x, sign, r, slack):
        left = r
        while groups and sign * groups[-1][0] < sign * x:
            value, lo = groups.pop()
            for i in range(lo, left):
                slack[i] += sign * (x - value)
            left = lo
        groups.append((x, left))
    cases = 0
    for n in range(1, 8):
        for a in permutations(range(n)):
            maxima, minima, slack = [], [], []
            for r, x in enumerate(a):
                slack = [z - 1 for z in slack]
                enlarge(maxima, x, 1, r, slack)
                enlarge(minima, x, -1, r, slack)
                slack.append(0)
                actual = [max(a[l:r+1])-min(a[l:r+1])-(r-l) for l in range(r+1)]
                assert slack == actual
                assert slack.count(0) == sum(len(set(a[l:r+1])) == max(a[l:r+1])-min(a[l:r+1])+1 for l in range(r+1))
            cases += 1
    return cases


def check_matrix_corners():
    n = 4
    a = [[(i*i + 2*j) % 7 for j in range(n)] for i in range(n)]
    def mixed(i, j):
        return a[i][j] - (a[i-1][j] if i else 0) - (a[i][j-1] if j else 0) + (a[i-1][j-1] if i and j else 0)
    diff = [[mixed(i,j) for j in range(n)] for i in range(n)]
    ranges = [(u,l,b,r) for u in range(n) for b in range(u,n) for l in range(n) for r in range(l,n)]
    for index, (u,l,b,r) in enumerate(ranges):
        delta = 1 if index % 2 else -2
        for i in range(u,b+1):
            for j in range(l,r+1):
                a[i][j] += delta
        for i,j,v in [(u,l,delta),(b+1,l,-delta),(u,r+1,-delta),(b+1,r+1,delta)]:
            if i < n and j < n:
                diff[i][j] += v
        assert all(diff[i][j] == mixed(i,j) for i in range(n) for j in range(n))
        for x,y,z,t in ranges:
            feasible = all(a[i][j] == a[i][y]+a[x][j]-a[x][y] for i in range(x,z+1) for j in range(y,t+1))
            interior_zero = all(diff[i][j] == 0 for i in range(x+1,z+1) for j in range(y+1,t+1))
            assert feasible == interior_zero
    return len(ranges)**2


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for a,b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def distances(adj, start, blocked=-1):
    d = [-1]*len(adj)
    if start == blocked:
        return d
    d[start] = 0
    todo = deque([start])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if d[v] < 0 and v != blocked:
                d[v] = d[u]+1
                todo.append(v)
    return d


def check_graph_certificates():
    cases = 0
    for n in range(2,6):
        edges = list(combinations(range(n),2))
        for mask in range(1 << len(edges)):
            active = [e for j,e in enumerate(edges) if mask >> j & 1]
            adj = adjacency(n,active)
            d = [distances(adj,i) for i in range(n)]
            if -1 in d[0]:
                continue
            for root in range(n):
                # Folding ancestor lists is the small-instance equivalent of folding LCAs.
                chain = {root: [root]}
                for v in sorted((v for v in range(n) if v != root),key=lambda v:d[root][v]):
                    pred = [u for u in adj[v] if d[root][u]+1 == d[root][v]]
                    common = set.intersection(*(set(chain[u]) for u in pred))
                    chain[v] = sorted(common,key=lambda u:d[root][u])+[v]
                for blocked in range(n):
                    remaining = distances(adj,root,blocked)
                    assert all((blocked in chain[v]) == (remaining[v] != d[root][v]) for v in range(n))
            if n <= 4:
                valid = [[0]*n for _ in range(n)]
                for chosen in combinations(active,n-1):
                    tree = adjacency(n,chosen)
                    if -1 in distances(tree,0):
                        continue
                    roots = [i for i in range(n) if distances(tree,i) == d[i]]
                    for x,y in product(roots,repeat=2):
                        valid[x][y] += 1
                for x,y in product(range(n),repeat=2):
                    spine = {v for v in range(n) if d[x][v]+d[y][v] == d[x][y]}
                    count = int(len(spine)==d[x][y]+1)
                    for v in set(range(n))-spine:
                        count *= sum(d[x][u]+1==d[x][v] and d[y][u]+1==d[y][v] for u in adj[v])
                    assert count == valid[x][y]
            cases += 1
    return cases


def check_diameter_sumsets():
    def tree_from_code(n, code):
        leaves_left = Counter(code)
        edges = []
        live = set(range(n))
        for v in code:
            leaf = min(x for x in live if not leaves_left[x])
            edges.append((leaf,v))
            live.remove(leaf)
            leaves_left[v] -= 1
        edges.append(tuple(sorted(live)))
        return adjacency(n,edges)
    def allowed(adj,root,blocked):
        parent = {root:blocked}
        depth = {root:0}
        walk = [root]
        for u in walk:
            for v in adj[u]:
                if v != parent[u]:
                    parent[v] = u
                    depth[v] = depth[u]+1
                    walk.append(v)
        top = max(depth.values())
        good, found = set(), set()
        for u in reversed(walk):
            sons = sum(v in good for v in adj[u] if v != parent[u])
            if depth[u] == top or sons:
                good.add(u)
            if depth[u] == top or sons >= 2:
                found.add(depth[u])
        return found
    cases = 0
    for n in range(2,7):
        for code in product(range(n),repeat=n-2):
            adj = tree_from_code(n,code)
            ds = [distances(adj,i) for i in range(n)]
            diam = max(max(row) for row in ds)
            if diam % 2 == 0:
                continue
            paths = []
            for u,v in combinations(range(n),2):
                if ds[u][v] != diam:
                    continue
                p = [u]
                while p[-1]!=v:
                    p.append(next(t for t in adj[p[-1]] if ds[t][v]+1==ds[p[-1]][v]))
                edge_set = {tuple(sorted(e)) for e in zip(p,p[1:])}
                paths.append(edge_set)
            a,b=p[diam//2:diam//2+2]
            actual = {len(i & j) for i,j in product(paths,repeat=2)}
            predicted = {1+i+j for i in allowed(adj,a,b) for j in allowed(adj,b,a)}
            assert actual == predicted
            cases += 1
    return cases


def check_divisor_gaps():
    def primes_powers(n):
        primes = [p for p in range(2,2*n+3) if all(p%d for d in range(2,int(p**0.5)+1))]
        powers = set()
        for p in primes:
            x = p
            while x<=2*n+2:
                powers.add(x)
                x *= p
        return sorted(p for p in powers if p<=n)+[min(p for p in powers if p>n)]
    cases=0
    for n in range(1,6):
        powers=primes_powers(n)
        for a in product(range(1,n+1),repeat=n):
            latest = {p:0 for p in powers}
            found=set()
            for i,x in enumerate(a+(0,),1):
                barriers = [p for p in powers if x%p==0]
                for p in barriers:
                    if i>latest[p]+1 and all(latest[t]>latest[p] for t in powers if t<p):
                        found.add(p)
                for p in barriers:
                    latest[p]=i
            exact=set()
            for left in range(n):
                multiple=1
                for x in a[left:]:
                    multiple=multiple//gcd(multiple,x)*x
                    t=1
                    while multiple%t==0:
                        t+=1
                    exact.add(t)
            assert exact==found
            cases+=1
    return cases


def check_quasikernel():
    cases=0
    for n in range(1,5):
        arcs=[(u,v) for u in range(n) for v in range(n) if u!=v]
        for mask in range(1<<len(arcs)):
            adj=[set() for _ in range(n)]
            for i,(u,v) in enumerate(arcs):
                if mask>>i&1: adj[u].add(v)
            marked=set();candidates=[]
            for u in range(n):
                if u not in marked:
                    candidates.append(u);marked.update({u}|adj[u])
            marked=set();chosen=set()
            for u in reversed(candidates):
                if u not in marked:
                    chosen.add(u);marked.update({u}|adj[u])
            assert all(not (adj[u]&chosen) for u in chosen)
            reached=marked|{w for v in marked for w in adj[v]}
            assert len(reached)==n
            cases+=1
    return cases


def check_strings_and_random_subsets():
    cases=0
    for n in (1,2,4,8):
        for s in map(''.join,product('ab',repeat=n)):
            ranks=[ord(x) for x in s];stride=1
            while stride<n:
                pairs=[(ranks[i],ranks[i^stride]) for i in range(n)]
                order={item:i for i,item in enumerate(sorted(set(pairs)))}
                ranks=[order[pair] for pair in pairs]
                stride*=2
            strings=[''.join(s[i^m] for i in range(n)) for m in range(n)]
            assert strings[ranks.index(min(ranks))]==min(strings)
            cases+=1
    for n in range(1,9):
        for s in map(''.join,product('()',repeat=n)):
            p=[0]
            for char in s: p.append(p[-1]+(1 if char=='(' else -1))
            found=0;prev=''
            for i in sorted(range(n),key=lambda i:s[i:]):
                suf=s[i:];h=0
                while h<min(len(suf),len(prev)) and suf[h]==prev[h]: h+=1
                stop=next((j for j in range(i+1,n+1) if p[j]<p[i]),n+1)
                found+=sum(p[j]==p[i] for j in range(i+h+1,stop))
                prev=suf
            exact={s[l:r] for l in range(n) for r in range(l+1,n+1)
                   if p[l]==p[r] and min(p[l:r+1])==p[l]}
            assert found==len(exact)
            cases+=1
    for counts in product(range(1,6),repeat=3):
        for k in range(1,7):
            total=8
            passed=sum(sum(a*b for a,b in zip(counts,bits))%k==0 for bits in product((0,1),repeat=3))
            assert passed==total if all(a%k==0 for a in counts) else passed<=total//2
            cases+=1
    return cases



def cheapest_brackets(pattern, costs):
    """Return a minimum-cost word, or None. Costs are (opening, closing) in '?' order."""
    from heapq import heappush, heappop
    offers = iter(costs)
    result = list(pattern)
    balance = total = 0
    heap = []
    for i, char in enumerate(pattern):
        if char == '?':
            opening, closing = next(offers)
            total += closing
            result[i] = ')'
            heappush(heap,(opening-closing,i))
        balance += 1 if result[i]=='(' else -1
        if balance < 0:
            if not heap:
                return None
            extra, pos = heappop(heap)
            total += extra
            result[pos] = '('
            balance += 2
    return (total,''.join(result)) if balance==0 else None


def shortest_digit_labels(n, edges, modulus):
    """Undirected edge i appends i+1. Return minimum route labels modulo modulus."""
    adj = [[] for _ in range(n)]
    for index,(a,b) in enumerate(edges,1):
        digits = [int(d) for d in str(index)]
        for source,target in [(a,b),(b,a)]:
            u = source
            for digit in digits[:-1]:
                v = len(adj)
                adj.append([])
                adj[u].append((digit,v))
                u = v
            adj[u].append((digits[-1],target))
    values = [None]*len(adj)
    values[0] = 0
    groups = deque([[0]])
    while groups:
        group = groups.popleft()
        prefix = values[group[0]]
        buckets = [[] for _ in range(10)]
        for u in group:
            for digit,v in adj[u]:
                if values[v] is None:
                    buckets[digit].append(v)
        for digit,bucket in enumerate(buckets):
            fresh = []
            for v in bucket:
                if values[v] is None:
                    values[v] = (prefix*10+digit)%modulus
                    fresh.append(v)
            if fresh:
                groups.append(fresh)
    return values[:n]


def check_heap_and_prefix_groups():
    from heapq import heappop, heappush
    random = Random(483)
    cases = 0
    for n in range(1,9):
        for pattern in product('()?',repeat=n):
            s=''.join(pattern)
            costs=[(random.randrange(9),random.randrange(9)) for char in s if char=='?']
            best=None
            for picks in product(range(2),repeat=len(costs)):
                choices=iter(picks)
                word=''.join('()'[next(choices)] if char=='?' else char for char in s)
                balance=0
                for char in word:
                    balance += 1 if char=='(' else -1
                    if balance<0: break
                if balance==0:
                    price=sum(pair[pick] for pair,pick in zip(costs,picks))
                    best=price if best is None else min(best,price)
            actual=cheapest_brackets(s,costs)
            assert (actual[0] if actual else None)==best
            if actual:
                price=balance=0;offers=iter(costs)
                for char,replacement in zip(s,actual[1]):
                    if char=='?':
                        price+=next(offers)[int(replacement==')')]
                    else:
                        assert char==replacement
                    balance+=1 if replacement=='(' else -1
                    assert balance>=0
                assert balance==0 and price==best
            cases+=1
    for _ in range(600):
        n=random.randrange(2,10)
        edges=[tuple(random.sample(range(n),2)) for _ in range(random.randrange(1,24))]
        adj=[[] for _ in range(n)]
        for i,(a,b) in enumerate(edges,1):
            adj[a].append((b,str(i)));adj[b].append((a,str(i)))
        best=[None]*n;todo=[(0,'',0)]
        while todo:
            _,s,u=heappop(todo)
            if best[u] is not None:continue
            best[u]=s
            for v,suffix in adj[u]:
                if best[v] is None:
                    candidate=s+suffix
                    heappush(todo,(len(candidate),candidate,v))
        mod=11
        expected=[int('0'+x)%mod if x is not None else None for x in best]
        assert shortest_digit_labels(n,edges,mod)==expected
        cases+=1
    return cases


def check_xor_stopping():
    from fractions import Fraction
    def transform(values):
        a=list(values);step=1
        while step<len(a):
            for start in range(0,len(a),2*step):
                for i in range(start,start+step):
                    x,y=a[i],a[i+step];a[i],a[i+step]=x+y,x-y
            step*=2
        return a
    cases=0
    for counts in product(range(4),repeat=4):
        n=sum(counts)
        if not n:continue
        rhs=[0,1,1,1]
        coefficients=transform(counts)
        spectrum=[Fraction(v,n+1-coefficients[i]) for i,v in enumerate(transform(rhs))]
        p=[x/4 for x in transform(spectrum)]
        # Check every equation of the original finite-state Markov chain, over exact rationals.
        for x in range(4):
            assert 0<=p[x]<=1
            assert (n+1)*p[x]==rhs[x]+sum(counts[g]*p[x^g] for g in range(4))
        cases+=1
    return cases


if __name__ == '__main__':
    checks=[check_permutation_slack,check_matrix_corners,check_graph_certificates,
            check_diameter_sumsets,check_divisor_gaps,check_quasikernel,check_strings_and_random_subsets,check_heap_and_prefix_groups,check_xor_stopping]
    counts={check.__name__: check() for check in checks}
    for name, count in counts.items(): print(name, count)
    print('Total small instances:',sum(counts.values()))
