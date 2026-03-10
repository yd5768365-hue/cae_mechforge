/**
 * TestFramework - 轻量级测试框架
 * 提供类似 Jest 的测试 API
 */

(function () {
  'use strict';

  // ==================== 状态 ====================
  const suites = [];
  let currentSuite = null;
  let currentTest = null;
  let beforeEachFn = null;
  let afterEachFn = null;

  // ==================== 测试定义 ====================

  /**
   * 定义测试套件
   * @param {string} name - 套件名称
   * @param {Function} fn - 套件函数
   */
  function describe(name, fn) {
    const suite = {
      name,
      tests: [],
      beforeEach: null,
      afterEach: null
    };

    const prevSuite = currentSuite;
    currentSuite = suite;
    fn();
    currentSuite = prevSuite;

    suites.push(suite);
  }

  /**
   * 定义测试用例
   * @param {string} name - 测试名称
   * @param {Function} fn - 测试函数
   */
  function it(name, fn) {
    if (!currentSuite) {
      throw new Error('it() must be called inside describe()');
    }

    currentSuite.tests.push({
      name,
      fn,
      async: fn.constructor.name === 'AsyncFunction'
    });
  }

  /**
   * 跳过测试
   * @param {string} name - 测试名称
   * @param {Function} fn - 测试函数
   */
  function xit(name, fn) {
    if (!currentSuite) return;
    currentSuite.tests.push({
      name,
      fn,
      skipped: true
    });
  }

  /**
   * 每个测试前执行
   * @param {Function} fn - 函数
   */
  function beforeEach(fn) {
    if (currentSuite) {
      currentSuite.beforeEach = fn;
    }
  }

  /**
   * 每个测试后执行
   * @param {Function} fn - 函数
   */
  function afterEach(fn) {
    if (currentSuite) {
      currentSuite.afterEach = fn;
    }
  }

  // ==================== 断言 ====================

  class Expectation {
    constructor(actual) {
      this.actual = actual;
      this.negated = false;
    }

    get not() {
      this.negated = !this.negated;
      return this;
    }

    toBe(expected) {
      const pass = this.actual === expected;
      this._assert(pass, `expected ${format(this.actual)} to be ${format(expected)}`);
    }

    toEqual(expected) {
      const pass = deepEqual(this.actual, expected);
      this._assert(pass, `expected ${format(this.actual)} to equal ${format(expected)}`);
    }

    toBeNull() {
      const pass = this.actual === null;
      this._assert(pass, `expected ${format(this.actual)} to be null`);
    }

    toBeUndefined() {
      const pass = this.actual === undefined;
      this._assert(pass, `expected ${format(this.actual)} to be undefined`);
    }

    toBeDefined() {
      const pass = this.actual !== undefined;
      this._assert(pass, `expected ${format(this.actual)} to be defined`);
    }

    toBeTruthy() {
      const pass = !!this.actual;
      this._assert(pass, `expected ${format(this.actual)} to be truthy`);
    }

    toBeFalsy() {
      const pass = !this.actual;
      this._assert(pass, `expected ${format(this.actual)} to be falsy`);
    }

    toBeTrue() {
      const pass = this.actual === true;
      this._assert(pass, `expected ${format(this.actual)} to be true`);
    }

    toBeFalse() {
      const pass = this.actual === false;
      this._assert(pass, `expected ${format(this.actual)} to be false`);
    }

    toBeGreaterThan(expected) {
      const pass = this.actual > expected;
      this._assert(pass, `expected ${format(this.actual)} to be greater than ${format(expected)}`);
    }

    toBeGreaterThanOrEqual(expected) {
      const pass = this.actual >= expected;
      this._assert(pass, `expected ${format(this.actual)} to be greater than or equal ${format(expected)}`);
    }

    toBeLessThan(expected) {
      const pass = this.actual < expected;
      this._assert(pass, `expected ${format(this.actual)} to be less than ${format(expected)}`);
    }

    toBeLessThanOrEqual(expected) {
      const pass = this.actual <= expected;
      this._assert(pass, `expected ${format(this.actual)} to be less than or equal ${format(expected)}`);
    }

    toBeCloseTo(expected, precision = 2) {
      const pass = Math.abs(this.actual - expected) < Math.pow(10, -precision);
      this._assert(pass, `expected ${format(this.actual)} to be close to ${format(expected)}`);
    }

    toContain(expected) {
      const pass = this.actual && this.actual.includes && this.actual.includes(expected);
      this._assert(pass, `expected ${format(this.actual)} to contain ${format(expected)}`);
    }

    toHaveLength(expected) {
      const pass = this.actual && this.actual.length === expected;
      this._assert(pass, `expected ${format(this.actual)} to have length ${format(expected)}`);
    }

    toHaveProperty(key, value) {
      const hasKey = this.actual && Object.prototype.hasOwnProperty.call(this.actual, key);
      if (value !== undefined) {
        const pass = hasKey && deepEqual(this.actual[key], value);
        this._assert(pass, `expected ${format(this.actual)} to have property ${format(key)} with value ${format(value)}`);
      } else {
        this._assert(hasKey, `expected ${format(this.actual)} to have property ${format(key)}`);
      }
    }

    toBeInstanceOf(expected) {
      const pass = this.actual instanceof expected;
      this._assert(pass, `expected ${format(this.actual)} to be instance of ${expected.name}`);
    }

    toThrow(expected) {
      let threw = false;
      let thrown = null;
      try {
        this.actual();
      } catch (e) {
        threw = true;
        thrown = e;
      }

      if (expected) {
        const pass = threw && thrown.message.includes(expected);
        this._assert(pass, `expected function to throw error containing "${expected}"`);
      } else {
        this._assert(threw, `expected function to throw`);
      }
    }

    toMatch(expected) {
      const pass = expected.test(this.actual);
      this._assert(pass, `expected ${format(this.actual)} to match ${expected}`);
    }

    toMatchObject(expected) {
      const pass = Object.keys(expected).every(key =>
        deepEqual(this.actual[key], expected[key])
      );
      this._assert(pass, `expected ${format(this.actual)} to match object ${format(expected)}`);
    }

    _assert(pass, message) {
      const finalPass = this.negated ? !pass : pass;
      if (!finalPass) {
        throw new AssertionError(this.negated ? `not ${message}` : message);
      }
    }
  }

  class AssertionError extends Error {
    constructor(message) {
      super(message);
      this.name = 'AssertionError';
    }
  }

  function expect(actual) {
    return new Expectation(actual);
  }

  // ==================== 工具函数 ====================

  function deepEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (typeof a !== typeof b) return false;

    if (typeof a === 'object') {
      const keysA = Object.keys(a);
      const keysB = Object.keys(b);
      if (keysA.length !== keysB.length) return false;

      for (const key of keysA) {
        if (!keysB.includes(key)) return false;
        if (!deepEqual(a[key], b[key])) return false;
      }
      return true;
    }

    return false;
  }

  function format(value) {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';
    if (typeof value === 'string') return `"${value}"`;
    if (typeof value === 'function') return '[Function]';
    if (Array.isArray(value)) return `[${value.map(format).join(', ')}]`;
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  // ==================== 运行测试 ====================

  async function runTest(suite, test) {
    try {
      // beforeEach
      if (suite.beforeEach) {
        await suite.beforeEach();
      }

      // Run test
      await test.fn();

      // afterEach
      if (suite.afterEach) {
        await suite.afterEach();
      }

      return { passed: true };
    } catch (error) {
      return {
        passed: false,
        error: error.message
      };
    }
  }

  async function runSuite(suite) {
    const results = {
      name: suite.name,
      tests: []
    };

    for (const test of suite.tests) {
      if (test.skipped) {
        results.tests.push({
          name: test.name,
          passed: true,
          skipped: true
        });
        continue;
      }

      // Emit event
      window.dispatchEvent(new CustomEvent('test-start', {
        detail: { suite: suite.name, test: test.name }
      }));

      const result = await runTest(suite, test);
      results.tests.push({
        name: test.name,
        passed: result.passed,
        error: result.error
      });

      // Emit event
      if (result.passed) {
        window.dispatchEvent(new CustomEvent('test-pass', {
          detail: { suite: suite.name, test: test.name }
        }));
      } else {
        window.dispatchEvent(new CustomEvent('test-fail', {
          detail: { suite: suite.name, test: test.name, error: result.error }
        }));
      }
    }

    // Emit suite complete
    window.dispatchEvent(new CustomEvent('suite-complete', {
      detail: results
    }));

    return results;
  }

  async function runAll() {
    for (const suite of suites) {
      await runSuite(suite);
    }
  }

  // ==================== 导出 ====================
  window.TestFramework = {
    describe,
    it,
    xit,
    beforeEach,
    afterEach,
    expect,
    runAll,
    runSuite,
    suites
  };

  // 简写导出
  window.describe = describe;
  window.it = it;
  window.xit = xit;
  window.beforeEach = beforeEach;
  window.afterEach = afterEach;
  window.expect = expect;

})();
