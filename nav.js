/* ═══════════════════════════════════════════════════════════
   BOLEM — Comportamiento del nav (compartido por las 13 páginas)

   Por qué existe: hasta el 16-ago cada página traía su propia copia del menú
   móvil pegada al final del HTML. Había cuatro implementaciones distintas y
   dos de ellas topaban la altura en 300px, así que en un teléfono el menú
   recortaba los últimos enlaces. La altura la define el CSS
   (.nav-mobile.open → calc(100dvh - nav)) con overflow-y:auto, y así el panel
   nunca recorta links por más ítems o más zoom que haya.

   Cargar con: <script src="[../]nav.js" defer></script>
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function initMenu() {
    var btn = document.getElementById('menuBtn');
    var menu = document.getElementById('mobileMenu');
    if (!btn || !menu) return;

    var line1 = document.getElementById('menuLine1');
    var line2 = document.getElementById('menuLine2');
    var abierto = false;

    function pintar() {
      menu.classList.toggle('open', abierto);
      btn.setAttribute('aria-expanded', String(abierto));
      if (line1) line1.style.transform = abierto ? 'rotate(45deg) translateY(4px)' : '';
      if (line2) {
        line2.style.transform = abierto ? 'rotate(-45deg) translateY(-3px)' : '';
        line2.style.width = abierto ? '1.5rem' : '1rem';
      }
    }

    btn.addEventListener('click', function () {
      abierto = !abierto;
      pintar();
    });

    // Tocar un enlace cierra el menú: si no, al volver con el botón de atrás
    // el panel sigue abierto tapando la página.
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        abierto = false;
        pintar();
      });
    });

    // Escape cierra, y el foco vuelve al botón que lo abrió.
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && abierto) {
        abierto = false;
        pintar();
        btn.focus();
      }
    });
  }

  // La barra se vuelve sólida al bajar. En el home arranca transparente sobre
  // la foto del hero, así que sin esto el logo se pierde contra la imagen.
  function initScroll() {
    var nav = document.querySelector('.site-nav');
    if (!nav) return;
    var ticking = false;
    function actualizar() {
      nav.classList.toggle('scrolled', window.scrollY > 50);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(actualizar);
      }
    }, { passive: true });
    actualizar();
  }

  function init() {
    initMenu();
    initScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
