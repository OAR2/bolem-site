# -*- coding: utf-8 -*-
"""Saca el Quick View de coleccion/index.html a quickview.css + quickview.js,
para que el home y la coleccion usen UNA sola copia.

Por que compartido y no copiado: este proyecto ya se quemo dos veces con copias
que se desincronizan — las tallas y precios viejos en las paginas satelite
(jul-2026) y la correccion del canon de marca que llego a unas paginas y a
otras no (54ac3ad, descubierto el 16-ago).

El JS ahora inyecta su propio markup y lee los datos de la tarjeta con
data-qv-* y, si no hay, de los hijos .product-name/.product-price/etc. Asi las
33 tarjetas de la coleccion siguen funcionando sin tocarles un atributo.
"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"
COL = os.path.join(ROOT, "coleccion", "index.html")
t = open(COL, encoding='utf-8').read()


def tajada(texto, ini, fin, que):
    i = texto.index(ini)
    j = texto.index(fin)
    assert j > i, "limites invertidos en " + que
    return texto[i:j], i, j


# ── 1. CSS ────────────────────────────────────────────────────────────────────
css, ci, cj = tajada(t, "    /* ─── QUICK VIEW MODAL ─── */",
                        "    /* ─── PAGE LOADER ─── */", "css")
css_limpio = "\n".join(l[4:] if l.startswith("    ") else l for l in css.split("\n")).rstrip() + "\n"
css_final = ("/* Quick View — componente compartido entre el home y la colección.\n"
             "   Extraído de coleccion/index.html el 2026-08-16. Una sola copia:\n"
             "   lo que se arregle acá vale para las dos páginas. */\n\n") + css_limpio
open(os.path.join(ROOT, "quickview.css"), "w", encoding="utf-8").write(css_final)
print("quickview.css:", len(css_final.split("\n")), "líneas")

# ── 2. markup ─────────────────────────────────────────────────────────────────
mk, mi, mj = tajada(t, "  <!-- QUICK VIEW MODAL -->", "  <!-- FOOTER -->", "markup")
markup = mk.rstrip()

# ── 3. JS viejo (se reemplaza por el compartido) ──────────────────────────────
js, ji, jj = tajada(t, "    // ─── QUICK VIEW ───", "    // ─── LISTA VIP (M3) ───", "js")

# ── 4. reescribir coleccion/index.html ────────────────────────────────────────
nuevo = t
# el bloque JS mas abajo primero, para no correr los indices
nuevo = nuevo[:ji] + nuevo[jj:]
nuevo = nuevo[:mi] + nuevo[mj:]
nuevo = nuevo[:ci] + nuevo[cj:]
# la llamada al init la hace ahora el propio quickview.js
nuevo = nuevo.replace("      initQuickView();\n", "")
assert "initQuickView" not in nuevo, "quedó una referencia a initQuickView"
assert "qv-modal" not in nuevo, "quedó markup del Quick View"
assert ".qv-overlay {" not in nuevo, "quedó CSS del Quick View"

# enganchar los archivos compartidos
ancla = '<link rel="stylesheet" href="../styles.css">'
assert ancla in nuevo, "no se encontró el link a styles.css"
nuevo = nuevo.replace(ancla, ancla + '\n  <link rel="stylesheet" href="../quickview.css">', 1)
nuevo = nuevo.replace("</body>", '  <script src="../quickview.js" defer></script>\n</body>', 1)
open(COL, "w", encoding="utf-8").write(nuevo)
print("coleccion/index.html: -%d líneas" % (len(t.split("\n")) - len(nuevo.split("\n"))))

# ── 5. quickview.js compartido ────────────────────────────────────────────────
JS = '''/* Quick View — componente compartido (home + colección).
   Extraído de coleccion/index.html el 2026-08-16.

   Inyecta su propio markup y se engancha a cualquier tarjeta que sea
   .product-card o lleve [data-qv]. Los datos salen de data-qv-* y, si no
   están, de los hijos .product-name / .product-price / .product-sizes /
   .product-cta — así las 33 tarjetas de la colección siguen igual.

   Conserva todo lo del original: galería con flechas, puntitos y swipe,
   Escape, flechas del teclado, trampa de foco, bloqueo del scroll de fondo
   y devolución del foco a la tarjeta al cerrar. */
(function () {
  'use strict';

  var MARKUP = %s;

  var etiquetasCat = {
    vestido: 'Vestido',
    blusa: 'Blusa',
    pantalon: 'Jeans y Pantalón',
    conjunto: 'Conjunto'
  };

  var descripciones = {
    vestido: 'Tela fluida que abraza cada curva con intención — de un brunch a una cena, sin cambiarte.',
    blusa: 'Versátil y femenina. Combinala con todo — jeans, palazzos, o sola con actitud.',
    pantalon: 'Corte que estiliza y tela que se adapta. Pensado para que te sientas cómoda todo el día sin sacrificar estilo.',
    conjunto: 'Look completo sin pensarlo. Dos piezas que funcionan juntas o por separado.'
  };

  function init() {
    if (!document.getElementById('qvModal')) {
      var cont = document.createElement('div');
      cont.innerHTML = MARKUP;
      while (cont.firstChild) document.body.appendChild(cont.firstChild);
    }

    var overlay = document.getElementById('qvOverlay');
    var modal = document.getElementById('qvModal');
    if (!overlay || !modal) return;

    var closeBtn = document.getElementById('qvClose');
    var continueBtn = document.getElementById('qvContinue');
    var qvName = document.getElementById('qvName');
    var qvDesc = document.getElementById('qvDesc');
    var qvPrice = document.getElementById('qvPrice');
    var qvSizes = document.getElementById('qvSizes');
    var qvCategory = document.getElementById('qvCategory');
    var qvCta = document.getElementById('qvCta');
    var qvImage = document.getElementById('qvImage');
    var qvPlaceholder = document.getElementById('qvPlaceholder');
    var qvPrev = document.getElementById('qvPrev');
    var qvNext = document.getElementById('qvNext');
    var qvDots = document.getElementById('qvDots');

    var imagenes = [];
    var indice = 0;
    var ultimoFoco = null;

    // Los datos pueden venir en data-qv-* (home) o en los hijos (colección).
    function datos(card) {
      var txt = function (sel) {
        var e = card.querySelector(sel);
        return e ? e.textContent.trim() : '';
      };
      var d = card.dataset;
      var cta = d.qvCta;
      if (!cta) {
        var a = card.querySelector('.product-cta');
        cta = a ? a.href : (card.tagName === 'A' ? card.href : '');
      }
      return {
        nombre: d.qvNombre || txt('.product-name') || txt('.lookbook-item__name'),
        precio: d.qvPrecio || txt('.product-price') || txt('.lookbook-item__price'),
        tallas: d.qvTallas || txt('.product-sizes') || '',
        categoria: d.qvCategoria || d.category || '',
        cta: cta,
        imagenes: d.images || ''
      };
    }

    function mostrar(i) {
      indice = i;
      qvImage.querySelectorAll('img').forEach(function (img, k) {
        img.classList.toggle('active', k === i);
      });
      qvDots.querySelectorAll('.qv-dot').forEach(function (p, k) {
        p.classList.toggle('active', k === i);
      });
    }

    function galeria(fuentes, nombre) {
      qvImage.querySelectorAll('img').forEach(function (img) { img.remove(); });
      qvDots.innerHTML = '';

      if (!fuentes || !fuentes.length) {
        qvPlaceholder.style.display = 'flex';
        qvPrev.classList.remove('visible');
        qvNext.classList.remove('visible');
        imagenes = [];
        return;
      }

      qvPlaceholder.style.display = 'none';
      imagenes = fuentes;

      fuentes.forEach(function (src, i) {
        var img = document.createElement('img');
        img.src = src;
        img.alt = nombre + ' — foto ' + (i + 1);
        img.loading = 'lazy';
        if (i === 0) img.classList.add('active');
        qvImage.appendChild(img);
      });

      if (fuentes.length > 1) {
        qvPrev.classList.add('visible');
        qvNext.classList.add('visible');
        fuentes.forEach(function (_, i) {
          var p = document.createElement('button');
          p.className = 'qv-dot' + (i === 0 ? ' active' : '');
          p.setAttribute('aria-label', 'Foto ' + (i + 1));
          p.addEventListener('click', function (e) { e.stopPropagation(); mostrar(i); });
          qvDots.appendChild(p);
        });
      } else {
        qvPrev.classList.remove('visible');
        qvNext.classList.remove('visible');
      }
      indice = 0;
    }

    function abrir(card) {
      var d = datos(card);
      qvName.textContent = d.nombre;
      qvPrice.textContent = d.precio;
      qvSizes.textContent = d.tallas;
      qvCategory.textContent = etiquetasCat[d.categoria] || d.categoria;
      qvCta.href = d.cta;
      qvDesc.textContent = descripciones[d.categoria] || descripciones.vestido;

      var fuentes = [];
      if (d.imagenes) {
        fuentes = d.imagenes.split(',').map(function (s) { return s.trim(); });
      } else {
        var img = card.querySelector('img');
        if (img) fuentes = [img.currentSrc || img.src];
      }
      galeria(fuentes, d.nombre);

      ultimoFoco = card;
      overlay.classList.add('active');
      modal.classList.add('active');
      modal.removeAttribute('aria-hidden');
      document.body.style.overflow = 'hidden';
      window.setTimeout(function () { closeBtn.focus(); }, 0);
    }

    function enfocables() {
      var sel = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';
      return Array.prototype.filter.call(modal.querySelectorAll(sel), function (el) {
        if (el === document.activeElement) return true;
        if (el.offsetParent === null) return false;
        var cs = window.getComputedStyle(el);
        return cs.visibility !== 'hidden' && cs.display !== 'none';
      });
    }

    function atraparTab(e) {
      if (e.key !== 'Tab') return;
      var lista = enfocables();
      if (!lista.length) { e.preventDefault(); return; }
      var primero = lista[0], ultimo = lista[lista.length - 1];
      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault(); ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault(); primero.focus();
      } else if (!modal.contains(document.activeElement)) {
        e.preventDefault(); primero.focus();
      }
    }

    function cerrar() {
      overlay.classList.remove('active');
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (ultimoFoco && typeof ultimoFoco.focus === 'function') ultimoFoco.focus();
      ultimoFoco = null;
    }

    qvPrev.addEventListener('click', function (e) {
      e.stopPropagation();
      if (imagenes.length < 2) return;
      mostrar(indice <= 0 ? imagenes.length - 1 : indice - 1);
    });
    qvNext.addEventListener('click', function (e) {
      e.stopPropagation();
      if (imagenes.length < 2) return;
      mostrar(indice >= imagenes.length - 1 ? 0 : indice + 1);
    });

    document.addEventListener('keydown', function (e) {
      if (!modal.classList.contains('active')) return;
      atraparTab(e);
      if (e.key === 'ArrowLeft') qvPrev.click();
      else if (e.key === 'ArrowRight') qvNext.click();
      else if (e.key === 'Escape') cerrar();
    });

    var tocoEnX = 0;
    qvImage.addEventListener('touchstart', function (e) {
      tocoEnX = e.changedTouches[0].clientX;
    }, { passive: true });
    qvImage.addEventListener('touchend', function (e) {
      if (imagenes.length < 2) return;
      var dif = tocoEnX - e.changedTouches[0].clientX;
      if (Math.abs(dif) > 40) (dif > 0 ? qvNext : qvPrev).click();
    }, { passive: true });

    document.querySelectorAll('.product-card, [data-qv]').forEach(function (card) {
      card.addEventListener('click', function (e) {
        if (e.target.closest('.product-cta')) return;
        e.preventDefault();
        abrir(card);
      });
      card.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
        if (e.target.closest('.product-cta')) return;
        e.preventDefault();
        abrir(card);
      });
    });

    closeBtn.addEventListener('click', cerrar);
    continueBtn.addEventListener('click', cerrar);
    overlay.addEventListener('click', cerrar);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
'''

import json as _json
open(os.path.join(ROOT, "quickview.js"), "w", encoding="utf-8").write(
    JS % _json.dumps(markup, ensure_ascii=False))
print("quickview.js: escrito")

# ── 6. los 5 precios con decimal incompleto ($74.5 -> $74.50) ─────────────────
t2 = open(COL, encoding='utf-8').read()
arreglados = 0


def cero(m):
    global arreglados
    arreglados += 1
    return m.group(0) + '0'


t2 = re.sub(r'(?<=class="product-price">)\$\d+\.\d(?=<)', cero, t2)
open(COL, "w", encoding="utf-8").write(t2)
print("precios completados a dos decimales:", arreglados)
