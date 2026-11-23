"""Reconcile the hard-problem source scan, official snapshot and public search filters."""
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def read_rows(filename):
    with (ASSETS / filename).open(encoding="utf-8", newline="") as f:
        return {row["problem"]: row for row in csv.DictReader(f)}


def verify():
    catalogue = read_rows("contest-index.csv")
    rows = read_rows("hard-scan.csv")
    payload, selections = (ASSETS / "hard-scan.js").read_text().strip().split("\nwindow.hardSelections = ")
    data = json.loads(payload.removeprefix("window.hardScan = ").removesuffix(";"))
    chosen = set(json.loads(selections.removesuffix(";")))
    assert set(data) == set(rows) == {k for k,r in catalogue.items() if 2000 < int(r["rating"]) <= 3000}
    assert chosen == {k for k,r in rows.items() if r["new_lesson"]}
    counters = Counter()
    for k,r in rows.items():
        for name in ("title","rating","official_tags","sharing_family","worked_or_mapped_lessons"):
            assert r[name] == catalogue[k][name], (k,name)
        statement, prose, implementation, pwords, iwords = data[k]
        assert statement and [statement,prose,implementation] == [r["statement_source"],r["solution_text_source"],r["implementation_source"]]
        for url in (v for v in [statement,prose,implementation] if v):
            assert urlsplit(url).scheme == "https" and urlsplit(url).hostname, (k,url)
        assert "|".join(pwords)==r["terms_in_solution_text"] and "|".join(iwords)==r["terms_in_implementation"]
        assert (prose or not pwords) and (implementation or not iwords)
        if k in chosen:
            article = (ROOT / r["new_lesson"]).read_text()
            assert r["new_lesson"] in r["worked_or_mapped_lessons"].split("|")
            assert 'class="worked-steps"' in article and "data-trace" in article
            assert "Show the reasoning" in article and "../templates/" in article
            contest,index = re.fullmatch(r"(\d+)([A-Z]\d*)",k).groups()
            assert "https://codeforces.com/problemset/problem/"+contest+"/"+index in article
            assert "dp" not in r["official_tags"].split("|")
        if "dp" not in r["official_tags"].split("|"):
            counters["problems"]+=1
            counters["solution or code"]+=bool(prose or implementation)
            counters["statement only"]+=not (prose or implementation)
            counters["previous mappings"]+=bool(r["earlier_lesson_paths"])
            counters["current mappings"]+=bool(r["worked_or_mapped_lessons"])
            counters["untagged"]+=not r["official_tags"]
    assert counters["problems"] == counters["solution or code"] + counters["statement only"]
    print(len(rows),"source-indexed problems,",len(chosen),"new worked lessons")
    print(dict(counters))


if __name__ == "__main__":
    verify()
