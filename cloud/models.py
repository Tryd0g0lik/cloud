# from django.core.cache.backends.base import BaseCache
#
#
# # from cachecontrol.cache. import BaseCache
#
#
# class NoHashCache(BaseCache):
#     def set(self, key, value, timeout=None, **kwargs):
#         # Сохраняем значение без хеширования
#         self._cache[key] = value
#
#     def get(self, key, default=None):
#         return self._cache.get(key, default)
#
#     def delete(self, key):
#         if key in self._cache:
#             del self._cache[key]
