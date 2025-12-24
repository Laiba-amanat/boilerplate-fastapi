# Pre-commit Hooks Usage Guide

This project uses pre-commit hooks to ensure code quality and consistency.

## 🔧 What are Pre-commit Hooks?

Pre-commit hooks are scripts that automatically run before each `git commit` to:
- Automatically format code
- Check code quality
- Prevent low-quality code commits

## ✅ Enabled Checks

### Basic Checks
- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml/json/toml/xml**: Check file syntax
- **check-added-large-files**: Prevent committing large files (>10MB)
- **check-merge-conflict**: Check for merge conflict markers
- **debug-statements**: Check for debug statements (e.g., `pdb.set_trace()`)
- **mixed-line-ending**: Unify line endings
- **check-case-conflict**: Prevent filename case conflicts

### Python Code Checks
- **ruff**: Code quality checking and auto-fix
- **ruff-format**: Code formatting (replaces black)

## 🚀 Usage

### Automatic Installation (Recommended)
```bash
# Automatically installed after cloning project
uv sync  # hooks will be automatically installed
```

### Manual Installation
```bash
# Install pre-commit
uv add --dev pre-commit

# Install hooks
uv run pre-commit install
```

### Manual Check
```bash
# Check all files
uv run pre-commit run --all-files

# Check specific file
uv run pre-commit run --files src/main.py

# Only run ruff check
uv run pre-commit run ruff --all-files
```

## 🔄 Workflow

1. **Write Code** - Normal development
2. **Commit Code** - `git commit -m "your message"`
3. **Auto Check** - pre-commit automatically runs
4. **If Issues** - Auto-fix or prompt manual fix
5. **Re-commit** - Re-commit after fixes

## 🛑 How to Disable Pre-commit Hooks

### Method 1: Complete Uninstall (Not Recommended)
```bash
# Uninstall hooks
uv run pre-commit uninstall

# Reinstall
uv run pre-commit install
```

### Method 2: Skip Single Check
```bash
# Skip this check (use with caution)
git commit --no-verify -m "urgent fix"
```

### Method 3: Disable Specific Check
Edit `.pre-commit-config.yaml` and comment out unwanted hooks:

```yaml
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      # - id: debug-statements    # Comment out unwanted checks
```

### Method 4: Set Environment Variable
```bash
# Temporarily disable
export SKIP=ruff,ruff-format
git commit -m "message"

# Or set in .env
echo "SKIP=ruff" >> .env
```

## 🎯 Recommended Configuration

### Team Development (Recommended: Enable All)
Suitable for team projects requiring unified code style.

### Personal Project (Selective Enable)
```yaml
# Minimal configuration - only keep basic checks
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### Strict Mode (Uncomment Optional Items)
Enable mypy type checking and bandit security checks.

## ❓ Common Questions

### Q: Commits are slow?
A: First run downloads tools, subsequent runs are fast. Use `--no-verify` to skip urgent commits.

### Q: Too many formatting changes?
A: First run `uv run pre-commit run --all-files` to format all files at once.

### Q: Want to customize rules?
A: Edit ruff configuration in `pyproject.toml`:

```toml
[tool.ruff]
extend-ignore = ["E501"]  # Ignore line length check
```

### Q: How to use in CI/CD?
A: In GitHub Actions:

```yaml
- name: Run pre-commit
  run: |
    uv sync
    uv run pre-commit run --all-files
```

## 📚 Reference Resources

- [Pre-commit Official Documentation](https://pre-commit.com/)
- [Ruff Configuration Guide](https://docs.astral.sh/ruff/)
- [Project CLAUDE.md](../CLAUDE.md) - Complete Development Guide
