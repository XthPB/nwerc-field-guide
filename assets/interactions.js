'use strict';
document.querySelectorAll('.lab').forEach(lab => {
  const frames = Array.from(lab.querySelectorAll('.frame'));
  const prev = lab.querySelector('[data-step="-1"]');
  const next = lab.querySelector('[data-step="1"]');
  const output = lab.querySelector('output');
  const play = lab.querySelector('[data-play]');
  let timer = null;
  function stop() {
    if (timer !== null) window.clearInterval(timer);
    timer = null; play.textContent = 'Play'; play.setAttribute('aria-pressed','false');
  }
  let i = 0;
  function move(delta) {
    frames[i].hidden = true;
    i = Math.max(0, Math.min(frames.length - 1, i + delta));
    frames[i].hidden = false;
    prev.disabled = i === 0;
    next.disabled = i === frames.length - 1;
    output.value = String(i + 1) + ' / ' + frames.length;
  }
  prev.addEventListener('click', () => {stop(); move(-1);});
  next.addEventListener('click', () => {stop(); move(1);});
  play.addEventListener('click', () => {
    if (timer !== null) {stop();return;}
    if (i === frames.length-1) move(-i);
    play.textContent = 'Pause'; play.setAttribute('aria-pressed','true');
    timer = window.setInterval(() => {
      move(1);
      if (i === frames.length-1) stop();
    }, 3000);
  });
  document.addEventListener('visibilitychange',() => {if (document.hidden) stop();});
});

const normalize = x => x.normalize('NFKD').toLowerCase().replace(/[–—-]/g,' ');
document.querySelectorAll('.vote').forEach(panel => {
  const buttons = [...panel.querySelectorAll('[data-seats]')];
  const seats = [...panel.querySelectorAll('.seatbar i')];
  const output = panel.querySelector('output');
  function update() {
    const selected = buttons.filter(b => b.getAttribute('aria-pressed') === 'true').map(b => Number(b.dataset.seats));
    const total = selected.reduce((a,b) => a+b, 0);
    seats.forEach((seat,i) => seat.classList.toggle('on', i < total));
    let result = total + (total === 1 ? ' seat.' : ' seats.');
    if(total < 5) result += ' This group needs ' + (5-total) + ' more to win.';
    else {
      const smallest = Math.min(...selected);
      const remainder = total-smallest;
      result = total+' seats win. Removing the '+smallest+'-seat party leaves '+remainder+'. ';
      result += remainder<5 ? 'Every member is essential.' : 'The remaining parties still win, so this group is not minimal.';
    }
    output.textContent = result;
  }
  for(const b of buttons) b.addEventListener('click',()=>{
    b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') !== 'true' ? 'true':'false'); update();
  });
  update();
});
const lessonSearch=document.getElementById('lessonSearch');
if(lessonSearch) {
  const chapter=document.getElementById('chapterFilter'),stage=document.getElementById('levelFilter');
  const entries=[...document.querySelectorAll('[data-search]')];
  function refreshLessons() {
    const tokens=normalize(lessonSearch.value).trim().split(/\s+/).filter(Boolean);
    let count=0;
    for(const entry of entries){
      entry.hidden = (chapter.value && entry.dataset.chapter !== chapter.value) ||
        (stage.value && entry.dataset.stage !== stage.value) ||
        !tokens.every(t=>normalize(entry.dataset.search).includes(t));
      if(!entry.hidden)++count;
    }
    document.getElementById('results').textContent=count===1 ? '1 lesson' : count+' lessons';
  }
  const startParams=new URLSearchParams(location.search);
  lessonSearch.value=startParams.get('q')||'';
  [lessonSearch,chapter,stage].forEach(el=>el.addEventListener('input',refreshLessons));
  refreshLessons();
}
function revealFragment(){
  if(!location.hash)return;
  let match;
  try{match=document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch{return;}
  if(match && match.matches('details')){match.open=true;match.scrollIntoView();}
}
revealFragment();
window.addEventListener('hashchange',revealFragment);


const list = document.querySelector('#cfRows');
if (list && window.problemCatalog) {
  const $ = id => document.getElementById(id);
  const filters=['cfText','cfScope','cfLow','cfHigh','cfTag','cfRound','cfYear','cfOrder'].map($);
  const rows=window.problemCatalog;
  const labels=window.lessonLabels;
  let found=[], page=0;
  const size=30;
  function option(el,value,label) {
    const opt=document.createElement('option'); opt.value=String(value);opt.textContent=label;el.append(opt);
  }
  for(let r=800;r<=3000;r+=100){
    option($('cfLow'),r,r);option($('cfHigh'),r,r);
  }
  $('cfLow').value='800';$('cfHigh').value='3000';
  const tags=Array.from(new Set(rows.flatMap(p=>p[4]))).sort();
  tags.forEach(t=>option($('cfTag'),t,t));
  function link(url,caption) {
    const a=document.createElement('a');a.href=url;a.textContent=caption;return a;
  }
  function render() {
    list.replaceChildren();
    const offset=page*size;
    for(const p of found.slice(offset,offset+size)){
      const [id,idx,name,rating,tags,contest,date,method,note]=p;
      const tr=document.createElement('tr');
      const cols=Array.from({length:3},()=>document.createElement('td'));
      cols[0].textContent=String(rating);
      cols[1].append(link('https://codeforces.com/problemset/problem/'+id+'/'+idx,id+idx+' · '+name));
      const sub=document.createElement('small');sub.textContent=[contest,date].filter(Boolean).join(' · ');cols[1].append(sub);
      if(note){const info=document.createElement('div');info.className='obs';info.textContent=note;cols[1].append(info);}
      const info=window.problemEvidence[String(id)+idx];
      function templateRow(keys,description) {
        const panel=document.createElement('div'); panel.className='tmpl';
        const caption=document.createElement('small'); caption.textContent=description;
        panel.append(caption);
        keys.forEach((key,i)=>{if(i)panel.append(' · ');panel.append(link('templates/'+key+'.html',window.templateLabels[key]));});
        cols[2].append(panel);
      }
      if(method){
        cols[2].append(link(labels[method][0],labels[method][1]));
        templateRow(window.problemTemplates[String(id)+idx],'Supporting templates');
      } else if(info.op.length){
        templateRow(info.op.map(op=>op[0]),'Building blocks visible in code');
        const examples=document.createElement('small');
        for(const [i,op] of info.op.entries()){
          if(i)examples.append(' · ');
          examples.append(link(op[2],op[1]));
        }
        cols[2].append(examples);
      } else {
        templateRow(info.candidates,'Starting points from official tags');
        const t=document.createElement('small');t.textContent=tags.join(', ');cols[2].append(t);
      }
      if(info.source){
        const ref=document.createElement('small');
        ref.append(link(info.source,'Reference implementation'));cols[1].append(ref);
      }
      tr.append(...cols);list.append(tr);
    }
    $('cfCount').textContent=found.length ? (offset+1)+'–'+Math.min(offset+size,found.length)+' of '+found.length+' matching problems' : 'No matches. Try a wider rating range or clear a filter.';
    $('cfPrev').disabled=page===0;
    $('cfNext').disabled=(page+1)*size>=found.length;
  }
  function filter() {
    page=0;
    const [query,scope,lo,hi,tag,round,year,order]=filters.map(el=>el.value);
    const words=normalize(query.trim()).split(/\s+/).filter(Boolean);
    found=rows.filter(p=>{
      const key=normalize([p[0]+p[1],p[2],p[4].join(' '),p[5],p[7] ? labels[p[7]][1] : '',p[8]].join(' '));
      return (scope==='all'||p[7]) && p[3]>=+lo && p[3]<=+hi && (!tag||p[4].includes(tag)) &&
        (!round||p[5].toLowerCase().includes(round)) && (!year||p[6].startsWith(year)) && words.every(w=>key.includes(w));
    });
    found.sort((a,b)=>order==='recent' ? b[6].localeCompare(a[6])||b[0]-a[0]||a[1].localeCompare(b[1]) :
      (order==='hard'?b[3]-a[3]:a[3]-b[3]) || b[0]-a[0] || a[1].localeCompare(b[1]));
    render();
  }
  filters.forEach(el=>el.addEventListener('input',filter));
  $('cfPrev').addEventListener('click',()=>{if(page>0){--page;render();}});
  $('cfNext').addEventListener('click',()=>{if((page+1)*size<found.length){++page;render();}});
  $('cfReset').addEventListener('click',()=>{
    $('cfText').value='';$('cfScope').value='annotated';$('cfLow').value='800';$('cfHigh').value='3000';
    $('cfTag').value='';$('cfRound').value='';$('cfYear').value='';$('cfOrder').value='easy';filter();
  });
  const params = new URLSearchParams(location.search);
  for(const [key,field] of [['scope','cfScope'],['year','cfYear'],['order','cfOrder'],['low','cfLow'],['high','cfHigh'],['tag','cfTag'],['round','cfRound']]) {
    const option = params.get(key);
    if (option && Array.from($(field).options).some(x => x.value===option)) $(field).value=option;
  }
  if(params.has('q')) $('cfText').value=params.get('q');
  filter();
}

