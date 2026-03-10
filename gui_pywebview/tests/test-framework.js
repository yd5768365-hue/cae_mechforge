/**
 * @fileoverview TestFramework - 轻量级测试框架
 * @description 无需外部依赖的单元测试框架
 * @module TestFramework
 * @version 1.0.0
 */

(function () {
  'use strict';

  // ==================== 状态 ====================
  const state = {
    currentSuite: null,
    tests: [],
    passed: 0,
    failed: 0,
    skipped: 0,
    errors: []
  };

  // ==================== 断言库 ====================

  class AssertionError extends Error {
    constructor(message, actual, expected) {
      super(message);
      this.name = 'AssertionError';
      this.actual = actual;
      this.expected = expected;
    }
  }

  const Expect = {
    toBe(actual) {
      return {
        _value: actual,

        toBe(expected) {
          if (this._value !== expected) {
            throw new AssertionError(
              `Expected ${JSON.stringify(expected)} but got ${JSON.stringify(this._value)}`,
              this._value,
              expected
            );
          }
        },

        toEqual(expected) {
          if (!deepEqual(this._value, expected)) {
            throw new AssertionError(
              `Expected ${JSON.stringify(expected)} but got ${JSON.stringify(this._value)}`,
              this._value,
              expected
            );
          }
        },

        toBeNull() {
          if (this._value !== null) {
            throw new AssertionError(
              `Expected null but got ${JSON.stringify(this._value)}`,
              this._value,
              null
            );
          }
        },

        toBeUndefined() {
          if (this._value !== undefined) {
            throw new AssertionError(
              `Expected undefined but got ${JSON.stringify(this._value)}`,
              this._value,
              undefined
            );
          }
        },

        toBeTruthy() {
          if (!this._value) {
            throw new AssertionError(
              `Expected truthy value but got ${JSON.stringify(this._value)}`,
              this._value,
              true
            );
          }
        },

        toBeFalsy() {
          if (this._value) {
            throw new AssertionError(
              `Expected falsy value but got ${JSON.stringify(this._value)}`,
              this._value,
              false
            );
          }
        },

        toBeGreaterThan(expected) {
          if (!(this._value > expected)) {
            throw new AssertionError(
              `Expected ${this._value} to be greater than ${expected}`,
              this._value,
              expected
            );
          }
        },

        toBeGreaterThanOrEqual(expected) {
          if (!(this._value >= expected)) {
            throw new AssertionError(
              `Expected ${this._value} to be greater than or equal to ${expected}`,
              this._value,
              expected
            );
          }
        },

        toBeLessThan(expected) {
          if (!(this._value < expected)) {
            throw new AssertionError(
              `Expected ${this._value} to be less than ${expected}`,
              this._value,
              expected
            );
          }
        },

        toBeLessThanOrEqual(expected) {
          if (!(this._value <= expected)) {
            throw new AssertionError(
              `Expected ${this._value} to be less than or equal to ${expected}`,
              this._value,
              expected
            );
          }
        },

        toContain(expected) {
          if (!this._value.includes(expected)) {
            throw new AssertionError(
              `Expected ${JSON.stringify(this._value)} to contain ${JSON.stringify(expected)}`,
              this._value,
              expected
            );
          }
        },

        toMatch(pattern) {
          if (!pattern.test(this._value)) {
            throw new AssertionError(
              `Expected ${JSON.stringify(this._value)} to match ${pattern}`,
              this._value,
              pattern
            );
          }
        },

        toThrow(expectedMessage) {
          if (typeof this._value !== 'function') {
            throw new AssertionError(
              `Expected function but got ${typeof this._value}`,
              this._value,
              'function'
            );
          }

          let threw = false;
          let thrownError = null;

          try {
            this._value();
          } catch (error) {
            threw = true;
            thrownError = error;
          }

          if (!threw) {
            throw new AssertionError(
              'Expected function to throw but it did not',
              null,
              expectedMessage
            );
          }

          if (expectedMessage && !thrownError.message.includes(expectedMessage)) {
            throw new AssertionError(
              `Expected error message to contain "${expectedMessage}" but got "${thrownError.message}"`,
              thrownError.message,
              expectedMessage
            );
          }
        },

        toBeInstanceOf(expectedClass) {
          if (!(this._value instanceof expectedClass)) {
            throw new AssertionError(
              `Expected instance of ${expectedClass.name} but got ${this._value?.constructor?.name}`,
              this._value,
              expectedClass
            );
          }
        },

        toHaveLength(expected) {
          if (this._value.length !== expected) {
            throw new AssertionError(
              `Expected length ${expected} but got ${this._value.length}`,
              this._value.length,
              expected
            );
          }
        },

        toBeDefined() {
          if (this._value === undefined) {
            throw new AssertionError(
              'Expected value to be defined but got undefined',
              undefined,
              'defined'
            );
          }
        },

        toBeNaN() {
          if (!Number.isNaN(this._value)) {
            throw new AssertionError(
              `Expected NaN but got ${this._value}`,
              this._value,
              NaN
            );
          }
        },

        not: {
          _value: actual,

          toBe(expected) {
            if (this._value === expected) {
              throw new AssertionError(
                `Expected not to be ${JSON.stringify(expected)}`,
                this._value,
                expected
              );
            }
          },

          toEqual(expected) {
            if (deepEqual(this._value, expected)) {
              throw new AssertionError(
                `Expected not to equal ${JSON.stringify(expected)}`,
                this._value,
                expected
              );
            }
          },

          toContain(expected) {
            if (this._value.includes(expected)) {
              throw new AssertionError(
                `Expected not to contain ${JSON.stringify(expected)}`,
                this._value,
                expected
              );
            }
          },

          toMatch(pattern) {
            if (pattern.test(this._value)) {
              throw new AssertionError(
                `Expected not to match ${pattern}`,
                this._value,
                pattern
              );
            }
          }
        }
      };
    }
  };

  // ==================== 深度比较 ====================

  function deepEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (typeof a !== typeof b) return false;

    if (typeof a === 'object') {
      if (Array.isArray(a) !== Array.isArray(b)) return false;

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

  // ==================== 测试定义 ====================

  function describe(name, fn) {
    const parentSuite = state.currentSuite;
    const suite = {
      name: parentSuite ? `${parentSuite.name} > ${name}` : name,
      tests: [],
      beforeEach: [],
      afterEach: []
    };

    state.currentSuite = suite;
    fn();
    state.currentSuite = parentSuite;

    if (parentSuite) {
      parentSuite.tests.push(suite);
    } else {
      state.tests.push(suite);
    }
  }

  function it(name, fn, timeout = 5000) {
    if (!state.currentSuite) {
      throw new Error('it() must be called inside describe()');
    }

    state.currentSuite.tests.push({
      name,
      fn,
      timeout,
      type: 'test'
    });
  }

  it.skip = function (name, fn) {
    if (!state.currentSuite) {
      throw new Error('it.skip() must be called inside describe()');
    }

    state.currentSuite.tests.push({
      name,
      fn,
      type: 'skip'
    });
  };

  it.only = function (name, fn, timeout = 5000) {
    if (!state.currentSuite) {
      throw new Error('it.only() must be called inside describe()');
    }

    state.currentSuite.tests.push({
      name,
      fn,
      timeout,
      type: 'only'
    });
  };

  function beforeEach(fn) {
    if (!state.currentSuite) {
      throw new Error('beforeEach() must be called inside describe()');
    }
    state.currentSuite.beforeEach.push(fn);
  }

  function afterEach(fn) {
    if (!state.currentSuite) {
      throw new Error('afterEach() must be called inside describe()');
    }
    state.currentSuite.afterEach.push(fn);
  }

  // ==================== 测试执行 ====================

  async function runTest(test, suite) {
    const startTime = performance.now();

    try {
      // 执行 beforeEach
      for (const fn of suite.beforeEach) {
        await fn();
      }

      // 执行测试
      await new Promise((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          reject(new Error(`Test timed out after ${test.timeout}ms`));
        }, test.timeout);

        Promise.resolve(test.fn()).then(
          () => {
            clearTimeout(timeoutId);
            resolve();
          },
          (error) => {
            clearTimeout(timeoutId);
            reject(error);
          }
        );
      });

      // 执行 afterEach
      for (const fn of suite.afterEach) {
        await fn();
      }

      const duration = performance.now() - startTime;
      return { status: 'passed', duration };
    } catch (error) {
      // 执行 afterEach（即使测试失败）
      for (const fn of suite.afterEach) {
        try {
          await fn();
        } catch (e) {
          // 忽略 afterEach 错误
        }
      }

      const duration = performance.now() - startTime;
      return { status: 'failed', error, duration };
    }
  }

  async function runSuite(suite, level = 0) {
    const indent = '  '.repeat(level);
    console.log(`${indent}${suite.name}`);

    const hasOnly = suite.tests.some(t => t.type === 'only');

    for (const test of suite.tests) {
      if (test.type === 'suite') {
        await runSuite(test, level + 1);
      } else if (test.type === 'skip') {
        console.log(`${indent}  ○ ${test.name}`);
        state.skipped++;
      } else if (test.type === 'only' || (!hasOnly && test.type === 'test')) {
        const result = await runTest(test, suite);

        if (result.status === 'passed') {
          console.log(`${indent}  ✓ ${test.name} (${result.duration.toFixed(0)}ms)`);
          state.passed++;
        } else {
          console.log(`${indent}  ✗ ${test.name}`);
          state.failed++;
          state.errors.push({
            suite: suite.name,
            test: test.name,
            error: result.error,
            duration: result.duration
          });
        }
      }
    }
  }

  async function run() {
    console.log('\n🧪 Running Tests...\n');

    const startTime = performance.now();

    for (const suite of state.tests) {
      await runSuite(suite);
    }

    const totalTime = performance.now() - startTime;

    // 输出结果
    console.log('\n' + '='.repeat(50));
    console.log(`Tests: ${state.passed + state.failed + state.skoked}`);
    console.log(`  ✅ Passed: ${state.passed}`);
    console.log(`  ❌ Failed: ${state.failed}`);
    console.log(`  ⏭️  Skipped: ${state.skipped}`);
    console.log(`Time: ${totalTime.toFixed(2)}ms`);
    console.log('='.repeat(50));

    // 输出错误详情
    if (state.errors.length > 0) {
      console.log('\nFailures:\n');
      state.errors.forEach(({ suite, test, error }, index) => {
        console.log(`${index + 1}) ${suite} > ${test}`);
        console.log(`   ${error.message}`);
        if (error.stack) {
          console.log(`   ${error.stack.split('\n')[1]?.trim() || ''}`);
        }
        console.log();
      });
    }

    // 返回结果
    return {
      passed: state.passed,
      failed: state.failed,
      skipped: state.skipped,
      total: state.passed + state.failed + state.skipped,
      success: state.failed === 0
    };
  }

  function reset() {
    state.currentSuite = null;
    state.tests = [];
    state.passed = 0;
    state.failed = 0;
    state.skipped = 0;
    state.errors = [];
  }

  // ==================== 导出 ====================
  window.TestFramework = {
    describe,
    it,
    beforeEach,
    afterEach,
    expect: Expect.toBe,
    run,
    reset
  };

  // 简写导出
  window.describe = describe;
  window.it = it;
  window.beforeEach = beforeEach;
  window.afterEach = afterEach;
  window.expect = Expect.toBe;

})();
