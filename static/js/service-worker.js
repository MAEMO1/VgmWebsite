// Service Worker for VGM Website
const CACHE_NAME = 'vgm-cache-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/css/style.css',
    '/static/images/LogoVGM.jpg',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
];

// Install Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
});

// Activate Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event handling with network-first strategy
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone the response as it can only be consumed once
                const responseToCache = response.clone();

                caches.open(CACHE_NAME)
                    .then((cache) => {
                        // Cache successful responses
                        if (event.request.method === 'GET') {
                            cache.put(event.request, responseToCache);
                        }
                    });

                return response;
            })
            .catch(() => {
                // If network request fails, try to get it from cache
                return caches.match(event.request);
            })
    );
});

// Handle push notifications
self.addEventListener('push', (event) => {
    const options = {
        body: event.data.text(),
        icon: '/static/images/LogoVGM.jpg',
        badge: '/static/images/LogoVGM.jpg',
        vibrate: [100, 50, 100],
    };

    event.waitUntil(
        self.registration.showNotification('VGM Notification', options)
    );
});
