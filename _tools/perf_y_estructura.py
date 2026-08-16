# -*- coding: utf-8 -*-
"""BOLEM 2026-08-16 — tres cambios pedidos por OAR:
  1. El carrusel continuo se muda del Vestidor al Lookbook.
  2. El Vestidor vuelve a botones de color (markup original).
  3. La navegación deja de trabarse.

Diagnóstico del punto 3 (medido): 70 cuadros de animación no completan en 45s.
Tres causas encontradas, todas en archivos reales del sitio (no en el draft):
  a) `backdrop-filter: blur(20px)` en 3 lugares, todos DETRÁS de un fondo que ya
     es 92–95% opaco: el desenfoque no se ve, pero obliga a releer y desenfocar
     todo lo que scrollea debajo, cuadro por cuadro.
  b) La textura de ruido de `body::before` es un SVG con feTurbulence estirado
     al viewport completo, fijo y sobre TODO (z-index 9999). Sin `background-size`
     el filtro se calcula al tamaño de la pantalla. Con tile de 256px se rasteriza
     una vez y se repite.
  c) El handler de scroll leía `hero.offsetHeight` en CADA evento — eso fuerza al
     navegador a recalcular layout de forma síncrona mientras scrolleás.
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"


def editar(rel, pares, opcionales=()):
    p = os.path.join(ROOT, rel)
    t = open(p, encoding='utf-8').read()
    for viejo, nuevo in pares:
        assert viejo in t, "NO ENCONTRADO en %s:\n  %r" % (rel, viejo[:80])
        t = t.replace(viejo, nuevo)
    for viejo, nuevo in opcionales:
        t = t.replace(viejo, nuevo)
    open(p, 'w', encoding='utf-8').write(t)
    print("  ok", rel)


# ── (a) fuera los tres backdrop-filter ────────────────────────────────────────
BLUR = "  backdrop-filter: blur(20px);\n  -webkit-backdrop-filter: blur(20px);\n"
editar("styles.css", [
    # nav base
    ("  background: rgba(250, 247, 243, 0.92);\n" + BLUR,
     "  background: rgba(250, 247, 243, 0.92);\n"),
    # menú móvil (este trae solo la versión sin prefijo)
    ("  background: rgba(250, 247, 243, 0.95);\n  backdrop-filter: blur(20px);\n",
     "  background: rgba(250, 247, 243, 0.95);\n"),
    # (c-bis) transition: all en un elemento cuya clase cambia con el scroll
    ("  transition: all var(--duration-mid) var(--ease-smooth);\n",
     "  transition: background-color var(--duration-mid) var(--ease-smooth),\n"
     "              border-color var(--duration-mid) var(--ease-smooth);\n"),
    # (b) la textura de ruido, de filtro a pantalla completa → tile de 256px
    ("  pointer-events: none;\n  opacity: 0.03;\n  background-image:",
     "  pointer-events: none;\n  opacity: 0.03;\n"
     "  /* tile fijo: el feTurbulence se rasteriza una vez, no al tamaño del viewport */\n"
     "  background-size: 256px 256px;\n  background-repeat: repeat;\n"
     "  background-image:"),
])

# el .site-nav--transparent.scrolled repite el par de líneas del blur
p = os.path.join(ROOT, "styles.css")
t = open(p, encoding='utf-8').read()
n = t.count(BLUR)
t = t.replace(BLUR, "")
open(p, 'w', encoding='utf-8').write(t)
print("  ok styles.css — backdrop-filter restantes eliminados:", n)
assert "backdrop-filter" not in open(p, encoding='utf-8').read(), "quedó algún backdrop-filter"

# ── (c) el handler de scroll deja de forzar layout en cada evento ─────────────
VIEJO_JS = """        window.addEventListener('scroll', () => {
            const scrollY = window.pageYOffset;
            const heroHeight = hero.offsetHeight;

            // Toggle scrolled class
            if (scrollY > heroHeight - 80) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        }, { passive: true });"""

NUEVO_JS = """        // El alto del hero se mide UNA vez (y al cambiar el tamaño de la ventana).
        // Leerlo dentro del scroll obliga a recalcular layout en cada evento y es
        // la causa principal de que la página se sintiera trabada al bajar.
        let umbral = hero.offsetHeight - 80;
        let pendiente = false, estabaScrolleado = null;
        addEventListener('resize', () => { umbral = hero.offsetHeight - 80; }, { passive: true });
        function pintarNav() {
            pendiente = false;
            const ahora = scrollY > umbral;
            if (ahora === estabaScrolleado) return;   // solo tocamos el DOM al cambiar
            estabaScrolleado = ahora;
            nav.classList.toggle('scrolled', ahora);
        }
        addEventListener('scroll', () => {
            if (!pendiente) { pendiente = true; requestAnimationFrame(pintarNav); }
        }, { passive: true });
        pintarNav();"""

editar("index.html", [(VIEJO_JS, NUEVO_JS)])

# ── CSS del draft: el carrusel se muda ───────────────────────────────────────
p = os.path.join(ROOT, "draft_paleta.css")
css = open(p, encoding='utf-8').read()


def cortar(texto, desde, hasta=None):
    i = texto.index(desde)
    j = texto.index(hasta) if hasta else len(texto)
    assert j > i
    return texto[:i] + texto[j:]


css = cortar(css, "/* ---------- Lookbook \u2192 carrusel horizontal", "/* ============ v3.1")
css = cortar(css, "/* ============ v3.4 \u2014 El Vestidor", "/* ============ v3.5")
css = cortar(css, "/* ============ v3.6 \u2014 Lookbook")

css += """
/* ============ v3.7 — el carrusel se muda al Lookbook ============
   OAR, 16-ago: la banda continua le sirve más al Lookbook (muchas piezas,
   ojeada ambiental) que al Vestidor, donde la decisión es deliberada y los
   botones de color la expresan mejor. El Vestidor vuelve a su markup original. */

.home-lookbook {
  --lgap: 1.25rem;
  --lcard: min(300px, calc((92vw - 2 * var(--lgap)) / 1.5));
}
@media (min-width: 768px) { .home-lookbook { --lcard: 300px; } }

.home-lookbook__inner { max-width: 1200px; }

.home-lookbook__grid {
  display: flex !important;
  width: max-content;
  overflow: visible;
  animation: lookbook-drift 84s linear infinite;
}
/* El respiro va como margen, no como gap: con gap, la mitad del recorrido no
   cae en el inicio de una tarjeta y la banda salta cada vuelta. */
.home-lookbook__grid > * { margin-right: var(--lgap); }
@keyframes lookbook-drift {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
.home-lookbook__banda {
  position: relative;
  overflow: hidden;
  margin-top: 2rem;
}
.home-lookbook__banda::before,
.home-lookbook__banda::after {
  content: '';
  position: absolute;
  top: 0; bottom: 0;
  width: clamp(24px, 5vw, 72px);
  z-index: 2;
  pointer-events: none;
}
.home-lookbook__banda::before { left: 0;  background: linear-gradient(90deg,  #FFFFFF 0%, rgba(255,255,255,0) 100%); }
.home-lookbook__banda::after  { right: 0; background: linear-gradient(270deg, #FFFFFF 0%, rgba(255,255,255,0) 100%); }

.home-lookbook__banda:hover .home-lookbook__grid,
.home-lookbook__banda:focus-within .home-lookbook__grid,
.home-lookbook__grid.is-paused { animation-play-state: paused; }
@media (prefers-reduced-motion: reduce) {
  .home-lookbook__grid { animation: none; }
}

.home-lookbook__grid .lookbook-item {
  flex: 0 0 var(--lcard);
  aspect-ratio: 3 / 4;
  overflow: hidden;
  position: relative;
}
.home-lookbook__grid .lookbook-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
/* Nombre y precio siempre visibles: en celular no hay hover y el precio
   es media decisión de compra. */
.home-lookbook__grid .lookbook-item .overlay {
  opacity: 1;
  transform: none;
  background: linear-gradient(transparent 45%, rgba(0,0,0,0.55) 100%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1rem;
  position: absolute;
  inset: 0;
}
.home-lookbook__grid .lookbook-item__name,
.home-lookbook__grid .lookbook-item__price { color: #FFFFFF; }
.home-lookbook__grid .lookbook-item__price { font-weight: 600; }

.lookbook-item--todo {
  flex: 0 0 var(--lcard);
  aspect-ratio: 3 / 4;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  background: var(--color-gold-soft);
  color: var(--color-ink);
  text-align: center;
  padding: 2rem;
}
.lookbook-item--todo strong {
  font-family: var(--font-display);
  font-size: clamp(1.25rem, 2.5vw, 1.75rem);
  font-weight: 400;
}
.lookbook-item--todo span {
  font-family: var(--font-body);
  font-size: var(--text-micro);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
.lookbook-item--todo:hover { background: var(--color-gold-light); }

/* ---------- El Vestidor, de vuelta a botones de color ---------- */
.home-vestidor__swatches { margin-top: 1.75rem; }
.vestidor-swatch {
  border: 2px solid rgba(26,26,26,0.15);
}
.vestidor-swatch:hover { border-color: rgba(26,26,26,0.45); }
.vestidor-swatch.active {
  border-color: var(--color-ink);
  box-shadow: 0 0 0 3px var(--color-gold-soft);
}
.home-vestidor__image { position: relative; }

/* ---------- Ninguna animación corre fuera de pantalla ----------
   El marquee y la banda del lookbook seguían animando con la sección fuera
   del viewport; el compositor pagaba por algo que nadie estaba viendo. */
.anim-dormida,
.anim-dormida * { animation-play-state: paused !important; }

/* Secciones largas fuera de pantalla: el navegador puede saltarse su layout */
.home-tallas,
.home-faq,
.home-instagram,
.home-comunidad { content-visibility: auto; contain-intrinsic-size: auto 600px; }
"""
open(p, 'w', encoding='utf-8').write(css)
print("  ok draft_paleta.css — v3.7")
