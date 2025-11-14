# Hot Take Generator - Frontend

React + TypeScript + Vite application for generating hot takes on any topic.

## Features

- 🔥 Generate hot takes in various styles
- 🔍 Web search integration
- 📰 News search integration
- 🌙 Dark mode support
- 📋 Copy, share, and save hot takes
- ⌨️ Keyboard shortcuts
- ♿ Accessible UI with ARIA support

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   Copy the example environment file and update with your values:
   ```bash
   cp .env.example .env
   ```

   Available environment variables:
   - `VITE_API_BASE_URL`: Backend API base URL (default: `http://localhost:8000`)

3. **Run the development server:**
   ```bash
   npm run dev
   ```

## Environment Configuration

The application uses environment variables for configuration. All environment variables must be prefixed with `VITE_` to be accessible in the client code.

**Files:**
- `.env` - Your local environment configuration (not committed to git)
- `.env.example` - Example configuration template (committed to git)
- `src/config.ts` - Centralized configuration with defaults

**Usage:**
The `config.ts` file provides type-safe access to environment variables:
```typescript
import config from './config';

fetch(`${config.apiBaseUrl}/api/endpoint`);
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Run tests with coverage
- `npm run lint` - Lint code

## Tech Stack

This project uses:
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Vitest** - Testing framework
- **@testing-library/react** - Testing utilities

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
