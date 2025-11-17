const CACHE_NAME = 'haven-ui-cache-v1';
const ASSETS_TO_CACHE = [
  '/haven-ui/index.html',
  '/haven-ui/assets/style.css',
  '/haven-ui/spa.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.origin === location.origin) {
    e.respondWith(
      caches.match(e.request).then((cached) => cached || fetch(e.request))
    );
  }
});
