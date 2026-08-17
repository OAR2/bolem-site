// BOLEM v2 — lo minimo. El sitio funciona entero sin este archivo.
(function () {
  var nav = document.getElementById('nav'), btn = document.getElementById('navBtn');
  if (nav && btn) btn.addEventListener('click', function () {
    var abierto = nav.classList.toggle('abierto');
    btn.setAttribute('aria-expanded', abierto ? 'true' : 'false');
  });
  // Galeria: sin JS se ven todas las fotos igual; esto solo sube la que se toca.
  var grande = document.getElementById('galPrincipal');
  var tira = document.querySelector('.gal-tira');
  if (grande && tira) tira.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-src]');
    if (!b) return;
    grande.src = b.dataset.src; grande.srcset = b.dataset.set;
    tira.querySelectorAll('button').forEach(function (o) {
      o.setAttribute('aria-current', o === b ? 'true' : 'false');
    });
  });
})();
