#include "../companion.hpp"
#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
using namespace guide;
int main(){
    std::mt19937 rng(542012); int checks=0;
    auto check=[&](bool ok){++checks;if(!ok){std::cerr<<"failed "<<checks<<"\n";std::exit(1);}};
    for(int trial=0;trial<230;++trial){
        int n=1+rng()%8;
        std::vector<int> a(n);
        for(int &x:a)x=int(rng()%10)-5;
        i64 best=0;
        for(int m=0;m<1<<n;++m)if(!(m&(m<<1))){
            i64 score=0; for(int i=0;i<n;++i)if(m>>i&1)score+=a[i];
            best=std::max(best,score);
        }
        check(independent_line(a)==best);
        std::vector<int> values=a;std::sort(values.begin(),values.end());
        std::vector<i64> cost(n);
        for(int x:a){
            i64 prefix=cost[0];
            for(int i=0;i<n;++i){prefix=std::min(prefix,cost[i]);cost[i]=prefix+std::abs(x-values[i]);}
        }
        check(isotonic_l1(a)==*std::min_element(cost.begin(),cost.end()));
        std::vector<std::pair<i64,int>> v;for(int i=0;i<n;++i)v.emplace_back(a[i],i);
        RangeArgMin tree(v);PrefixCounts freq(10);std::vector<int> roots{0};
        for(int x:a)roots.push_back(freq.add(roots.back(),x+5));
        for(int l=0;l<n;++l)for(int r=l+1;r<=n;++r){
            check(tree.query(l,r)==*std::min_element(v.begin()+l,v.begin()+r));
            std::vector<int> ref(a.begin()+l,a.begin()+r);std::sort(ref.begin(),ref.end());
            for(int k=1;k<=r-l;++k)check(freq.kth(roots[l],roots[r],k)==ref[k-1]+5);
        }
        int side=freq.add(roots[0],0);
        check(freq.kth(0,side,1)==0);
        check(freq.kth(0,roots.back(),1)==values.front()+5);
        for(int i=0;i+2<n;++i){
            Best x{i64(a[i]),1,i},y{i64(a[i+1]),1,i+1},z{i64(a[i+2]),1,i+2};
            Best got=combine_best(combine_best(x,y),z),rev=combine_best(x,combine_best(y,z));
            i64 high=std::max({x.score,y.score,z.score});
            check(got.score==high && got.ways==int(x.score==high)+int(y.score==high)+int(z.score==high) && got.id==(x.score==high?i:y.score==high?i+1:i+2));
            check(got.score==rev.score&&got.ways==rev.ways&&got.id==rev.id);
        }
        std::vector<std::vector<i64>> d(n,std::vector<i64>(n));
        for(auto &row:d)for(auto &x:row)x=rng()%22;
        std::vector<int> order(n-1);std::iota(order.begin(),order.end(),1);
        i64 open=INT64_MAX,closed=INT64_MAX;
        do{int last=0;i64 c=0;for(int j:order){c+=d[last][j];last=j;}open=std::min(open,c);closed=std::min(closed,c+(n==1?0:d[last][0]));}while(std::next_permutation(order.begin(),order.end()));
        check(held_karp(d,false)==open);check(held_karp(d,true)==closed);
    }
    check(combine_best(Best{},Best{-7,0,3}).id==3);
    check(combine_best(Best{0,1000000006,1},Best{0,1,2}).ways==0);
for(int h=1;h<=3;++h)for(int w=1;w<=3;++w)for(int mask=0;mask<(1<<(h*w));++mask){
        std::vector<std::string> board(h,std::string(w,'.'));
        for(int pos=0;pos<h*w;++pos)if(mask>>pos&1)board[pos/w][pos%w]='#';
        for(int K=0;K<=4;++K){
            int count=0; auto go=[&](auto&& self,int r,int c,int prev,int turns)->void{
                if(r==h||c==w||board[r][c]!='.'||turns>K)return;
                if(r==h-1&&c==w-1){++count;return;}
                self(self,r,c+1,0,turns+(prev==1));self(self,r+1,c,1,turns+(prev==0));
            };go(go,0,0,-1,0);check(turn_paths(board,K)==count);
        }
    }
    for(int d=1;d<=14;++d){int count=0;
        for(int m=0;m<311;++m){int sum=0;for(int x=m;x;x/=10)sum+=x%10;if(m&&sum%d==0)++count;
            check(digit_sum_bound("000"+std::to_string(m),d)==count);
        }
    }
    check(digit_sum_bound("1"+std::string(9999,'0'),1)>=0);
    for(int n=0;n<=8;++n)for(int mask=0;mask<(1<<n);++mask){
        std::string s;SuffixAutomaton a;
        for(int j=0;j<n;++j){s+=char('a'+((mask>>j)&1));a.append(s.back());}
        std::set<std::string> all;for(int l=0;l<n;++l)for(int r=l+1;r<=n;++r)all.insert(s.substr(l,r-l));
        std::set<std::string> paths;auto travel=[&](auto&& self,int v,const std::string& p)->void{
            for(int c=0;c<26;++c)if(a.nodes[v].next[c]>=0){auto q=p+char('a'+c);paths.insert(q);self(self,a.nodes[v].next[c],q);}
        };travel(travel,0,"");check(paths==all);
    }


for (int trial=0;trial<150;++trial) {
        int n=1+rng()%9;
        std::vector<std::vector<int>> tree(n);
        for(int v=1;v<n;++v){int p=rng()%v;tree[v].push_back(p);tree[p].push_back(v);}
        std::vector<int> exact(n);
        for (int mask=1;mask<(1<<n);++mask) {
            int s=0;while(!(mask>>s&1))++s;
            std::vector<int> seen{s};int used=1<<s;
            for(std::size_t k=0;k<seen.size();++k)for(int v:tree[seen[k]])if((mask>>v&1)&&!(used>>v&1)){used|=1<<v;seen.push_back(v);}
            if(used==mask)for(int v:seen)++exact[v];
        }
        for(int mod:{1,2,6,12,97,1000000007}) {
            auto got=connected_sets(tree,mod);
            for(int v=0;v<n;++v)check(got[v]==exact[v]%mod);
        }
    }


    std::cout<<"The ten new C++17 building blocks passed "<<checks<<" comparisons and assertions, including brute-force tours, independent sets, interval order statistics, absolute-error fits, obstacles and turn counts, decimal bounds, substring automata, and rerooting under prime and composite moduli.\n";
}
