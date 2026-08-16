# -*- coding: utf-8 -*-
"""Dos cambios aprobados por OAR (2026-08-16):

  A. HERO CON PRODUCTO — la clienta llega de Instagram, donde venia viendo
     fotos; dos pantallas de tipografia antes de la primera prenda es un
     frenazo. Foto a sangre a la derecha, texto a la izquierda, fondo blanco.

  B. MOVER EL COLOR — el unico bloque de color fuerte se lo llevaba la captura
     de contactos. Pasa al Vestidor, que es el momento de producto; la foto va
     "enmarcada" en blanco sobre el crema para que el vestido blanco no se
     pierda contra el fondo. El VIP queda en blanco y su formulario de un solo
     campo se vuelve un boton directo: WhatsApp ya muestra el nombre de quien
     escribe, asi que el campo era friccion sin ganancia.

Todo va al draft (draft_paleta.css + el generador). index.html real no se toca
hasta que Monica apruebe.
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"

# ── A+B: CSS ─────────────────────────────────────────────────────────────────
CSS = """

/* ============ v3.8 — hero con producto + el color se muda ============ */

/* ---------- A. HERO: texto a la izquierda, prenda a sangre a la derecha ---- */
.home-hero {
  display: block;
  padding: 0;
  overflow: hidden;
}
.home-hero__inner {
  text-align: left;
  margin: 0;
  max-width: 34rem;
  padding: 7rem var(--content-padding) 6rem;
}
.home-hero__title,
.home-hero__subtitle { margin-left: 0; margin-right: 0; }
.home-hero__actions { justify-content: flex-start; }
.home-hero .gold-line { margin-left: 0 !important; }

.home-hero__foto {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 44%;
  overflow: hidden;
}
.home-hero__foto img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* el encuadre alto deja la cara dentro aunque la ventana sea baja */
  object-position: 50% 22%;
  display: block;
}
/* La foto no choca contra el texto: se desvanece en el borde interno */
.home-hero__foto::before {
  content: '';
  position: absolute;
  top: 0; bottom: 0; left: 0;
  width: 18%;
  z-index: 1;
  background: linear-gradient(90deg, #FFFFFF 0%, rgba(255,255,255,0) 100%);
}
/* El indicador de scroll se corre al eje del texto, no al centro de la pantalla */
.home-hero__scroll { left: var(--content-padding); transform: none; }

@media (max-width: 899px) {
  /* En celular la foto va arriba y el texto debajo: la prenda sigue siendo
     lo primero, sin robarle ancho a la lectura. */
  .home-hero { display: flex; flex-direction: column; min-height: 0; }
  .home-hero__foto {
    position: static;
    width: 100%;
    height: min(52vh, 420px);
    order: -1;
  }
  .home-hero__foto::before { display: none; }
  .home-hero__inner { max-width: none; padding: 3rem var(--content-padding) 4rem; }
  .home-hero__scroll { display: none; }
}

/* ---------- B. El color se muda al Vestidor ---------- */
.home-vestidor { background: var(--color-gold-soft); }
/* El vestido blanco sobre crema se perderia: la foto va montada en blanco,
   como una lamina enmarcada contra una pared de color. */
.home-vestidor__image {
  background: #FFFFFF;
  padding: 1rem;
}
.home-vestidor__cta {
  background: var(--color-ink);
  border-color: var(--color-ink);
  color: #FFFFFF;
}
.home-vestidor__cta:hover {
  background: transparent;
  color: var(--color-ink);
  border-color: var(--color-ink);
}
.vestidor-swatch { border-color: rgba(26,26,26,0.2); }
.vestidor-swatch.active { box-shadow: 0 0 0 3px #FFFFFF; }

/* ---------- B. La Lista VIP se calla ---------- */
.home-vip { background: #FFFFFF; }
.home-vip__cta {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 1.5rem;
  padding: 1rem 2.25rem;
  background: #25D366;
  color: var(--color-ink);
  font-family: var(--font-accent);
  font-size: var(--text-micro);
  letter-spacing: 0.25em;
  text-transform: uppercase;
  font-weight: var(--weight-medium);
  transition: background var(--duration-fast);
}
.home-vip__cta:hover { background: #1DB856; }
.home-vip__cta svg { width: 1.1rem; height: 1.1rem; }
"""

p = os.path.join(ROOT, "draft_paleta.css")
t = open(p, encoding='utf-8').read()
assert "v3.8" not in t, "el bloque v3.8 ya estaba"
open(p, 'w', encoding='utf-8').write(t + CSS)
print("draft_paleta.css: bloque v3.8 agregado")

# ── generador: markup del hero y del VIP ─────────────────────────────────────
G = r'C:\tmp\bolem_preview_v3.py'
g = open(G, encoding='utf-8').read()

HERO = r'''
# 2b. HERO CON PRODUCTO: una prenda a sangre junto al texto.
#     Se elige el Maxi Cobalto: color fuerte sobre fondo claro, se sostiene
#     contra el blanco y no es la primera tarjeta de la banda de abajo.
foto_hero = (
    '        <div class="home-hero__foto">\n'
    '            <img src="assets/productos/vestido-cobalto-800.webp"\n'
    '                 srcset="assets/productos/vestido-cobalto-800.webp 800w, '
    'assets/productos/vestido-cobalto.webp 1200w"\n'
    '                 sizes="(min-width: 900px) 44vw, 100vw"\n'
    '                 alt="Vestido maxi azul cobalto plus size &mdash; BOLEM El Salvador"\n'
    '                 width="600" height="900" fetchpriority="high" decoding="async">\n'
    '        </div>\n'
)
ancla_hero = '    <section class="home-hero">\n'
assert ancla_hero in txt, "no se encontro la apertura del hero"
txt = txt.replace(ancla_hero, ancla_hero + foto_hero, 1)

# 2c. La Lista VIP deja de pedir un nombre para mandarte a WhatsApp: el campo
#     era friccion sin ganancia (WhatsApp ya muestra el nombre de quien escribe)
#     y ademas convertia un formulario en un salto inesperado.
form_viejo_ini = txt.index('            <form id="vipForm"')
form_viejo_fin = txt.index('</form>', form_viejo_ini) + len('</form>\n')
WA_VIP = ('https://wa.me/50368590899?text=' +
          quote('Hola, quiero unirme a la Lista VIP de BOLEM'))
txt = txt[:form_viejo_ini] + (
    '            <a href="%s" target="_blank" rel="noopener" class="home-vip__cta">\n'
    '                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l'
    '6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 '
    '11.821 0 00-3.48-8.413A11.815 11.815 0 0012.05 0m0 21.785h-.004a9.87 9.87 0 '
    '01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 '
    '4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 '
    '5.45-4.437 9.884-9.885 9.884"/></svg>\n'
    '                Unirme por WhatsApp\n'
    '            </a>\n') % WA_VIP + txt[form_viejo_fin:]

# el manejador viejo apuntaba a #vipForm y a #vipNombre: sin ellos, reventaba
# y se llevaba por delante el resto del script (incluidos los swatches).
js_ini = txt.index("        document.getElementById('vipForm').addEventListener('submit'")
js_fin = txt.index("});", txt.index("window.open(`https://wa.me/", js_ini)) + len("});\n")
txt = txt[:js_ini] + txt[js_fin:]
assert "vipNombre" not in txt, "quedo una referencia a vipNombre"
assert "vipForm" not in txt, "quedo una referencia a vipForm"

'''

marca = "# 3. EL VESTIDOR se queda como est"
i = g.index(marca)
g = g[:i] + HERO.lstrip("\n") + "\n" + g[i:]

# sanity nuevos
v = 'print("Quick View enganchado:"'
n = ('print("hero con foto:", "home-hero__foto" in txt,\n'
     '      "| VIP sin formulario:", "vipForm" not in txt and "home-vip__cta" in txt)\n'
     'print("Quick View enganchado:"')
assert v in g
g = g.replace(v, n, 1)

open(G, 'w', encoding='utf-8').write(g)
print("generador: hero con producto + VIP como boton")
