"""Validate deployable URLs, responsive images, SEO, and historic routes."""
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
import re

ROOT = Path(__file__).resolve().parents[1]
errors = []
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.refs=[]; self.canonical=None; self.robots=''; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a.get('href')
        if tag=='meta' and a.get('name')=='robots': self.robots=a.get('content','')
        for name in ('href','src'):
            if a.get(name): self.refs.append(a[name])
        for name in ('srcset','data-srcset'):
            for item in a.get(name,'').split(','):
                if item.strip(): self.refs.append(item.strip().split()[0])

sitemap=ET.parse(ROOT/'sitemap.xml')
locations=[e.text for e in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
origin=locations[0].split('/blog')[0].rstrip('/') if '/blog' in locations[0] else None
home=Page((ROOT/'index.html').read_text(encoding='utf-8'))
origin=home.canonical.rstrip('/')
seen_titles={}; seen_descriptions={}
for location in locations:
    route=location.removeprefix(origin+'/')
    path=ROOT/(route+'index.html' if not route or route.endswith('/') else route+'.html')
    text=path.read_text(encoding='utf-8'); page=Page(text)
    if 'noindex' in page.robots: errors.append(f'{route}: production is noindex')
    if page.canonical!=location: errors.append(f'{route}: canonical mismatch')
    if 'property="og:image"' not in text: errors.append(f'{route}: missing sharing image')
    for pattern, seen in [(r'<title>(.*?)</title>',seen_titles),(r'<meta name="description" content="([^"]+)"',seen_descriptions)]:
        value=re.search(pattern,text).group(1)
        if value in seen: errors.append(f'{route}: duplicate metadata with {seen[value]}')
        seen[value]=route
    schemas=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text)]
    types=[s.get('@type') for s in schemas]
    if route and 'BreadcrumbList' not in types: errors.append(f'{route}: missing breadcrumbs')
    if route.startswith('blog/') and route!='blog/' and ('Article' not in types or 'article-byline' not in text): errors.append(f'{route}: incomplete article')
    if route.startswith('coleccion/') and route!='coleccion/':
        from seo_bolem import CATEGORIES
        key=next(k for k,v in CATEGORIES.items() if route.endswith(v[0]))
        categories=re.findall(r'data-category="([^"]+)"',text)
        catalog=json.loads((ROOT/'_data/catalogo.json').read_text(encoding='utf-8'))['productos']
        expected=sum(p['categoria']==key for p in catalog)
        if len(categories)!=expected or set(categories)!={key}: errors.append(f'{route}: wrong category products')
    for ref in page.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc or not u.path: continue
        dest=(path.parent/unquote(u.path)).resolve()
        if not (dest.exists() or dest.with_suffix('.html').exists()): errors.append(f'{route}: missing {ref}')
for css in (ROOT/'ui').glob('*.css'):
    for ref in re.findall(r'url\([\'"]?([^\)\'\"]+)',css.read_text(encoding='utf-8')):
        if not urlsplit(ref).scheme and not (css.parent/ref).exists(): errors.append('Missing font/asset '+ref)
for alias in ['nosotros','guia-de-tallas']:
    text=(ROOT/(alias+'.html')).read_text(encoding='utf-8')
    if 'http-equiv="refresh"' not in text: errors.append('Missing historic route '+alias)
for p in json.loads((ROOT/'_data/catalogo.json').read_text(encoding='utf-8'))['productos']:
    text=(ROOT/'prendas'/(p['id']+'.html')).read_text(encoding='utf-8')
    schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text).group(1))
    if schema['offers']['price']!=p['precio']: errors.append('Wrong price '+p['id'])
    if schema['offers']['url']!=origin+'/prendas/'+p['id']: errors.append('Wrong product URL '+p['id'])
assert not errors, '\n'.join(errors)
print(f'PASS: {len(locations)} public pages; responsive images, fonts, canonicals, schemas and historic routes.')
