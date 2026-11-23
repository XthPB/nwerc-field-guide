"""Reconcile the public practice filters, evidence files and tag-pair counts."""
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def read_csv(name):
    with (ASSETS / name).open(encoding="utf-8", newline="") as table:
        return list(csv.DictReader(table))


def verify():
    payload = (ASSETS / "contest-index.js").read_text(encoding="utf-8")
    data = json.loads(payload.split("=", 1)[1].strip().removesuffix(";"))
    records = {row["problem"]: row for row in read_csv("contest-index.csv")}
    earlier = {row["problem"] for row in read_csv("dp-audit.csv")}
    fresh = {row["problem"]: row for row in read_csv("advanced-dp-follow-up.csv")}
    assert set(records) == {r[0] for r in data["rows"]}
    assert set(data["previous"]) == earlier
    assert set(data["priorFamilies"]) == {int(records[k]["sharing_family"]) for k in earlier if k in records}
    assert not (set(fresh) & earlier)
    pairs = defaultdict(Counter)
    hard_families = defaultdict(set)
    same_file = set()
    tiers = Counter()
    for k, title, rating, tag_ids, family, is_followup in data["rows"]:
        row = records[k]
        tags = [data["tags"][i] for i in tag_ids]
        assert (row["title"], int(row["rating"]), int(row["sharing_family"])) == (title, rating, family)
        assert 800 <= rating <= 3000 and rating % 100 == 0
        assert tags == list(filter(None, row["official_tags"].split("|"))) and len(tags) == len(set(tags))
        assert bool(is_followup) == (k in fresh)
        assert row["published_implementation"] == data["primary"].get(k, "")
        if row["published_implementation"]:
            target = urlsplit(row["published_implementation"])
            assert target.hostname == "github.com" and "/blob/" in target.path and len(target.path.split("/blob/")[1].split("/")[0]) == 40
        mapped = data["mapped"].get(k, [])
        paths = [data["urls"].get(slug, "course/" + slug + ".html") for slug in mapped]
        assert row["worked_or_mapped_lessons"] == "|".join(paths)
        for path in paths:
            same_file.add(path)
        for slug in mapped:
            assert data["titles"][slug] and data["lessonsT"][slug]
            for key in data["lessonsT"][slug]:
                same_file.add("templates/" + key + ".html")
        if k in fresh:
            assert "dp" in tags and rating >= 1700 and fresh[k]["guide_modules"] == "|".join(paths)
            tiers[fresh[k]["depth"]] += 1
        bucket = 0 if rating < 1700 else 1 if rating < 2000 else 2 if rating < 2500 else 3
        for pair in combinations(sorted(tags), 2):
            pairs[pair][bucket] += 1
            if rating >= 2000:
                pairs[pair]["mapped"] += bool(mapped)
                hard_families[pair].add(family)
    for path in same_file:
        name, _, fragment = path.partition("#")
        assert (ROOT / name).is_file(), name
        if fragment:
            assert ('id="' + fragment + '"') in (ROOT / name).read_text(encoding="utf-8")
    rows = read_csv("tag-pairs.csv")
    assert len(rows) == len(pairs)
    for row in rows:
        key = (row["first_tag"], row["second_tag"])
        fields = ["800_to_1600_ids", "1700_to_1900_ids", "2000_to_2400_ids", "2500_to_3000_ids"]
        for i, col in enumerate(fields):
            assert int(row[col]) == pairs[key][i], (key, col)
        assert int(row["mapped_2000_to_3000_ids"]) == pairs[key]["mapped"]
        assert int(row["2000_to_3000_families"]) == len(hard_families[key])
    print(f"{len(records):,} official IDs, {len(rows)} tag pairs across all ratings, "
          f"{len(fresh)} DP follow-up families, {len(data['primary']):,} implementation links")
    print(dict(tiers))


if __name__ == "__main__":
    verify()
