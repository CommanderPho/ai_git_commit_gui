# Git AI Commit Upgrade Guide

This guide explains how to upgrade the Git AI Commit tool to the latest version.

## 🔍 Check Current Version

First, check your currently installed version:

```bash
git-ai-commit-gui --help
```

Or view version information in the GUI interface.

## 🚀 Upgrade Methods

### Method 1: Using uv tool (Recommended)

If you installed via `uv tool install`:

```bash
# Upgrade to latest version
uv tool upgrade git-ai-commit-gui

# Verify upgrade result
git-ai-commit-gui --help
```

**If upgrade fails, try reinstalling:**
```bash
# Uninstall old version
uv tool uninstall git-ai-commit-gui

# Install latest version
uv tool install git-ai-commit-gui
```

### Method 2: Using pip

If you installed via `pip install`:

```bash
# Upgrade to latest version
pip install --upgrade git-ai-commit-gui

# Verify upgrade result
git-ai-commit-gui --help
```

**If upgrade fails, try forcing reinstall:**
```bash
# Force reinstall
pip install --force-reinstall git-ai-commit-gui
```

### Method 3: Upgrade from Source

If you installed from GitHub source:

```bash
# Enter project directory
cd ai_git_commit_gui

# Pull latest code
git pull origin main

# Update dependencies with uv
uv sync

# Or reinstall with pip
pip install -e .
```

## ✅ Verify Upgrade

After upgrade, verify the new version is working properly:

```bash
# Check version information
git-ai-commit-gui --help

# Test basic functionality
git-ai-commit-gui --auto
```

## 🔧 Upgrade Troubleshooting

### Issue 1: Command Not Found After Upgrade

**Solution:**
```bash
# Reinstall
uv tool uninstall git-ai-commit-gui
uv tool install git-ai-commit-gui

# Or check PATH environment variable
echo $PATH
```

### Issue 2: Dependency Conflicts

**Solution:**
```bash
# Clear cache
pip cache purge

# Reinstall
pip uninstall git-ai-commit-gui
pip install git-ai-commit-gui
```

### Issue 3: Configuration File Compatibility

New versions may update the configuration file format. If you encounter configuration issues:

```bash
# Backup existing configuration
cp ~/.git_ai_commit/config.json ~/.git_ai_commit/config.json.backup

# Delete configuration file to let the program regenerate it
rm ~/.git_ai_commit/config.json

# Restart program and reconfigure
git-ai-commit-gui
```

## 📋 Version Changelog

### v0.2.0 (Latest)
- Feature improvements and performance optimization
- Fixed known issues
- Updated dependency versions

### v0.1.1
- Initial stable release
- Basic functionality complete

## 🆘 Getting Help

If you encounter issues during the upgrade:

1. **Check error logs**: Pay attention to error messages during the upgrade process
2. **Check system requirements**: Ensure Python version >= 3.12
3. **Submit an Issue**: Submit a bug report on the GitHub repository
4. **Contact support**: Send an email to the developer

## 📞 Contact

- GitHub Issues: https://github.com/duolabmeng6/ai_git_commit_gui/issues
- Developer email: 1715109585@qq.com

---

⚠️ **Important Note**: It's recommended to back up important configuration files and data before upgrading.
