module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    node: true  // Add Node.js support for vite.config.ts
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',  // Add TypeScript support
    'plugin:react/recommended',        // Add React support
    'plugin:react-hooks/recommended'   // Add React Hooks support
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh', 'react', '@typescript-eslint'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'react/react-in-jsx-scope': 'off',  // Not needed with React 17+
    'react/no-unescaped-entities': 'off',  // Allow apostrophes in text
    '@typescript-eslint/no-unused-vars': 'warn',  // Better unused var handling
    '@typescript-eslint/no-explicit-any': 'warn',  // Warn about any types
    'no-unused-vars': 'off',  // Turn off base rule in favor of TypeScript version
    'no-inner-declarations': 'off',  // Allow function declarations in blocks
    'no-prototype-builtins': 'off',  // Allow hasOwnProperty usage
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
}
