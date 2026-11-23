#include "../audit_patterns.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
#include <random>
#include <set>
using namespace audit_dp;
int main() {
  std::mt19937 gen(19731);
  int cases = 0;
  for (int it = 0; it < 320; ++it) {
    int n = gen() % 9;
    std::vector<int> a(n);
    for (int &x : a)
      x = int(gen() % 8);
    std::vector<unsigned> a_unsigned(a.begin(), a.end());
    std::vector<std::pair<i64, i64>> coins;
    std::vector<std::pair<int, i64>> items;
    for (int v : a) {
      coins.push_back({v + 1, 1});
      items.push_back({v + 1, int(gen() % 15) - 3});
    }
    std::set<int> sums;
    for (int mask = 0; mask < (1 << n); ++mask) {
      int value = 0;
      for (int i = 0; i < n; ++i)
        if (mask >> i & 1)
          value += a[i] + 1;
      sums.insert(value);
    }
    int missing = 0;
    while (sums.count(missing))
      ++missing;
    assert(covered_prefix(coins) == missing - 1);
    ++cases;
    for (unsigned k = 0; k < 8; ++k) {
      int want = 0;
      for (int m = 1; m < (1 << n); ++m) {
        bool valid = true;
        for (int i = 0; i < n; ++i)
          for (int j = 0; j < i; ++j)
            if ((m >> i & 1) && (m >> j & 1) && unsigned(a[i] ^ a[j]) > k)
              valid = false;
        want += valid;
      }
      assert(XorSubsets(a_unsigned, k, 3).answer() == want);
      ++cases;
    }
    // Exhaust every possible next interval without using first/last
    // preprocessing.
    auto closed = [&](auto &&self, int pos) -> i64 {
      if (pos == n)
        return 0;
      i64 win = self(self, pos + 1);
      for (int end = pos; end < n; ++end) {
        std::set<int> vals(a.begin() + pos, a.begin() + end + 1);
        bool ok = true;
        for (int j = 0; j < n; ++j)
          if ((j < pos || j > end) && vals.count(a[j]))
            ok = false;
        if (ok) {
          int value = 0;
          for (int x : vals)
            value ^= x;
          win = std::max(win, value + self(self, end + 1));
        }
      }
      return win;
    };
    assert(closed_interval_score(a) == closed(closed, 0));
    ++cases;
    int cap = gen() % 10;
    knapsack_without_each(items, cap,
                          [&](int skip, const std::vector<i64> &table) {
                            for (int b = 0; b <= cap; ++b) {
                              i64 optimum = 0;
                              for (int m = 0; m < (1 << n); ++m)
                                if (!(m >> skip & 1)) {
                                  int wt = 0;
                                  i64 val = 0;
                                  for (int i = 0; i < n; ++i)
                                    if (m >> i & 1) {
                                      wt += items[i].first;
                                      val += items[i].second;
                                    }
                                  if (wt <= b)
                                    optimum = std::max(optimum, val);
                                }
                              assert(table[b] == optimum);
                              ++cases;
                            }
                          });
  }
  assert(covered_prefix({{7, 1}, {1, 1}, {2, 2}}) == 5);
  assert(covered_prefix({{1, 0}, {2, 3}}) == 0);
  for (int n = 0; n <= 8; ++n) {
    for (int m = 0; m < (1 << n); ++m) {
      std::string text;
      for (int i = 0; i < n; ++i)
        text += (m >> i & 1) ? 'Q' : 'A';
      i64 count = 0;
      for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
          for (int k = j + 1; k < n; ++k)
            count += text[i] == 'Q' && text[j] == 'A' && text[k] == 'Q';
      assert(count_qaq(text) == count);
      ++cases;
    }
  }
  // Independent LCS oracle: enumerate subsequences of the fixed target.
  for (const std::string target : {"", "A", "AB", "BAA", "ABBA"})
    for (int n = 0; n <= 7; ++n) {
      std::vector<i64> hist(target.size() + 1);
      for (int m = 0; m < (1 << n); ++m) {
        std::string word;
        for (int j = 0; j < n; ++j)
          word += (m >> j & 1) ? 'A' : 'B';
        int top = 0;
        for (unsigned mask = 0; mask < (1U << target.size()); ++mask) {
          std::size_t j = 0;
          int length = 0;
          bool found = true;
          for (unsigned i = 0; i < target.size(); ++i)
            if (mask >> i & 1) {
              j = word.find(target[i], j);
              if (j == std::string::npos) {
                found = false;
                break;
              }
              ++j;
              ++length;
            }
          if (found)
            top = std::max(top, length);
        }
        ++hist[top];
      }
      assert(count_by_lcs(target, "AB", n) == hist);
      ++cases;
    }
  // Independent tail-sum expectation: propagate mass of unstopped processes for
  // 1,000 draws.
  for (int m = 1; m <= 12; ++m) {
    auto dp = gcd_waits(m);
    for (int g = 1; g <= m; ++g) {
      std::vector<long double> p(m + 1);
      p[g] = 1;
      long double wait = 0;
      for (int step = 0; step < 1000; ++step) {
        std::vector<long double> next(m + 1);
        for (int d = 2; d <= m; ++d) {
          wait += p[d];
          for (int x = 1; x <= m; ++x)
            next[std::gcd(d, x)] += p[d] / m;
        }
        p.swap(next);
      }
      assert(std::abs(wait - dp[g]) < 1e-10L);
      ++cases;
    }
  }
  std::cout << cases << " comparisons passed\n";
}
