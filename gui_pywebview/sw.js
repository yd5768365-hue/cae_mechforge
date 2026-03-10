/**
 * @fileoverview Service Worker - 离线缓存和性能优化
 * @description 提供资源缓存、离线支持和性能优化
 * @version 1.0.0
 */

const CACHE_NAME = 'mechforge-ai-v1';
const STATIC_CACHE = 'mechforge-static-v1';
const DYNAMIC_CACHE = 'mechforge-dynamic-v1';
const IMAGE_CACHE = 'mechforge-images-v1';

// 需要预缓存的核心资源
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/styles.css',
  '/styles-modular.css',
  '/css/variables.css',
  '/css/layout.css',
  '/css/effects.css',
  '/core/utils.js',
  '/core/event-bus.js',
  '/core/api-client.js',
  '/core/error-handler.js',
  '/app/main.js',
  '/app/ui/particles.js',
  '/app/ui/mascot.js',
  '/dj-whale.png'
];

// 缓存策略配置
const CACHE_STRATEGIES = {
  // 静态资源 - Cache First
  static: {
    pattern: /\.(js|css|json)$/,
    maxAge: 30 * 24 * 60 * 60 * 1000, // 30天
    maxEntries: 100
  },
  // 图片资源 - Cache First
  images: {
    pattern: /\.(png|jpg|jpeg|gif|svg|webp|ico)$/,
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7天
    maxEntries: 50
  },
  // API 请求 - Network First
  api: {
    pattern: /\/api\//,
    maxAge: 5 * 60 * 1000, // 5分钟
    maxEntries: 50
  },
  // 字体 - Cache First
  fonts: {
    pattern: /\.(woff|woff2|ttf|otf|eot)$/,
    maxAge: 365 * 24 * 60 * 60 * 1000, // 1年
    maxEntries: 20
  }
};

// ==================== 安装阶段 ====================

self.addEventListener('install', (event) => {
  console.log('[SW] Installing...');

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Pre-caching assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => {
        console.log('[SW] Pre-cache complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Pre-cache failed:', error);
      })
  );
});

// ==================== 激活阶段 ====================

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...');

  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => {
              return name.startsWith('mechforge-') &&
                name !== STATIC_CACHE &&
                name !== DYNAMIC_CACHE &&
                name !== IMAGE_CACHE;
            })
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Activation complete');
        return self.clients.claim();
      })
  );
});

// ==================== 请求拦截 ====================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 跳过非 GET 请求
  if (request.method !== 'GET') {
    return;
  }

  // 跳过跨域请求
  if (url.origin !== self.location.origin) {
    return;
  }

  // 根据资源类型选择策略
  const strategy = getStrategy(request);

  switch (strategy) {
    case 'static':
      event.respondWith(cacheFirst(request, STATIC_CACHE));
      break;
    case 'image':
      event.respondWith(cacheFirst(request, IMAGE_CACHE));
      break;
    case 'api':
      event.respondWith(networkFirst(request, DYNAMIC_CACHE));
      break;
    case 'font':
      event.respondWith(cacheFirst(request, STATIC_CACHE));
      break;
    default:
      event.respondWith(networkFirst(request, DYNAMIC_CACHE));
  }
});

// ==================== 缓存策略 ====================

/**
 * 获取请求的策略类型
 * @param {Request} request - 请求对象
 * @returns {string} 策略类型
 */
function getStrategy(request) {
  const url = request.url;

  if (CACHE_STRATEGIES.images.pattern.test(url)) {
    return 'image';
  }
  if (CACHE_STRATEGIES.static.pattern.test(url)) {
    return 'static';
  }
  if (CACHE_STRATEGIES.api.pattern.test(url)) {
    return 'api';
  }
  if (CACHE_STRATEGIES.fonts.pattern.test(url)) {
    return 'font';
  }

  return 'default';
}

/**
 * Cache First 策略
 * 优先从缓存获取，失败时从网络获取
 * @param {Request} request - 请求对象
 * @param {string} cacheName - 缓存名称
 * @returns {Promise<Response>}
 */
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  if (cached) {
    // 检查缓存是否过期
    const dateHeader = cached.headers.get('sw-cache-date');
    if (dateHeader) {
      const age = Date.now() - parseInt(dateHeader, 10);
      const strategy = getStrategy(request);
      const maxAge = CACHE_STRATEGIES[strategy]?.maxAge || 24 * 60 * 60 * 1000;

      if (age < maxAge) {
        return cached;
      }
    } else {
      return cached;
    }
  }

  try {
    const response = await fetch(request);

    if (response.ok) {
      // 克隆响应并添加缓存时间戳
      const responseToCache = response.clone();
      const headers = new Headers(responseToCache.headers);
      headers.set('sw-cache-date', Date.now().toString());

      const modifiedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers
      });

      cache.put(request, modifiedResponse);

      // 清理旧缓存
      cleanCache(cacheName, CACHE_STRATEGIES[getStrategy(request)]?.maxEntries || 100);
    }

    return response;
  } catch (error) {
    console.error('[SW] Cache first failed:', error);

    // 如果有缓存，返回缓存（即使过期）
    if (cached) {
      return cached;
    }

    throw error;
  }
}

/**
 * Network First 策略
 * 优先从网络获取，失败时从缓存获取
 * @param {Request} request - 请求对象
 * @param {string} cacheName - 缓存名称
 * @returns {Promise<Response>}
 */
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);

    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);

    if (cached) {
      return cached;
    }

    throw error;
  }
}

/**
 * Stale While Revalidate 策略
 * 立即返回缓存，同时更新缓存
 * @param {Request} request - 请求对象
 * @param {string} cacheName - 缓存名称
 * @returns {Promise<Response>}
 */
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  // 后台更新缓存
  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch((error) => {
      console.error('[SW] Background fetch failed:', error);
    });

  // 返回缓存或等待网络
  return cached || fetchPromise;
}

// ==================== 缓存管理 ====================

/**
 * 清理缓存
 * @param {string} cacheName - 缓存名称
 * @param {number} maxEntries - 最大条目数
 */
async function cleanCache(cacheName, maxEntries) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();

  if (keys.length > maxEntries) {
    const toDelete = keys.slice(0, keys.length - maxEntries);
    await Promise.all(toDelete.map((key) => cache.delete(key)));
    console.log(`[SW] Cleaned ${toDelete.length} entries from ${cacheName}`);
  }
}

/**
 * 清理所有缓存
 */
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map((name) => caches.delete(name)));
  console.log('[SW] All caches cleared');
}

// ==================== 消息处理 ====================

self.addEventListener('message', (event) => {
  const { type, payload } = event.data;

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'CLEAR_CACHES':
      event.waitUntil(clearAllCaches());
      break;

    case 'GET_CACHE_STATUS':
      event.waitUntil(
        caches.keys().then((names) => {
          return Promise.all(
            names.map(async (name) => {
              const cache = await caches.open(name);
              const keys = await cache.keys();
              return { name, count: keys.length };
            })
          );
        }).then((status) => {
          event.ports[0].postMessage({ status });
        })
      );
      break;

    case 'PRECACHE':
      event.waitUntil(
        caches.open(STATIC_CACHE)
          .then((cache) => cache.addAll(payload.urls))
          .then(() => {
            event.ports[0].postMessage({ success: true });
          })
          .catch((error) => {
            event.ports[0].postMessage({ success: false, error: error.message });
          })
      );
      break;

    default:
      console.log('[SW] Unknown message type:', type);
  }
});

// ==================== 后台同步 ====================

self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  console.log('[SW] Background sync executed');
  // 实现后台同步逻辑
}

// ==================== 推送通知 ====================

self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};

  const options = {
    body: data.body || 'New notification',
    icon: '/dj-whale.png',
    badge: '/dj-whale.png',
    tag: data.tag || 'default',
    requireInteraction: data.requireInteraction || false,
    actions: data.actions || []
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'MechForge AI', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      if (clientList.length > 0) {
        return clientList[0].focus();
      }
      return clients.openWindow('/');
    })
  );
});

console.log('[SW] Service Worker loaded');
