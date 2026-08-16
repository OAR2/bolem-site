/* Quick View — componente compartido (home + colección).
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

  var MARKUP = "  <!-- QUICK VIEW MODAL -->\n  <div class=\"qv-overlay\" id=\"qvOverlay\" aria-hidden=\"true\"></div>\n  <div class=\"qv-modal\" id=\"qvModal\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"qvName\" aria-hidden=\"true\">\n    <button class=\"qv-close\" id=\"qvClose\" aria-label=\"Cerrar\">\n      <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M18 6L6 18M6 6l12 12\"/></svg>\n    </button>\n    <div class=\"qv-image\" id=\"qvImage\">\n      <div class=\"qv-image-placeholder\" id=\"qvPlaceholder\">\n        <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><circle cx=\"8.5\" cy=\"8.5\" r=\"1.5\"/><path d=\"m21 15-5-5L5 21\"/></svg>\n        <span>Foto próximamente</span>\n      </div>\n      <button class=\"qv-arrow qv-arrow--prev\" id=\"qvPrev\" aria-label=\"Foto anterior\">\n        <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M15 18l-6-6 6-6\"/></svg>\n      </button>\n      <button class=\"qv-arrow qv-arrow--next\" id=\"qvNext\" aria-label=\"Siguiente foto\">\n        <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M9 18l6-6-6-6\"/></svg>\n      </button>\n      <div class=\"qv-dots\" id=\"qvDots\"></div>\n    </div>\n    <div class=\"qv-content\">\n      <span class=\"qv-eyebrow\">SS26 Collection</span>\n      <h3 class=\"qv-name\" id=\"qvName\"></h3>\n      <p class=\"qv-desc\" id=\"qvDesc\"></p>\n      <div class=\"qv-details\">\n        <div class=\"qv-detail\">\n          <span class=\"qv-detail-label\">Precio</span>\n          <span class=\"qv-detail-value\" id=\"qvPrice\"></span>\n        </div>\n        <div class=\"qv-detail\">\n          <span class=\"qv-detail-label\">Tallas</span>\n          <span class=\"qv-detail-value\" id=\"qvSizes\"></span>\n        </div>\n        <div class=\"qv-detail\">\n          <span class=\"qv-detail-label\">Categoría</span>\n          <span class=\"qv-detail-value\" id=\"qvCategory\"></span>\n        </div>\n      </div>\n      <a class=\"qv-cta\" id=\"qvCta\" target=\"_blank\" rel=\"noopener\">\n        <svg viewBox=\"0 0 24 24\" fill=\"currentColor\"><path d=\"M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z\"/></svg>\n        Apartar via WhatsApp\n      </a>\n      <button class=\"qv-continue\" id=\"qvContinue\">Seguir viendo</button>\n    </div>\n  </div>";

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
