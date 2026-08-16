const panel=document.getElementById('panel'),burger=document.getElementById('burger');
if(burger)burger.onclick=()=>{panel.classList.toggle('open');burger.classList.toggle('x')};
document.querySelectorAll('.g-item').forEach(it=>it.addEventListener('click',e=>{
  if(e.target.closest('.mapbtn')){e.preventDefault();return;}
  it.classList.toggle('open');
}));
function lang(l){
  const t=document.getElementById('logoTxt');
  if(t){t.textContent=l==='en'?'TVG':'테오화랑';t.className='txt'+(l==='en'?' en':'');}
  document.querySelectorAll('.panel a[data-ko]').forEach(a=>{
    a.innerHTML = l==='en' ? a.dataset.en : a.dataset.ko+' <em>'+a.dataset.en+'</em>';});
  document.getElementById('ko').classList.toggle('on',l==='ko');
  document.getElementById('en').classList.toggle('on',l==='en');
  document.documentElement.lang=l; try{localStorage.setItem('tvg-lang',l)}catch(e){}
}
const ko=document.getElementById('ko'),en=document.getElementById('en');
if(ko){ko.onclick=()=>lang('ko');en.onclick=()=>lang('en');}
