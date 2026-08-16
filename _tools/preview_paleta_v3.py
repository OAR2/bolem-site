import sys, io, re
from urllib.parse import quote
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"
txt = open(ROOT + r"\index.html", encoding="utf-8").read()

# 1. Inyectar CSS del draft + marcar el tab
txt = txt.replace('home.css">', 'home.css">\n    <link rel="stylesheet" href="draft_paleta.css">', 1)
txt = re.sub(r'<title>.*?</title>', '<title>[PREVIEW PALETA v3] BOLEM</title>', txt, count=1, flags=re.S)

# 2. HERO: fuera el botón a Instagram (Mónica: la clienta YA viene de ahí).
#    Sobrevive solo en el cierre de la página (.home-cta__btn-ig).
ig_btn = ('                <a href="https://www.instagram.com/bolem_sv" target="_blank" '
          'class="home-hero__btn-secondary">@bolem_sv</a>\n')
assert ig_btn in txt, "no se encontró el botón IG del hero"
txt = txt.replace(ig_btn, "", 1)

# 3. EL VESTIDOR se queda como está: markup original, botones de color.
#    (OAR 16-ago: la banda continua se muda al Lookbook; acá la decisión es
#     deliberada y los swatches la expresan mejor.)

# 4. LOOKBOOK: 16 piezas + puerta a la colección, en banda continua.
#    Nombres, precios e imágenes salen del JSON-LD de coleccion/index.html
#    (fuente estructurada), no de los nombres de archivo.
PIEZAS = [
    ("Vestido Mangas Globo",     "$85",    "vestido-mangas-globo-amarillo"),
    ("Vestido Maxi Smocked",     "$74.50", "vestido-maxi-smocked-blanco"),
    ("Vestido Maxi Cobalto",     "$65",    "vestido-cobalto"),
    ("Jeans Flare",              "$65",    "jeans-flare"),
    ("Conjunto Palazzo Blanco",  "$55",    "conjunto-blanco-palazzo"),
    ("Vestido Batik de Algodón", "$55",    "vestido-batik-coral"),
    ("Conjunto Satinado",        "$55",    "conjunto-negro-satinado"),
    ("Vestido para Eventos",     "$45",    "vestido-eventos-sage"),
    ("Conjunto Palazzo Burdeos", "$45",    "conjunto-burdeos"),
    ("Vestido Midi de Algodón",  "$44.90", "vestido-midi-algodon-indigo"),
    ("Pantalón de Lino",         "$35",    "pantalon-lino"),
    ("Conjunto Chaleco + Short", "$35",    "conjunto-chaleco-short-crema"),
    ("Vestido Broderie",         "$34.90", "vestido-broderie-rojo"),
    ("Blusa Denim Peplum",       "$29",    "blusa-denim-peplum"),
    ("Blusa Peplum Gingham",     "$26",    "blusa-peplum-gingham"),
    ("Blusa Off Shoulder",       "$22",    "blusa-off-shoulder"),
]


def pieza(nombre, precio, slug, dup):
    base = "assets/productos/" + slug
    wa = 'https://wa.me/50368590899?text=' + quote('Hola, me interesa el %s. Mi talla es: ' % nombre)
    extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
    alt = '' if dup else '%s plus size &mdash; BOLEM El Salvador' % nombre
    return (
        '                    <a href="%s" target="_blank" rel="noopener" class="lookbook-item"%s>\n'
        '                        <img src="%s-800.webp"\n'
        '                             srcset="%s-480.webp 480w, %s-800.webp 800w"\n'
        '                             sizes="(min-width: 768px) 300px, 60vw"\n'
        '                             alt="%s" width="600" height="800" decoding="async">\n'
        '                        <div class="overlay">\n'
        '                            <span class="lookbook-item__name">%s</span>\n'
        '                            <span class="lookbook-item__price">%s</span>\n'
        '                        </div>\n'
        '                    </a>\n'
    ) % (wa, extra, base, base, base, alt, nombre, precio)


def puerta(dup):
    extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
    return ('                    <a href="coleccion/" class="lookbook-item--todo"%s>\n'
            '                        <strong>Y 17 piezas m&aacute;s</strong>\n'
            '                        <span>Ver la colecci&oacute;n completa</span>\n'
            '                    </a>\n') % extra


def vuelta(dup):
    return "".join(pieza(n, p, s, dup) for n, p, s in PIEZAS) + puerta(dup)


# Dos vueltas idénticas: la animación recorre -50% y reengancha sin costura.
grid_nuevo = (
    '            <div class="home-lookbook__banda" role="group" aria-label="Piezas de la colección">\n'
    '                <div class="home-lookbook__grid">\n'
    + vuelta(False) + vuelta(True) +
    '                </div>\n'
    '            </div>\n'
)

m_look = re.search(r'([ \t]*<section id="lookbook".*?</section>\n)', txt, re.S)
assert m_look, "no se encontró el lookbook"
look = m_look.group(1)


def bloque_div(s, ini):
    """Devuelve (inicio, fin) del <div> que abre en `ini`, contando anidados.
    Un regex no-codicioso corta en el primer </div>, que aquí está DENTRO de la
    primera tarjeta (el .overlay) — eso dejaba tarjetas huérfanas fuera del
    carrusel, a 1200px de ancho cada una."""
    prof = 0
    for m in re.finditer(r'<div\b|</div>', s[ini:]):
        prof += 1 if m.group(0) == '<div' else -1
        if prof == 0:
            return ini, ini + m.end()
    raise AssertionError("div sin cerrar en el lookbook")


i = look.index('<div class="home-lookbook__grid">')
a, b = bloque_div(look, i)
while a > 0 and look[a - 1] in ' \t':
    a -= 1
if look[b:b + 1] == '\n':
    b += 1
look_nuevo = look[:a] + grid_nuevo + look[b:]
assert 'lookbook-item--todo' in look_nuevo, "no se reemplazó la parrilla del lookbook"
assert 'lookbook-item--large' not in look_nuevo, "quedaron tarjetas viejas huérfanas"

# 5. Tagline de Nuestra Esencia: "hacemos ropa" sonaba a fábrica (Mónica).
m_filo = re.search(r'([ \t]*<section id="filosofia".*?</section>\n)', txt, re.S)
m_vest = re.search(r'([ \t]*<section class="home-vestidor">.*?</section>\n)', txt, re.S)
assert m_filo and m_vest, "no se encontraron las secciones"
filo, vest = m_filo.group(1), m_vest.group(1)

filo_nuevo = filo.replace(
    'No hacemos ropa.<br>\n                    <em>Hacemos confianza.</em>',
    'Aqu&iacute; tu talla no es la excepci&oacute;n.<br>\n                    <em>Es la regla.</em>',
    1)
assert filo_nuevo != filo, "no se cambió el tagline"

# El texto del vestidor acompaña a los botones de color
vest_nuevo = vest.replace(
    'Toc&aacute; un color y decid&iacute; con cu&aacute;l te lo llev&aacute;s.',
    'Toc&aacute; un color y decid&iacute; con cu&aacute;l te lo llev&aacute;s.', 1)

# 6. Orden nuevo: hero > LOOKBOOK > VESTIDOR > Esencia > ...
txt = (txt.replace(filo, "@@S1@@", 1)
          .replace(vest, "@@S2@@", 1)
          .replace(look, "@@S3@@", 1))
txt = (txt.replace("@@S1@@", look_nuevo, 1)
          .replace("@@S2@@", vest_nuevo, 1)
          .replace("@@S3@@", filo_nuevo, 1))

# 7. JS del draft
draft_js = """
    <script>
    // === DRAFT v3.7: movimiento (respeta prefers-reduced-motion) ===
    (function () {
        var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        // -- Nada anima fuera de pantalla --------------------------------------
        // El marquee y la banda del lookbook seguían corriendo con su sección
        // fuera del viewport: el compositor pagaba por algo que nadie veía.
        var animadas = document.querySelectorAll('.home-marquee, .home-lookbook__banda');
        if (animadas.length && 'IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    e.target.classList.toggle('anim-dormida', !e.isIntersecting);
                });
            }, { rootMargin: '100px' });
            animadas.forEach(function (el) { el.classList.add('anim-dormida'); io.observe(el); });
        }

        // -- Lookbook: al tocar una tarjeta la banda se frena, para poder leerla.
        // En celular no hay hover; sin esto se toca un blanco en movimiento.
        var banda = document.querySelector('.home-lookbook__banda');
        var pista = banda && banda.querySelector('.home-lookbook__grid');
        if (banda && pista && !reduced) {
            var soltar = null;
            banda.addEventListener('pointerdown', function () {
                clearTimeout(soltar);
                pista.classList.add('is-paused');
            }, { passive: true });
            banda.addEventListener('pointerup', function () {
                soltar = setTimeout(function () { pista.classList.remove('is-paused'); }, 3000);
            }, { passive: true });
        }

        // -- Vestidor: los colores rotan solos cada 5s hasta que la usuaria elige
        var seccion = document.querySelector('.home-vestidor');
        var swatches = Array.prototype.slice.call(document.querySelectorAll('.vestidor-swatch'));
        if (seccion && swatches.length && !reduced) {
            var idx = 0, timer = null, detenido = false;
            function paso() { idx = (idx + 1) % swatches.length; swatches[idx].click(); }
            function arrancar() { if (!detenido && !timer) timer = setInterval(paso, 5000); }
            function pausar() { clearInterval(timer); timer = null; }
            new IntersectionObserver(function (entries) {
                entries.forEach(function (e) { e.isIntersecting ? arrancar() : pausar(); });
            }, { threshold: 0.35 }).observe(seccion);
            seccion.addEventListener('mouseenter', pausar);
            seccion.addEventListener('mouseleave', function () { arrancar(); });
            swatches.forEach(function (sw) {
                sw.addEventListener('click', function (ev) {
                    if (ev.isTrusted) { detenido = true; pausar(); }
                    idx = swatches.indexOf(sw);
                });
            });
        }
    })();
    </script>
"""
txt = txt.replace("</body>", draft_js + "</body>", 1)

open(ROOT + r"\draft_paleta-preview.html", "w", encoding="utf-8").write(txt)

# sanity
order = re.findall(r'<section[^>]*class="([\w-]+)"', txt)
print("orden:", " > ".join(order[:6]))
print("swatches del vestidor:", txt.count('class="vestidor-swatch'), "(esperado 4, botones de color)")
print("banda lookbook:", txt.count('home-lookbook__banda'), "| tarjetas:", txt.count('data-lb') + txt.count('class="lookbook-item"'),
      "(esperado 32 = 16 x2) + puertas:", txt.count('lookbook-item--todo'), "(esperado 2)")
print("sin flechas viejas:", 'data-lb-next' not in txt, "| sin wheel handler:", "addEventListener('wheel'" not in txt)
print("tagline:", "Es la regla" in txt, "| css inyectado:", "draft_paleta.css" in txt)
