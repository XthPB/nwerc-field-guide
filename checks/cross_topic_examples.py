"""Small independent checks for the worked examples in the subject tracks."""
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
from math import gcd
from random import Random

rng = Random(20251130)
tests = Counter()
def check(group, computed, expected):
    assert computed == expected, (group, computed, expected)
    tests[group] += 1

def subsets(items):
    return (s for size in range(len(items)+1) for s in combinations(items,size))

def graph_distances(adj, start):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v]+1
                queue.append(w)
    return dist

for _ in range(160):
    starts = [rng.randrange(8) for _ in range(6)]
    intervals = [(x,x+rng.randint(1,4)) for x in starts]
    chosen, last = 0, -1
    for l,r in sorted(intervals,key=lambda q:q[1]):
        if l>=last:
            last,chosen=r,chosen+1
    feasible = [s for s in subsets(intervals) if all(r<=a or b<=l for (l,r),(a,b) in combinations(s,2))]
    check("interval exchange",chosen,max(map(len,feasible)))
    w = [rng.randrange(1,6) for _ in range(4)]
    deadlines = [rng.randrange(1,12) for _ in range(4)]
    jobs = sorted(zip(deadlines,w))
    kept = []
    for deadline,duration in jobs:
        kept.append(duration)
        if sum(kept)>deadline:
            kept.remove(max(kept))
    def fits(s):
        time=0
        for deadline,duration in s:
            time+=duration
            if time>deadline:return False
        return True
    check("deadline repair",len(kept),max(len(s) for s in subsets(jobs) if fits(s)))
    n=rng.randint(2,11)
    adj=[[] for i in range(n)]
    for i in range(1,n):
        parent=rng.randrange(i)
        adj[i].append(parent)
        adj[parent].append(i)
    d0=graph_distances(adj,0)
    a=max(d0,key=d0.get)
    da=graph_distances(adj,a)
    b=max(da,key=da.get)
    db=graph_distances(adj,b)
    for v in range(n):
        check("tree eccentricity",max(da[v],db[v]),max(graph_distances(adj,v).values()))
    rects=[]
    for j in range(5):
        x,y=rng.randrange(5),rng.randrange(5)
        rects.append((x,y,x+rng.randint(1,3),y+rng.randint(1,3)))
    xs=sorted({x for lo,_,hi,_ in rects for x in (lo,hi)})
    sweep=0
    for x,xx in zip(xs,xs[1:]):
        ys=sorted((l,r) for a,l,b,r in rects if a<=x<b)
        previous=-1;length=0
        for l,r in ys:
            length+=max(0,r-max(previous,l))
            previous=max(previous,r)
        sweep+=(xx-x)*length
    cells={(x,y) for a,l,b,r in rects for x in range(a,b) for y in range(l,r)}
    check("union area",sweep,len(cells))
    seq=[rng.randrange(4) for _ in range(8)]
    last_seen={}
    for r,x in enumerate(seq):
        last_seen[x]=r
        for l in range(r+1):
            check("offline distinct",sum(i>=l for i in last_seen.values()),len(set(seq[l:r+1])))
    m=rng.randint(1,12); n=rng.randint(1,12); a0=rng.randrange(m); b0=rng.randrange(n)
    period=m*n//gcd(m,n)
    brute=[i for i in range(period) if i%m==a0 and i%n==b0]
    g=gcd(m,n)
    if (b0-a0)%g:
        actual=[]
    else:
        ng=n//g
        k0=(((b0-a0)//g)*pow(m//g,-1,ng))%ng if ng>1 else 0
        actual=[(a0+m*k0)%period]
    check('CRT',actual,brute)
    word=''.join(rng.choice('abc') for j in range(10))
    pref=[0]*len(word)
    for i in range(1,len(word)):
        j=pref[i-1]
        while j and word[i]!=word[j]:j=pref[j-1]
        pref[i]=j+(word[i]==word[j])
    borders=[];j=pref[-1]
    while j:
        borders.append(j);j=pref[j-1]
    check("prefix links",sorted(borders),[i for i in range(1,len(word)) if word[:i]==word[-i:]])
    profit=[rng.randint(1,10) for j in range(3)]
    costs=[rng.randint(1,9) for j in range(2)]
    needed=[{j for j in range(2) if rng.random()<.6} for _ in profit]
    best=max(sum(profit[j] for j in picked)-sum(costs[h] for h in set().union(*(needed[j] for j in picked))) for picked in subsets(range(3)))
    cut=10**9
    for kept in subsets(range(5)):
        place=set(kept)
        violation=any(j in place and any(3+h not in place for h in needed[j]) for j in range(3))
        cut=min(cut,sum(profit[j] for j in range(3) if j not in place)+sum(costs[h] for h in range(2) if h+3 in place)+int(violation)*(sum(profit)+1))
    check('maximum closure cut',sum(profit)-cut,best)
for n in range(1,9):
    words=list(product(range(2),repeat=n))
    canon={min(w[k:]+w[:k] for k in range(n)) for w in words}
    check('rotation orbits',sum(2**gcd(k,n) for k in range(n))//n,len(canon))
for n in range(1,7):
    for k in range(1,5):
        exact=sum(max(out) for out in product(range(1,n+1),repeat=k))
        tail=sum(1-Fraction(j,n)**k for j in range(n))
        check('expected maximum',tail,Fraction(exact,n**k))
for n in range(1,8):
    orders=list(permutations(range(n)))
    mean=Fraction(sum(sum(p[i]==max(p[:i+1]) for i in range(n)) for p in orders),len(orders))
    check('record indicators',mean,sum(Fraction(1,i) for i in range(1,n+1)))
for a,b in product(range(25),repeat=2):
    predicted=(a+b)%3==0 and min(2*a-b,2*b-a)>=0
    brute=any((2*x+y,x+2*y)==(a,b) for x in range(a+1) for y in range(b+1))
    check('pile witness',predicted,brute)
def mex(vals):
    x=0
    while x in vals:x+=1
    return x
@lru_cache(None)
def strip(n):
    return mex({strip(i)^strip(n-2-i) for i in range(n-1)})
@lru_cache(None)
def composite(state):
    options=set()
    for j,n in enumerate(state):
        for i in range(n-1):
            pieces=[*state[:j],*state[j+1:],i,n-2-i]
            options.add(composite(tuple(sorted(x for x in pieces if x>=2))))
    return mex(options)
for left,right in product(range(8),repeat=2):
    check('independent games',strip(left)^strip(right),composite((left,right)))
print(dict(tests))
print(sum(tests.values()),'checks passed')
