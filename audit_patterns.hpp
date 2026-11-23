#pragma once
#include <algorithm>
#include <cstdint>
#include <map>
#include <numeric>
#include <string>
#include <utility>
#include <vector>

namespace audit_dp {
using i64 = std::int64_t;
constexpr i64 mod = 1'000'000'007;

// Positive denominations, nonnegative stocks, total value fits in int64_t.
inline i64 covered_prefix(std::vector<std::pair<i64, i64>> coins) {
  std::sort(coins.begin(), coins.end());
  i64 reach = 0;
  for (auto [weight, stock] : coins) {
    if (stock == 0)
      continue;
    if (weight - 1 > reach)
      break;
    reach += weight * stock;
  }
  return reach;
}

// The number of index triples spelling QAQ. The answer must fit in int64_t.
inline i64 count_qaq(const std::string &text) {
  i64 left = 0, right = std::count(text.begin(), text.end(), 'Q'), answer = 0;
  for (char c : text) {
    if (c == 'Q') {
      --right;
      ++left;
    }
    if (c == 'A')
      answer += left * right;
  }
  return answer;
}

// Select disjoint closed intervals, scoring the XOR of their distinct
// nonnegative values.
inline i64 closed_interval_score(const std::vector<int> &a) {
  const int n = int(a.size());
  std::vector<int> keys = a;
  std::sort(keys.begin(), keys.end());
  keys.erase(std::unique(keys.begin(), keys.end()), keys.end());
  std::vector<int> id(n), first(keys.size(), n), last(keys.size(), -1),
      seen(keys.size(), -1);
  for (int i = 0; i < n; ++i) {
    id[i] =
        int(std::lower_bound(keys.begin(), keys.end(), a[i]) - keys.begin());
    first[id[i]] = std::min(first[id[i]], i);
    last[id[i]] = i;
  }
  std::vector<i64> best(n + 1);
  for (int l = 0; l < n; ++l) {
    best[l + 1] = std::max(best[l + 1], best[l]);
    int end_needed = l, reward = 0;
    for (int r = l; r < n; ++r) {
      int x = id[r];
      if (first[x] < l)
        break;
      end_needed = std::max(end_needed, last[x]);
      if (seen[x] != l) {
        reward ^= a[r];
        seen[x] = l;
      }
      if (r == end_needed)
        best[r + 1] = std::max(best[r + 1], best[l] + reward);
    }
  }
  return best[n];
}

// At each leaf call visit(omitted_index,
// table_of_best_values_at_every_capacity). Items have positive integer weights.
// Values and any feasible sum fit in int64_t.
template <class Visitor>
void knapsack_without_each(const std::vector<std::pair<int, i64>> &items,
                           int capacity, Visitor visit) {
  if (items.empty())
    return;
  auto add = [&](std::vector<i64> &table, int first, int last) {
    for (int i = first; i < last; ++i) {
      auto [weight, value] = items[i];
      for (int c = capacity; c >= weight; --c)
        table[c] = std::max(table[c], table[c - weight] + value);
    }
  };
  auto descend = [&](auto &&self, int l, int r,
                     const std::vector<i64> &outside) -> void {
    if (r - l == 1) {
      visit(l, outside);
      return;
    }
    int m = l + (r - l) / 2;
    {
      auto next = outside;
      add(next, m, r);
      self(self, l, m, next);
    }
    {
      auto next = outside;
      add(next, l, m);
      self(self, m, r, next);
    }
  };
  descend(descend, 0, int(items.size()), std::vector<i64>(capacity + 1));
}

// Entry j counts length-n strings over a distinct-character alphabet whose LCS
// with target is exactly j, modulo mod. Intended for small target lengths.
inline std::vector<i64> count_by_lcs(const std::string &target,
                                     const std::string &alphabet, int n) {
  using Row = std::vector<int>;
  std::map<Row, i64> states{{Row(target.size() + 1), 1}};
  for (int i = 0; i < n; ++i) {
    std::map<Row, i64> next;
    for (const auto &[row, count] : states) {
      for (char c : alphabet) {
        Row after(row.size());
        for (std::size_t j = 1; j < row.size(); ++j)
          after[j] = (c == target[j - 1]) ? row[j - 1] + 1
                                          : std::max(row[j], after[j - 1]);
        auto &ways = next[after];
        ways = (ways + count) % mod;
      }
    }
    states.swap(next);
  }
  std::vector<i64> answer(target.size() + 1);
  for (const auto &[row, count] : states)
    answer[row.back()] = (answer[row.back()] + count) % mod;
  return answer;
}

// Uniform draws from 1..m. Index g gives the expected additional draws to
// gcd 1. The transparent quadratic version is intended for small m.
inline std::vector<long double> gcd_waits(int m) {
  std::vector<long double> wait(m + 1);
  for (int g = 2; g <= m; ++g) {
    long double rhs = m;
    int stays = 0;
    for (int x = 1; x <= m; ++x) {
      int d = std::gcd(g, x);
      if (d == g)
        ++stays;
      else
        rhs += wait[d];
    }
    wait[g] = rhs / (m - stays);
  }
  return wait;
}

// Count nonempty index subsets whose every pair has XOR <= bound, modulo mod.
// All input values and bound must fit in bits low bits, with 1 <= bits <= 31.
class XorSubsets {
  struct Node {
    int count = 0;
    int child[2] = {-1, -1};
  };
  std::vector<Node> nodes{Node{}};
  std::vector<i64> pow2;
  unsigned bound;
  int bits;
  int count(int u) const { return u < 0 ? 0 : nodes[u].count; }
  i64 empty_side(int u, int v) const {
    return (pow2[count(u)] + pow2[count(v)] - 1 + mod) % mod;
  }
  // Both selected sides are nonempty. Only pairs between the sides are tested.
  i64 cross(int u, int v, int bit) const {
    if (u < 0 || v < 0)
      return 0;
    if (bit < 0)
      return (pow2[count(u)] - 1) * (pow2[count(v)] - 1) % mod;
    auto a = nodes[u].child, b = nodes[v].child;
    if (((bound >> bit) & 1U) == 0)
      return (cross(a[0], b[0], bit - 1) + cross(a[1], b[1], bit - 1)) % mod;
    i64 x = (cross(a[0], b[1], bit - 1) + empty_side(a[0], b[1])) % mod;
    i64 y = (cross(a[1], b[0], bit - 1) + empty_side(a[1], b[0])) % mod;
    return (x * y % mod - empty_side(u, v) + mod) % mod;
  }
  i64 within(int u, int bit) const {
    if (u < 0)
      return 0;
    if (bit < 0)
      return (pow2[count(u)] - 1 + mod) % mod;
    int a = nodes[u].child[0], b = nodes[u].child[1];
    if (((bound >> bit) & 1U) == 0)
      return (within(a, bit - 1) + within(b, bit - 1)) % mod;
    return (pow2[count(a)] + pow2[count(b)] - 2 + cross(a, b, bit - 1) + mod) %
           mod;
  }

public:
  XorSubsets(const std::vector<unsigned> &values, unsigned limit, int bit_count)
      : pow2(values.size() + 1, 1), bound(limit), bits(bit_count) {
    for (std::size_t i = 1; i < pow2.size(); ++i)
      pow2[i] = pow2[i - 1] * 2 % mod;
    for (unsigned x : values) {
      int u = 0;
      ++nodes[u].count;
      for (int k = bits - 1; k >= 0; --k) {
        unsigned side = (x >> k) & 1U;
        int v = nodes[u].child[side];
        if (v < 0) {
          v = int(nodes.size());
          nodes[u].child[side] = v;
          nodes.emplace_back();
        }
        u = v;
        ++nodes[u].count;
      }
    }
  }
  i64 answer() const { return within(0, bits - 1); }
};
} // namespace audit_dp
