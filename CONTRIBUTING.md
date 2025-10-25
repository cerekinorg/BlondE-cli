# Contributing to BlondE-CLI

Thank you for your interest in contributing to BlondE-CLI! 🎉

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Pull Request Process](#pull-request-process)
6. [Coding Standards](#coding-standards)
7. [Testing](#testing)

---

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something great together.

---

## How to Contribute

### Reporting Bugs

Found a bug? Please open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

### Suggesting Features

Have an idea? Open an issue with:
- Feature description
- Use case / motivation
- Proposed implementation (optional)

### Contributing Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/BlondE-cli.git
cd BlondE-cli
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### 3. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

---

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-streaming-support`
- `bugfix/fix-memory-leak`
- `docs/improve-readme`

### Commit Messages

Write clear, concise commit messages:
```
feat: add streaming support for chat responses

- Implement streaming API for OpenRouter
- Add --stream flag to chat command
- Update documentation

Fixes #123
```

**Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

---

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)
- [ ] Commits are clean and well-described

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. Automated tests will run
2. Maintainers will review
3. Address feedback
4. Once approved, your PR will be merged!

---

## Coding Standards

### Python Style

Follow PEP 8 with these specifics:
- Line length: 100 characters
- Use type hints where possible
- Docstrings for all public functions

```python
def fix_code(file_path: str, preview: bool = False) -> Dict[str, Any]:
    """Fix bugs in a Python file using AI.
    
    Args:
        file_path: Path to the file to fix
        preview: If True, show diff without applying
        
    Returns:
        Dictionary with fix results
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    pass
```

### File Organization

```
BlondE-cli/
├── cli.py              # Main CLI application
├── memory.py           # Memory management
├── tools.py            # Agentic tools
├── model_selector.py   # Model selection UI
├── utils.py            # Utility functions
├── models/             # Model adapters
│   ├── openrouter.py
│   ├── openai.py
│   ├── local.py
│   └── hf.py
└── tests/              # Test suite
    ├── test_cli.py
    ├── test_memory.py
    └── test_tools.py
```

### Code Quality

Use these tools:
```bash
# Format code
black cli.py

# Check types
mypy cli.py

# Lint
pylint cli.py

# Sort imports
isort cli.py
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cli.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Writing Tests

Place tests in `tests/` directory:

```python
import pytest
from cli import extract_code

def test_extract_code_with_markdown():
    """Test code extraction from markdown."""
    text = "```python\nprint('hello')\n```"
    result = extract_code(text)
    assert result == "print('hello')"

def test_extract_code_without_markdown():
    """Test extraction when no markdown present."""
    text = "print('hello')"
    result = extract_code(text)
    assert result == "print('hello')"
```

### Test Coverage

Aim for:
- Unit tests for all functions
- Integration tests for commands
- Edge case coverage
- Minimum 80% code coverage

---

## Areas Needing Help

### High Priority
- [ ] Web UI implementation
- [ ] Plugin system
- [ ] Team collaboration features
- [ ] Streaming API support

### Medium Priority
- [ ] More model adapters (Anthropic, Cohere, etc.)
- [ ] Custom model fine-tuning
- [ ] Export/import memory
- [ ] Multi-language support

### Low Priority / Nice to Have
- [ ] VS Code extension
- [ ] Docker support
- [ ] Cloud deployment guide
- [ ] Performance optimizations

---

## Documentation

### Where to Add Docs

- User-facing: `docs/` directory or markdown files
- Code: Inline docstrings and comments
- API: Use proper type hints and docstrings

### Documentation Style

```python
"""Module for managing AI memory using vector databases.

This module provides the MemoryManager class for storing and retrieving
conversational context using ChromaDB as the vector store backend.

Example:
    >>> memory = MemoryManager(user_id="alice")
    >>> memory.add_conversation("How do I sort a list?", "Use sorted()")
    >>> memory.retrieve_relevant_context("sorting")
    [{'text': 'How do I sort...', 'score': 0.95}]
"""
```

---

## Questions?

- **GitHub Issues:** https://github.com/cerekinorg/BlondE-cli/issues
- **Discussions:** https://github.com/cerekinorg/BlondE-cli/discussions

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

---

**Thank you for contributing to BlondE-CLI!** 🚀

Every contribution, no matter how small, helps make this project better.
