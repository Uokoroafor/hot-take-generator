# Contributing

Thanks for your interest in contributing.

## Getting Started

1. Fork the repo and create a feature branch.
2. Set up the project:
   - `make quick-start` for local native setup
   - or `make quick-start-docker` for Docker setup
3. Make your changes and add/update tests where relevant.

## Before Opening a PR

1. Run checks locally:
   - `make lint`
   - `make test`
2. Keep PRs focused and easy to review.
3. Update docs if behavior or setup changed.

## Pull Request Guidelines

1. Use a clear title and description.
2. Explain what changed and why.
3. Mention any tradeoffs or follow-up tasks.

## Reporting Issues

When opening an issue, include:

1. Steps to reproduce
2. Expected vs actual behavior
3. Logs/screenshots (if helpful)
4. Your environment (OS, Node/Python versions)

## Security

Do not commit secrets or `.env` files. Use `.env.example` for configuration templates.
