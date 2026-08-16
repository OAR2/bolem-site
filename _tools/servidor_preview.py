# -*- coding: utf-8 -*-
"""Servidor local para ver el sitio BOLEM como lo servira el host real.

Por que existe: el sitio enlaza rutas SIN extension (`nosotros`,
`guia-de-tallas`, `coleccion/`). Eso es correcto y deliberado — asi las sirven
Cloudflare Pages y GitHub Pages, y asi quedaron los canonicals del SEO. Pero al
abrir el HTML directo desde el disco no hay nadie que resuelva esas rutas: el
navegador muestra el indice de la carpeta y la pagina "parece rota".

Este servidor imita al host real: para /nosotros prueba nosotros.html, y para
/coleccion/ prueba coleccion/index.html. Con eso el preview se navega completo.

Uso:  doble clic en _tools/ver-preview.cmd
      (o desde la raiz del repo:  python _tools/servidor_preview.py)
"""
import http.server
import os
import socketserver
import sys
import threading
import webbrowser

PUERTO = 8777
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=RAIZ, **kw)

    def translate_path(self, path):
        destino = super().translate_path(path)
        if os.path.isdir(destino):
            indice = os.path.join(destino, "index.html")
            if os.path.exists(indice):
                return indice
        if not os.path.exists(destino):
            con_html = destino + ".html"
            if os.path.exists(con_html):
                return con_html
        return destino

    def log_message(self, formato, *args):
        # sin ruido: solo interesan los 404
        if args and str(args[1]).startswith("4"):
            sys.stderr.write("  404  %s\n" % args[0])


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PUERTO), Handler) as srv:
        url = "http://127.0.0.1:%d/" % PUERTO
        print("BOLEM — preview navegable")
        print("  " + url)
        print("  (la coleccion real:  http://127.0.0.1:%d/coleccion/ )" % PUERTO)
        print("\nDejar esta ventana abierta. Ctrl+C para cerrar.\n")
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nservidor cerrado")


if __name__ == "__main__":
    main()
