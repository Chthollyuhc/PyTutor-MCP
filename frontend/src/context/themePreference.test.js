import test from 'node:test';
import assert from 'node:assert/strict';
import { getValidTheme, resolveTheme } from './themePreference.js';

test('follows the operating system when no saved preference exists', () => {
  assert.equal(resolveTheme(null, 'light'), 'light');
  assert.equal(resolveTheme(null, 'dark'), 'dark');
});

test('a valid saved preference overrides the operating system', () => {
  assert.equal(resolveTheme('light', 'dark'), 'light');
  assert.equal(resolveTheme('dark', 'light'), 'dark');
});

test('invalid stored or system values fall back safely', () => {
  assert.equal(getValidTheme('system'), null);
  assert.equal(resolveTheme('sepia', 'light'), 'light');
  assert.equal(resolveTheme('sepia', 'unknown'), 'dark');
});
