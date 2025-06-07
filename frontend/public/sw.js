// Service Worker for DrFirst Business Case Generator
// Version: 1.0
const CACHE_NAME = 'drfirst-business-case-v1';
const STATIC_CACHE_NAME = 'drfirst-static-v1';
const DYNAMIC_CACHE_NAME = 'drfirst-dynamic-v1';

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  // Add your static assets here
];

// API endpoints to cache with network-first strategy
const API_CACHE_PATTERNS = [
  /^https:\/\/drfirst-backend-.*\.run\.app\/api\//,
  /^https:\/\/.*\.googleapis\.com\//,
  /^https:\/\/.*\.firebaseapp\.com\//
];

// Assets that should be cached with cache-first strategy
const CACHE_FIRST_PATTERNS = [
  /\.(?:png|jpg|jpeg|svg|gif|webp|ico)$/,
  /\.(?:woff|woff2|eot|ttf|otf)$/,
  /\.(?:css|js)$/
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME && 
                cacheName !== CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http requests
  if (!request.url.startsWith('http')) {
    return;
  }

  event.respondWith(
    handleRequest(request)
  );
});

async function handleRequest(request) {
  const url = new URL(request.url);

  try {
    // Strategy 1: Cache-first for static assets (CSS, JS, images, fonts)
    if (CACHE_FIRST_PATTERNS.some(pattern => pattern.test(url.pathname))) {
      return await cacheFirst(request);
    }

    // Strategy 2: Network-first for API calls
    if (API_CACHE_PATTERNS.some(pattern => pattern.test(request.url))) {
      return await networkFirst(request);
    }

    // Strategy 3: Stale-while-revalidate for HTML pages
    if (request.destination === 'document' || url.pathname.endsWith('.html')) {
      return await staleWhileRevalidate(request);
    }

    // Strategy 4: Network-only for everything else
    return await fetch(request);

  } catch (error) {
    console.error('[SW] Request failed:', error);
    
    // Return offline fallback if available
    if (request.destination === 'document') {
      const cache = await caches.open(STATIC_CACHE_NAME);
      return await cache.match('/') || await cache.match('/index.html');
    }
    
    throw error;
  }
}

// Cache-first strategy: Try cache first, fallback to network
async function cacheFirst(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  const cached = await cache.match(request);
  
  if (cached) {
    console.log('[SW] Cache hit:', request.url);
    return cached;
  }
  
  console.log('[SW] Cache miss, fetching:', request.url);
  const response = await fetch(request);
  
  // Cache successful responses
  if (response.ok) {
    cache.put(request, response.clone());
  }
  
  return response;
}

// Network-first strategy: Try network first, fallback to cache
async function networkFirst(request) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  
  try {
    console.log('[SW] Network first:', request.url);
    const response = await fetch(request, {
      // Add timeout for faster fallback
      signal: AbortSignal.timeout(5000)
    });
    
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    const cached = await cache.match(request);
    
    if (cached) {
      return cached;
    }
    
    throw error;
  }
}

// Stale-while-revalidate strategy: Return cached version immediately, update in background
async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  const cached = await cache.match(request);
  
  // Fetch in background
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch((error) => {
    console.warn('[SW] Background fetch failed:', error);
  });
  
  // Return cached version immediately if available
  if (cached) {
    console.log('[SW] Stale while revalidate - cache hit:', request.url);
    return cached;
  }
  
  // If not cached, wait for network
  console.log('[SW] Stale while revalidate - cache miss:', request.url);
  return await fetchPromise;
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Implement background sync logic here
  console.log('[SW] Performing background sync...');
}

// Push notifications (if needed)
self.addEventListener('push', (event) => {
  console.log('[SW] Push received:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'New update available',
    icon: '/icon-192.png',
    badge: '/badge-72.png',
    tag: 'drfirst-notification',
    renotify: true
  };
  
  event.waitUntil(
    self.registration.showNotification('DrFirst Business Case Generator', options)
  );
});

// Cache cleanup - run periodically
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CACHE_CLEANUP') {
    event.waitUntil(cleanupCaches());
  }
});

async function cleanupCaches() {
  console.log('[SW] Cleaning up caches...');
  
  const cache = await caches.open(DYNAMIC_CACHE_NAME);
  const requests = await cache.keys();
  
  // Remove old entries (older than 7 days)
  const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
  
  for (const request of requests) {
    const response = await cache.match(request);
    const dateHeader = response.headers.get('date');
    
    if (dateHeader) {
      const responseDate = new Date(dateHeader).getTime();
      if (responseDate < oneWeekAgo) {
        console.log('[SW] Removing old cache entry:', request.url);
        await cache.delete(request);
      }
    }
  }
}

console.log('[SW] Service worker loaded successfully'); 