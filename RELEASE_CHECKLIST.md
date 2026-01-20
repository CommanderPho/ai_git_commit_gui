# Git AI Commit v0.2.1 Release Checklist

## ✅ Pre-release Checklist
- [x] Version number updated to 0.2.1
- [x] Encoding fix code implemented and tested
- [x] Package build successful
- [x] Command-line tool tests passed
- [x] Release notes updated

## 🚀 Release Steps

### 1. Publish to PyPI
```bash
# Method 1: Using environment variable (Recommended)
export UV_PUBLISH_TOKEN='your-pypi-token'
uv publish

# Method 2: Specify token directly
uv publish --token YOUR_PYPI_TOKEN

# Method 3: Test publish first
uv publish --index testpypi --token YOUR_TEST_PYPI_TOKEN
```

### 2. Verify Release
```bash
# Wait a few minutes then test installation
pip install --upgrade git-ai-commit-gui==0.2.1

# Or use uv
uv tool install git-ai-commit-gui==0.2.1 --force
```

### 3. Create GitHub Release
- Use content from `create_release.md`
- Upload built wheel and tar.gz files
- Tag: v0.2.1

### 4. Test New Version
```bash
# Test basic functionality
git-ai-commit-gui --help

# Test auto mode (Windows users focus on this)
git-ai-commit-gui --auto
```

## 🐛 Changes in This Release
- Fixed UnicodeDecodeError encoding issue in Windows environment
- Added intelligent encoding detection and multi-encoding support
- Enhanced --auto mode stability
- Improved error handling and debug information

## 📋 Post-release Tasks
- [ ] Publish to PyPI
- [ ] Create GitHub Release
- [ ] Notify users to upgrade
- [ ] Update documentation
- [ ] Monitor user feedback

## 🔗 Related Links
- PyPI page: https://pypi.org/project/git-ai-commit-gui/
- GitHub repository: https://github.com/duolabmeng6/ai_git_commit_gui
- Issue tracker: https://github.com/duolabmeng6/ai_git_commit_gui/issues
