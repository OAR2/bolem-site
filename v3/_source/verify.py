"""Bounded integrity checks for BOLEM v3; no external dependencies."""
import pathlib,json,re,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=pathlib.Path(__file__).resolve().parents[2]; V3=ROOT/'v3'
if not V3.exists():
 ROOT=pathlib.Path('C:/Users/othma/dev/projects/bolem-site');V3=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'_data/catalogo.json').read_text(encoding='utf-8'))
errors=[];links=0
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.h1=0;self.noindex=False
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if 'id'in a:self.ids.append(a['id'])
  if t=='meta' and a.get('name')=='robots':self.noindex='noindex'in a.get('content','')
  for k in ['href','src']:
   if k in a:self.refs.append(a[k])
pages=list(V3.rglob('*.html'))
for p in pages:
 h=p.read_text(encoding='utf-8');parser=Parse();parser.feed(h)
 if parser.h1!=1:errors.append(f'{p.name}: {parser.h1} H1')
 if not parser.noindex:errors.append(f'{p.name}: missing noindex')
 if len(set(parser.ids))!=len(parser.ids):errors.append(f'{p.name}: duplicate IDs')
 for ref in parser.refs:
  url=urlsplit(ref)
  if url.scheme or url.netloc:continue
  if ref=='#':errors.append(f'{p.name}: placeholder link')
  if not url.path:continue
  dest=(p.parent/unquote(url.path)).resolve();links+=1
  if not(dest.exists() or dest.with_suffix('.html').exists()):errors.append(f'{p.name}: missing {ref}')
products=D['productos'];catalog=(V3/'coleccion/index.html').read_text(encoding='utf-8')
assert len(re.findall(r'class="product-card"',catalog))==len(products),'Catalogue card count mismatch'
for p in products:
 path=V3/'prendas'/(p['id']+'.html')
 if not path.exists():errors.append('Missing product '+p['id']);continue
 h=path.read_text(encoding='utf-8')
 for s in p['tallas']:
  if f'value="{s}"' not in h:errors.append('Missing size '+p['id']+' '+s)
 if len(re.findall(r'data-photo="\d+"',h))!=len(p['fotos']):errors.append('Photo count '+p['id'])
 if not re.search(r'data-product-price="\$'+re.escape(f'{p["precio"]:.2f}'.removesuffix('.00'))+'"',h):errors.append('Price '+p['id'])
for k in D['categorias']:
 expected=sum(p['categoria']==k for p in products)
 if f'data-filter="{k}" aria-pressed="false">{D["categorias"][k]["etiqueta"]} <span>{expected}</span>' not in catalog:errors.append('Category count '+k)
print(f'{len(pages)} pages; {len(products)} products; {links} local resources; {len(errors)} errors')
for e in errors:print(e)
sys.exit(bool(errors))
