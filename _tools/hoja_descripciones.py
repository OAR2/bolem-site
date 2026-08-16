# -*- coding: utf-8 -*-
"""Genera la hoja de preguntas para Monica — insumo de las paginas de producto.

Por que existe: las 33 prendas del catalogo tienen nombre, precio, tallas y
foto, y NADA MAS. Cero texto. Eso es justo lo que a Google le falta para
mostrarlas, y es tambien lo que una clienta necesita leer antes de mandar
plata por WhatsApp a una marca que no conoce.

Y no se puede inventar. La tela, si transparenta, si estira, si encoge y como
se lava NO se ven en una foto. Escribirlo a ojo seria publicar datos falsos
sobre ropa que la gente compra por talla, y eso vuelve como devolucion.

Por eso la hoja NO le pide a Monica que escriba descripciones —eso no pasa
nunca— sino que conteste cuatro preguntas por prenda, por nota de voz, con la
prenda en la mano. Del audio sale el texto.

Las fotos van incrustadas en el archivo (base64) porque la pagina publicada no
puede pedirle imagenes a otro servidor.

Uso:  python _tools/hoja_descripciones.py
Sale: output/hoja-descripciones-bolem.html  (se publica como artifact)
"""
import base64
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# El entregable NO vive en este repo: todo lo que esta aca se publica en
# GitHub Pages, y esta hoja es un documento de trabajo con las 33 fotos
# adentro. Va a output/ del repo de OAR, que es donde viven los entregables.
SALIDA = os.path.join('G:/My Drive/00 - TOOLS/CLAUDE', 'output', 'hoja-descripciones-bolem.html')

PREGUNTAS = [
    ('La tela', '¿De qué es y cómo se siente? ¿Estira? ¿Transparenta? ¿Pesa o es fresca? ¿Se lava a máquina?'),
    ('Cómo queda', '¿Es fiel a la talla, corre chica o corre grande? ¿Es holgada arriba, marca cintura, cae suelta?'),
    ('Para cuándo', '¿En qué ocasión te la imaginás puesta? Trabajo, una fiesta, un domingo, la playa.'),
    ('Por qué esta', '¿Por qué la elegiste vos, entre todo lo que viste en la feria? Esto es lo que nadie más puede copiar.'),
]


def b64(ruta):
    """Miniatura incrustada. Las fotos van DENTRO del archivo porque la pagina
    publicada no puede pedirle imagenes a otro servidor. Con las de 480px el
    archivo pesaba 1.2 MB y el publicador lo rechazaba con 502; a 200px de
    ancho pesa la sexta parte y sigue sobrando para reconocer la prenda, que
    es lo unico que tiene que hacer esta foto."""
    from PIL import Image
    im = Image.open(ruta)
    im.thumbnail((200, 300))
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=72)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def main():
    datos = json.load(open(os.path.join(RAIZ, '_data', 'catalogo.json'), encoding='utf-8'))
    productos = datos['productos']
    etiquetas = {k: v['etiqueta'] for k, v in datos['categorias'].items()}

    # Prioridad: las 4 que el sitio ya destaca. El resto lo ordena Monica —
    # cual se vende mas es dato suyo, no nuestro (rules/identidad: sin fuente,
    # no se inventa un ranking).
    productos = sorted(productos, key=lambda p: (not p.get('destacada'), p['categoria'], p['nombre']))

    tarjetas = []
    faltantes = []
    for i, p in enumerate(productos):
        foto = p['fotos'][0].replace('.webp', '-480.webp')
        ruta = os.path.join(RAIZ, 'assets', 'productos', foto)
        if not os.path.exists(ruta):
            faltantes.append(foto)
            continue
        tallas = ' · '.join(p['tallas'])
        destacada = ' <span class="badge">empezá por esta</span>' if p.get('destacada') else ''
        preguntas = '\n'.join(
            '          <li><b>%s.</b> %s</li>' % (t, q) for t, q in PREGUNTAS)
        tarjetas.append("""
      <article class="prenda" data-i="{i}">
        <div class="foto"><img src="data:image/webp;base64,{img}" alt="{nombre}" loading="lazy"></div>
        <div class="cuerpo">
          <p class="meta"><span class="num">{n:02d}</span> · {categoria} · ${precio} · tallas {tallas}</p>
          <h2>{nombre}{destacada}</h2>
          <ol class="preguntas">
{preguntas}
          </ol>
          <p class="opcional">Si tenés la cinta a mano: busto, cintura y cadera <b>de la prenda acostada</b>, por talla. Eso arregla la tabla de tallas de una vez.</p>
          <textarea placeholder="Si preferís escribir, acá. Si mandás nota de voz, decí primero el número {n:02d}." aria-label="Notas sobre {nombre}"></textarea>
          <button class="listo" type="button">Marcar lista</button>
        </div>
      </article>""".format(i=i, img=b64(ruta), nombre=p['nombre'].replace('"', '&quot;'),
                           n=i + 1, categoria=etiquetas.get(p['categoria'], p['categoria']),
                           precio=('%.2f' % p['precio']).rstrip('0').rstrip('.'),
                           tallas=tallas, destacada=destacada, preguntas=preguntas))

    if faltantes:
        print('ABORTADO — faltan fotos 480px:', faltantes)
        return 1

    html = PLANTILLA.replace('<!--TARJETAS-->', '\n'.join(tarjetas)) \
                    .replace('{{TOTAL}}', str(len(tarjetas)))
    # Acentos a entidades HTML. La pagina se publica dentro de un envoltorio
    # que no controlamos, y una declaracion de charset que llegue tarde el
    # navegador la ignora: servida como latin-1 se leia "MA3nica" y "sabA(c)s".
    # Con entidades se ve bien pase lo que pase con el charset.
    html = html.encode('ascii', 'xmlcharrefreplace').decode('ascii')
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    open(SALIDA, 'w', encoding='ascii', newline='').write(html)
    print('   %d prendas · %d KB' % (len(tarjetas), os.path.getsize(SALIDA) // 1024))
    print('   ' + SALIDA)
    return 0


PLANTILLA = r"""<title>Las 33 Prendas de BOLEM</title>
<style>
  :root {
    --papel: #F7F4EF;
    --sup: #FFFFFF;
    --sup2: #F1EDE6;
    --tinta: #211C17;
    --tinta2: #6B6259;
    --linea: #DED7CC;
    --linea-suave: #EBE5DB;
    --verde: #2C6049;
    --verde-claro: #E4EFE8;
    --sobre-verde: #FFFFFF;
    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", system-ui, sans-serif;
    --mono: ui-monospace, "Cascadia Mono", Consolas, "SF Mono", Menlo, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --papel: #191512; --sup: #221D19; --sup2: #2A241F;
      --tinta: #EDE7DF; --tinta2: #A79C90;
      --linea: #372F28; --linea-suave: #2C2621;
      --verde: #7FC3A3; --verde-claro: #1E3A2E; --sobre-verde: #14100D;
    }
  }
  :root[data-theme="dark"] {
    --papel: #191512; --sup: #221D19; --sup2: #2A241F;
    --tinta: #EDE7DF; --tinta2: #A79C90;
    --linea: #372F28; --linea-suave: #2C2621;
    --verde: #7FC3A3; --verde-claro: #1E3A2E; --sobre-verde: #14100D;
  }

  body { background: var(--papel); color: var(--tinta); font-family: var(--sans); font-size: 1.0625rem; line-height: 1.55; -webkit-font-smoothing: antialiased; }
  .wrap { max-width: 44rem; margin: 0 auto; padding: 0 1rem 6rem; }

  header { padding: 2.5rem 0 1.5rem; border-bottom: 1px solid var(--linea); }
  .eyebrow { font-family: var(--mono); font-size: .7rem; letter-spacing: .14em; text-transform: uppercase; color: var(--tinta2); }
  h1 { font-family: var(--serif); font-size: clamp(2rem, 7vw, 2.9rem); line-height: 1.05; font-weight: 400; margin: .5rem 0 0; text-wrap: balance; }
  .deck { color: var(--tinta2); margin-top: .9rem; max-width: 40ch; }
  .como { background: var(--sup); border: 1px solid var(--linea); border-left: 3px solid var(--verde); border-radius: 3px; padding: 1rem 1.1rem; margin-top: 1.4rem; font-size: .97rem; }
  .como b { color: var(--tinta); }
  .como p + p { margin-top: .6rem; }

  .barra { position: sticky; top: 0; z-index: 5; background: var(--papel); border-bottom: 1px solid var(--linea); padding: .7rem 0; margin-bottom: 1.5rem; display: flex; align-items: center; gap: .8rem; }
  .barra .cuenta { font-family: var(--mono); font-size: .8rem; color: var(--tinta2); white-space: nowrap; font-variant-numeric: tabular-nums; }
  .riel { flex: 1; height: 5px; background: var(--linea-suave); border-radius: 99px; overflow: hidden; }
  .relleno { height: 100%; width: 0%; background: var(--verde); transition: width .3s ease; }

  .prenda { display: grid; grid-template-columns: 7.5rem 1fr; gap: 1rem; background: var(--sup); border: 1px solid var(--linea); border-radius: 3px; padding: 1rem; margin-bottom: 1rem; align-items: start; }
  @media (max-width: 33rem) { .prenda { grid-template-columns: 5rem 1fr; gap: .8rem; padding: .8rem; } }
  .prenda.hecha { background: var(--verde-claro); border-color: var(--verde); }
  .prenda.hecha .preguntas, .prenda.hecha textarea, .prenda.hecha .opcional { display: none; }
  .foto img { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 2px; display: block; background: var(--sup2); }
  .meta { font-family: var(--mono); font-size: .68rem; letter-spacing: .06em; text-transform: uppercase; color: var(--tinta2); }
  .meta .num { color: var(--verde); font-weight: 700; }
  .cuerpo h2 { font-family: var(--serif); font-size: 1.3rem; font-weight: 400; line-height: 1.2; margin: .25rem 0 .8rem; text-wrap: balance; }
  .badge { display: inline-block; font-family: var(--mono); font-size: .6rem; letter-spacing: .1em; text-transform: uppercase; background: var(--verde); color: var(--sobre-verde); padding: .2rem .45rem; border-radius: 2px; vertical-align: middle; margin-left: .4rem; }
  .preguntas { list-style: none; display: flex; flex-direction: column; gap: .5rem; margin: 0 0 .8rem; font-size: .95rem; color: var(--tinta2); }
  .preguntas b { color: var(--tinta); font-weight: 600; }
  .opcional { font-size: .85rem; color: var(--tinta2); border-top: 1px dashed var(--linea); padding-top: .6rem; margin-bottom: .7rem; }
  textarea { width: 100%; min-height: 4rem; font-family: var(--sans); font-size: 1rem; color: var(--tinta); background: var(--sup2); border: 1px solid var(--linea); border-radius: 2px; padding: .6rem .7rem; resize: vertical; margin-bottom: .6rem; }
  textarea:focus-visible, button:focus-visible { outline: 2px solid var(--verde); outline-offset: 2px; }
  ::placeholder { color: var(--tinta2); opacity: .75; }
  button { font-family: var(--sans); font-size: .9rem; font-weight: 600; cursor: pointer; border-radius: 3px; padding: .55rem 1rem; border: 1px solid var(--verde); background: transparent; color: var(--verde); }
  .prenda.hecha .listo { background: var(--verde); color: var(--sobre-verde); }
  .cierre { margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--linea); display: flex; flex-direction: column; gap: .9rem; }
  .cierre h2 { font-family: var(--serif); font-size: 1.5rem; font-weight: 400; }
  .btn-grande { align-self: flex-start; background: var(--verde); color: var(--sobre-verde); border-color: var(--verde); font-size: 1rem; padding: .75rem 1.3rem; }
  #estado { font-family: var(--mono); font-size: .78rem; color: var(--verde); min-height: 1.2em; }
  #salida { min-height: 8rem; font-family: var(--mono); font-size: .8rem; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <header>
    <div class="eyebrow">BOLEM · para Mónica · agosto 2026</div>
    <h1>Las 33 prendas, contadas por vos</h1>
    <p class="deck">Cada prenda del sitio tiene hoy nombre, precio y foto. Nada más. Esto es lo que falta — y solo lo sabés vos, porque las tuviste en la mano.</p>
    <div class="como">
      <p><b>Cómo se hace:</b> agarrá la prenda, mirá las cuatro preguntas y contestá por <b>nota de voz</b>. Decí primero el número que aparece arriba del nombre. Escribir también sirve, pero la voz es más rápida.</p>
      <p><b>No hace falta hacerlas todas hoy.</b> Empezá por las cuatro marcadas y seguí por las que más se venden — eso lo sabés vos. Con ocho ya se puede armar la primera tanda de páginas.</p>
      <p><b>Si no sabés algo, decilo.</b> Es mil veces mejor que quede en blanco a que el sitio diga que una tela no transparenta y sí lo haga.</p>
    </div>
  </header>

  <div class="barra">
    <span class="cuenta"><span id="hechas">0</span>/{{TOTAL}} listas</span>
    <div class="riel"><div class="relleno" id="relleno"></div></div>
  </div>

  <main><!--TARJETAS--></main>

  <section class="cierre">
    <h2>Cuando quieras mandarlo</h2>
    <p>Si escribiste algo, este botón lo junta todo para pegarlo en el chat. Las notas de voz mandalas por aparte, diciendo el número de cada prenda.</p>
    <button class="btn-grande" id="copiar" type="button">Copiar lo que escribí</button>
    <div id="estado" role="status" aria-live="polite"></div>
    <textarea id="salida" readonly aria-label="Tus respuestas, listas para copiar"></textarea>
  </section>
</div>

<script>
  var tarjetas = Array.prototype.slice.call(document.querySelectorAll('.prenda'));
  var hechas = document.getElementById('hechas');
  var relleno = document.getElementById('relleno');
  var salida = document.getElementById('salida');
  var estado = document.getElementById('estado');

  function guardar(k, v) { try { localStorage.setItem('bolem-desc-' + k, v); } catch (e) {} }
  function leer(k) { try { return localStorage.getItem('bolem-desc-' + k) || ''; } catch (e) { return ''; } }

  function progreso() {
    var n = tarjetas.filter(function (t) { return t.classList.contains('hecha'); }).length;
    hechas.textContent = n;
    relleno.style.width = (n / tarjetas.length * 100) + '%';
  }

  tarjetas.forEach(function (t) {
    var i = t.dataset.i;
    var ta = t.querySelector('textarea');
    var btn = t.querySelector('.listo');
    ta.value = leer('t' + i);
    if (leer('h' + i) === '1') t.classList.add('hecha');
    ta.addEventListener('input', function () { guardar('t' + i, ta.value); armar(); });
    btn.addEventListener('click', function () {
      var ya = t.classList.toggle('hecha');
      guardar('h' + i, ya ? '1' : '0');
      btn.textContent = ya ? 'Lista ✓' : 'Marcar lista';
      progreso();
    });
    if (t.classList.contains('hecha')) btn.textContent = 'Lista ✓';
  });

  function armar() {
    var lineas = ['DESCRIPCIONES BOLEM — lo que escribió Mónica', ''];
    tarjetas.forEach(function (t) {
      var v = t.querySelector('textarea').value.trim();
      if (!v) return;
      lineas.push(t.querySelector('.meta').textContent.trim().split('·')[0].trim()
        + ' — ' + t.querySelector('h2').childNodes[0].textContent.trim());
      lineas.push(v);
      lineas.push('');
    });
    var txt = lineas.join('\n').trim();
    salida.value = txt === 'DESCRIPCIONES BOLEM — lo que escribió Mónica' ? '' : txt;
    return salida.value;
  }

  document.getElementById('copiar').addEventListener('click', function () {
    var txt = armar();
    if (!txt) { estado.textContent = 'Todavía no has escrito nada (las notas de voz van por aparte).'; return; }
    function alterno() {
      salida.removeAttribute('readonly');
      salida.select(); salida.setSelectionRange(0, 999999);
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) {}
      salida.setAttribute('readonly', '');
      estado.textContent = ok ? 'Copiado. Pegalo en el chat.' : 'No se pudo copiar solo — seleccioná el texto y copialo a mano.';
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(txt).then(function () { estado.textContent = 'Copiado. Pegalo en el chat.'; }, alterno);
    } else { alterno(); }
  });

  progreso(); armar();
</script>
"""


if __name__ == '__main__':
    sys.exit(main())
