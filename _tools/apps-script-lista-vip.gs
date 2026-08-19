/**
 * BOLEM — receptor de la Lista VIP
 * ================================
 *
 * QUE PROBLEMA RESUELVE
 * El formulario de la coleccion pedia nombre y WhatsApp, decia "Listo, te
 * escribimos" y TIRABA los datos: solo abria un chat con el mensaje prellenado.
 * Si la clienta no presionaba enviar en WhatsApp, se iba y nadie se enteraba de
 * que estuvo ahi. Un formulario que aparenta capturar y no captura es peor que
 * no tenerlo.
 *
 * Ahora los datos caen en la pestana CLIENTAS de la Hoja Madre, y ADEMAS se
 * abre WhatsApp como siempre. Las dos cosas, no una en lugar de la otra.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * COMO SE INSTALA (5 minutos, lo hace OAR una sola vez)
 *
 *  1. Abrir la Hoja Madre:
 *     https://docs.google.com/spreadsheets/d/1-fow67oGgzEw4OM2Pq_gu2sus-gl_kTHCfuZYobwWgQ
 *  2. Menu  Extensiones -> Apps Script
 *  3. Borrar lo que haya y pegar TODO este archivo. Guardar.
 *  4. Cambiar SECRETO por una palabra cualquiera (la misma que va en el sitio).
 *  5. Boton  Implementar -> Nueva implementacion
 *       Tipo:                 Aplicacion web
 *       Ejecutar como:        Yo
 *       Quien tiene acceso:   CUALQUIER PERSONA        <-- importante
 *  6. Copiar la URL que termina en /exec
 *  7. Pegarla en coleccion/index.html, en la constante VIP_ENDPOINT,
 *     junto con el mismo secreto. Volver a subir el sitio.
 *
 * Mientras VIP_ENDPOINT este vacio, el sitio se comporta exactamente como hoy:
 * abre WhatsApp y no falla. O sea que esto se puede subir sin haberlo instalado.
 * ─────────────────────────────────────────────────────────────────────────────
 */

var HOJA = 'CLIENTAS';
var SECRETO = 'CAMBIAR-ESTO';   // la misma palabra tiene que ir en el sitio


function doPost(e) {
  try {
    var datos = JSON.parse(e.postData.contents);

    if (datos.secreto !== SECRETO) {
      return responder({ ok: false, error: 'secreto' });
    }

    var nombre = String(datos.nombre || '').trim();
    var tel = String(datos.whatsapp || '').replace(/\D/g, '');
    if (tel.length === 11 && tel.indexOf('503') === 0) tel = tel.slice(3);
    if (nombre.length < 2 || tel.length !== 8) {
      return responder({ ok: false, error: 'datos' });
    }

    var ws = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(HOJA);
    if (!ws) return responder({ ok: false, error: 'no existe la pestana ' + HOJA });

    // Una clienta que se apunta dos veces no es dos clientas. Se busca por
    // WhatsApp, que es el identificador de verdad — el nombre lo escribe ella y
    // puede venir distinto cada vez (regla de identidad de OAR).
    var filas = ws.getDataRange().getValues();
    var colTel = 2;   // C = whatsapp
    for (var i = 1; i < filas.length; i++) {
      var existente = String(filas[i][colTel]).replace(/\D/g, '').slice(-8);
      if (existente && existente === tel) {
        // Ya estaba: se anota que volvio, no se duplica la fila.
        var notas = String(filas[i][10] || '');
        ws.getRange(i + 1, 11).setValue(
          (notas ? notas + ' | ' : '') + 'volvio a apuntarse ' + hoy());
        return responder({ ok: true, estado: 'ya-estaba', fila: i + 1 });
      }
    }

    var id = 'CLI-' + Utilities.formatDate(new Date(), 'America/El_Salvador', 'yyMMdd-HHmmss');
    ws.appendRow([
      id,                       // id_clienta
      nombre,                   // nombre
      "'+503 " + tel,           // whatsapp (apostrofe para que no lo lea como numero)
      '',                       // ciudad
      '',                       // talla_habitual
      '',                       // primera_compra
      '',                       // ultima_compra
      '',                       // compras_total
      '',                       // gastado_total
      'sitio web - lista VIP',  // origen
      'se apunto ' + hoy() + (datos.pagina ? ' desde ' + datos.pagina : '')
    ]);
    return responder({ ok: true, estado: 'nueva', id: id });

  } catch (err) {
    return responder({ ok: false, error: String(err) });
  }
}


function doGet() {
  // Sirve para probar desde el navegador que la implementacion respondio.
  return responder({ ok: true, vivo: true, hoja: HOJA });
}


function hoy() {
  return Utilities.formatDate(new Date(), 'America/El_Salvador', 'yyyy-MM-dd HH:mm');
}


function responder(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
