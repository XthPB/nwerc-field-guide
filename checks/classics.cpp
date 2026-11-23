#include "../companion.hpp"
#include <cmath>
#include <iostream>
#include <map>
#include <stdexcept>

using guide::i64;
using std::string;
using std::vector;

static int comparisons = 0;

static void check(bool correct, const char* method) {
    ++comparisons;
    if (!correct) throw std::runtime_error(method);
}

template<class Visit>
void words(string& prefix, const string& alphabet, std::size_t limit, Visit visit) {
    visit(prefix);
    if (prefix.size() == limit) return;
    for (char c : alphabet) {
        prefix.push_back(c);
        words(prefix, alphabet, limit, visit);
        prefix.pop_back();
    }
}

static bool balanced(const string& text) {
    int depth = 0;
    for (char c : text) {
        depth += (c == '(' ? 1 : -1);
        if (depth < 0) return false;
    }
    return depth == 0;
}

static int brute_fillings(string text) {
    auto unknown = text.find('?');
    if (unknown == string::npos) return balanced(text) ? 1 : 0;
    text[unknown] = '(';
    int answer = brute_fillings(text);
    text[unknown] = ')';
    return answer + brute_fillings(text);
}

static void test_brackets(const string& text) {
    int total = brute_fillings(text);
    for (int mod : {1, 7, 998244353})
        check(guide::bracket_completions(text, mod) == total % mod, "bracket fillings");
    int intervals = 0, best = 0, ways = 1;
    for (std::size_t left = 0; left < text.size(); ++left) {
        for (std::size_t len = 1; left + len <= text.size(); ++len) {
            if (!brute_fillings(text.substr(left, len))) continue;
            ++intervals;
            if (static_cast<int>(len) > best) {
                best = static_cast<int>(len);
                ways = 1;
            } else if (static_cast<int>(len) == best) {
                ++ways;
            }
        }
    }
    check(guide::possible_bracket_intervals(text) == intervals, "feasible intervals");
    if (text.find('?') == string::npos)
        check(guide::longest_brackets(text) == std::make_pair(best, ways), "balanced suffix");
}

static int brute_erase(const string& text, std::map<string, int>& known) {
    auto saved = known.find(text);
    if (saved != known.end()) return saved->second;
    int best = static_cast<int>(text.size());
    for (std::size_t i = 0; i < text.size(); ++i) {
        for (std::size_t len = 1; i + len <= text.size(); ++len) {
            string part = text.substr(i, len);
            if (!std::equal(part.begin(), part.end(), part.rbegin())) continue;
            best = std::min(best, 1 + brute_erase(text.substr(0, i) + text.substr(i + len), known));
        }
    }
    known[text] = best;
    return best;
}

static i64 brute_spread(vector<int> values) {
    if (values.empty()) return 0;
    i64 best = std::numeric_limits<i64>::max();
    std::sort(values.begin(), values.end());
    do {
        int low = values.front(), high = values.front();
        i64 sum = 0;
        for (int x : values) {
            low = std::min(low, x);
            high = std::max(high, x);
            sum += static_cast<i64>(high) - low;
        }
        best = std::min(best, sum);
    } while (std::next_permutation(values.begin(), values.end()));
    return best;
}

static void test_arrays(const string& text) {
    const int symbol[] = {-3, 0, 4};
    vector<int> values;
    for (char c : text) values.push_back(symbol[c - 'a']);
    auto prefix = guide::prefix_sums(values);
    std::map<i64, i64> counts;
    i64 best = std::numeric_limits<i64>::lowest();
    for (std::size_t l = 0; l <= values.size(); ++l) {
        i64 sum = 0;
        for (std::size_t r = l; r < values.size(); ++r) {
            sum += values[r];
            check(prefix[r + 1] - prefix[l] == sum, "prefix sum");
            ++counts[sum];
            best = std::max(best, sum);
        }
    }
    check(prefix.front() == 0, "empty prefix");
    for (int target = -4; target <= 4; ++target)
        check(guide::subarray_sum_count(values, target) == counts[target], "prefix frequencies");
    if (!values.empty()) check(guide::maximum_nonempty_subarray(values) == best, "Kadane");
    check(guide::minimum_prefix_spread(values) == brute_spread(values), "sorted endpoints");
}

static void test_coins() {
    const int target = 24;
    for (int mask = 0; mask < 32; ++mask) {
        vector<int> sizes;
        for (int k = 1; k <= 5; ++k) if (mask & (1 << (k - 1))) sizes.push_back(k);
        vector<int> distance(target + 1, -1);
        std::queue<int> pending;
        pending.push(0);
        distance[0] = 0;
        while (!pending.empty()) {
            int sum = pending.front();
            pending.pop();
            for (int k : sizes) {
                if (sum + k <= target && distance[sum + k] < 0) {
                    distance[sum + k] = distance[sum] + 1;
                    pending.push(sum + k);
                }
            }
        }
        for (int t = 0; t <= target; ++t)
            check(guide::minimum_coin_count(t, sizes) == distance[t], "exact coin change");
    }
}

// Enumerate physical initial layouts and branch on the actual observations.
// Uniform bias gives each possible total number of bad cards equal mass.
// Keep each layout's unconditional mass throughout the decision tree.
using Layout = std::pair<int, long double>;
static long double brute_cards(int index, int n, bool flipped,
                               const vector<Layout>& layouts, int ok, int one, int rest) {
    if (index == n || layouts.empty()) return 0;
    vector<Layout> good, bad;
    long double good_mass = 0, bad_mass = 0;
    for (auto layout : layouts) {
        bool initially_bad = (layout.first >> index) & 1;
        if (initially_bad != flipped) {
            bad.push_back(layout);
            bad_mass += layout.second;
        } else {
            good.push_back(layout);
            good_mass += layout.second;
        }
    }
    return good_mass * ok + brute_cards(index + 1, n, flipped, good, ok, one, rest)
         + std::min(bad_mass * one + brute_cards(index + 1, n, flipped, bad, ok, one, rest),
                    bad_mass * rest + brute_cards(index + 1, n, !flipped, bad, ok, one, rest));
}

static void test_cards() {
    for (int n = 0; n <= 6; ++n) {
        vector<int> frequencies(n + 1);
        for (int mask = 0; mask < (1 << n); ++mask)
            ++frequencies[__builtin_popcount(static_cast<unsigned>(mask))];
        vector<Layout> layouts;
        for (int mask = 0; mask < (1 << n); ++mask) {
            int bits = __builtin_popcount(static_cast<unsigned>(mask));
            layouts.emplace_back(mask, 1.0L / ((n + 1) * frequencies[bits]));
        }
        for (int ok = 1; ok <= 3; ++ok)
            for (int one = 2; one <= 5; ++one)
                for (int rest = 1; rest <= 6; ++rest) {
                    long double brute = brute_cards(0, n, false, layouts, ok, one, rest);
                    check(std::abs(guide::optimal_card_time(n, ok, one, rest) - brute) < 1e-10L,
                          "shared hidden bias and optimal action");
                }
    }
}

int main() {
    string prefix;
    words(prefix, "()?", 7, test_brackets);
    words(prefix, "abc", 6, test_arrays);
    std::map<string, int> deletions{{"", 0}};
    words(prefix, "abc", 7, [&](const string& text) {
        vector<int> labels(text.begin(), text.end());
        check(guide::palindrome_deletions(labels) == brute_erase(text, deletions), "palindrome deletion");
    });
    test_coins();
    test_cards();
    check(guide::minimum_prefix_spread({1, 4, 5, 10}) == 14, "published example");
    check(guide::subarray_sum_count({0, 1, -1, 0}, 0) == 6, "published example");
    check(guide::maximum_nonempty_subarray({-3, 4, -1, 2, -5}) == 5, "published example");
    check(guide::minimum_prefix_spread({INT32_MIN, INT32_MAX}) == 4294967295LL, "wide spread");
    std::cout << comparisons << " comparisons passed across ten C++17 functions.\n";
}
