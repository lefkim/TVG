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

/* 이미지 확대 보기 */
(function(){
  const zs=[...document.querySelectorAll('.zoomable')];
  if(!zs.length) return;
  const lb=document.createElement('div'); lb.id='lb'; lb.tabIndex=-1;
  lb.innerHTML='<button class="cl" aria-label="닫기">&times;</button>'
    +'<button class="pv" aria-label="이전">&#8249;</button>'
    +'<button class="nx" aria-label="다음">&#8250;</button>'
    +'<img alt=""><div class="cap"></div>';
  document.body.appendChild(lb);
  const im=lb.querySelector('img'), cap=lb.querySelector('.cap');
  let i=0;
  function show(n){
    i=(n+zs.length)%zs.length; const el=zs[i];
    lb.classList.remove('rdy');
    im.onload=()=>lb.classList.add('rdy');
    im.src=el.dataset.full; im.alt=el.dataset.cap||'';
    cap.innerHTML=(el.dataset.cap?'<b>'+el.dataset.cap+'</b>':'')
      +(zs.length>1?'  '+(i+1)+' / '+zs.length:'');
    lb.querySelector('.pv').style.display=lb.querySelector('.nx').style.display=
      zs.length>1?'block':'none';
  }
  function open(n){ show(n); lb.classList.add('on');
    document.body.style.overflow='hidden'; lb.focus(); }
  function close(){ lb.classList.remove('on','rdy'); im.src='';
    document.body.style.overflow=''; }
  zs.forEach((el,n)=>el.addEventListener('click',()=>open(n)));
  lb.addEventListener('click',e=>{
    if(e.target.classList.contains('pv')) return show(i-1);
    if(e.target.classList.contains('nx')) return show(i+1);
    if(e.target===im) return show(i+1);
    close();
  });
  document.addEventListener('keydown',e=>{
    if(!lb.classList.contains('on')) return;
    if(e.key==='Escape') close();
    else if(e.key==='ArrowLeft') show(i-1);
    else if(e.key==='ArrowRight') show(i+1);
  });
})();
