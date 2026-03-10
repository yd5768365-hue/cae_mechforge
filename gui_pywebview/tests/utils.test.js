/**
 * @fileoverview Utils 模块单元测试
 * @module Tests/Utils
 */

(function () {
  'use strict';

  const { describe, it, expect, beforeEach, afterEach } = TestFramework;

  describe('Utils', () => {
    describe('DOM 操作', () => {
      describe('$()', () => {
        it('应该返回元素', () => {
          const div = document.createElement('div');
          div.id = 'test-element';
          document.body.appendChild(div);

          const result = Utils.$('test-element');
          expect(result).toBe(div);

          document.body.removeChild(div);
        });

        it('应该返回 null 当元素不存在', () => {
          const result = Utils.$('non-existent');
          expect(result).toBeNull();
        });
      });

      describe('$$()', () => {
        it('应该返回 NodeList', () => {
          const container = document.createElement('div');
          container.innerHTML = '<span class="test"></span><span class="test"></span>';
          document.body.appendChild(container);

          const result = Utils.$$('.test');
          expect(result.length).toBe(2);

          document.body.removeChild(container);
        });
      });
    });

    describe('字符串处理', () => {
      describe('escapeHtml()', () => {
        it('应该转义 HTML 标签', () => {
          const input = '<script>alert("xss")</script>';
          const result = Utils.escapeHtml(input);
          expect(result).toBe('&lt;script&gt;alert("xss")&lt;/script&gt;');
        });

        it('应该处理 null', () => {
          expect(Utils.escapeHtml(null)).toBe('');
        });

        it('应该处理 undefined', () => {
          expect(Utils.escapeHtml(undefined)).toBe('');
        });

        it('应该处理数字', () => {
          expect(Utils.escapeHtml(123)).toBe('123');
        });
      });

      describe('truncate()', () => {
        it('应该截断长字符串', () => {
          const result = Utils.truncate('Hello World', 8);
          expect(result).toBe('Hello...');
        });

        it('应该返回原字符串当长度足够', () => {
          const result = Utils.truncate('Hi', 10);
          expect(result).toBe('Hi');
        });

        it('应该处理空字符串', () => {
          expect(Utils.truncate('', 5)).toBe('');
        });

        it('应该支持自定义后缀', () => {
          const result = Utils.truncate('Hello World', 8, '…');
          expect(result).toBe('Hello W…');
        });
      });

      describe('generateId()', () => {
        it('应该生成唯一 ID', () => {
          const id1 = Utils.generateId();
          const id2 = Utils.generateId();
          expect(id1).not.toBe(id2);
        });

        it('应该支持前缀', () => {
          const id = Utils.generateId('btn');
          expect(id.startsWith('btn-')).toBe(true);
        });
      });

      describe('toCamelCase()', () => {
        it('应该转换短横线命名', () => {
          expect(Utils.toCamelCase('hello-world')).toBe('helloWorld');
        });

        it('应该处理多个短横线', () => {
          expect(Utils.toCamelCase('hello-world-test')).toBe('helloWorldTest');
        });
      });

      describe('toKebabCase()', () => {
        it('应该转换驼峰命名', () => {
          expect(Utils.toKebabCase('helloWorld')).toBe('hello-world');
        });

        it('应该处理多个大写字母', () => {
          expect(Utils.toKebabCase('HelloWorldTest')).toBe('hello-world-test');
        });
      });
    });

    describe('函数工具', () => {
      describe('debounce()', () => {
        it('应该延迟执行', (done) => {
          let count = 0;
          const fn = () => count++;
          const debounced = Utils.debounce(fn, 50);

          debounced();
          debounced();
          debounced();

          expect(count).toBe(0);

          setTimeout(() => {
            expect(count).toBe(1);
            done();
          }, 100);
        });
      });

      describe('throttle()', () => {
        it('应该限制执行频率', (done) => {
          let count = 0;
          const fn = () => count++;
          const throttled = Utils.throttle(fn, 100);

          throttled();
          throttled();
          throttled();

          expect(count).toBe(1);

          setTimeout(() => {
            expect(count).toBe(1);
            done();
          }, 50);
        });
      });

      describe('memoize()', () => {
        it('应该缓存结果', () => {
          let callCount = 0;
          const fn = (x) => {
            callCount++;
            return x * 2;
          };
          const memoized = Utils.memoize(fn);

          expect(memoized(5)).toBe(10);
          expect(memoized(5)).toBe(10);
          expect(callCount).toBe(1);
        });

        it('应该处理不同参数', () => {
          const fn = (x) => x * 2;
          const memoized = Utils.memoize(fn);

          expect(memoized(5)).toBe(10);
          expect(memoized(10)).toBe(20);
        });
      });

      describe('pipe()', () => {
        it('应该从左到右执行函数', () => {
          const add1 = (x) => x + 1;
          const mul2 = (x) => x * 2;
          const result = Utils.pipe(add1, mul2)(5);
          expect(result).toBe(12); // (5 + 1) * 2
        });
      });

      describe('compose()', () => {
        it('应该从右到左执行函数', () => {
          const add1 = (x) => x + 1;
          const mul2 = (x) => x * 2;
          const result = Utils.compose(add1, mul2)(5);
          expect(result).toBe(11); // (5 * 2) + 1
        });
      });
    });

    describe('时间处理', () => {
      describe('getTimestamp()', () => {
        it('应该返回格式化时间', () => {
          const result = Utils.getTimestamp();
          expect(result).toMatch(/^\[\d{2}:\d{2}\]$/);
        });
      });

      describe('formatDateTime()', () => {
        it('应该格式化日期', () => {
          const date = new Date('2024-01-15 14:30:00');
          const result = Utils.formatDateTime(date);
          expect(result).toBe('2024-01-15 14:30:00');
        });

        it('应该支持自定义格式', () => {
          const date = new Date('2024-01-15 14:30:00');
          const result = Utils.formatDateTime(date, 'YYYY年MM月DD日');
          expect(result).toBe('2024年01月15日');
        });
      });

      describe('delay()', () => {
        it('应该延迟执行', async () => {
          const start = Date.now();
          await Utils.delay(50);
          const elapsed = Date.now() - start;
          expect(elapsed).toBeGreaterThanOrEqual(50);
        });
      });
    });

    describe('随机数', () => {
      describe('random()', () => {
        it('应该在范围内', () => {
          const result = Utils.random(10, 20);
          expect(result).toBeGreaterThanOrEqual(10);
          expect(result).toBeLessThanOrEqual(20);
        });
      });

      describe('randomInt()', () => {
        it('应该返回整数', () => {
          const result = Utils.randomInt(1, 6);
          expect(Number.isInteger(result)).toBe(true);
          expect(result).toBeGreaterThanOrEqual(1);
          expect(result).toBeLessThanOrEqual(6);
        });
      });

      describe('randomChoice()', () => {
        it('应该从数组中选择', () => {
          const arr = ['a', 'b', 'c'];
          const result = Utils.randomChoice(arr);
          expect(arr).toContain(result);
        });
      });

      describe('randomColor()', () => {
        it('应该返回 HEX 颜色', () => {
          const result = Utils.randomColor();
          expect(result).toMatch(/^#[0-9A-Fa-f]{6}$/);
        });
      });
    });

    describe('对象操作', () => {
      describe('deepClone()', () => {
        it('应该深拷贝对象', () => {
          const obj = { a: { b: 1 } };
          const clone = Utils.deepClone(obj);
          expect(clone).toEqual(obj);
          expect(clone).not.toBe(obj);
          expect(clone.a).not.toBe(obj.a);
        });

        it('应该处理数组', () => {
          const arr = [1, [2, 3]];
          const clone = Utils.deepClone(arr);
          expect(clone).toEqual(arr);
          expect(clone).not.toBe(arr);
        });

        it('应该处理日期', () => {
          const date = new Date();
          const clone = Utils.deepClone(date);
          expect(clone.getTime()).toBe(date.getTime());
        });
      });

      describe('mergeObjects()', () => {
        it('应该合并对象', () => {
          const result = Utils.mergeObjects({ a: 1 }, { b: 2 });
          expect(result).toEqual({ a: 1, b: 2 });
        });

        it('后面的值应该覆盖前面的', () => {
          const result = Utils.mergeObjects({ a: 1 }, { a: 2 });
          expect(result.a).toBe(2);
        });
      });

      describe('pick()', () => {
        it('应该选择指定属性', () => {
          const result = Utils.pick({ a: 1, b: 2, c: 3 }, ['a', 'c']);
          expect(result).toEqual({ a: 1, c: 3 });
        });
      });

      describe('omit()', () => {
        it('应该排除指定属性', () => {
          const result = Utils.omit({ a: 1, b: 2, c: 3 }, ['b']);
          expect(result).toEqual({ a: 1, c: 3 });
        });
      });

      describe('toQueryString()', () => {
        it('应该转换对象为查询字符串', () => {
          const result = Utils.toQueryString({ page: 1, size: 10 });
          expect(result).toBe('page=1&size=10');
        });

        it('应该编码特殊字符', () => {
          const result = Utils.toQueryString({ name: 'hello world' });
          expect(result).toBe('name=hello%20world');
        });

        it('应该过滤 null 值', () => {
          const result = Utils.toQueryString({ a: 1, b: null, c: undefined });
          expect(result).toBe('a=1');
        });
      });
    });

    describe('验证工具', () => {
      describe('isEmpty()', () => {
        it('应该识别 null', () => {
          expect(Utils.isEmpty(null)).toBe(true);
        });

        it('应该识别空字符串', () => {
          expect(Utils.isEmpty('')).toBe(true);
        });

        it('应该识别空数组', () => {
          expect(Utils.isEmpty([])).toBe(true);
        });

        it('应该识别空对象', () => {
          expect(Utils.isEmpty({})).toBe(true);
        });

        it('应该识别非空值', () => {
          expect(Utils.isEmpty('text')).toBe(false);
          expect(Utils.isEmpty([1])).toBe(false);
          expect(Utils.isEmpty({ a: 1 })).toBe(false);
        });
      });

      describe('isNumber()', () => {
        it('应该识别数字', () => {
          expect(Utils.isNumber(123)).toBe(true);
          expect(Utils.isNumber(0)).toBe(true);
        });

        it('应该拒绝 NaN', () => {
          expect(Utils.isNumber(NaN)).toBe(false);
        });

        it('应该拒绝字符串', () => {
          expect(Utils.isNumber('123')).toBe(false);
        });
      });

      describe('isString()', () => {
        it('应该识别字符串', () => {
          expect(Utils.isString('text')).toBe(true);
        });

        it('应该拒绝数字', () => {
          expect(Utils.isString(123)).toBe(false);
        });
      });

      describe('isFunction()', () => {
        it('应该识别函数', () => {
          expect(Utils.isFunction(() => {})).toBe(true);
        });

        it('应该拒绝对象', () => {
          expect(Utils.isFunction({})).toBe(false);
        });
      });

      describe('isObject()', () => {
        it('应该识别对象', () => {
          expect(Utils.isObject({})).toBe(true);
        });

        it('应该拒绝数组', () => {
          expect(Utils.isObject([])).toBe(false);
        });

        it('应该拒绝 null', () => {
          expect(Utils.isObject(null)).toBe(false);
        });
      });
    });
  });

})();
