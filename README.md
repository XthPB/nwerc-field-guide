# NWERC Field Guide

[Read the NWERC Field Guide](https://xthpb.github.io/nwerc-field-guide/)

The [subject tracks](https://xthpb.github.io/nwerc-field-guide/#subjects) include 138 new worked lessons, 32 foundation articles and 61 BAPC case studies. The [practice index](https://xthpb.github.io/nwerc-field-guide/practice.html) provides rating and intersecting-tag filters for 10,384 Codeforces IDs. The [tag-pair explorer](https://xthpb.github.io/nwerc-field-guide/combinations.html) covers all 570 observed official tag pairs at 2000–3000. The [50 follow-up technique notes](https://xthpb.github.io/nwerc-field-guide/followup.html) complement the one-problem walkthroughs. The [advanced DP workshops](https://xthpb.github.io/nwerc-field-guide/tracks/advanced.html) cover one individually derived problem per band from 1700 to 3000. Run the [Python differential checks](checks/advanced_workshops.py) with Python 3.9 or newer.

The [six-part reading path](https://xthpb.github.io/nwerc-field-guide/path.html) connects 235 lessons in 34 units, from a first prefix table to combined contest techniques. The 21 topic chapters provide a shorter route to individual subjects. Each lesson walks through an example, explains the state and update, and asks a small variation with a revealable answer. Equations, diagrams, filters and step controls work offline after downloading the repository and opening `index.html`.

- [Audit of 1,500 Codeforces DP problems, rated 800–3000](https://xthpb.github.io/nwerc-field-guide/audit.html)
- [Why each child needs a different rerooting message](https://xthpb.github.io/nwerc-field-guide/lessons/rerootproduct.html)
- [When the next coin leaves a gap](https://xthpb.github.io/nwerc-field-guide/lessons/contiguouscoins.html)
- [Which voting groups need every member?](https://xthpb.github.io/nwerc-field-guide/lessons/pivotweight.html)
- [Can the cashier make an unsplittable payout?](https://xthpb.github.io/nwerc-field-guide/lessons/adversarycoins.html)
- [Visit every city with a set and a last stop](https://xthpb.github.io/nwerc-field-guide/lessons/tour.html)
- [Grid and lattice paths](https://xthpb.github.io/nwerc-field-guide/08-grids.html)
- [Digit DP and large bounds](https://xthpb.github.io/nwerc-field-guide/10-digits.html)
- [Search the problem index](https://xthpb.github.io/nwerc-field-guide/codeforces.html)
- [Browse code templates](https://xthpb.github.io/nwerc-field-guide/templates.html)
- [Follow the contest coverage map](https://xthpb.github.io/nwerc-field-guide/coverage.html)
- [Compare the same idea across contest problems](https://xthpb.github.io/nwerc-field-guide/coverage.html#shared)
- [See the most-solved Codeforces examples in five rating bands](https://xthpb.github.io/nwerc-field-guide/coverage.html#classics)
- [Read the sources and checks](https://xthpb.github.io/nwerc-field-guide/sources.html)

The seeded audit spans all 23 rating bands. Each row links to its evidence and cheat-sheet pages, and identifies how the templates were selected. The [results CSV](assets/dp-audit.csv), [sampling frame](assets/audit-frame.csv) and [draw verification](checks/draw_audit.py) are available for reuse.

The public template pages are read-only copies of relevant ICPC cheat-sheet sections and DP companion material. The problem index identifies authored mappings, code-supported building blocks and tag-based starting points. NWERC 2022 and 2023 problem details are withheld for practice.

The site runs directly from the repository root on GitHub Pages. Font and KaTeX notices are included in `assets/`.

The [verification code](checks/) includes brute-force oracles for the C++17 headers and independent Python checks for selected derivations.

The [per-subject inventory](https://xthpb.github.io/nwerc-field-guide/subjects-inventory.html) gives distinct family counts and links to published implementations. The [catalogue check](checks/contest_catalog.py) recomputes every tag-pair count and reconciles the search index with the downloadable CSV files.
