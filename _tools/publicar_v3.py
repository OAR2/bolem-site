"""Build the September design at the public root, preserving historic routes.

This only builds files. GitHub Pages deploys after an explicit git push.
"""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
default_origin = 'https://' + (ROOT/'CNAME').read_text().strip() if (ROOT/'CNAME').exists() else 'https://oar2.github.io/bolem-site'
parser.add_argument('--origin', default=default_origin)
args = parser.parse_args()
origin = args.origin.rstrip('/')
if urlsplit(origin).scheme != 'https':
    raise SystemExit('Origin must be an HTTPS URL')
subprocess.run([sys.executable, str(ROOT/'v3/_source/build.py')], check=True)
data = json.loads((ROOT/'_data/catalogo.json').read_text(encoding='utf-8'))
products = {p['id']: p for p in data['productos']}

def url(path):
    return origin + '/' + path

def product_schema(p):
    return {'@context': 'https://schema.org', '@type': 'Product',
            'name': p['nombre'], 'sku': p['id'],
            'image': [url('assets/productos/'+f) for f in p['fotos']],
            'description': p.get('descripcion') or p.get('alt', p['nombre']),
            'offers': {'@type': 'Offer', 'price': p['precio'], 'priceCurrency': 'USD',
                       'url': url('prendas/'+p['id']),
                       'availability': 'https://schema.org/'+('OutOfStock' if p.get('agotada') else 'InStock')}}

def metadata(text, route, schemas=None):
    text = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="index,follow">', text)
    title = re.search(r'<title>(.*?)</title>', text, re.S).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', text).group(1)
    image = url('assets/productos/'+products.get(Path(route).name, products['vestido-cobalto'])['fotos'][0])
    tags = (f'<link rel="canonical" href="{html.escape(url(route), quote=True)}">'
            f'<meta property="og:type" content="website"><meta property="og:locale" content="es_SV">'
            f'<meta property="og:site_name" content="BOLEM"><meta property="og:title" content="{title}">'
            f'<meta property="og:description" content="{desc}"><meta property="og:url" content="{url(route)}">'
            f'<meta property="og:image" content="{image}"><meta name="twitter:card" content="summary_large_image">')
    if schemas:
        tags += '<script type="application/ld+json">'+json.dumps(schemas, ensure_ascii=False).replace('</','<\\/')+'</script>'
    return text.replace('</head>', tags+'</head>')

routes = []
for source in sorted((ROOT/'v3').rglob('*.html')):
    relative = source.relative_to(ROOT/'v3')
    if any(part.startswith('_') for part in relative.parts):
        continue
    route = relative.as_posix().removesuffix('index.html') if relative.name == 'index.html' else relative.with_suffix('').as_posix()
    text = '\n'.join(line.rstrip() for line in source.read_text(encoding='utf-8').splitlines())
    # v3 sits one level below the public root; shared photography moves up with it.
    text = text.replace('../assets/', 'assets/') if len(relative.parts)==1 else text.replace('../../assets/', '../assets/')
    schemas = None
    if relative.parts[0] == 'prendas':
        schemas = product_schema(products[relative.stem])
    elif route == 'coleccion/':
        schemas = {'@context':'https://schema.org', '@type':'ItemList',
                   'itemListElement':[{'@type':'ListItem','position':i+1,'item':product_schema(p)} for i,p in enumerate(products.values())]}
    elif route == '':
        schemas = {'@context':'https://schema.org','@type':'Organization','name':'BOLEM',
                   'url':url(''),'sameAs':['https://instagram.com/bolem_sv']}
    destination = ROOT/relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(metadata(text, route, schemas), encoding='utf-8')
    routes.append(route)
shutil.copytree(ROOT/'v3/ui', ROOT/'ui', dirs_exist_ok=True)

# Old links keep working, including clients that don't execute JavaScript.
aliases = {'nosotros.html':'nosotras', 'guia-de-tallas.html':'tallas',
           'coleccion/vestidos-plus-size.html':'coleccion/?categoria=vestido',
           'coleccion/blusas-plus-size.html':'coleccion/?categoria=blusa',
           'coleccion/jeans-y-pantalones-plus-size.html':'coleccion/?categoria=pantalon',
           'coleccion/conjuntos-plus-size.html':'coleccion/?categoria=conjunto'}
for old, target in aliases.items():
    relative_target = ('../' if '/' in old else '')+target
    (ROOT/old).write_text(f'<!doctype html><html lang="es-SV"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BOLEM</title><meta name="robots" content="noindex,follow"><link rel="canonical" href="{url(target)}"><meta http-equiv="refresh" content="0;url={relative_target}"></head><body><h1>BOLEM</h1><p><a href="{relative_target}">Continuar a la página actualizada</a></p></body></html>', encoding='utf-8')

not_found = (ROOT/'index.html').read_text(encoding='utf-8')
not_found = re.sub(r'<main id="main">.*?</main>', '<main id="main" class="wrap section"><h1>No encontramos esta página.</h1><p>Podés seguir explorando la colección de BOLEM.</p><a class="button button-ink" href="coleccion/">Ver la colección</a></main>', not_found, flags=re.S)
not_found = re.sub(r'<link rel="canonical"[^>]*>', '', not_found)
not_found = re.sub(r'<script type="application/ld\+json">.*?</script>', '', not_found)
not_found = not_found.replace('content="index,follow"','content="noindex,follow"').replace('<head>',f'<head><base href="{url("")}">')
not_found = re.sub(r'<title>.*?</title>', '<title>Página no encontrada — BOLEM</title>', not_found)
(ROOT/'404.html').write_text(not_found,encoding='utf-8')
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{html.escape(url(route))}</loc></url>\n' for route in routes)+'</urlset>\n',encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+url('sitemap.xml')+'\n',encoding='utf-8')
(ROOT/'llms.txt').write_text('# BOLEM\n\nModa plus size en El Salvador. Mónica elige e importa las prendas.\n\n'+f'- [Colección]({url("coleccion/")})\n- [Guía de tallas]({url("tallas")})\n- [Envíos y cambios]({url("cambios")})\n- [Historia]({url("nosotras")})\n\nTallas XL a 4XL según la prenda; algunas incluyen L. Confirmar disponibilidad por WhatsApp antes de apartar. Envío $3.50 área metropolitana y $5 resto del país, 1–3 días hábiles.\n',encoding='utf-8')
(ROOT/'.nojekyll').touch()
print(f'Built {len(routes)} public pages, {len(aliases)} historic routes. Origin: {origin}')
