# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- MkDocs documentation site with Material theme
- Auto-generated Python API reference via mkdocstrings
- Documentation build step in CI pipeline
- Pre-commit hooks for code quality (ruff, ESLint, TypeScript)
- Comprehensive frontend test suite with Vitest + React Testing Library

### Changed
- Updated documentation to use UK English spelling

### Fixed
- Fixed mkdocstrings paths configuration

## [0.1.0] - 2025-11-23

### Added
- Initial release
- FastAPI backend with OpenAI and Anthropic agent support
- React frontend with TypeScript and Vite
- Multiple hot take styles (controversial, sarcastic, optimistic, etc.)
- Web search integration with Brave and Serper providers
- News context integration with NewsAPI
- Docker and Docker Compose setup
- Comprehensive backend test suite with pytest
- Makefile with development shortcuts

[Unreleased]: https://github.com/Uokoroafor/hot-take-generator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Uokoroafor/hot-take-generator/releases/tag/v0.1.0
