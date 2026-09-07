'use strict';
document.documentElement.classList.add('js');
/* Comparación de acento (revisión OAR 2026-09-06): ?acento=rojo / fucsia / oficial.
   El sitio ya usa el acento oficial por defecto; esto es solo para comparar. Se recuerda entre páginas para
   poder recorrer el sitio entero en una variante. ?acento=rojo vuelve al original. */
try{const a=new URLSearchParams(location.search).get('acento');if(a)sessionStorage.setItem('acento',a);const v=sessionStorage.getItem('acento');if(['rojo','fucsia','oficial'].includes(v))document.documentElement.dataset.acento=v;else document.documentElement.removeAttribute('data-acento')}catch(e){}
const menuButton=document.querySelector('.menu-toggle');
const mobileNav=document.querySelector('#mobile-nav');
function closeMenu(){mobileNav.hidden=true;menuButton.setAttribute('aria-expanded','false')}
menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')==='true';mobileNav.hidden=open;menuButton.setAttribute('aria-expanded',String(!open))});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!mobileNav.hidden){closeMenu();menuButton.focus()}});
document.addEventListener('click',e=>{if(!e.target.closest('.site-header'))closeMenu()});
matchMedia('(min-width:701px)').addEventListener('change',e=>{if(e.matches)closeMenu()});
const filterForm=document.querySelector('#catalog-filters');
if(filterForm){
 const grid=document.querySelector('#catalog-grid');
 const cards=Array.from(grid.querySelectorAll('.product-card'));
 const sizeSelect=filterForm.elements.talla,sortSelect=filterForm.elements.orden;
 const categoryButtons=Array.from(filterForm.querySelectorAll('[data-filter]'));
 let category='all';
 const normalizeCategory=value=>categoryButtons.some(b=>b.dataset.filter===value)?value:'all';
 function applyFilters(push=true){
  categoryButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===category)));
  let visible=0;
  const ordered=[...cards].sort((a,b)=>sortSelect.value==='menor'?Number(a.dataset.price)-Number(b.dataset.price):sortSelect.value==='mayor'?Number(b.dataset.price)-Number(a.dataset.price):Number(a.dataset.index)-Number(b.dataset.index));
  ordered.forEach(card=>{const show=(category==='all'||card.dataset.category===category)&&(!sizeSelect.value||card.dataset.sizes.split('|').includes(sizeSelect.value));card.hidden=!show;if(show)visible++;grid.append(card)});
  document.querySelector('#result-count').textContent=`${visible} ${visible===1?'prenda':'prendas'}`;
  document.querySelector('#empty-state').hidden=visible!==0;
  if(push){const url=new URL(location.href);url.search='';if(category!=='all')url.searchParams.set('categoria',category);if(sizeSelect.value)url.searchParams.set('talla',sizeSelect.value);if(sortSelect.value!=='original')url.searchParams.set('orden',sortSelect.value);history.pushState(null,'',url)}
 }
 function readURL(){const q=new URLSearchParams(location.search);category=normalizeCategory(q.get('categoria'));sizeSelect.value=q.get('talla')||'';if(sizeSelect.selectedIndex<0)sizeSelect.value='';sortSelect.value=q.get('orden')||'original';if(sortSelect.selectedIndex<0)sortSelect.value='original';applyFilters(false)}
 categoryButtons.forEach(b=>b.addEventListener('click',()=>{category=b.dataset.filter;applyFilters()}));
 filterForm.addEventListener('submit',e=>e.preventDefault());
 filterForm.addEventListener('change',()=>applyFilters());
 function resetFilters(){category='all';sizeSelect.value='';sortSelect.value='original';applyFilters()}
 filterForm.addEventListener('reset',e=>{e.preventDefault();resetFilters()});
 document.querySelector('[data-reset]').addEventListener('click',resetFilters);
 addEventListener('popstate',readURL);readURL();
}
const detail=document.querySelector('.product-detail');
if(detail){
 let imageIndex=0;
 function updateWA(){const size=detail.querySelector('input[name=size]:checked')?.value;const text=`Hola, me interesa ${detail.dataset.productName} (${detail.dataset.productPrice}), código ${detail.dataset.id}.${size?' Busco talla '+size+'.':' Necesito ayuda con mi talla.'} Me gusta la foto ${imageIndex+1}. ¿Me confirmás disponibilidad?`;document.querySelectorAll('.product-wa').forEach(a=>a.href='https://wa.me/50368590899?text='+encodeURIComponent(text))}
 detail.querySelectorAll('input[name=size]').forEach(r=>r.addEventListener('change',updateWA));
 const mainImage=detail.querySelector('.main-photo img');
 detail.querySelectorAll('[data-photo]').forEach(btn=>btn.addEventListener('click',()=>{imageIndex=Number(btn.dataset.photo);mainImage.src=btn.dataset.full;mainImage.srcset=btn.dataset.srcset;mainImage.alt=`${detail.dataset.productName} — foto ${imageIndex+1}`;detail.querySelectorAll('[data-photo]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));updateWA()}));
}
