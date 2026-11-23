'use strict';
const key=location.hash.slice(1);
const target=document.getElementById(key);
if(target && target.matches('li[id]')){
  const dest=target.querySelector('a[href^="lessons/"]');
  if(dest)location.replace(dest.href);
}
