/* WILLIE PWA service worker (minimal offline cache) */
const CACHE = "willi-v11";

const CORE = [
  "./",
  "./index.html",
  "./app.html",
  "./manifest.webmanifest"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((c) => c.addAll(CORE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
    ])
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  // Network-first for HTML (so updates arrive), cache fallback.
  const isHtml =
    req.headers.get("accept")?.includes("text/html") ||
    new URL(req.url).pathname.endsWith(".html");

  if (isHtml) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() =>
          caches.match(req).then(
            (r) =>
              r ||
              caches.match("./").then(
                (root) => root || caches.match("./index.html").then((i) => i || caches.match("./app.html"))
              )
          )
        )
    );
    return;
  }

  /* firebase-config.json: vždy sieť — nikdy neservovať starý cache (zlý kľúč by ostal navždy). */
  const path = new URL(req.url).pathname;
  if (path.endsWith("/firebase-config.json")) {
    event.respondWith(fetch(req));
    return;
  }

  // Cache-first for same-origin static assets; network fallback.
  const url = new URL(req.url);
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req).then((hit) => {
        if (hit) return hit;
        return fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        });
      })
    );
  }
});
