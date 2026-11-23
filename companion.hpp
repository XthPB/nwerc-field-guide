#pragma once
#include <algorithm>
#include <cassert>
#include <array>
#include <string>
#include <cstdint>
#include <limits>
#include <queue>
#include <unordered_map>
#include <utility>
#include <vector>

namespace guide {
using i64 = std::int64_t;

// [state]
// Example of a layered DP. A 1-bit state says if the last house was taken.
// Values may be negative. Choosing nothing is allowed.
inline i64 independent_line(const std::vector<int>& reward) {
    i64 skipped = 0;
    i64 taken = std::numeric_limits<i64>::lowest();
    for (int value : reward) {
        i64 next_taken = skipped + value;
        skipped = std::max(skipped, taken);
        taken = next_taken;
    }
    return std::max(skipped, taken);
}
// [/state]

// [bestcount]
// Merge DISJOINT candidate sets. Use ways mod 1e9+7 at every stage.
// id == -1 is the empty identity. A count can be zero modulo the modulus.
struct Best {
    i64 score = 0;
    int ways = 0;
    int id = -1;
};
inline Best combine_best(Best a, Best b) {
    if (a.id == -1) return b;
    if (b.id == -1) return a;
    if (a.score != b.score) return a.score > b.score ? a : b;
    return {a.score, (a.ways + b.ways) % 1000000007, std::min(a.id, b.id)};
}
// [/bestcount]

// [argpair]
// Entries are in coordinate order. Query the half-open range [left, right).
// Store (second value, original index). A smaller ID wins score ties.
class RangeArgMin {
    using Entry = std::pair<i64, int>;
    int n;
    std::vector<Entry> tree;
public:
    explicit RangeArgMin(const std::vector<Entry>& entries)
        : n(static_cast<int>(entries.size())), tree(2 * n) {
        std::copy(entries.begin(), entries.end(), tree.begin() + n);
        for (int k = n - 1; k > 0; --k)
            tree[k] = std::min(tree[2*k], tree[2*k+1]);
    }
    Entry query(int left, int right) const {
        assert(0 <= left && left < right && right <= n);
        Entry answer = {std::numeric_limits<i64>::max(), std::numeric_limits<int>::max()};
        for (left += n, right += n; left < right; left /= 2, right /= 2) {
            if (left & 1) answer = std::min(answer, tree[left++]);
            if (right & 1) answer = std::min(answer, tree[--right]);
        }
        return answer;
    }
};
// [/argpair]

// [heldkarp]
// Directed complete cost matrix, nonnegative finite costs, 1 <= n <= 20.
// Every route must cost less than INF. For n=1 the empty tour costs zero.
// At n=20 this layout uses 160 MiB. Mask bit 0 fixes the start city.
inline i64 held_karp(const std::vector<std::vector<i64>>& cost, bool return_to_start) {
    int n = static_cast<int>(cost.size());
    assert(1 <= n && n <= 20);
    if (n == 1) return 0;
    const i64 inf = std::numeric_limits<i64>::max() / 4;
    int masks = 1 << n;
    std::vector<i64> best(static_cast<std::size_t>(masks) * n, inf);
    auto at = [&](int mask, int v) -> i64& { return best[static_cast<std::size_t>(mask)*n+v]; };
    at(1, 0) = 0;
    for (int mask = 1; mask < masks; mask += 2) {
        for (int last = 0; last < n; ++last) {
            if (at(mask, last) == inf) continue;
            for (int next = 1; next < n; ++next) {
                int bit = 1 << next;
                if (mask & bit) continue;
                i64& candidate = at(mask | bit, next);
                candidate = std::min(candidate, at(mask, last) + cost[last][next]);
            }
        }
    }
    i64 answer = inf;
    for (int v = 1; v < n; ++v)
        answer = std::min(answer, at(masks-1, v) + (return_to_start ? cost[v][0] : 0));
    return answer;
}
// [/heldkarp]

// [persist]
// Rank domain [0, ranks). Node zero is the shared empty tree.
// add(old_root, rank) returns a new version. Other roots stay valid.
// kth(before, after, k) requires nested multiset versions and 1-based k.
class PrefixCounts {
    struct Node { int child[2]{0,0}; int count = 0; };
    int ranks;
    std::vector<Node> nodes{Node{}};
    int insert(int old, int lo, int hi, int rank) {
        int cur = static_cast<int>(nodes.size());
        Node copy = nodes[old];
        ++copy.count;
        nodes.push_back(copy);
        if (hi - lo == 1) return cur;
        int mid = lo + (hi-lo)/2;
        int side = rank >= mid;
        int child = insert(copy.child[side], side ? mid : lo, side ? hi : mid, rank);
        nodes[cur].child[side] = child;
        return cur;
    }
public:
    explicit PrefixCounts(int number_of_ranks) : ranks(number_of_ranks) { assert(ranks > 0); }
    int add(int root, int rank) {
        assert(0 <= rank && rank < ranks);
        return insert(root, 0, ranks, rank);
    }
    int kth(int before, int after, int k) const {
        assert(1 <= k && k <= nodes[after].count - nodes[before].count);
        int lo = 0, hi = ranks;
        while (hi-lo > 1) {
            int mid = lo + (hi-lo)/2;
            int a = nodes[before].child[0], b = nodes[after].child[0];
            int left_count = nodes[b].count - nodes[a].count;
            bool right = k > left_count;
            if (right) { k -= left_count; lo = mid; }
            else hi = mid;
            before = nodes[before].child[right];
            after = nodes[after].child[right];
        }
        return lo;
    }
};
// [/persist]

// [slopeheap]
// Minimum sum of absolute corrections to make a sequence nondecreasing.
inline i64 isotonic_l1(const std::vector<int>& a) {
    std::priority_queue<int> breakpoint;
    i64 cost = 0;
    for (int value : a) {
        breakpoint.push(value);
        if (breakpoint.top() > value) {
            cost += static_cast<i64>(breakpoint.top()) - value;
            breakpoint.pop();
            breakpoint.push(value);
        }
    }
    return cost;
}
// [/slopeheap]
// [turnpaths]
// Count right/down paths with at most K direction changes, modulo 1e9+7.
// '.' is open, '#' is blocked. Nonempty rectangular grid. The first move is free.
inline int turn_paths(const std::vector<std::string>& board, int K) {
    assert(!board.empty() && !board[0].empty() && K >= 0);
    int h=static_cast<int>(board.size()), w=static_cast<int>(board[0].size());
    if (board[0][0]!='.' || board[h-1][w-1]!='.') return 0;
    if (h==1 && w==1) return 1;
    K=std::min(K,h+w-3);
    using Directions=std::array<int,2>; // 0: right, 1: down
    std::vector<std::vector<Directions>> row(w, std::vector<Directions>(K+1));
    const int mod=1000000007;
    for (int r=0; r<h; ++r) {
        for (int c=0; c<w; ++c) {
            std::vector<Directions> cell(K+1);
            if (board[r][c]=='.') {
                if (r==0 && c==1) cell[0][0]=1;
                if (r==1 && c==0) cell[0][1]=1;
                for (int k=0; k<=K; ++k) {
                    if (c>0) cell[k][0]=(cell[k][0]+static_cast<i64>(row[c-1][k][0])
                                          +(k?row[c-1][k-1][1]:0))%mod;
                    if (r>0) cell[k][1]=(cell[k][1]+static_cast<i64>(row[c][k][1])
                                          +(k?row[c][k-1][0]:0))%mod;
                }
            }
            row[c]=std::move(cell);
        }
    }
    i64 answer=0;
    for (const auto& counts:row.back()) answer=(answer+counts[0]+counts[1])%mod;
    return static_cast<int>(answer);
}
// [/turnpaths]

// [longdigits]
// Positive decimal integers <= the decimal string bound with digit sum divisible
// by divisor, modulo 1e9+7. Leading zeros in the input bound are allowed.
inline int digit_sum_bound(const std::string& bound,int divisor) {
    assert(!bound.empty() && divisor>0);
    const int mod=1000000007;
    std::vector<std::array<int,2>> cur(divisor), next(divisor);
    cur[0][1]=1;
    for (char ch:bound) {
        assert(ch>='0' && ch<='9');
        std::fill(next.begin(),next.end(),std::array<int,2>{});
        for (int rem=0; rem<divisor; ++rem) for (int tight=0; tight<=1; ++tight) {
            int limit=tight?ch-'0':9;
            for (int d=0; d<=limit; ++d) {
                int& cell=next[(rem+d)%divisor][tight && d==limit];
                cell=(cell+cur[rem][tight])%mod;
            }
        }
        cur.swap(next);
    }
    return static_cast<int>((static_cast<i64>(cur[0][0])+cur[0][1]+mod-1)%mod);
}
// [/longdigits]

// [suffixauto]
// Lowercase a-z. Each path from the initial state is a distinct substring.
// Number of distinct substrings = sum(len[v] - len[link[v]]) over non-root states.
struct SuffixAutomaton {
    struct State {
        int length=0, link=-1;
        std::array<int,26> next;
        State() { next.fill(-1); }
    };
    std::vector<State> nodes{State{}};
    int last=0;
    void append(char ch) {
        int c=ch-'a';
        assert(c>=0 && c<26);
        int cur=static_cast<int>(nodes.size());
        nodes.emplace_back();
        nodes[cur].length=nodes[last].length+1;
        int p=last;
        while (p!=-1 && nodes[p].next[c]==-1) {
            nodes[p].next[c]=cur;
            p=nodes[p].link;
        }
        if (p==-1) nodes[cur].link=0;
        else {
            int q=nodes[p].next[c];
            if (nodes[p].length+1==nodes[q].length) nodes[cur].link=q;
            else {
                int clone=static_cast<int>(nodes.size());
                State copied=nodes[q];
                copied.length=nodes[p].length+1;
                nodes.push_back(copied);
                while (p!=-1 && nodes[p].next[c]==q) {
                    nodes[p].next[c]=clone;
                    p=nodes[p].link;
                }
                nodes[q].link=nodes[cur].link=clone;
            }
        }
        last=cur;
    }
};
// [/suffixauto]

// [rerootsets]
// For every vertex, connected vertex sets containing it, modulo mod.
// Input: connected undirected simple tree, 0-based; 1 <= mod <= 2^31-1.
inline std::vector<i64> connected_sets(const std::vector<std::vector<int>>& g,int mod) {
    assert(mod>=1);
    int n=static_cast<int>(g.size());
    if (n==0) return {};
    std::vector<int> parent(n,-1),order{0};
    for (std::size_t i=0;i<order.size();++i) {
        int u=order[i];
        for (int v:g[u]) if (v!=parent[u]) {
            parent[v]=u; order.push_back(v);
        }
    }
    const i64 one=1%mod;
    std::vector<i64> down(n,one),up(n),answer(n);
    for (int i=n-1;i>0;--i) {
        int u=order[i],p=parent[u];
        down[p]=down[p]*(1+down[u])%mod;
    }
    for (int u:order) {
        int degree=static_cast<int>(g[u].size());
        std::vector<i64> prefix(degree+1,one);
        auto factor=[&](int v){return 1+(v==parent[u]?up[u]:down[v]);};
        for (int j=0;j<degree;++j)
            prefix[j+1]=prefix[j]*factor(g[u][j])%mod;
        answer[u]=prefix[degree];
        i64 suffix=one;
        for (int j=degree-1;j>=0;--j) {
            int v=g[u][j];
            if (v!=parent[u]) up[v]=prefix[j]*suffix%mod;
            suffix=suffix*factor(v)%mod;
        }
    }
    return answer;
}
// [/rerootsets]

// [kadane]
// Nonempty input. Index-sized vectors of int have sums that fit in i64.
inline i64 maximum_nonempty_subarray(const std::vector<int>& gain) {
    assert(!gain.empty());
    i64 ending = gain.front();
    i64 best = ending;
    for (std::size_t i = 1; i < gain.size(); ++i) {
        ending = gain[i] + std::max<i64>(0, ending);
        best = std::max(best, ending);
    }
    return best;
}
// [/kadane]

// [prefix1]
// Sum on [left, right) is prefix[right] - prefix[left].
inline std::vector<i64> prefix_sums(const std::vector<int>& values) {
    std::vector<i64> prefix(values.size() + 1);
    for (std::size_t i = 0; i < values.size(); ++i)
        prefix[i + 1] = prefix[i] + values[i];
    return prefix;
}
// [/prefix1]

// [prefixcount]
// Count nonempty subarrays with the requested sum, including signed entries.
inline i64 subarray_sum_count(const std::vector<int>& values, int target) {
    std::unordered_map<i64, i64> frequency{{0, 1}};
    i64 prefix = 0, answer = 0;
    for (int value : values) {
        prefix += value;
        auto found = frequency.find(prefix - target);
        if (found != frequency.end()) answer += found->second;
        ++frequency[prefix];
    }
    return answer;
}
// [/prefixcount]

// [bracketsuffix]
// Length and number of longest balanced substrings. CF 5C uses {0, 1}
// when no nonempty balanced substring exists.
inline std::pair<int, int> longest_brackets(const std::string& s) {
    int n = static_cast<int>(s.size());
    std::vector<int> ending(n + 1);
    int best = 0, count = 0;
    for (int i = 1; i <= n; ++i) {
        if (s[i - 1] != ')') continue;
        int opening = i - ending[i - 1] - 1;  // 1-based string position
        if (opening < 1 || s[opening - 1] != '(') continue;
        ending[i] = ending[i - 1] + 2 + ending[opening - 1];
        if (ending[i] > best) {
            best = ending[i];
            count = 1;
        } else if (ending[i] == best) {
            ++count;
        }
    }
    return {best, best == 0 ? 1 : count};
}
// [/bracketsuffix]

// [balancewalk]
// Replace each '?' independently with '(' or ')'. Count balanced results.
inline int bracket_completions(const std::string& s, int mod) {
    assert(mod >= 1);
    int n = static_cast<int>(s.size());
    std::vector<i64> ways(n + 1), next(n + 1);
    ways[0] = 1 % mod;
    for (int i = 0; i < n; ++i) {
        std::fill(next.begin(), next.end(), 0);
        for (int open = 0; open <= i; ++open) {
            if (s[i] != ')')
                next[open + 1] = (next[open + 1] + ways[open]) % mod;
            if (s[i] != '(' && open > 0)
                next[open - 1] = (next[open - 1] + ways[open]) % mod;
        }
        ways.swap(next);
    }
    return static_cast<int>(ways[0]);
}

// Each nonempty interval counts once if at least one replacement works.
inline i64 possible_bracket_intervals(const std::string& s) {
    int n = static_cast<int>(s.size());
    i64 answer = 0;
    for (int left = 0; left < n; ++left) {
        int low = 0, high = 0;
        for (int right = left; right < n; ++right) {
            char c = s[right];
            high += (c == ')' ? -1 : 1);
            if (high < 0) break;
            if (c == '(') ++low;
            else low = (low == 0 ? 1 : low - 1);
            if (low == 0) ++answer;
        }
    }
    return answer;
}
// [/balancewalk]

// [paldelete]
// One move erases any contiguous palindrome in the current sequence.
inline int palindrome_deletions(const std::vector<int>& a) {
    int n = static_cast<int>(a.size());
    std::vector<std::vector<int>> cost(n + 1, std::vector<int>(n + 1));
    for (int left = n - 1; left >= 0; --left) {
        for (int right = left; right < n; ++right) {
            cost[left][right] = 1 + cost[left + 1][right];
            for (int partner = left + 1; partner <= right; ++partner) {
                if (a[left] != a[partner]) continue;
                int wrapped = std::max(1, cost[left + 1][partner - 1]);
                cost[left][right] = std::min(cost[left][right],
                                             wrapped + cost[partner + 1][right]);
            }
        }
    }
    return n == 0 ? 0 : cost[0][n - 1];
}
// [/paldelete]

// [sortedends]
// Order the input to minimize the sum of max(prefix) - min(prefix).
inline i64 minimum_prefix_spread(std::vector<int> a) {
    std::sort(a.begin(), a.end());
    int n = static_cast<int>(a.size());
    std::vector<i64> cost(n);
    for (int len = 2; len <= n; ++len) {
        // Both cells still describe length len - 1 as left advances.
        for (int left = 0; left <= n - len; ++left) {
            int right = left + len - 1;
            i64 width = static_cast<i64>(a[right]) - a[left];
            cost[left] = width + std::min(cost[left], cost[left + 1]);
        }
    }
    return n == 0 ? 0 : cost[0];
}
// [/sortedends]

// [exactcoins]
// Positive sizes, unlimited stock. Return -1 when target cannot be made.
inline int minimum_coin_count(int target, const std::vector<int>& sizes) {
    assert(target >= 0);
    std::vector<int> fewest(static_cast<std::size_t>(target) + 1, -1);
    fewest[0] = 0;
    for (int total = 1; total <= target; ++total) {
        for (int size : sizes) {
            assert(size > 0);
            if (size > total || fewest[total - size] < 0) continue;
            int candidate = 1 + fewest[total - size];
            if (fewest[total] < 0 || candidate < fewest[total])
                fewest[total] = candidate;
        }
    }
    return fewest[target];
}
// [/exactcoins]

// [posteriorcards]
// Given a common rate chosen uniformly from [0,1], the initial card
// orientations are conditionally independent. Process them left to right.
inline long double optimal_card_time(int n, long double correct,
                                     long double flip_one, long double flip_rest) {
    assert(n >= 0);
    std::vector<long double> next(n + 1, 0), current(n + 1);
    for (int seen = n - 1; seen >= 0; --seen) {
        for (int bad = 0; bad <= seen; ++bad) {
            long double chance_bad = (bad + 1.0L) / (seen + 2.0L);
            long double good_cost = correct + next[bad];
            long double repair_one = flip_one + next[bad + 1];
            long double reverse_rest = flip_rest + next[seen - bad];
            current[bad] = (1 - chance_bad) * good_cost
                         + chance_bad * std::min(repair_one, reverse_rest);
        }
        current.swap(next);
    }
    return next[0];
}
// [/posteriorcards]

} // namespace guide
