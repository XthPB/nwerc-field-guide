#include "../dp_templates.hpp"
#include <cassert>
#include <iostream>
#include <map>
#include <queue>
#include <random>
using namespace std;
using namespace nwerc_dp;
int main() {
    mt19937 rng(11232026);
    map<string,int> ok;
    auto checked=[&](string family,bool success) {
        if (!success) { cerr<<"CHECK FAILED "<<family<<"\n"; exit(1); }
        ++ok[family];
    };
    for(int t=0;t<400;++t) {
        int n=rng()%12;
        vector<int> w(n); vector<i64> signed_values(n),a(n);
        for(int i=0;i<n;++i) { w[i]=1+rng()%9; signed_values[i]=int(rng()%19)-9; a[i]=int(rng()%13)-6; }
        int target=int(rng()%31)-15, half=accumulate(w.begin(),w.end(),0)/2;
        i64 cnt=0, majority=0; int best=0; bitset<128> can;
        for (int m=0;m<(1<<n);++m) {
            i64 sum=0;int weight=0, smallest=100, len=0; i64 last=-100;
            bool increasing=true;
            for (int i=0;i<n;++i) if(m>>i&1) {
                weight+=w[i];smallest=min(smallest,w[i]);sum+=signed_values[i];
                increasing &= a[i]>last; last=a[i];++len;
            }
            can.set(weight); cnt+=sum==target;
            majority+=weight>half && weight-smallest<=half;
            if(increasing) best=max(best,len);
        }
        checked("MITM exact count",cnt==count_subset_sum(signed_values,target));
        checked("bitset reachability",can==reachable<127>(w));
        checked("minimal majorities",majority==minimal_majorities(w));
        auto ix=lis_indices(a); bool valid=(int)ix.size()==best;
        for(int i=1;i<(int)ix.size();++i)valid &= ix[i-1]<ix[i] && a[ix[i-1]]<a[ix[i]];
        checked("strict LIS witness",valid);
    }
    for(int t=0;t<250;++t) {
        int n=1+rng()%10;vector<int>a(n),pref(n+1);for(int& v:a)v=rng()%8;
        partial_sum(a.begin(),a.end(),pref.begin()+1);
        int k=1+rng()%n; i64 best=INT64_MAX;
        for(int cuts=0;cuts<(1<<(n-1));++cuts) if(__builtin_popcount((unsigned)cuts)==k-1) {
            i64 val=0;int last=0;
            for(int j=1;j<=n;++j) if(j==n || (cuts>>(j-1)&1)) {
                int sum=pref[j]-pref[last];val+=sum*sum;last=j;
            }
            best=min(best,val);
        }
        checked("Monge partition",square_partition(a,k)==best);
        vector<vector<i64>> d(n,vector<i64>(n));
        for(int len=2;len<=n;++len)for(int l=0;l+len<=n;++l){
            int r=l+len-1;d[l][r]=INT64_MAX;
            for(int j=l;j<r;++j)d[l][r]=min(d[l][r],d[l][j]+d[j+1][r]+pref[r+1]-pref[l]);
        }
        checked("Knuth merging",merge_cost(a)==d[0][n-1]);
        int b=rng()%8;vector<i64>s(1<<b);for(auto& v:s)v=int(rng()%11)-5;
        auto z=subset_zeta(s);bool valid=true;
        for(int m=0;m<(1<<b);++m){i64 expected=0;for(int j=0;j<=m;++j)if((m&j)==j)expected+=s[j];valid &= expected==z[m];}
        checked("subset zeta",valid);
        int size=1+rng()%18;vector<vector<int>> graph(size);for(int v=1;v<size;++v){int u=rng()%v;graph[u].push_back(v);graph[v].push_back(u);}
        auto ans=distance_sums(graph);valid=true;
        for(int v=0;v<size;++v) {
            vector<int> dist(size,-1);queue<int> q;q.push(v);dist[v]=0;
            while(!q.empty()){int u=q.front();q.pop();for(int f:graph[u])if(dist[f]==-1){dist[f]=dist[u]+1;q.push(f);}}
            valid &= accumulate(dist.begin(),dist.end(),0LL)==ans[v];
        }
        checked("tree rerooting",valid);
    }
    int digits=0;
    checked("digit DP",classy(-1)==0);
    for(int n=0;n<=15000;++n) {
        int c=0;for(int v=n;v;v/=10)c+=v%10!=0;digits+=c<=3;
        if(n%23==0 || n==15000) checked("digit DP",classy(n)==digits);
    }
    for(int m=0;m<=5;++m) for(int p: {1,2,3,4,5,6,8,11,12,97}) for(int t=0;t<12;++t) {
        int n=1<<m,steps=rng()%9;vector<i64> a(n),k(n);for(int i=0;i<n;++i){a[i]=rng()%p;k[i]=rng()%p;}
        auto direct=a;
        for(int u=0;u<steps;++u){vector<i64> next(n);for(int i=0;i<n;++i)for(int j=0;j<n;++j)next[i]=(next[i]+direct[j]*k[i^j])%p;direct.swap(next);}
        checked("powered XOR convolution",xor_steps(a,k,steps,p)==direct);
    }
    for(int n:{2,4,6,8,10}) for(int v=0;v<(1<<n);++v) {
        string s(n,'a');for(int i=0;i<n;++i)if(v>>i&1)s[i]='b';
        int cnt=0;
        for(int mask=0;mask<(1<<(n-1));++mask) {
            if((__builtin_popcount((unsigned)mask)+1)%2)continue;
            vector<string> parts;int start=0;
            for(int i=0;i<n;++i)if(i==n-1 || (mask>>i&1)){parts.push_back(s.substr(start,i-start+1)); start=i+1;}
            bool good=true;for(size_t i=0;i<parts.size()/2;++i)good &= parts[i]==parts[parts.size()-1-i];cnt+=good;
        }
        checked("eertree paired blocks",cnt==mirrored_block_splits(s));
    }
    checked("published example",minimal_majorities({3,1,4,1,5})==4);
    checked("published example",minimal_majorities({191,24,148,38,8,28,9,1,3,3,12})==38);
    checked("published example",minimal_majorities({1,2,3,4})==3);
    checked("published example",mirrored_block_splits("abcdcdab")==1);
    checked("published example",mirrored_block_splits("abbababababbab")==3);
    checked("hand trace",xor_steps({1,2},{1,3},2,6)==vector<i64>({4,2}));
const vector<int> euros{1,2,5,10,20,50,100,200,500};
    auto accepts_half = [](const vector<int>& cash, int n) {
        if (n%2) return false;
        vector<char> possible(n/2+1);
        possible[0]=true;
        for (int coin : cash) for (int s=n/2;s>=coin;--s) possible[s] |= possible[s-coin];
        return bool(possible[n/2]);
    };
    for (int total=1;total<=110;++total) {
        bool every=true;
        vector<int> cash;
        auto all = [&](auto&& self,int idx,int left)->void {
            if (!every) return;
            if (left==0) {every=accepts_half(cash,total);return;}
            if (idx==int(euros.size()) || euros[idx]>left) return;
            self(self,idx+1,left);
            cash.push_back(euros[idx]);self(self,idx,left-euros[idx]);cash.pop_back();
        };
        all(all,0,total);
        auto found=unsplittable_payout(total);
        checked("Bisecting Bargain vs unrestricted payout search",found.empty()==every);
        if(!found.empty()) checked("Bisecting Bargain witness",accumulate(found.begin(),found.end(),0)==total && !accepts_half(found,total) && all_of(found.begin(),found.end(),[&](int x){return find(euros.begin(),euros.end(),x)!=euros.end();}));
    }
    for(int total : {201,398,500,900,9998,9999,10000}) {
        auto cash=unsplittable_payout(total);
        if(!cash.empty())checked("large payout witness",accumulate(cash.begin(),cash.end(),0)==total && !accepts_half(cash,total));
    }


    for(const auto& p:ok)cout<<p.first<<"|"<<p.second<<"\n";
}

