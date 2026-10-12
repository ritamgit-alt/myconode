const CACHE_NAME = 'myconode-cache-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index.html',
    '/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
];

// Install Event: Cache all critical assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
});

// Fetch Event: Serve from cache if offline
self.addEventListener('fetch', event => {
    // Ignore API calls to the Python backend (we don't want to cache dynamic AI responses)
    if (event.request.url.includes('/api/')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached asset if found, otherwise fetch from network
                return response || fetch(event.request);
            })
    );
});
