/**
 * Utils 单元测试
 */

describe('Utils', () => {
  describe('DOM 选择器', () => {
    it('should select element by ID', () => {
      const el = document.createElement('div');
      el.id = 'test-el';
      document.body.appendChild(el);

      const result = Utils.$('test-el');
      expect(result).toBe(el);

      document.body.removeChild(el);
    });


    it('should return null for non-existent element', () => {
      const result = Utils.$('non-existent');
      expect(result).toBeNull();
    });

    it('should select multiple elements', () => {
      const div1 = document.createElement('div');
      const div2 = document.createElement('div');
      div1.className = 'test-class';
      div2.className = 'test-class';
      document.body.appendChild(div1);
      document.body.appendChild(div2);

      const results = Utils.$$('test-class');
      expect(results).toHaveLength(2);

      document.body.removeChild(div1);
      document.body.removeChild(div2);
    });
  });

  describe('字符串工具', () => {
    it('should escape HTML', () => {
      const input = '<script>alert("xss")</script>';
      const result = Utils.escapeHtml(input);
      expect(result).not.toContain('<');
      expect(result).not.toContain('>');
    });

    it('should truncate text', () => {
      const text = 'This is a long text';
      const result = Utils.truncate(text, 10);
      expect(result).toContain('...');
    });


    it('should format timestamp', () => {
      const timestamp = Utils.getTimestamp();
      expect(timestamp).toMatch(/^\d{2}:\d{2}$/);
    });

    it('should generate random numbers', () => {
      const num = Utils.random(1, 10);
      expect(num).toBeGreaterThanOrEqual(1);
      expect(num).toBeLessThanOrEqual(10);
    });

    it('should generate random integers', () => {
      const num = Utils.randomInt(1, 10);
      expect(num).toBeGreaterThanOrEqual(1);
      expect(num).toBeLessThanOrEqual(10);
    });
  });

  describe('DOM 操作', () => {
    it('should create elements', () => {
      const el = Utils.create('div', { className: 'test' });
      expect(el).toBeDefined();
      expect(el.className).toBe('test';
      expect(el).toBeTruthy();
      expect(el).toBeTruthy();
      expect(el).toBeTruthy();
    });

    it('should handle missing elements', () => {
      expect(Utils.$('missing')).toBeNull();
    });
  });

  describe('事件处理', () => {
    it('should handle events', () => {
      expect(Utils.debounce).toBeDefined();
      expect(Utils.throttle).toBeDefined();
    });
  });
});
