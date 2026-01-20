# GitHub Release v0.2.1 Release Notes

## 🎉 Git AI Commit v0.2.1 Released

### 📋 Version Information
- **Version**: v0.2.1
- **Release Date**: 2025-06-23
- **Compatibility**: Python 3.12+

### ✨ Major Updates

#### 🐛 Critical Fixes
- **Fixed Windows Encoding Issue**: Resolved `UnicodeDecodeError: 'gbk' codec can't decode byte 0xa7` error in Windows environment
- **Enhanced Cross-platform Compatibility**: Added intelligent encoding detection and multi-encoding support
- **Improved Error Handling**: Better encoding error handling and debug information

#### 🔧 Technical Improvements
- Added `safe_subprocess_run()` function with support for UTF-8, GBK, GB2312 and other encodings
- Optimized encoding handling for all Git command calls
- Enhanced stability in Windows Chinese environment

#### 🚀 Auto Mode Optimization
- Fixed encoding issues in `--auto` mode on Windows
- Improved reliability of auto-commit workflow
- Better error message display

### 🚀 Upgrade Methods

#### Using uv tool (Recommended)
```bash
uv tool upgrade git-ai-commit-gui
```

#### Using pip
```bash
pip install --upgrade git-ai-commit-gui
```

#### Upgrade from Source
```bash
git pull origin main
uv sync
```

### 📦 Downloads

- **Wheel Package**: `git_ai_commit_gui-0.2.1-py3-none-any.whl`
- **Source Package**: `git_ai_commit_gui-0.2.1.tar.gz`

### 🔗 Related Links

- [PyPI Page](https://pypi.org/project/git-ai-commit-gui/)
- [Upgrade Guide](UPGRADE_GUIDE.md)
- [Build Guide](BUILD_GUIDE.md)
- [User Documentation](README.md)

### 🐛 Issue Reporting

If you encounter issues during upgrade or usage, please:
1. Check the [Upgrade Guide](UPGRADE_GUIDE.md)
2. Submit a [GitHub Issue](https://github.com/duolabmeng6/ai_git_commit_gui/issues)
3. Contact developer: 1715109585@qq.com

### 🙏 Acknowledgments

Thank you for your support and feedback!

---

**Complete Changelog**: https://github.com/duolabmeng6/ai_git_commit_gui/compare/v0.2.0...v0.2.1
