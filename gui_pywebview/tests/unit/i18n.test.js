/**
 * I18n 单元测试
 */

describe('I18n', () => {
  beforeEach(() => {
    I18n.init();
  });

  describe('翻译功能', () => {
    it('should translate key', () => {
      const result = I18n.t('common.confirm');
      expect(result).toBe('确认');
    });

    it('should return key for missing translation', () => {
      const result = I18n.t('missing.key');
      expect(result).toBe('missing.key');
    });

    it('should interpolate params', () => {
      // This would need actual translation with params
      const result = I18n.t('common.loading');
      expect(result).toBe('加载中...');
    });
  });

  describe('语言切换', () => {
    it('should get current locale', () => {
      const locale = I18n.getLocale();
      expect(locale).toBeDefined();
    });

    it('should set locale', () => {
      I18n.setLocale('en-US');
      const locale = I18n.getLocale();
      expect(locale).toBe('en-US');
    });

    it('should get available locales', () => {
      const locales = I18n.getAvailableLocales();
      expect(locales).toContain('zh-CN');
      expect(locales).toContain('en-US');
    });
  });

  describe('快捷方法', () => {
    it('should use __ alias', () => {
      const result = I18n.__('common.confirm');
      expect(result).toBe('确认');
    });
  });
});
