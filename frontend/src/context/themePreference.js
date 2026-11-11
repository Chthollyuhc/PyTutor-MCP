export function getValidTheme(value) {
  return value === 'light' || value === 'dark' ? value : null;
}

export function resolveTheme(preference, systemTheme) {
  return getValidTheme(preference) || getValidTheme(systemTheme) || 'dark';
}
