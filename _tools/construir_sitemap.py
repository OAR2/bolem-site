# -*- coding: utf-8 -*-
"""Reescribe sitemap.xml a partir de los archivos que EXISTEN de verdad.

Estaba escrito a mano con 11 direcciones. Al pasar de 33 prendas en una sola
pagina a 49 paginas propias, mantenerlo a mano garantiza que se quede viejo —
y un mapa del sitio viejo le esconde a Google justo lo nuevo.

Ahora se deriva: barre el repo, arma la lista, y le pone a cada direccion la
fecha real del archivo. Nada se escribe a mano.

Uso:
    python _tools/construir_sitemap.py --revisar
    python _tools/construir_sitemap.py [--fecha 2026-08-17]
"""
import io, os, sys, json, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIO = 'https://bolemsv.com'
DESTINO = os.path.join(ROOT, 'sitemap.xml')

# Paginas que NO van al mapa: no aportan nada a un buscador.
FUERA = {'404.html'}

# prioridad y frecuencia por tipo de pagina
PERFIL = {
    'home':     ('1.0', 'weekly'),
    'coleccion': ('0.9', 'weekly'),
    'prenda':   ('0.8', 'weekly'),
    'guia':     ('0.8', 'monthly'),
    'blog':     ('0.7', 'monthly'),
    'pagina':   ('0.6', 'monthly'),
    'legal':    ('0.3', 'yearly'),
}
LEGALES = {'privacidad', 'terminos', 'cambios'}


def fecha_de(p, respaldo):
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
    except OSError:
        return respaldo


def url_de(rel):
    """index.html -> /  ·  nosotros.html -> /nosotros  ·  blog/index.html -> /blog"""
    rel = rel.replace(os.sep, '/')
    if rel == 'index.html':
        return SITIO + '/'
    if rel.endswith('/index.html'):
        return SITIO + '/' + rel[:-len('/index.html')]
    return SITIO + '/' + rel[:-len('.html')]


def tipo_de(rel):
    rel = rel.replace(os.sep, '/')
    if rel == 'index.html':
        return 'home'
    if rel.startswith('prendas/'):
        return 'prenda'
    if rel == 'coleccion/index.html':
        return 'coleccion'
    if rel == 'guia-de-tallas.html':
        return 'guia'
    if rel.startswith('blog/'):
        return 'blog'
    if rel[:-5] in LEGALES:
        return 'legal'
    return 'pagina'


def main(revisar, fecha_fija):
    hoy = fecha_fija or datetime.date.today().isoformat()
    filas = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(('.', '_')) and d != 'assets']
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            rel = os.path.relpath(os.path.join(base, f), ROOT)
            if rel.replace(os.sep, '/') in FUERA:
                continue
            filas.append((rel, os.path.join(base, f)))

    orden = {'home': 0, 'coleccion': 1, 'prenda': 2, 'guia': 3,
             'pagina': 4, 'blog': 5, 'legal': 6}
    filas.sort(key=lambda x: (orden[tipo_de(x[0])], url_de(x[0])))

    partes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    grupo_previo = None
    cuenta = {}
    for rel, ruta in filas:
        t = tipo_de(rel)
        cuenta[t] = cuenta.get(t, 0) + 1
        if t != grupo_previo:
            partes.append('')
            partes.append('  <!-- %s -->' % {
                'home': 'Inicio', 'coleccion': 'Coleccion',
                'prenda': 'Una pagina por prenda (generadas de _data/catalogo.json)',
                'guia': 'Guia de tallas', 'pagina': 'Paginas',
                'blog': 'Blog', 'legal': 'Legales'}[t])
            grupo_previo = t
        pr, fr = PERFIL[t]
        partes.append('  <url>')
        partes.append('    <loc>%s</loc>' % url_de(rel))
        partes.append('    <lastmod>%s</lastmod>' % fecha_de(ruta, hoy))
        partes.append('    <changefreq>%s</changefreq>' % fr)
        partes.append('    <priority>%s</priority>' % pr)
        partes.append('  </url>')
    partes.append('')
    partes.append('</urlset>')
    nuevo = '\n'.join(partes) + '\n'

    viejo = open(DESTINO, encoding='utf-8').read() if os.path.exists(DESTINO) else ''
    n_viejo = viejo.count('<url>')
    print('direcciones: %d -> %d' % (n_viejo, nuevo.count('<url>')))
    for t in ('home', 'coleccion', 'prenda', 'guia', 'pagina', 'blog', 'legal'):
        if cuenta.get(t):
            print('   %-10s %d' % (t, cuenta[t]))
    if nuevo == viejo:
        print('\nsin cambios')
        return 0
    if revisar:
        print('\n(--revisar: no se escribio nada)')
        return 0
    open(DESTINO, 'w', encoding='utf-8').write(nuevo)
    print('\nescrito: sitemap.xml')
    return 0


if __name__ == '__main__':
    f = None
    if '--fecha' in sys.argv:
        f = sys.argv[sys.argv.index('--fecha') + 1]
    sys.exit(main('--revisar' in sys.argv, f))
