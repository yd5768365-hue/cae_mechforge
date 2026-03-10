/**
 * CacheManager 单元测试
 */

describe('CacheManager', () => {
  beforeEach(() => {
    CacheManager.clear();
  });

  describe('基本操作', () => {
    it('should set and get value', () => {
      CacheManager.set('key', 'value');
      const result = CacheManager.get('key');
      expect(result).toBe('value');
    });

    it('should return default for missing key', () => {
      const result = CacheManager.get('missing', 'default');
      expect(result).toBe('default');
    });

    it('should check existence', () => {
      CacheManager.set('key', 'value');
      expect(CacheManager.has('key')).toBe(true);
      expect(CacheManager.has('missing')).toBe(false);
    });

    it('should remove value', () => {
      CacheManager.set('key', 'value');
      CacheManager.remove('key');
      expect(CacheManager.has('key')).toBe(false);
    });

    it('should clear all', () => {
      CacheManager.set('key1', 'value1');
      CacheManager.set('key2', 'value2');
      CacheManager.clear();
      expect(CacheManager.has('key1')).toBe(false);
      expect(CacheManager.has('key2')).toBe(false);
    });
  });

  describe('TTL 功能', () => {
    it('should expire after TTL', (done) => {
      CacheManager.set('key', 'value', 100);
      expect(CacheManager.has('key')).toBe(true);

      setTimeout(() => {
        expect(CacheManager.has('key')).toBe(false);
        done();
      }, 150);
    });

    it('should not expire before TTL', () => {
      CacheManager.set('key', 'value', 5000);
      expect(CacheManager.has('key')).toBe(true);
    });
  });

  describe('remember 功能', async () => {
    it('should cache factory result', async () => {
      let callCount = 0;
      const factory = () => {
        callCount++;
        return 'value';
      };

      const result1 = await CacheManager.remember('key', factory);
      const result2 = await CacheManager.remember('key', factory);

      expect(result1).toBe('value');
      expect(result2).toBe('value');
      expect(callCount).toBe(1);
    });
  });

  describe('统计', () => {
    it('should return stats', () => {
      CacheManager.set('key1', 'value1');
      CacheManager.set('key2', 'value2');

      const stats = CacheManager.getStats();
      expect(stats.memory).toBe(2);
    });
  });
});
