# -*- coding: utf-8 -*-
"""v3.9 — tres pedidos de OAR (2026-08-16):

  1. Fuera el precio de las bandas. Que primero guste la prenda y despues se
     mire el numero; el precio sigue estando en la ficha del Quick View.
  2. El logotipo: mas presencia y sin la E en rojo.
  3. Una fila de categorias para quien llega buscando algo puntual.
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"

# ── 1+2+3: CSS del draft ─────────────────────────────────────────────────────
CSS = """

/* ============ v3.9 ============ */

/* ---------- 1. Sin precio en las bandas ----------
   El precio predispone antes de que la prenda guste. Vive en la ficha. */
.home-lookbook__grid .lookbook-item__price { display: none; }
.home-lookbook__grid .lookbook-item .overlay {
  background: linear-gradient(transparent 55%, rgba(0,0,0,0.5) 100%);
}

/* ---------- 2. El logotipo ----------
   Estaba en la misma serif que los titulares, asi que en el nav competia con
   ellos en vez de leerse como marca. En sans ancha y espaciada se lee como
   logotipo, y la E vuelve a tinta: el color de la pagina vive en las fotos. */
.nav-logo,
.site-nav--dark .nav-logo,
.footer-logo {
  font-family: var(--font-body);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.34em;
  /* el espaciado agrega aire despues de la ultima letra: se descuenta */
  margin-right: -0.34em;
}
.nav-logo,
.site-nav--dark .nav-logo { font-size: clamp(1.35rem, 1.9vw, 1.75rem); color: var(--color-ink); }
.footer-logo { font-size: 1.15rem; }
.nav-logo .accent,
.site-nav--dark .nav-logo .accent,
.site-nav--dark.scrolled .nav-logo .accent { color: inherit; }

/* ---------- 3. Categorías: puertas de entrada ---------- */
.home-categorias { padding: 4.5rem var(--content-padding) 1rem; }
.home-categorias__inner { max-width: 1200px; margin: 0 auto; }
.home-categorias__header { margin-bottom: 2rem; }
.home-categorias__titulo {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  color: var(--color-ink);
  margin-top: 0.5rem;
  line-height: 1.15;
}
.home-categorias__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}
@media (min-width: 860px) {
  .home-categorias__grid { grid-template-columns: repeat(4, 1fr); gap: 1.25rem; }
}
.home-categoria {
  position: relative;
  display: block;
  aspect-ratio: 4 / 5;
  overflow: hidden;
  background: var(--color-warm);
}
.home-categoria img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s ease;
}
.home-categoria:hover img { transform: scale(1.05); }
.home-categoria__label {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  padding: 1rem 1.1rem;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  color: #FFFFFF;
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: 500;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.home-categoria__label small {
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  opacity: 0.85;
}
"""

p = os.path.join(ROOT, "draft_paleta.css")
t = open(p, encoding='utf-8').read()
assert "v3.9" not in t, "el bloque v3.9 ya estaba"
open(p, 'w', encoding='utf-8').write(t + CSS)
print("draft_paleta.css: bloque v3.9")

# ── 3b. la colección aprende a recibir la categoría por la dirección ─────────
COL = os.path.join(ROOT, "coleccion", "index.html")
c = open(COL, encoding='utf-8').read()
viejo = """    // ─── CATEGORY TILES → filtro ───
    function initCategoryTiles() {"""
nuevo = """    // ─── LLEGAR YA FILTRADA DESDE OTRA PÁGINA ───
    // El home manda a coleccion/#vestido, #blusa, #pantalon o #conjunto.
    // Sin esto, la clienta que toca "Jeans" en el home aterriza en el catálogo
    // completo y tiene que volver a filtrar.
    function initFiltroDesdeHash() {
      var cat = (location.hash || '').replace('#', '');
      if (!cat) return;
      var btn = document.querySelector('.filter-btn[data-filter="' + cat + '"]');
      if (!btn) return;
      btn.click();
      var grid = document.getElementById('catalogo');
      if (grid) grid.scrollIntoView();
    }

    // ─── CATEGORY TILES → filtro ───
    function initCategoryTiles() {"""
assert viejo in c, "no se encontró initCategoryTiles"
c = c.replace(viejo, nuevo, 1)
v2 = "      initCategoryTiles();"
assert v2 in c, "no se encontró la llamada a initCategoryTiles"
c = c.replace(v2, v2 + "\n      initFiltroDesdeHash();", 1)
open(COL, 'w', encoding='utf-8').write(c)
print("coleccion/index.html: filtro por dirección")

# ── generador: quitar precio + insertar la sección de categorías ─────────────
G = r'C:\tmp\bolem_preview_v3.py'
g = open(G, encoding='utf-8').read()

# 1. fuera el <span> del precio de las tarjetas de la banda
v3 = """        '                        <div class="overlay">\\n'
        '                            <span class="lookbook-item__name">%s</span>\\n'
        '                            <span class="lookbook-item__price">%s</span>\\n'
        '                        </div>\\n'"""
n3 = """        '                        <div class="overlay">\\n'
        '                            <span class="lookbook-item__name">%s</span>\\n'
        '                        </div>\\n'"""
assert v3 in g, "no se encontró el overlay de la tarjeta"
g = g.replace(v3, n3, 1)
v4 = """         esc(d['cta']), esc(d['fotos']), base, base, base, alt, carga,
         esc(d['nombre']), esc(d['precio']))"""
n4 = """         esc(d['cta']), esc(d['fotos']), base, base, base, alt, carga,
         esc(d['nombre']))"""
assert v4 in g
g = g.replace(v4, n4, 1)

CATS = r'''
# 4b. CATEGORÍAS: puertas de entrada para quien llega buscando algo puntual.
#     Fotos y etiquetas salen de las tarjetas que la colección ya tiene; los
#     conteos se calculan del catálogo, para que no puedan quedar viejos.
def leer_categorias():
    col = open(ROOT + r"\coleccion\index.html", encoding="utf-8").read()
    tiles = []
    for trozo in re.split(r'(?=<a href="#catalogo" class="category-tile")', col)[1:]:
        trozo = trozo[:trozo.index('</a>') + 4]
        tgt = re.search(r'data-filter-target="([^"]+)"', trozo)
        img = re.search(r'<img src="([^"]+)"', trozo)
        lab = re.search(r'class="category-tile-label">(.*?)<small>', trozo, re.S)
        if tgt and img and lab:
            tiles.append((tgt.group(1), lab.group(1).strip(), img.group(1).replace("../", "")))
    return tiles


CATS = leer_categorias()
assert len(CATS) == 4, "se esperaban 4 categorías, hay %d" % len(CATS)
_cuenta = {}
for _d in CATALOGO.values():
    _cuenta[_d['cat']] = _cuenta.get(_d['cat'], 0) + 1
assert sum(_cuenta.values()) == 33


def tarjeta_cat(slug, etiqueta, foto):
    base = re.sub(r'\.webp$', '', foto)
    n = _cuenta.get(slug, 0)
    return (
        '                <a href="coleccion/#%s" class="home-categoria">\n'
        '                    <img src="%s-480.webp"\n'
        '                         srcset="%s-480.webp 480w, %s-800.webp 800w"\n'
        '                         sizes="(min-width: 860px) 25vw, 50vw"\n'
        '                         alt="%s plus size &mdash; BOLEM El Salvador"\n'
        '                         width="600" height="750" loading="lazy" decoding="async">\n'
        '                    <span class="home-categoria__label">%s<small>%d estilos</small></span>\n'
        '                </a>\n'
    ) % (slug, base, base, base, esc(etiqueta), esc(etiqueta), n)


seccion_cats = (
    '\n    <!-- ============ CATEGORÍAS ============ -->\n'
    '    <section class="home-categorias">\n'
    '        <div class="home-categorias__inner">\n'
    '            <div class="home-categorias__header">\n'
    '                <span class="section-eyebrow">Buscá por tipo</span>\n'
    '                <h2 class="home-categorias__titulo">¿Ya sabés qué andás buscando?</h2>\n'
    '            </div>\n'
    '            <div class="home-categorias__grid">\n'
    + "".join(tarjeta_cat(s, e, f) for s, e, f in CATS) +
    '            </div>\n'
    '        </div>\n'
    '    </section>\n'
)
'''

marca = "m_look = re.search"
i = g.index(marca)
g = g[:i] + CATS.lstrip("\n") + "\n" + g[i:]

# insertar la sección justo antes del lookbook (que ya subió al segundo puesto)
v5 = 'txt = (txt.replace("@@S1@@", look_nuevo, 1)'
n5 = 'txt = (txt.replace("@@S1@@", seccion_cats + look_nuevo, 1)'
assert v5 in g
g = g.replace(v5, n5, 1)

v6 = 'print("hero con foto:"'
n6 = ('print("categorías:", txt.count(\'class="home-categoria"\'), "(esperado 4) | filtro por dirección:",\n'
      '      "coleccion/#vestido" in txt)\n'
      'print("sin precio en las bandas:", txt.count(\'lookbook-item__price\') == 0)\n'
      'print("hero con foto:"')
assert v6 in g
g = g.replace(v6, n6, 1)

open(G, 'w', encoding='utf-8').write(g)
print("generador: sin precio + categorías")
