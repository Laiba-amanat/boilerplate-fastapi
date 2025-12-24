# 🤝 Contributing Guide

Thank you for your interest in the Enterprise FastAPI Backend Template project! We welcome all forms of contributions.

## 🚀 Quick Start

1. **Fork the project** to your GitHub account
2. **Clone** your fork to your local machine
3. **Create a branch** for your feature or fix
4. **Develop and test** your changes
5. **Submit** a Pull Request

## 💻 Development Environment Setup

```bash
# Clone your fork
git clone https://github.com/your-username/FastAPI-Template.git
cd FastAPI-Template

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Copy environment configuration
cp .env.example .env
# Edit .env file and set necessary configurations

# Initialize database
uv run aerich init-db

# Run development server
uv run uvicorn src:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Code Standards

We use the following tools to maintain code quality:

```bash
# Code formatting
uv run ruff format src/

# Code checking
uv run ruff check src/

# Type checking
uv run mypy src/

# Run tests
uv run pytest
```

## 🎯 Types of Contributions

We welcome the following types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Documentation improvements**
- 🧪 **Test additions**
- ⚡ **Performance optimizations**
- 🎨 **Code refactoring**

## 📝 Commit Standards

Please use clear commit messages:

```
Type(scope): Short description

Detailed description (if needed)
```

Examples:
- `feat(api): Add user export functionality`
- `fix(auth): Fix JWT token expiration handling`
- `docs(readme): Update installation instructions`

## 🔄 Pull Request Process

1. **Ensure** your code passes all checks
2. **Update** relevant documentation
3. **Add** appropriate tests
4. **Fill out** all information in the PR template
5. **Wait** for code review

## 🧪 Testing

Please add tests for your changes:

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_your_feature.py

# Generate coverage report
uv run pytest --cov=src --cov-report=html
```

## 📚 Documentation

If your changes affect user experience, please update relevant documentation:

- **README.md** - Project overview and quick start
- **CLAUDE.md** - Detailed developer guide
- **API Documentation** - If there are API changes

## 🐛 Reporting Issues

Found a bug? Please use our issue template to report:

1. Check if there's already a similar issue
2. Use the appropriate issue template
3. Provide detailed reproduction steps
4. Include relevant environment information

## 💡 Feature Requests

Have a good idea? We'd love to hear it:

1. Use the feature request template
2. Clearly describe the use case
3. Consider backward compatibility
4. Discuss implementation approach

## ❓ Need Help?

- 🌐 Visit [Official Website](http://fastapi.infyai.cn/) for latest documentation
- 📖 Check [CLAUDE.md](CLAUDE.md) developer guide
- 🔍 Search existing issues
- 💬 Ask questions in discussions
- 📧 Contact maintainers

## 🏆 Contributors

Thank you to all developers who have contributed to this project!

---

**Every contribution matters, no matter how small. Thank you for helping improve this project!** 🙏
