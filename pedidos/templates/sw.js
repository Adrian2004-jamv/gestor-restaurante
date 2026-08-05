// Service worker del Gestor de Pedidos y Catering.
// Se sirve desde la raiz (/sw.js) para poder controlar todo el sitio.
// Al cambiar los archivos de ESENCIALES, sube el numero de VERSION.

const VERSION = "gestor-v1";
const PAGINA_SIN_CONEXION = "/sin-conexion/";

const ESENCIALES = [
  PAGINA_SIN_CONEXION,
  "/static/css/bootstrap.min.css",
  "/static/css/style.css",
  "/static/css/all.min.css",
  "/static/js/jquery-3.7.1.min.js",
  "/static/js/bootstrap.bundle.min.js",
  "/static/js/main.js",
  "/static/img/icons/icon-192.png"
];

self.addEventListener("install", function (evento) {
  evento.waitUntil(
    caches.open(VERSION).then(function (cache) {
      // addAll falla entero si un archivo da 404, por eso se cachea uno a uno
      return Promise.all(
        ESENCIALES.map(function (ruta) {
          return cache.add(ruta).catch(function () {
            console.warn("No se pudo cachear:", ruta);
          });
        })
      );
    })
  );

  self.skipWaiting();
});

self.addEventListener("activate", function (evento) {
  evento.waitUntil(
    caches.keys().then(function (claves) {
      return Promise.all(
        claves
          .filter(function (clave) {
            return clave !== VERSION;
          })
          .map(function (clave) {
            return caches.delete(clave);
          })
      );
    })
  );

  self.clients.claim();
});

self.addEventListener("fetch", function (evento) {
  const peticion = evento.request;
  const url = new URL(peticion.url);

  // Solo GET del propio sitio
  if (peticion.method !== "GET") return;
  if (url.origin !== self.location.origin) return;

  // El admin y las imagenes subidas siempre van a la red
  if (url.pathname.startsWith("/admin/")) return;
  if (url.pathname.startsWith("/media/")) return;

  // Estaticos: primero el cache, que es lo que hace rapida la app
  if (url.pathname.startsWith("/static/")) {
    evento.respondWith(
      caches.match(peticion).then(function (guardado) {
        return (
          guardado ||
          fetch(peticion).then(function (respuesta) {
            const copia = respuesta.clone();
            caches.open(VERSION).then(function (cache) {
              cache.put(peticion, copia);
            });
            return respuesta;
          })
        );
      })
    );
    return;
  }

  // Paginas: primero la red para no mostrar datos viejos
  evento.respondWith(
    fetch(peticion)
      .then(function (respuesta) {
        const copia = respuesta.clone();
        caches.open(VERSION).then(function (cache) {
          cache.put(peticion, copia);
        });
        return respuesta;
      })
      .catch(function () {
        return caches.match(peticion).then(function (guardado) {
          return guardado || caches.match(PAGINA_SIN_CONEXION);
        });
      })
  );
});
