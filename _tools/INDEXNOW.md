# Avisos de cambios a buscadores

Después de una publicación exitosa en GitHub Pages, `indexnow.yml` compara las
páginas del sitemap con el último inventario aceptado, guardado en la caché de
GitHub Actions. Envía solo URLs nuevas, modificadas o retiradas. No envía previews
v3 ni páginas no incluidas en el sitemap. Si la caché vence, se reenvía el inventario.

`indexnow-key.txt` es el archivo público de prueba de dominio exigido por IndexNow.
No contiene credenciales de Google, GitHub ni Cloudflare. Debe permanecer publicado.

La primera ejecución notifica las 67 páginas. HTTP 200 significa recibido;
HTTP 202 significa recibido con verificación de clave pendiente. Ninguno confirma
indexación o posiciones. El protocolo beneficia a los buscadores participantes;
las solicitudes de Google siguen gestionándose en Search Console.

Para previsualizar sin enviar:

```powershell
python _tools/notificar_indexnow.py --state "$env:TEMP\bolem-indexnow-state.json"
```

Agregar `--submit` solo cuando el sitio haya terminado de publicarse.
Para operación habitual, revisar el resultado del workflow de GitHub Actions.
Una ejecución manual está disponible para recuperarse de fallos, después del despliegue.

Documentación: https://www.indexnow.org/documentation
