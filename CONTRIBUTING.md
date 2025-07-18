# Contributing to QuestBoard

Thank you for your interest in contributing to QuestBoard! We appreciate your time and effort in making this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/Himo-kai/QuestBoard.git
   cd QuestBoard
   ```
3. **Set up** the development environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```
4. **Create a branch** for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-short-description
   ```

## Development Workflow

1. **Start** the development server
   ```bash
   flask run
   ```

2. **Run tests** to ensure everything works
   ```bash
   pytest
   ```

3. **Format and lint** your code
   ```bash
   black .
   flake8
   mypy .
   ```

4. **Commit** your changes with a descriptive message
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push** to your fork
   ```bash
   git push origin your-branch-name
   ```

## Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **isort** for import sorting
- **mypy** for type checking

Run the following before committing:
```bash
black .
isort .
flake8
mypy .
```

## Testing

We use `pytest` for testing. Follow these guidelines:

- Write tests for all new features and bug fixes
- Keep tests focused and independent
- Use fixtures for common test data
- Follow the Arrange-Act-Assert pattern

Run tests with:
```bash
pytest
```

### Test Coverage

We aim for high test coverage. Check coverage with:
```bash
pytest --cov=questboard tests/
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Ensure tests pass and coverage is maintained
3. Submit a pull request with a clear description of changes
4. Reference any related issues
5. Wait for code review and address any feedback

## Reporting Issues

When reporting issues, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Any relevant logs or screenshots

## Feature Requests

For feature requests:

1. Check if the feature already exists
2. Explain why this feature would be useful
3. Provide as much detail as possible
4. Consider opening a discussion first for major features

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.
