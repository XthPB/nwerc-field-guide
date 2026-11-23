"""Validate the opening a reader sees on each lesson and its linked previews."""
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


def document(path):
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def prompt(node):
    return node.get_text(" ", strip=True)


def opening(page, path):
    main = page.select_one("main")
    first = main.h1.find_next_sibling()
    assert first is not None and first.name == "p", path
    assert "problem-context" in first.get("class", ()), path
    assert len(prompt(first).split()) >= 12, path
    assert len(main.select("p.lead.problem-context")) == 1, path
    return prompt(first)


def main():
    chapters = sorted(ROOT.glob("[0-9]*.html"))
    tracks = sorted((ROOT / "tracks").glob("*.html"))
    lessons = {}
    case_notes = Counter()
    for folder in ("lessons", "course", "reference", "regional"):
        pattern = "foundations-*.html" if folder == "reference" else "*.html"
        for path in sorted((ROOT / folder).glob(pattern)):
            page = document(path)
            key = path.relative_to(ROOT).as_posix()
            lessons[key] = opening(page, path)
            if folder == "lessons":
                example = next(h for h in page.select("h2") if "Work one example" in prompt(h))
                figure = example.find_next_sibling()
                assert figure.name == "figure" and figure.find_next_sibling().name == "p", path
                for item in page.select("details.technical ul.indexlist li"):
                    if item.find("p", recursive=False):
                        case = item.find("p", recursive=False)
                        assert "case-brief" in case.get("class", ()), (path, prompt(item.a))
                        assert case.find_next_sibling("p") is not None, path
                        case_notes[prompt(case)] += 1
    assert len(set(lessons.values())) == len(lessons), "A lesson reuses another lesson's opening"
    for path in [*chapters, *tracks, ROOT / "dp.html"]:
        opening(document(path), path)
    index = document(ROOT / "methods.html")
    listed = {}
    for card in index.select("article.picker"):
        target = card.a["href"]
        assert prompt(card.p) == lessons[target], target
        assert lessons[target] in card["data-search"], target
        assert target not in listed, target
        listed[target] = True
    assert set(listed) == {p for p in lessons if not p.startswith("regional/")}
    linked = []
    for chapter in chapters:
        for row in document(chapter).select("ul.indexlist li[id]"):
            if row.a and row.a["href"].startswith("lessons/"):
                target = row.a["href"]
                assert prompt(row.select_one("span.small")) == lessons[target], target
                linked.append(target)
    assert len(set(linked)) == len(linked) == sum(p.startswith("lessons/") for p in lessons)
    notes = document(ROOT / "followup.html").select("article.contest-hit")
    workshops = document(ROOT / "workshops.html").select("details.fold")
    for item in [*notes, *workshops]:
        title = item.find(["h3", "summary"])
        para = title.find_next_sibling()
        assert para.name == "p" and "problem-context" in para.get("class", ()), prompt(title)
        assert len(prompt(para).split()) >= 12, prompt(title)
    assert all("review-question" in fold.summary.get("class", ()) for fold in
               document(ROOT / "review.html").select("details.fold"))
    for path in [ROOT / "coverage.html", ROOT / "archive.html"]:
        case_notes.update(prompt(p) for p in document(path).select("li > p.case-brief"))
    print(f"{len(lessons)} lessons, {len(chapters) + len(tracks) + 1} chapter and subject openings, "
          f"{len(notes)} short notes, {len(workshops)} workshops, {len(case_notes)} distinct contest briefs")


if __name__ == "__main__":
    main()
