/**
 * Validator 单元测试
 */

describe('Validator', () => {
  describe('必填验证', () => {
    it('should validate required', () => {
      expect(Validator.isRequired('test')).toBe(true);
      expect(Validator.isRequired('')).toBe(false);
      expect(Validator.isRequired(null)).toBe(false);
      expect(Validator.isRequired(undefined)).toBe(false);
    });

    it('should validate empty', () => {
      expect(Validator.isEmpty('')).toBe(true);
      expect(Validator.isEmpty('test')).toBe(false);
    });
  });

  describe('邮箱验证', () => {
    it('should validate email', () => {
      expect(Validator.isEmail('test@example.com')).toBe(true);
      expect(Validator.isEmail('invalid')).toBe(false);
      expect(Validator.isEmail('test@')).toBe(false);
    });
  });

  describe('URL 验证', () => {
    it('should validate URL', () => {
      expect(Validator.isUrl('https://example.com')).toBe(true);
      expect(Validator.isUrl('not-a-url')).toBe(false);
    });
  });

  describe('数字验证', () => {
    it('should validate numeric', () => {
      expect(Validator.isNumeric('123')).toBe(true);
      expect(Validator.isNumeric('abc')).toBe(false);
    });

    it('should validate integer', () => {
      expect(Validator.isInteger('123')).toBe(true);
      expect(Validator.isInteger('123.45')).toBe(false);
    });
  });

  describe('规则验证', () => {
    it('should validate with rules', () => {
      const result = Validator.validate('test', 'required');
      expect(result.valid).toBe(true);
    });

    it('should validate min length', () => {
      const result = Validator.validate('test', 'minLength', 3);
      expect(result.valid).toBe(true);

      const result2 = Validator.validate('te', 'minLength', 3);
      expect(result2.valid).toBe(false);
    });

    it('should validate max length', () => {
      const result = Validator.validate('test', 'maxLength', 10);
      expect(result.valid).toBe(true);
    });

    it('should validate range', () => {
      const result = Validator.validate(5, 'range', 1, 10);
      expect(result.valid).toBe(true);

      const result2 = Validator.validate(15, 'range', 1, 10);
      expect(result2.valid).toBe(false);
    });
  });

  describe('表单验证', () => {
    it('should validate form', () => {
      const data = {
        name: 'test',
        email: 'test@example.com'
      };

      const schema = {
        name: [{ rule: 'required' }],
        email: [{ rule: 'required' }, { rule: 'email' }]
      };

      const result = Validator.validateForm(data, schema);
      expect(result.valid).toBe(true);
    });

    it('should return errors for invalid form', () => {
      const data = {
        name: '',
        email: 'invalid'
      };

      const schema = {
        name: [{ rule: 'required' }],
        email: [{ rule: 'email' }]
      };

      const result = Validator.validateForm(data, schema);
      expect(result.valid).toBe(false);
      expect(result.errors).toBeDefined();
    });
  });
});
