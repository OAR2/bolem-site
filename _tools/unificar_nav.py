# -*- coding: utf-8 -*-
"""Un solo nav para las 13 paginas del sitio.

Por que existe: al 16-ago habia TRES navs distintos conviviendo. El home decia
"Tallas" y tenia FAQ pero no "Inicio"; la coleccion decia "Guia de Tallas";
nosotras y las cuatro del blog llamaban al boton "Escribinos" en vez de
"WhatsApp". Tres nombres para la misma pagina y dos para el mismo boton: por
eso al navegar se sentia que uno se salia del sitio.

Ademas cada pagina traia su propia copia del menu movil pegada al final del
HTML —cuatro implementaciones— y dos topaban la altura en 300px, con lo que en
un telefono se recortaban los ultimos enlaces. El comportamiento vive ahora en
`nav.js`, uno solo.

Decision tomada aca: FAQ y Lookbook salen del nav. No son paginas del sitio,
son secciones del home; mezclarlas con paginas reales es lo que hacia que el
nav del home tuviera que ser distinto al de todos los demas.

Regla de la casa: TODO o NADA. Si una sola pagina no calza con un patron
conocido, el script aborta sin escribir un solo archivo.

Uso:  python _tools/unificar_nav.py          (aplica)
      python _tools/unificar_nav.py --dry    (solo reporta)
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WA = ('https://wa.me/50368590899?text=Hola%2C%20vi%20la%20p%C3%A1gina%20de%20'
      'BOLEM%20y%20quiero%20saber%20m%C3%A1s')

ICONO_WA = (
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">'
    '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15'
    '-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475'
    '-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52'
    '.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207'
    '-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297'
    '-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487'
    '.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413'
    '.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>'
    '<path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.5.5 0 00.611.611'
    'l4.458-1.495A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.347 0'
    '-4.518-.801-6.24-2.144l-.436-.348-3.17 1.063 1.063-3.17-.348-.436A9.956 9.956 0 012 12'
    'C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>'
)

# pagina -> (prefijo de rutas, clave del enlace activo)
PAGINAS = {
    'index.html':                                          ('',     'inicio'),
    'nosotros.html':                                        ('',     'nosotros'),
    'guia-de-tallas.html':                                  ('',     'tallas'),
    'cambios.html':                                         ('',     None),
    'terminos.html':                                        ('',     None),
    'privacidad.html':                                      ('',     None),
    '404.html':                                             ('',     None),
    'coleccion/index.html':                                 ('../',  'coleccion'),
    'blog/index.html':                                      ('../',  'blog'),
    'blog/guia-tallas-plus-size.html':                      ('../',  'blog'),
    'blog/historia-bolem-moda-plus-size-el-salvador.html':  ('../',  'blog'),
    'blog/looks-plus-size-clima-calido.html':               ('../',  'blog'),
}

ENLACES = [
    ('inicio',    './',              'Inicio'),
    ('coleccion', 'coleccion/',      'Colección'),
    ('tallas',    'guia-de-tallas',  'Guía de tallas'),
    ('nosotros',  'nosotros',        'Nosotras'),
    ('blog',      'blog/',           'Blog'),
]


def construir_nav(prefijo, activo, atributos):
    esc = []
    mov = []
    for clave, ruta, etiqueta in ENLACES:
        act = ' active' if clave == activo else ''
        aria = ' aria-current="page"' if clave == activo else ''
        esc.append('    <a href="%s%s" class="nav-link%s"%s>%s</a>'
                   % (prefijo, ruta, act, aria, etiqueta))
        mov.append('        <a href="%s%s" class="nav-mobile-link%s"%s>%s</a>'
                   % (prefijo, ruta, act, aria, etiqueta))
    return '\n'.join([
        '<nav %s>' % atributos,
        '    <a href="%s./" class="nav-logo" aria-label="BOLEM — inicio">BOL<span class="accent">E</span>M</a>' % prefijo,
        '    <div class="nav-links">',
        '\n'.join(esc),
        '    </div>',
        '    <a href="%s" target="_blank" rel="noopener" class="nav-cta desktop-only">%s WhatsApp</a>' % (WA, ICONO_WA),
        '    <button id="menuBtn" class="nav-menu-btn" aria-label="Menú" aria-expanded="false" aria-controls="mobileMenu">',
        '      <span id="menuLine1"></span>',
        '      <span id="menuLine2"></span>',
        '    </button>',
        '    <div id="mobileMenu" class="nav-mobile">',
        '      <div class="nav-mobile-inner">',
        '\n'.join(mov),
        '        <a href="%s" target="_blank" rel="noopener" class="nav-mobile-link">WhatsApp</a>' % WA,
        '      </div>',
        '    </div>',
        '  </nav>',
    ])


# Las cuatro copias del menu movil que habia sueltas por el sitio.
VIEJO_JS = [
    # home: bloque dentro del <script> grande
    re.compile(r'\n[ \t]*// === Mobile Menu ===.*?\n[ \t]*\}\);\n(?=\n[ \t]*// === Nav scroll)', re.S),
    # nosotros + las cuatro del blog
    re.compile(r'\n[ \t]*(?:<!-- *Mobile menu toggle *-->\s*)?<script>\s*'
               r'document\.querySelector\(\'\.nav-menu-btn\'\).*?</script>\n', re.S),
    # guia / cambios / terminos / privacidad
    re.compile(r'\n[ \t]*<script>\s*var menuBtn = document\.getElementById\(\'menuBtn\'\);.*?</script>\n', re.S),
    # coleccion: bloque dentro del DOMContentLoaded
    re.compile(r'\n[ \t]*// Mobile menu\n[ \t]*var menuBtn = document\.querySelector.*?\n[ \t]*\}\n', re.S),
]

# Solo el nav de arriba. El <nav class="footer-nav"> del pie tambien es un
# <nav> y no se toca: por eso el patron exige `site-nav` en la etiqueta.
RE_NAV = re.compile(r'<nav\b[^>]*\bsite-nav\b[^>]*>.*?</nav>', re.S)
RE_NAVJS = re.compile(r'<script src="[^"]*nav\.js"[^>]*></script>')


def procesar(ruta, prefijo, activo, contenido):
    problemas = []

    # 1 — el nav
    navs = RE_NAV.findall(contenido)
    if len(navs) != 1:
        problemas.append('esperaba 1 <nav>, encontre %d' % len(navs))
        return contenido, problemas

    if ruta == 'index.html':
        atributos = 'id="mainNav" class="site-nav site-nav--transparent site-nav--dark"'
    else:
        atributos = 'class="site-nav"'
    contenido = RE_NAV.sub(lambda m: construir_nav(prefijo, activo, atributos), contenido, count=1)

    # 2 — fuera las copias del menu movil
    quitados = 0
    for patron in VIEJO_JS:
        contenido, n = patron.subn('\n', contenido)
        quitados += n
    if quitados != 1:
        problemas.append('esperaba quitar 1 menu movil viejo, quite %d' % quitados)

    # 3 — cargar el comportamiento compartido
    if not RE_NAVJS.search(contenido):
        etiqueta = '  <script src="%snav.js" defer></script>\n' % prefijo
        if '</body>' not in contenido:
            problemas.append('no encontre </body>')
        else:
            contenido = contenido.replace('</body>', etiqueta + '</body>', 1)

    return contenido, problemas


def main():
    seco = '--dry' in sys.argv
    resultados = []
    fallas = []

    for ruta, (prefijo, activo) in PAGINAS.items():
        completa = os.path.join(RAIZ, ruta)
        if not os.path.exists(completa):
            fallas.append('%s — no existe' % ruta)
            continue
        original = open(completa, encoding='utf-8').read()
        nuevo, problemas = procesar(ruta, prefijo, activo, original)
        if problemas:
            fallas.append('%s — %s' % (ruta, '; '.join(problemas)))
        else:
            resultados.append((completa, ruta, nuevo, nuevo != original))

    if fallas:
        print('ABORTADO — no se escribio ningun archivo:')
        for f in fallas:
            print('   x ' + f)
        return 1

    for completa, ruta, nuevo, cambio in resultados:
        if cambio and not seco:
            open(completa, 'w', encoding='utf-8', newline='').write(nuevo)
        print('   %s %s' % ('*' if cambio else '=', ruta))

    print('\n%d paginas, %d modificadas%s'
          % (len(resultados), sum(1 for r in resultados if r[3]), ' (simulacro)' if seco else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
