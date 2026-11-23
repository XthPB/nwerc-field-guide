(() => {
  const rows = window.dpAudit,
    meta = window.dpAuditLessons;
  const tags = [...new Set(rows.flatMap((r) => r.tags))].sort();
  const byId = (id) => document.getElementById(id),
    node = (type, text) => {
      const n = document.createElement(type);
      if (text) n.textContent = text;
      return n;
    };
  const tagA = byId("tag-a"),
    tagB = byId("tag-b"),
    rating = byId("audit-rating"),
    status = byId("audit-verdict"),
    query = byId("audit-query"),
    panel = byId("audit-panel");
  for (const select of [tagA, tagB])
    for (const t of tags) select.add(new Option(t, t));
  for (const n of [...new Set(rows.map((r) => r.rating))].sort((a, b) => a - b))
    rating.add(new Option(n, n));
  for (const v of [...new Set(rows.map((r) => r.verdict))].sort())
    status.add(new Option(v, v));
  const addLink = (parent, url, title) => {
    const a = node("a", title);
    a.href = url;
    parent.append(a);
  };
  const lessonLinks = (p, slugs) =>
    slugs.forEach((slug, i) => {
      if (i) p.append(" · ");
      addLink(p, "lessons/" + slug + ".html", meta.titles[slug]);
    });
  const params = new URLSearchParams(location.search);
  for (const [name, el] of [
    ["tag", tagA],
    ["with", tagB],
    ["rating", rating],
    ["verdict", status],
    ["q", query],
    ["panel", panel],
  ])
    if (params.has(name)) el.value = params.get(name);
  let page = 0,
    filtered = [];
  function describe(r) {
    const wrap = node("li"),
      detail = node("details");
    detail.className = "audit-row";
    wrap.append(detail);
    const sum = node("summary");
    sum.append(node("small", r.id + " · " + r.rating));
    const title = node("span", r.title);
    title.className = "issue-title";
    sum.append(title, node("small", r.verdict));
    detail.append(sum);
    const line = () => {
      const p = node("p");
      detail.append(p);
      return p;
    };
    const n = line();
    n.textContent =
      r.note ||
      "A retrieval pass compared the source with the published lessons. The suggestions below still require an individual solution check.";
    if (r.lessons.length) {
      const p = line();
      p.append("Lessons checked against the original guide · ");
      lessonLinks(p, r.lessons);
    }
    if (r.followup) {
      const p = line();
      p.append("Worked follow-up · ");
      lessonLinks(p, [r.followup]);
    }
    if (!r.note && r.signals.length) {
      const p = line();
      p.className = "evidence-note";
      p.append("Paired terms found in solution prose · ");
      r.signals.forEach(([slug, name], i) => {
        if (i) p.append(" · ");
        addLink(p, "lessons/" + slug + ".html", name);
      });
    }
    if (!r.note && r.index.length) {
      const p = line();
      p.append("Also listed in an author’s technique index · ");
      r.index.forEach((v, i) => {
        if (i) p.append(" · ");
        addLink(p, v.url, meta.titles[v.slug]);
      });
    }
    if (!r.note && r.top.length) {
      const p = line();
      p.className = "evidence-note";
      p.append("Search suggestions · ");
      lessonLinks(p, r.top);
    }
    if (r.bridge) {
      const p = line();
      p.append("Worked contest connection · ");
      addLink(p, r.bridge[0], r.bridge[1]);
    }
    if (r.templateKeys.length) {
      const p = line();
      p.append(r.templateBasis + " · ");
      r.templateKeys.forEach((t, i) => {
        if (i) p.append(" · ");
        addLink(p, "templates/" + t + ".html", meta.templateTitles[t]);
      });
    }
    const p = line();
    addLink(p, r.url, "Codeforces statement");
    if (r.kind !== "Statement only") {
      p.append(" · ");
      addLink(p, r.source, r.kind);
    } else p.append(" · Statement evidence only");
    const ts = line();
    ts.className = "evidence-note";
    ts.textContent =
      ["dp", ...r.tags].join(" · ") +
      (r.panel ? " · Ten-per-rating review" : "");
    return wrap;
  }
  function render() {
    const needle = query.value
      .trim()
      .toLowerCase()
      .replace(/^cf\s*(?=\d)/, "");
    filtered = rows.filter(
      (r) =>
        (!tagA.value || r.tags.includes(tagA.value)) &&
        (!tagB.value || r.tags.includes(tagB.value)) &&
        (!rating.value || r.rating === +rating.value) &&
        (!status.value || r.verdict === status.value) &&
        (!panel.value ||
          (panel.value === "panel" && r.panel) ||
          (panel.value === "full" && r.depth === "Individual verdict") ||
          (panel.value === "step" && r.depth === "Technique check")) &&
        (!needle ||
          (r.id + " " + r.title + " " + r.note + " " + r.tags.join(" "))
            .toLowerCase()
            .includes(needle)),
    );
    const pages = Math.ceil(filtered.length / 25);
    page = Math.max(0, Math.min(page, pages - 1));
    const list = byId("audit-list");
    list.replaceChildren(
      ...filtered.slice(page * 25, (page + 1) * 25).map(describe),
    );
    byId("audit-count").textContent = filtered.length
      ? filtered.length +
        " problems · Showing " +
        (page * 25 + 1) +
        "–" +
        Math.min((page + 1) * 25, filtered.length)
      : "No problems match these filters.";
    byId("audit-prev").disabled = page === 0;
    byId("audit-next").disabled = page + 1 >= pages;
    const url = new URLSearchParams();
    for (const [name, el] of [
      ["tag", tagA],
      ["with", tagB],
      ["rating", rating],
      ["verdict", status],
      ["q", query],
      ["panel", panel],
    ])
      if (el.value) url.set(name, el.value);
    if (location.protocol === "http:" || location.protocol === "https:")
      history.replaceState(
        null,
        "",
        location.pathname + (url.size ? "?" + url : "") + location.hash,
      );
  }
  [tagA, tagB, rating, status, panel].forEach((x) =>
    x.addEventListener("change", () => {
      page = 0;
      render();
    }),
  );
  query.addEventListener("input", () => {
    page = 0;
    render();
  });
  byId("audit-prev").addEventListener("click", () => {
    page--;
    render();
  });
  byId("audit-next").addEventListener("click", () => {
    page++;
    render();
  });
  render();
})();
