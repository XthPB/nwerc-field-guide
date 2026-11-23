from itertools import product,combinations,permutations,accumulate
from collections import Counter
from math import comb
from functools import lru_cache
from random import Random
from pathlib import Path
rng=Random(46217);checks=Counter()
def ck(name,actual,expected):
    assert actual==expected,(name,actual,expected)
    checks[name]+=1
for n in range(1,9):
    paths=0
    for up in combinations(range(2*n),n):
        used=set(up);bal=0
        for i in range(2*n):
            bal+=-1 if i in used else 1
            if bal<0:break
        else:paths+=1
    ck('ballot paths',paths,comb(2*n,n)-comb(2*n,n-1))
for h in range(2,5):
 for w in range(2,5):
  dest=(h-1,w-1);cells=list(product(range(h),range(w)))
  cls=lambda u:(u[0]==dest[0],u[1]==dest[1])
  for start in cells:
   dp={start:1};cd=Counter([cls(start)])
   for t in range(1,5):
    nd=Counter();ncd=Counter()
    for a in cells:
     for b in cells:
      if a!=b and (a[0]==b[0] or a[1]==b[1]):nd[b]+=dp.get(a,0)
    for c,v in cd.items():
     first=next(a for a in cells if cls(a)==c)
     for b in cells:
      if b!=first and (b[0]==first[0] or b[1]==first[1]):ncd[cls(b)]+=v
    dp=nd;cd=ncd;ck('rook classes',cd[(True,True)],dp[dest])
@lru_cache(None)
def inv(n,k):
 if k<0:return 0
 if n==0:return int(k==0)
 return sum(inv(n-1,k-j) for j in range(n))
for n in range(1,8):
 freq=Counter(sum(x>y for i,x in enumerate(p) for y in p[i+1:]) for p in permutations(range(n)))
 for k in range(n*(n-1)//2+1):ck('inversion insertion',inv(n,k),freq[k])
@lru_cache(None)
def erase(s):
 if not s:return 1
 return sum(erase(s[:i]+s[i+2:]) for i in range(len(s)-1) if s[i]==s[i+1])
@lru_cache(None)
def interval(s):
 if not s:return 1
 return sum(interval(s[1:k])*interval(s[k+1:])*comb(len(s)//2,(k+1)//2) for k in range(1,len(s),2) if s[0]==s[k])
for n in (0,2,4,6,8):
 for s in map(''.join,product('ab',repeat=n)):ck('interleaved deletion orders',interval(s),erase(s))
@lru_cache(None)
def brute_remove(s):
 if not s:return 0
 return max((r-l)**2+brute_remove(s[:l]+s[r:]) for l in range(len(s)) for r in range(l+1,len(s)+1) if len(set(s[l:r]))==1)
def remove_dp(s):
 @lru_cache(None)
 def go(l,r,k):
  if l>r:return 0
  return max([go(l,r-1,0)+(k+1)**2]+[go(i+1,r-1,0)+go(l,i,k+1) for i in range(l,r) if s[i]==s[r]])
 return go(0,len(s)-1,0)
for n in range(7):
 for s in map(''.join,product('ab',repeat=n)):ck('interval with a carry',remove_dp(s),brute_remove(s))
def words(g):
 h=len(g);w=len(g[0])
 @lru_cache(None)
 def go(r,c):
  if (r,c)==(h-1,w-1):return [g[r][c]]
  return [g[r][c]+v for a,b in [(r+1,c),(r,c+1)] if a<h and b<w for v in go(a,b)]
 return go(0,0)
for t in range(140):
 h,w=rng.randrange(1,5),rng.randrange(1,5);board=[[rng.choice('abc') for _ in range(w)] for _ in range(h)]
 f={(0,0)};s=board[0][0]
 while (h-1,w-1) not in f:
  q={(a,b) for u,v in f for a,b in [(u+1,v),(u,v+1)] if a<h and b<w};best=min(board[a][b] for a,b in q);f={(a,b) for a,b in q if board[a][b]==best};s+=best
 ck('lexicographic diagonal frontier',s,min(words(board)))
for trial in range(130):
 n=rng.randrange(1,9);h=[rng.randrange(5) for _ in range(n)]
 @lru_cache(None)
 def glide(i):
  can=[j for j in range(n) if i!=j and h[j]<h[i] and all(h[k]<h[i] for k in range(min(i,j)+1,max(i,j)))]
  return 1+max([0]+[glide(j) for j in can])
 a=[0]*n
 for i in sorted(range(n),key=h.__getitem__):
  l=next((j for j in range(i-1,-1,-1) if h[j]>=h[i]),-1);r=next((j for j in range(i+1,n) if h[j]>=h[i]),n)
  a[i]=1+max([0]+[a[j] for j in range(l+1,r) if h[j]<h[i]])
 ck('mountain barriers',a,[glide(i) for i in range(n)])
for n in range(1,6):
 for trial in range(36):
  items=[(rng.randint(1,4),rng.randint(0,7),rng.randint(0,7)) for _ in range(n)]
  brute=0
  for k in range(1,n+1):
   for seq in permutations(items,k):
    wt=val=0
    for w,s,v in seq:
     if wt>s:break
     wt+=w;val+=v
    else:brute=max(brute,val)
  table={0:0}
  for w,s,v in sorted(items,key=lambda a:a[0]+a[1]):
   old=table.copy()
   for q,x in old.items():
    if q<=s:table[q+w]=max(table.get(q+w,-1),x+v)
  ck('stack exchange before knapsack',max(table.values()),brute)
for n in range(1,8):
 for trial in range(65):
  g=[[] for _ in range(n)]
  for v in range(1,n):
   u=rng.randrange(v);g[u].append(v);g[v].append(u)
  def dist(root):
   d=[-1]*n;d[root]=0;q=[root]
   for u in q:
    for v in g[u]:
     if d[v]<0:d[v]=d[u]+1;q.append(v)
   return d
  for u in range(n):
   d=dist(u)
   for v in g[u]:
    e=dist(v);side=sum(x for x,y in zip(d,e) if y<x)
    ck('squared-distance reroot',sum(x*x for x in d)+2*sum(d)-4*side+n,sum(x*x for x in e))
for hi in range(36):
 for lo in range(hi+1):
  def F(a,b):
   if min(a,b)<0:return 0
   f={(True,True):1}
   for j in range(max(a,b).bit_length()-1,-1,-1):
    nd=Counter()
    for (ta,tb),v in f.items():
     for x,y in [(0,0),(0,1),(1,0)]:
      a0=(a>>j)&1;b0=(b>>j)&1
      if ta and x>a0 or tb and y>b0:continue
      nd[(ta and x==a0,tb and y==b0)]+=v
    f=nd
   return sum(f.values())
  actual=F(hi,hi)-F(lo-1,hi)-F(hi,lo-1)+F(lo-1,lo-1)
  ck('bounded no-carry pairs',actual,sum((a&b)==0 for a in range(lo,hi+1) for b in range(lo,hi+1)))
print(sum(checks.values()),'independent comparisons across',len(checks),'additional derivations')
print(dict(checks))

