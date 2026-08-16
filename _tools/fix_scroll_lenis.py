# -*- coding: utf-8 -*-
"""Arregla el salto al catalogo en coleccion/index.html.

Sintoma (OAR): tocar "Jeans" en el home lleva a la coleccion filtrada, pero la
pagina se queda arriba. Pasa con las cuatro categorias.

Causa: la pagina usa Lenis, que corre un bucle en requestAnimationFrame y
REIMPONE su propia posicion de scroll en cada cuadro. Cualquier
`scrollIntoView` o `window.scrollTo` nativo se mueve un instante y Lenis lo
devuelve a cero. La unica forma de moverla es pedirselo a Lenis.

Por que no lo detecte antes: verifique en una pestana de segundo plano, donde
Chrome congela requestAnimationFrame. Sin bucle de Lenis, nada devolvia el
scroll, y la prueba dio verde. Falso positivo del mismo tipo que el de las
mediciones de rendimiento.

De paso: `new Lenis(...)` es lo primero del arranque y depende de un CDN
externo. Si ese CDN falla, la excepcion se lleva por delante TODO lo que viene
despues — filtros, tarjetas, Quick View. Queda envuelto en try/catch.
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COL = os.path.join(r"C:\Users\othma\dev\projects\bolem-site", "coleccion", "index.html")
t = open(COL, encoding='utf-8').read()

# ── 1. exponer la instancia de Lenis y no morir si el CDN falla ──────────────
viejo = """      var lenis = new Lenis({
        duration: 1.4,
        easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }
      });
      function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
      requestAnimationFrame(raf);"""
nuevo = """      // Lenis viene de un CDN. Si no carga, la excepcion se llevaria por
      // delante todo lo que sigue (filtros, tarjetas, Quick View), asi que la
      // pagina tiene que poder seguir sin el.
      try {
        var lenis = new Lenis({
          duration: 1.4,
          easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }
        });
        // se expone porque es el UNICO que puede mover el scroll: su bucle
        // reimpone su posicion en cada cuadro y pisa cualquier scroll nativo
        window.__lenis = lenis;
        function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
        requestAnimationFrame(raf);
      } catch (e) {
        console.warn('[BOLEM] Lenis no cargo; el scroll queda nativo', e);
      }"""
assert viejo in t, "no se encontro la creacion de Lenis"
t = t.replace(viejo, nuevo, 1)

# ── 2. un solo camino para bajar al catalogo ─────────────────────────────────
viejo2 = """    // ─── LLEGAR YA FILTRADA DESDE OTRA PÁGINA ───"""
nuevo2 = """    // ─── BAJAR AL CATÁLOGO ───
    // Con Lenis activo hay que pedirselo a el: su bucle reimpone la posicion
    // cada cuadro y devuelve a cero cualquier scroll nativo.
    function irAlCatalogo(inmediato) {
      var grid = document.getElementById('catalogo');
      if (!grid) return;
      var L = window.__lenis;
      if (L && typeof L.scrollTo === 'function') {
        L.scrollTo(grid, { offset: -80, immediate: !!inmediato });
      } else {
        grid.scrollIntoView({ behavior: inmediato ? 'auto' : 'smooth' });
      }
    }

    // ─── LLEGAR YA FILTRADA DESDE OTRA PÁGINA ───"""
assert viejo2 in t
t = t.replace(viejo2, nuevo2, 1)

viejo3 = """      btn.click();
      var grid = document.getElementById('catalogo');
      if (!grid) return;
      // La pagina usa Lenis, que se apropia del scroll y suele ignorar
      // scrollIntoView. Se intenta el nativo y, si no movio nada, se empuja a
      // mano. Si ninguno funciona, la clienta aterriza arriba pero YA filtrada.
      grid.scrollIntoView();
      window.setTimeout(function () {
        if (window.scrollY < 40) {
          window.scrollTo(0, grid.getBoundingClientRect().top + window.scrollY - 80);
        }
      }, 400);
    }"""
nuevo3 = """      btn.click();
      // Dos cuadros de espera: el filtro acaba de ocultar tarjetas y hay que
      // dejar que el layout se asiente antes de medir a donde bajar.
      // Llegando desde otra pagina el salto es directo, no animado: nadie
      // quiere ver 1800px de recorrido antes de encontrar lo que busca.
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { irAlCatalogo(true); });
      });
    }"""
assert viejo3 in t, "no se encontro el fallback viejo"
t = t.replace(viejo3, nuevo3, 1)

# las tarjetas DENTRO de la coleccion tenian el mismo problema
viejo4 = """          var btn = document.querySelector('.filter-btn[data-filter="' + target + '"]');
          if (btn) btn.click();
          var grid = document.getElementById('catalogo');
          if (grid) grid.scrollIntoView({ behavior: 'smooth' });"""
nuevo4 = """          var btn = document.querySelector('.filter-btn[data-filter="' + target + '"]');
          if (btn) btn.click();
          irAlCatalogo(false);"""
assert viejo4 in t, "no se encontraron las tarjetas internas"
t = t.replace(viejo4, nuevo4, 1)

open(COL, 'w', encoding='utf-8').write(t)
print("coleccion/index.html: scroll delegado a Lenis")
print("  - instancia expuesta en window.__lenis")
print("  - new Lenis() envuelto en try/catch")
print("  - un solo irAlCatalogo() para las dos entradas (hash y tarjetas internas)")
