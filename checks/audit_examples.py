"""Independent checks of the eight small contest-connection examples."""
from collections import Counter
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import gcd
from operator import xor


def pairwise_xor_score(bits):
    """Count the arrays directly, without a tight-prefix recurrence."""
    numbers = range(1 << bits)
    return sum((a & b) >= (a ^ b) for a, b in product(numbers, repeat=2))


def interval_cost(values):
    return sum(len(values) - 1 - values[::-1].index(v) - values.index(v)
               for v in set(values))


def star_components(removed):
    """Count components containing marked leaves after the admissible removals."""
    adjacent = [[1, 2, 3], [0], [0], [0]]
    seen = set(removed)
    groups = []
    for start in range(4):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        group = set()
        while stack:
            u = stack.pop()
            if u in (1, 2, 3):
                group.add(u)
            for v in adjacent[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        if group:
            groups.append(group)
    return groups


def main():
    # On a tree with two leaves below a parent, enumerate possible next jumps.
    leaf_slopes = (3, 5)
    parent_cost = min(4 * slope for slope in leaf_slopes)
    assert parent_cost == 12
    assert min([10 * slope for slope in leaf_slopes] + [10 + parent_cost]) == 22

    path = [6, 10, 15]
    counts = Counter(reduce(gcd, path[l:r])
                     for l in range(len(path)) for r in range(l + 1, len(path) + 1))
    assert sum(amount for value, amount in counts.items() if value % 2 == 0) == 3
    assert counts[2] == counts[6] == counts[10] == 1

    # Use geometric slopes to group the points reachable on one selected line.
    points = {'A': (0, 0), 'B': (1, 0), 'C': (2, 0), 'D': (0, 1)}
    directions = {}
    for label, (x, y) in points.items():
        if label != 'A':
            direction = 'vertical' if x == 0 else Fraction(y, x)
            directions.setdefault(direction, ['A']).append(label)
    chances = Counter()
    for line in directions.values():
        for label in line:
            chances[label] += Fraction(1, len(directions) * len(line))
    assert [chances[label] for label in points] == [Fraction(5, 12), Fraction(1, 6),
                                                    Fraction(1, 6), Fraction(1, 4)]

    assert pairwise_xor_score(1) == 2 and pairwise_xor_score(2) == 6
    for old, value, expected in [([1, 2], 1, [2, 0, 0]),
                                 ([1, 2, 1], 1, [1, 1, 1, 0])]:
        actual = [interval_cost(old[start:] + [value]) - interval_cost(old[start:])
                  for start in range(len(old) + 1)]
        assert actual == expected

    routes = ([1, 2, 4], [1, 3, 4])
    assert [reduce(xor, route) for route in routes] == [7, 6]
    assert (1 ^ 2) ^ (2 ^ 4) ^ 2 == 7
    assert len(star_components(set())) == 1 and len(star_components({0})) == 3

    for piles, minimum in [([1, 2, 3], 3), ([1, 2, 3, 3], 2)]:
        sizes = [size for size in range(1, len(piles) + 1)
                 for subset in combinations(piles, size) if reduce(xor, subset) == 0]
        assert min(sizes) == minimum
    print('Eight cross-topic examples passed.')


if __name__ == '__main__':
    main()
