# Contributing to phal-plugin-save-conversations

Thanks for your interest in contributing!

## Development Setup

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Getting Started

```bash
git clone https://github.com/OscillateLabsLLC/phal-plugin-save-conversations
cd phal-plugin-save-conversations

# Install dependencies (including test and dev extras)
uv sync --extra test --extra dev
```

## Common Commands

```bash
# Run tests with coverage
uv run pytest

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy phal_plugin_save_conversations/
```

## Code Style

This project uses:

- **Formatting**: `ruff format` (line length: 119)
- **Linting**: `ruff` with pycodestyle, pyflakes, and isort rules
- **Type Checking**: `mypy`

## Pull Requests

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make your changes and add tests where applicable
3. Run `uv run ruff check .` and `uv run pytest` to ensure everything passes
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat:`, `fix:`, `docs:`)
5. Open a pull request

**PR Guidelines:**
- Keep PRs focused on a single concern
- Include tests for new functionality
- Ensure all CI checks pass

## Release Process

This project uses [release-please](https://github.com/googleapis/release-please) for automated versioning based on conventional commits.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
