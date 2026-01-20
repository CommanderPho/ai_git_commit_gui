# Git AI Commit Build and Release Guide

This guide explains how to build and publish the Git AI Commit package using uv.

## Prerequisites

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Ensure the project is ready for packaging:
- ✅ `pyproject.toml` is fully configured
- ✅ `README.md` exists
- ✅ `LICENSE` file exists
- ✅ All source code files are in place

## Building the Package

### 1. Clean Previous Build Artifacts
```bash
rm -rf dist/ build/ *.egg-info/
```

### 2. Build Package
```bash
uv build
```

This will generate in the `dist/` directory:
- Source distribution (`.tar.gz`)
- Binary distribution (`.whl`)

### 3. Verify Build Results
```bash
ls -la dist/
```

You should see files similar to:
```
git_ai_commit_gui-0.1.0-py3-none-any.whl
git_ai_commit_gui-0.1.0.tar.gz
```

## Testing the Package

### 1. Test Installation in Isolated Environment
```bash
uv run --with ./dist/git_ai_commit_gui-0.1.0-py3-none-any.whl --no-project -- python -c "import gui_main; print('Import successful')"
```

### 2. Test Command-line Tool
```bash
uv run --with ./dist/git_ai_commit_gui-0.1.0-py3-none-any.whl --no-project -- git-ai-commit-gui --help
```

## Publishing to PyPI

### 1. Prepare PyPI Account
- Register a [PyPI](https://pypi.org/) account
- Generate API Token: Account settings → API tokens → Add API token

### 2. Publish to Test Environment (Recommended)
```bash
uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN
```

### 3. Verify Installation from Test Environment
```bash
uv run --with git-ai-commit-gui --index https://test.pypi.org/simple/ --no-project -- git-ai-commit-gui
```

### 4. Publish to Production PyPI
```bash
uv publish --token YOUR_PYPI_TOKEN
```

## Environment Variable Configuration

For convenience, you can set environment variables:

```bash
# Set PyPI Token
export UV_PUBLISH_TOKEN="your-pypi-token-here"

# Set Test PyPI Token
export UV_PUBLISH_TOKEN_TESTPYPI="your-test-pypi-token-here"
```

Then you can simplify the publish command:
```bash
# Publish to test environment
uv publish --index testpypi

# Publish to production environment
uv publish
```

## Version Management

### Update Version Number
Edit the version number in `pyproject.toml`:
```toml
[project]
version = "0.1.1"  # Update version number
```

### Version Number Guidelines
Follow [Semantic Versioning](https://semver.org/):
- `0.1.0` → `0.1.1` (Patch version)
- `0.1.0` → `0.2.0` (Minor version)
- `0.1.0` → `1.0.0` (Major version)

## FAQ

### Q: What to do if build fails?
A: Check:
- Is `pyproject.toml` syntax correct?
- Are all dependencies installed?
- Are there syntax errors in source code?

### Q: What to do if publish fails?
A: Check:
- Is the API Token correct?
- Does the version number already exist?
- Is the network connection working?

### Q: How to revoke a published version?
A: PyPI does not allow deletion of published versions, you can only publish a new version.

## Automated Publishing

You can use GitHub Actions to automate the publishing process. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    - name: Build package
      run: uv build
    - name: Publish to PyPI
      run: uv publish
      env:
        UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

## Related Links

- [uv Official Documentation](https://docs.astral.sh/uv/)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Semantic Versioning Specification](https://semver.org/)
