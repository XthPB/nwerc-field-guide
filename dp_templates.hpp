#pragma once
#include <algorithm>
#include <array>
#include <bitset>
#include <cstdint>
#include <limits>
#include <numeric>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace nwerc_dp {
using i64 = std::int64_t;

// [bitset]
// One-use nonnegative weights. W is the largest sum the caller wants.
template <std::size_t W>
std::bitset<W+1> reachable(const std::vector<int>& weights) {
    std::bitset<W+1> bits;
    bits.set(0);
    for (int weight : weights) {
        bits |= bits << weight;
    }
    return bits;
}
// [/bitset]

// [adversarycoins]
// NWERC 2025 B, 1 <= total <= 10000. An empty result means every payout splits.
inline std::vector<int> unsplittable_payout(int total) {
    if (total % 2) return std::vector<int>(total, 1);
    const std::array<int, 7> low{1, 2, 5, 10, 20, 50, 100};
    const std::array<int, 7> limit{1, 4, 1, 1, 4, 1, 1};
    std::array<int, 7> counts{};
    std::vector<int> witness;
    auto search = [&](auto&& self, int type, int left) -> bool {
        if (type < static_cast<int>(low.size())) {
            for (int k = 0; k <= limit[type] && k * low[type] <= left; ++k) {
                counts[type] = k;
                if (self(self, type + 1, left - k * low[type])) return true;
            }
            return false;
        }
        for (int fives = 0; 500 * fives <= left; ++fives) {
            int rest = left - 500 * fives;
            if (rest % 200) continue;
            std::vector<int> payout;
            for (int i = 0; i < static_cast<int>(low.size()); ++i) {
                payout.insert(payout.end(), counts[i], low[i]);
            }
            payout.insert(payout.end(), rest / 200, 200);
            payout.insert(payout.end(), fives, 500);
            if (!reachable<5000>(payout)[total / 2]) {
                witness = std::move(payout);
                return true;
            }
        }
        return false;
    };
    search(search, 0, total);
    return witness;
}
// [/adversarycoins]

// [pivotweight]
// Positive weights, n <= 60 and total weight fitting an int.
inline i64 minimal_majorities(std::vector<int> weights) {
    int half = std::accumulate(weights.begin(), weights.end(), 0) / 2;
    std::sort(weights.rbegin(), weights.rend());
    std::vector<i64> ways(half + 1);
    ways[0] = 1;
    i64 result = 0;
    for (int weight : weights) {
        for (int s = std::max(0, half - weight + 1); s <= half; ++s) {
            result += ways[s];
        }
        for (int s = half; s >= weight; --s) {
            ways[s] += ways[s - weight];
        }
    }
    return result;
}
// [/pivotweight]

// [exactjoin]
// Includes the empty subset. All sums, complements, and the result must fit i64.
inline std::vector<i64> half_sums(const std::vector<i64>& a, int lo, int hi) {
    std::vector<i64> sums{0};
    for (int i = lo; i < hi; ++i) {
        auto old_size = sums.size();
        sums.resize(2 * old_size);
        for (std::size_t j = 0; j < old_size; ++j) {
            sums[old_size + j] = sums[j] + a[i];
        }
    }
    return sums;
}
inline i64 count_subset_sum(const std::vector<i64>& a, i64 target) {
    int mid = static_cast<int>(a.size()) / 2;
    auto left = half_sums(a, 0, mid);
    auto right = half_sums(a, mid, static_cast<int>(a.size()));
    std::sort(right.begin(), right.end());
    i64 count = 0;
    for (i64 sum : left) {
        auto bounds = std::equal_range(right.begin(), right.end(), target - sum);
        count += bounds.second - bounds.first;
    }
    return count;
}
// [/exactjoin]

// [lis]
// A strict LIS, returning indices. For nondecreasing use upper_bound.
inline std::vector<int> lis_indices(const std::vector<i64>& a) {
    std::vector<i64> tails;
    std::vector<int> end, parent(a.size(), -1);
    for (int i = 0; i < static_cast<int>(a.size()); ++i) {
        int k = std::lower_bound(tails.begin(), tails.end(), a[i]) - tails.begin();
        if (k > 0) parent[i] = end[k-1];
        if (k == static_cast<int>(tails.size())) {
            tails.push_back(a[i]);
            end.push_back(i);
        } else {
            tails[k] = a[i];
            end[k] = i;
        }
    }
    std::vector<int> chain;
    for (int i = end.empty() ? -1 : end.back(); i != -1; i = parent[i]) {
        chain.push_back(i);
    }
    std::reverse(chain.begin(), chain.end());
    return chain;
}
// [/lis]

// [sos]
// Nonempty array of power-of-two length. Sums must fit i64.
inline std::vector<i64> subset_zeta(std::vector<i64> a) {
    for (std::size_t bit = 1; bit < a.size(); bit *= 2) {
        for (std::size_t mask = 0; mask < a.size(); ++mask) {
            if (mask & bit) a[mask] += a[mask ^ bit];
        }
    }
    return a;
}
// [/sos]

// [tight]
// Counts integers in [0,n] with at most three nonzero decimal digits.
inline i64 classy(i64 n) {
    if (n < 0) return 0;
    std::array<std::array<i64,4>,2> cur{};
    cur[1][0] = 1;
    for (char digit : std::to_string(n)) {
        decltype(cur) next{};
        for (int tight = 0; tight <= 1; ++tight) {
            int limit = tight ? digit - '0' : 9;
            for (int used = 0; used <= 3; ++used) {
                for (int d = 0; d <= limit; ++d) {
                    int count = used + (d != 0);
                    if (count <= 3) {
                        next[tight && d == limit][count] += cur[tight][used];
                    }
                }
            }
        }
        cur = next;
    }
    i64 result = 0;
    for (const auto& row : cur) result += std::accumulate(row.begin(), row.end(), i64{0});
    return result;
}
// [/tight]

// [reroot]
// Adjacency list of a connected, unweighted, simple tree.
inline std::vector<i64> distance_sums(const std::vector<std::vector<int>>& graph) {
    int n = static_cast<int>(graph.size());
    if (n == 0) return {};
    std::vector<int> parent(n, -1), order{0}, size(n, 1);
    std::vector<i64> ans(n);
    for (std::size_t i = 0; i < order.size(); ++i) {
        int u = order[i];
        for (int v : graph[u]) {
            if (v == parent[u]) continue;
            parent[v] = u;
            order.push_back(v);
        }
    }
    for (int i = n-1; i > 0; --i) {
        int v = order[i];
        size[parent[v]] += size[v];
        ans[0] += size[v]; // Each root path pays once per edge.
    }
    for (int i = 1; i < n; ++i) {
        int v = order[i];
        ans[v] = ans[parent[v]] + n - 2LL * size[v];
    }
    return ans;
}
// [/reroot]

// [monge]
// Exactly k nonempty pieces, cost squared segment sum. Inputs >= 0.
// Contract: 1 <= k <= n and square of total sum < INF.
inline i64 square_partition(const std::vector<int>& a, int k) {
    const i64 inf = std::numeric_limits<i64>::max()/4;
    int n = static_cast<int>(a.size());
    std::vector<i64> pref(n+1), prev(n+1, inf), next(n+1);
    for (int i = 0; i < n; ++i) pref[i+1] = pref[i] + a[i];
    prev[0] = 0;
    for (int g = 1; g <= k; ++g) {
        std::fill(next.begin(), next.end(), inf);
        auto fill = [&](auto&& self, int l, int r, int lo, int hi) -> void {
            if (l > r) return;
            int mid = l + (r-l)/2, best = lo;
            for (int j = lo; j <= std::min(hi, mid-1); ++j) {
                if (prev[j] == inf) continue;
                i64 width = pref[mid] - pref[j];
                i64 candidate = prev[j] + width*width;
                if (candidate < next[mid]) {
                    next[mid] = candidate;
                    best = j;
                }
            }
            self(self, l, mid-1, lo, best);
            self(self, mid+1, r, best, hi);
        };
        fill(fill, g, n, g-1, n-1);
        prev.swap(next);
    }
    return prev[n];
}
// [/monge]

// [knuth]
// Nonnegative pile weights and all costs fitting i64 below INF.
inline i64 merge_cost(const std::vector<int>& a) {
    int n = static_cast<int>(a.size());
    if (n < 2) return 0;
    std::vector<i64> p(n+1);
    for (int i=0; i<n; ++i) p[i+1]=p[i]+a[i];
    std::vector<std::vector<i64>> d(n, std::vector<i64>(n));
    std::vector<std::vector<int>> opt(n, std::vector<int>(n));
    for (int i=0; i<n; ++i) opt[i][i]=i;
    for (int len=2; len<=n; ++len) {
        for (int l=0; l+len<=n; ++l) {
            int r=l+len-1;
            d[l][r]=std::numeric_limits<i64>::max()/4;
            for (int j=opt[l][r-1]; j<=std::min(r-1,opt[l+1][r]); ++j) {
                i64 cost=d[l][j]+d[j+1][r]+p[r+1]-p[l];
                if (cost<=d[l][r]) {
                    d[l][r]=cost;
                    opt[l][r]=j;
                }
            }
        }
    }
    return d[0][n-1];
}
// [/knuth]

// [xor]
// Length N is a power of two. Initial/kernel entries are in [0,p).
// Requires 2*N*p to fit signed 64 bits; uses GCC/Clang __int128 for products.
inline std::vector<i64> xor_steps(std::vector<i64> initial,
                                  std::vector<i64> kernel,
                                  std::uint64_t steps, i64 p) {
    const i64 n = static_cast<i64>(initial.size()), mod = n*p;
    auto transform = [=](std::vector<i64>& a) {
        for (i64 h=1; h<n; h*=2) {
            for (i64 block=0; block<n; block+=2*h) {
                for (i64 j=block; j<block+h; ++j) {
                    i64 u=a[j], v=a[j+h];
                    a[j]=(u+v)%mod;
                    a[j+h]=(u-v+mod)%mod;
                }
            }
        }
    };
    auto mul = [=](i64 x,i64 y) -> i64 {
        return static_cast<i64>(static_cast<__int128>(x)*y%mod);
    };
    transform(initial);
    transform(kernel);
    for (i64 i=0; i<n; ++i) {
        i64 base=kernel[i], power=1%mod;
        for (auto t=steps; t>0; t>>=1) {
            if (t&1) power=mul(power,base);
            base=mul(base,base);
        }
        initial[i]=mul(initial[i],power);
    }
    transform(initial);
    for (auto& value:initial) value/=n;
    return initial;
}
// [/xor]

// [palcut]
// Count splits into matching outer blocks (their total number must be even).
// Lowercase a-z, even length, result modulo 1e9+7. O(n log n).
inline int mirrored_block_splits(const std::string& s) {
    constexpr int mod = 1000000007;
    struct Node {
        int len=0, link=0, diff=0, series=0, subtotal=0;
        std::array<int,26> next{};
    };
    int n=static_cast<int>(s.size()), last=1;
    std::vector<Node> nodes(2);
    nodes.reserve(n+2);
    nodes[0].len=-1; // Imaginary root. Node 1 is the empty palindrome.
    std::string text(1,'#');
    std::vector<int> ways(n+1);
    ways[0]=1;
    for (int i=1; i<=n; ++i) {
        char ch=(i%2) ? s[(i-1)/2] : s[n-i/2];
        text.push_back(ch);
        int k=ch-'a';
        auto suffix = [&](int v) {
            while (text[i-1-nodes[v].len]!=ch) v=nodes[v].link;
            return v;
        };
        int parent=suffix(last);
        if (!nodes[parent].next[k]) {
            int id=static_cast<int>(nodes.size());
            nodes.emplace_back();
            nodes[parent].next[k]=id;
            auto& cur=nodes[id];
            cur.len=nodes[parent].len+2;
            cur.link=cur.len==1 ? 1 : nodes[suffix(nodes[parent].link)].next[k];
            const auto& link=nodes[cur.link];
            cur.diff=cur.len-link.len;
            cur.series=(cur.diff==link.diff) ? link.series : cur.link;
        }
        last=nodes[parent].next[k];
        for (int v=last; nodes[v].len>0; v=nodes[v].series) {
            auto& u=nodes[v];
            u.subtotal=ways[i-nodes[u.series].len-u.diff];
            if (u.diff==nodes[u.link].diff) {
                u.subtotal=(u.subtotal+nodes[u.link].subtotal)%mod;
            }
            if (i%2==0) ways[i]=(ways[i]+u.subtotal)%mod;
        }
    }
    return ways[n];
}
// [/palcut]
} // namespace nwerc_dp

