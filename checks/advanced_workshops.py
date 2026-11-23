"""Differential tests for the published DP reference. Run with Python 3.9+."""
import itertools as it
import random
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import advanced_dp as a

rng = random.Random(105562)
tests = Counter()
def check(name, actual, expected):
    assert actual == expected, (name,actual,expected)
    tests[name] += 1

def merge(x,y):
    x,y=list(x),list(y); out=[]
    while x and y:
        out.append((x if x[0]<y[0] else y).pop(0))
    return tuple(out+x+y)

def lis(seq):
    tails = []
    for i,x in enumerate(seq):
        tails.append(1+max([d for j,d in enumerate(tails) if seq[j]<x] or [0]))
    return max(tails, default=0)

for _ in range(90):
    h,w=rng.randint(1,4),rng.randint(1,4)
    g=[[rng.choice([-1,1]) for _ in range(w)] for _ in range(h)]
    frontier={(0,0,g[0][0])}
    for step in range(h+w-2):
        frontier={(u,v,s+g[u][v]) for i,j,s in frontier for u,v in [(i+1,j),(i,j+1)] if u<h and v<w}
    choices={s for _,_,s in frontier}
    for k in range(-h-w,h+w+1):check('grid',a.grid_sum_possible(g,k),k in choices)
    word=[rng.randrange(3) for _ in range(rng.randint(1,7))]
    def score(wd):
        return sum((1 if max(wd[i:])==c else -1)*10**c for i,c in enumerate(wd))
    check('suffix',a.suffix_score(word,[1,10,100]),max(score(word[:i]+[c]+word[i+1:]) for i in range(len(word)) for c in range(3)))
for n in [1,2,3]:
    for perm in it.permutations(range(2*n)):
        ok=False
        for side in it.combinations(range(2*n),n):
            left=[x for i,x in enumerate(perm) if i in side]
            right=[x for i,x in enumerate(perm) if i not in side]
            ok |= merge(left,right)==perm
        actual=a.unmerge(perm)
        check('queues',actual is not None,ok)
        if actual:check('queue witness',merge(*actual),perm)
shifts=range(1,6)
tbl=a.shift_tables(5,shifts)
raw=[]
for assign in it.product(range(3),repeat=len(shifts)):
    x=sum(k for k,d in zip(shifts,assign) if d==1)
    y=sum(k for k,d in zip(shifts,assign) if d==2)
    raw.append((x,y,sum(1<<k for k,d in zip(shifts,assign) if d)))
for x in range(32):
    for y in range(32):check('shift',a.equalization_cost(x,y,tbl),min(cost for i,j,cost in raw if x>>i==y>>j))
for mask in range(128):
    labels=[mask>>i&1 for i in range(7)]
    def strings(i):
        if i>=3:return {(labels[i],)}
        L,R=strings(2*i+1),strings(2*i+2)
        return {(labels[i],)+word for u in L for v in R for word in (u+v,v+u)}
    check('preorder',a.preorder_count(labels),len(strings(0)))
@lru_cache(None)
def brute_tiles(freq):
    options=[0]
    for i in range(len(freq)):
        for group in ((i,i,i),(i,i+1,i+2)):
            if max(group)>=len(freq): continue
            f=list(freq)
            for j in group:f[j]-=1
            if min(f)>=0:options.append(1+brute_tiles(tuple(f)))
    return max(options)
for freq in it.product(range(4),repeat=4):check('tiles',a.tile_triples(freq),brute_tiles(freq))
M=998244353
for _ in range(120):
    cells=[(rng.randrange(4),i//3,i%3) for i in range(rng.randint(1,9))]
    @lru_cache(None)
    def ev(i):
        label,x,y=cells[i]
        eligible=[ev(j)+(x-u)**2+(y-v)**2 for j,(vlabel,u,v) in enumerate(cells) if vlabel<label]
        return sum(eligible)*pow(len(eligible),-1,M)%M if eligible else 0
    check('expectation',a.expected_squared(cells),[ev(i) for i in range(len(cells))])
    periods=[rng.randrange(2,7) for i in range(4)]
    table=a.road_table(periods[0])
    for period in periods[1:]:table=a.join_roads(table,a.road_table(period))
    for start in range(60):
        clock=start
        for period in periods:clock+=1+(clock%period==0)
        check('road',table[start],clock-start)
    arr=[rng.randrange(-6,7) for i in range(1<<rng.randrange(1,5))]
    for mask,ans in enumerate(a.xor_block_bests(arr)):
        perm=[arr[i^mask] for i in range(len(arr))]
        check('xor',ans,max(sum(perm[i:j]) for i in range(len(perm)+1) for j in range(i,len(perm)+1)))
    queries=[(rng.randrange(len(arr)),rng.randrange(-6,7)) for j in range(15)]
    check('lis',a.lis_edits(arr,queries),[lis(arr[:i]+[x]+arr[i+1:]) for i,x in queries])
    n,cap=rng.randrange(1,5),rng.randrange(1,4)
    rules=[]
    for j in range(4):
        l=rng.randrange(n);r=rng.randrange(l,n);rules.append((l,r,rng.randrange(cap+1),rng.randrange(1,8)))
    check('zoning',a.zoning_profit(n,cap,rules),max(sum(x*x for x in H)-sum(fee for l,r,t,fee in rules if max(H[l:r+1])>t) for H in it.product(range(cap+1),repeat=n)))
    text=''.join(rng.choice('abc?') for j in range(7))
    if text.count('?')<=3:
        patterns=[(''.join(rng.choice('abc') for j in range(rng.randint(1,3))),rng.randrange(-3,5)) for i in range(5)]
        scores=[]
        for perm in it.permutations('abc',text.count('?')):
            letters=iter(perm);s=''.join(next(letters) if c=='?' else c for c in text)
            scores.append(sum(w*sum(s.startswith(p,i) for i in range(len(s))) for p,w in patterns))
        check('wildcards',a.wildcard_score(text,patterns,'abc'),max(scores))
    seq=[rng.randrange(4) for i in range(rng.randint(1,12))];k=rng.randrange(4)
    ways=[1]
    for r in range(1,len(seq)+1):
        ways.append(sum(ways[l] for l in range(r) if sum(v==1 for v in Counter(seq[l:r]).values())<=k))
    check('singleton',a.isolated_partitions(seq,k),ways[-1]%M)
    f=[rng.randrange(7) for i in range(16)];g=[rng.randrange(6) for i in range(16)]
    for ops in ['&','|','&|']:
        expected=[0]*16
        for op in ops:
            for i in range(16):
                for j in range(16):expected[(i&j) if op=='&' else (i|j)]+=f[i]*g[j]
        check('truth',a.truth_merge(f,g,ops),expected)
print(dict(tests))
print(sum(tests.values()),'checks passed')
