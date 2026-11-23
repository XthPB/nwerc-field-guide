(() => {
  "use strict";
  const data = window.contestIndex;
  const form = document.querySelector("#contest-filter");
  if (!data || !form) return;
  const previousAudit = new Set(data.previous);
  const priorFamilies = new Set(data.priorFamilies);
  const fields = ["keyword","scope","min","max","tag","tag2","tag3"];
  const control = Object.fromEntries(fields.map(key => [key,document.getElementById(key)]));
  const list = document.getElementById("contest-rows");
  const count = document.getElementById("contest-count");
  const pageText = document.getElementById("contest-page");
  const prev = document.getElementById("prev-page");
  const next = document.getElementById("next-page");
  const defaults = {keyword:"",scope:"all",min:"2000",max:"3000",tag:"",tag2:"",tag3:""};
  let page = 0, matches = [], perPage = 24;
  function readAddress() {
    const params = new URLSearchParams(location.search);
    for (const key of fields) {
      const element = control[key], value = params.get(key);
      element.value = value === null ? defaults[key] : value;
      if (element.tagName === "SELECT" && element.selectedIndex < 0) element.value = defaults[key];
    }
  }
  function element(tag, content, className) {
    const el=document.createElement(tag);
    if (content !== undefined) el.textContent=content;
    if (className) el.className=className;
    return el;
  }
  function anchor(href,label) {
    const a=element("a",label);
    a.href=href;
    return a;
  }
  function linksLine(label, entries) {
    const p=element("p",label+" ");
    entries.forEach(([href,title],i) => {
      if(i) p.append(" · ");
      p.append(anchor(href,title));
    });
    return p;
  }
  function paint() {
    list.replaceChildren();
    const fragment=document.createDocumentFragment();
    for(const [id,title,rating,tagIds] of matches.slice(page*perPage,(page+1)*perPage)) {
      const box=element("article",undefined,"contest-hit");
      const h=element("h2"), parts=id.match(/^(\d+)([A-Z]\d*)$/);
      h.append(anchor("https://codeforces.com/problemset/problem/"+parts[1]+"/"+parts[2],id+" · "+title+" · "+rating));
      box.append(h);
      const tags=tagIds.map(i=>data.tags[i]);
      box.append(element("p",tags.length ? tags.join(" · ") : "No official tags in this snapshot", "tags"));
      const mapped=data.mapped[id] || [];
      if(mapped.length) box.append(linksLine("Study",mapped.map(k=>[data.urls[k] || "course/"+k+".html",data.titles[k]])));
      if(previousAudit.has(id)) box.append(linksLine("Previous review",[["audit.html?q="+id+"#explorer","Open the earlier DP audit entry"]]));
      if(data.primary[id]) box.append(linksLine("Implementation",[[data.primary[id],"Read a published solution"]]));
      const keys=mapped.length ? mapped.flatMap(k=>data.lessonsT[k]) : tags.map(t=>data.tagT[t]).filter(Boolean);
      const unique=[...new Set(keys)].slice(0,3);
      if(unique.length) box.append(linksLine(mapped.length?"Supporting templates":"Template suggestions from tags",unique.map(k=>["templates/"+k+".html",data.templates[k]])));
      if(!unique.length) box.append(linksLine("Find a starting point", [["methods.html","Browse techniques"],["templates.html","Browse the template library"]]));
      fragment.append(box);
    }
    list.append(fragment);
    if (!matches.length) list.append(element("p",Number(control.min.value)>Number(control.max.value)?"The minimum rating exceeds the maximum. Change either bound to see results.":"No problems match these filters. Remove a tag or widen the rating range."));
    const totalPages=Math.ceil(matches.length/perPage);
    pageText.textContent=matches.length?"Page "+(page+1)+" of "+totalPages:"0 pages";
    prev.disabled=page===0;
    next.disabled=page+1>=totalPages;
  }
  function filter(save) {
    const words=control.keyword.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const selected=[...new Set([control.tag.value,control.tag2.value,control.tag3.value].filter(Boolean))].map(t=>data.tags.indexOf(t));
    const lo=Number(control.min.value),hi=Number(control.max.value),scope=control.scope.value;
    const families=new Set();
    matches=data.rows.filter(([id,title,rating,tags,family,fresh])=>{
      if (rating<lo || rating>hi || (scope==="followup" && !fresh) || (scope==="mapped"&&!data.mapped[id])) return false;
      if ((scope==="sourced"&&!data.primary[id]) || (scope==="newfamily"&&priorFamilies.has(family))) return false;
      if (!selected.every(t=>tags.includes(t)) || !words.every(w=>(id+" "+title).toLowerCase().includes(w))) return false;
      if ((scope==="family"||scope==="newfamily") && families.has(family)) return false;
      families.add(family);
      return true;
    });
    count.textContent=matches.length.toLocaleString("en-US")+(scope==="family"||scope==="newfamily"||scope==="followup"?" matching families":" matching problem IDs");
    page=0;
    if(save) {
      const params=new URLSearchParams();
      for(const key of fields) if(control[key].value!==defaults[key]) params.set(key,control[key].value);
      const query=params.toString();
      try { history.replaceState(null,"",location.pathname+(query?"?"+query:"")+location.hash); } catch (_) { /* Some offline readers do not allow local history changes. */ }
    }
    paint();
  }
  form.addEventListener("submit",e=>e.preventDefault());
  form.addEventListener("input",()=>filter(true));
  document.getElementById("clear-filters").addEventListener("click",()=>{for(const key of fields) control[key].value=defaults[key];filter(true);});
  prev.addEventListener("click",()=>{if(page>0){page--;paint();count.scrollIntoView({block:"start"});}});
  next.addEventListener("click",()=>{if((page+1)*perPage<matches.length){page++;paint();count.scrollIntoView({block:"start"});}});
  window.addEventListener("popstate",()=>{readAddress();filter(false);});
  readAddress();filter(false);
})();
