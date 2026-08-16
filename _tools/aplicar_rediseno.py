# -*- coding: utf-8 -*-
"""UNA SOLA VEZ — ya se corrio el 2026-08-16 sobre index.html.
Reescribe el home con la estructura del rediseno. No es idempotente: sus
asserts fallan al segundo intento porque los cambios ya estan aplicados.
Queda como registro de que se hizo, no como herramienta a repetir."""
import sys, io, re
from urllib.parse import quote
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"
txt = open(ROOT + r"\index.html", encoding="utf-8").read()

# 1. Inyectar CSS del draft + marcar el tab
txt = txt.replace('home.css">', 'home.css">'
                  '\n    <link rel="stylesheet" href="quickview.css">', 1)

# 2. HERO: fuera el botón a Instagram (Mónica: la clienta YA viene de ahí).
#    Sobrevive solo en el cierre de la página (.home-cta__btn-ig).
ig_btn = ('                <a href="https://www.instagram.com/bolem_sv" target="_blank" '
          'class="home-hero__btn-secondary">@bolem_sv</a>\n')
assert ig_btn in txt, "no se encontró el botón IG del hero"
txt = txt.replace(ig_btn, "", 1)

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


# 3. EL VESTIDOR se queda como está: markup original, botones de color.
#    (OAR 16-ago: la banda continua se muda al Lookbook; acá la decisión es
#     deliberada y los swatches la expresan mejor.)

# 4. LOOKBOOK: las 33 piezas en dos bandas, con Quick View al tocar.
#    Los datos (nombre, precio, tallas, categoria, fotos, enlace de WhatsApp)
#    se LEEN de coleccion/index.html, que es la fuente. Si Monica cambia un
#    precio alla, el home cambia solo; una lista propia aca se desincroniza,
#    que es exactamente lo que paso con las paginas satelite en julio.
def leer_catalogo():
    col = open(ROOT + r"\coleccion\index.html", encoding="utf-8").read()
    prods = {}
    for trozo in re.split(r'(?=<div class="product-card)', col)[1:]:
        did = re.search(r'data-id="([^"]+)"', trozo)
        if not did:
            continue

        def tx(cls):
            m = re.search(r'class="%s"[^>]*>(.*?)<' % cls, trozo, re.S)
            return m.group(1).strip() if m else ''

        cat = re.search(r'data-category="([^"]+)"', trozo)
        imgs = re.search(r'data-images="([^"]+)"', trozo)
        img1 = re.search(r'<img src="([^"]+)"[^>]*class="product-img"', trozo)
        cta = re.search(r'<a href="(https://wa\.me/[^"]+)" class="product-cta"', trozo)
        crudas = imgs.group(1) if imgs else (img1.group(1) if img1 else '')
        # la coleccion vive en /coleccion/, el home en la raiz
        fotos = ",".join(s.strip().replace("../", "") for s in crudas.split(",") if s.strip())
        prods[did.group(1)] = dict(
            nombre=tx('product-name'), precio=tx('product-price'),
            tallas=tx('product-sizes'), cat=cat.group(1) if cat else '',
            fotos=fotos, cta=cta.group(1) if cta else '')
    return prods


CATALOGO = leer_catalogo()
assert len(CATALOGO) == 33, "se esperaban 33 productos, hay %d" % len(CATALOGO)

# Fila de arriba: lo que se lleva puesto completo. Fila de abajo: lo que se combina.
ORDEN_1 = ["vestido-mangas-globo", "vestido-maxi-smocked", "vestido-cobalto", "jeans-flare",
           "conjunto-blanco-palazzo", "vestido-batik", "conjunto-negro-satinado",
           "vestido-eventos-sage", "conjunto-burdeos", "vestido-midi-algodon",
           "pantalon-lino", "conjunto-chaleco-short", "vestido-broderie-rojo",
           "blusa-denim-peplum", "blusa-peplum-gingham", "blusa-off-shoulder"]
ORDEN_2 = ["chaleco-elegante-marfil", "chaleco-sastre", "pantalon-formal-crema",
           "vestido-utilitario-crema", "vestido-verano-rojo", "vestido-shirtdress",
           "blusa-peplum-crema", "blusa-balloon", "blusa-halter-olivo", "blusa-wrap-marino",
           "blusa-negra-botones", "blusa-peplum-blush", "chaleco-cardigan-beige",
           "blusa-blazer-negro", "top-peplum-negro", "camisa-fucsia", "blusa-peplum-rayas"]
assert len(set(ORDEN_1 + ORDEN_2)) == 33, "las dos filas no cubren el catalogo sin repetir"
for _id in ORDEN_1 + ORDEN_2:
    assert _id in CATALOGO, "id que no existe en la coleccion: " + _id


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


def pieza(pid, dup, prioritaria=False):
    d = CATALOGO[pid]
    portada = d['fotos'].split(',')[0]
    base = re.sub(r'\.webp$', '', portada)
    extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
    alt = '' if dup else esc('%s plus size \u2014 BOLEM El Salvador' % d['nombre'])
    # Las copias reutilizan las mismas URLs: no cuestan una descarga mas.
    # Las copias comparten URL con las originales: ser lazy no les ahorra una
    # sola descarga (salen del cache) y sí las expone a entrar en blanco cuando
    # la banda las trae a la vista. Van eager, en prioridad baja.
    if dup or not prioritaria:
        carga = 'loading="eager" fetchpriority="low"'
    else:
        carga = 'loading="eager"'
    # href a la coleccion = camino real sin JS y enlace interno que Google sigue.
    # El de WhatsApp pasa a data-qv-cta: ahora se llega ahi DESPUES de ver la
    # ficha, no en el primer clic.
    return (
        '                    <a href="coleccion/" class="lookbook-item" data-qv%s\n'
        '                       data-qv-nombre="%s" data-qv-precio="%s" data-qv-tallas="%s"\n'
        '                       data-qv-categoria="%s" data-qv-cta="%s"\n'
        '                       data-images="%s">\n'
        '                        <img src="%s-480.webp"\n'
        '                             srcset="%s-480.webp 480w, %s-800.webp 800w"\n'
        '                             sizes="(min-width: 768px) 300px, 60vw"\n'
        '                             alt="%s" width="600" height="800" decoding="async" %s>\n'
        '                        <div class="overlay">\n'
        '                            <span class="lookbook-item__name">%s</span>\n'
        '                        </div>\n'
        '                    </a>\n'
    ) % (extra, esc(d['nombre']), esc(d['precio']), esc(d['tallas']), esc(d['cat']),
         esc(d['cta']), esc(d['fotos']), base, base, base, alt, carga,
         esc(d['nombre']))


def puerta(dup):
    extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
    return ('                    <a href="coleccion/" class="lookbook-item--todo"%s>\n'
            '                        <strong>Ver la colecci&oacute;n completa</strong>\n'
            '                        <span>33 piezas, con filtros y tallas</span>\n'
            '                    </a>\n') % extra


def vuelta(orden, con_puerta, dup):
    s = "".join(pieza(pid, dup, prioritaria=(i < 6 and con_puerta))
                for i, pid in enumerate(orden))
    return s + (puerta(dup) if con_puerta else "")


# Cada fila lleva sus piezas DOS veces: la animacion recorre exactamente la
# mitad y reengancha sin costura. Las dos filas tienen 17 tarjetas cada una,
# asi que con la misma duracion van a la misma velocidad en sentidos opuestos.
grid_nuevo = (
    '            <div class="home-lookbook__banda" role="group" aria-label="Piezas de la colecci\u00f3n">\n'
    '                <div class="home-lookbook__grid">\n'
    + vuelta(ORDEN_1, True, False) + vuelta(ORDEN_1, True, True) +
    '                </div>\n'
    '                <div class="home-lookbook__grid home-lookbook__grid--rev">\n'
    + vuelta(ORDEN_2, False, False) + vuelta(ORDEN_2, False, True) +
    '                </div>\n'
    '            </div>\n'
)

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
txt = (txt.replace("@@S1@@", seccion_cats + look_nuevo, 1)
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
txt = txt.replace("</body>", draft_js +
                  '    <script src="quickview.js" defer></script>\n</body>', 1)

open(ROOT + r"\index.html", "w", encoding="utf-8").write(txt)

# sanity
order = re.findall(r'<section[^>]*class="([\w-]+)"', txt)
print("orden:", " > ".join(order[:6]))
print("swatches del vestidor:", txt.count('class="vestidor-swatch'), "(esperado 4, botones de color)")
print("filas del lookbook:", txt.count('class="home-lookbook__grid'), "(esperado 2) | en reversa:",
      txt.count('home-lookbook__grid--rev'), "(esperado 1)")
print("tarjetas:", txt.count('class="lookbook-item"'), "(esperado 66 = (16+17) x2) + puertas:",
      txt.count('lookbook-item--todo'), "(esperado 2)")
_slugs = set(ORDEN_1) | set(ORDEN_2)
print("piezas únicas entre las dos filas:", len(_slugs), "(esperado 33, sin repetir)")
print("sin flechas viejas:", 'data-lb-next' not in txt, "| sin wheel handler:", "addEventListener('wheel'" not in txt)
print("tagline:", "Es la regla" in txt)
print("categorías:", txt.count('class="home-categoria"'), "(esperado 4) | filtro por dirección:",
      "coleccion/#vestido" in txt)
print("sin precio en las bandas:", txt.count('lookbook-item__price') == 0)
print("hero con foto:", "home-hero__foto" in txt,
      "| VIP sin formulario:", "vipForm" not in txt and "home-vip__cta" in txt)
print("Quick View enganchado:", "quickview.css" in txt and "quickview.js" in txt,
      "| tarjetas con data-qv:", txt.count("data-qv-nombre"), "(esperado 66)")
print("sin wa.me en el href de las tarjetas:", 'class="lookbook-item" data-qv' in txt
      and 'href="https://wa.me' not in txt.split('home-lookbook__banda')[1].split("</section>")[0])
