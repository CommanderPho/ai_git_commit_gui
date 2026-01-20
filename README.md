# Git AI Commit - Intelligent Commit Assistant

> 🤖 AI-powered Git commit message generator for smarter, more standardized code commits

[![PyPI version](https://badge.fury.io/py/git-ai-commit-gui.svg)](https://pypi.org/project/git-ai-commit-gui/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![alt text](image.png)
## 📖 Project Overview

Git AI Commit is a modern Git commit assistant that combines AI technology with an intuitive graphical interface to help developers:

- 📊 **Intelligent Analysis**: Automatically analyze Git changes and generate structured reports
- 🤖 **AI Generation**: Generate standardized commit messages using the GLM-4-Flash model
- 🖥️ **Graphical Interface**: Friendly GUI interface with simple and intuitive operation
- ⚙️ **Flexible Configuration**: Support custom API configuration and personalized settings

## ✨ Features

### Core Features
- 🔍 **Git Change Analysis**: Deep analysis of code changes, identifying modified, added, and deleted files
- 📝 **Smart Commit Messages**: Generate standardized commit messages based on change content
- 🎯 **One-Click Commit**: Complete workflow from analysis, generation, to commit
- ⚡ **Auto Mode (--auto)**: Command-line automatic execution of complete workflow without GUI interaction
- 💾 **Configuration Management**: Persistent storage of API configuration and user preferences

### Interface Features
- 🎨 **Modern UI**: Native interface based on PySide6 with fast response
- 📱 **Compact Design**: Optimized window layout to save screen space
- 🔄 **Async Processing**: Multi-threaded processing to avoid UI freezing
- 💡 **Smart Tips**: Real-time status feedback and operation guidance

## 🚀 Quick Start

### 🎯 One-Click Launch (Simplest)

#### ⚡ Fast Auto Mode (Recommended)
```bash
# Install and auto-commit - no GUI interaction required
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install git-ai-commit-gui
cd /your/git/project
git-ai-commit-gui --auto
```

#### 🖥️ GUI Interface Mode
```bash
# Method 1: Install and run directly with uv (Recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install git-ai-commit-gui
git-ai-commit-gui

# Method 2: Temporary run with uv
uv run --from git-ai-commit-gui git-ai-commit-gui
```

### System Requirements
- Python 3.12+
- Git (installed and configured)
- Network connection (for AI API calls)

### Installation Methods

#### 🚀 Using uv (Recommended)

**Method 1: Global Installation (Recommended)**
```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install the tool
uv tool install git-ai-commit-gui

# 3. Use directly
git-ai-commit-gui
```

**Method 2: Temporary Run**
```bash
# Install uv and run temporarily
curl -LsSf https://astral.sh/uv/install.sh | sh
uv run --from git-ai-commit-gui git-ai-commit-gui
```

**Method 3: Run from Source**
```bash
# 1. Clone the project
git clone https://github.com/duolabmeng6/ai_git_commit_gui.git
cd ai_git_commit_gui

# 2. Install dependencies and run
uv sync
uv run git-ai-commit-gui
```

#### 📦 Using pip

```bash
# Install
pip install git-ai-commit-gui

# Run
git-ai-commit-gui
```

#### 🛠️ Developer Installation

```bash
# 1. Clone the project
git clone https://github.com/duolabmeng6/ai_git_commit_gui.git
cd ai_git_commit_gui

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Launch application
python gui_main.py
```

## 📋 Usage Guide

### Initial Setup

1. **Launch Application**
   ```bash
   # If globally installed
   git-ai-commit-gui

   # Or run temporarily with uv
   uv run --from git-ai-commit-gui git-ai-commit-gui
   ```

2. **Configure API Settings**
   - Switch to the "Settings" tab
   - Enter API URL: `https://api.kenhong.com/v1`
   - Enter API key
   - Set model name: `glm-4-flash`
   - Click "Save Settings"

3. **Select Git Repository**
   - Enter or browse to select a Git repository in "Repository Path"
   - The app will automatically validate the repository

### Basic Workflow

1. **View Changes**: Click the "View Changes" button to analyze uncommitted changes in the current repository
2. **AI Analysis**: Click the "AI Summarize Changes" button to generate an intelligent commit message
3. **Execute Commit**: After confirming the commit message, click "Git Commit" to complete the commit

### Command Line Usage

#### 🚀 Auto Mode (--auto)

**One-Click Auto Commit** - Automatically complete the entire workflow without manual intervention:
```bash
# Auto mode: Analyze changes → AI generate commit message → Auto commit → Close program
git-ai-commit-gui --auto

# Auto mode with specified repository path
git-ai-commit-gui /path/to/repo --auto

# Auto mode using current directory
git-ai-commit-gui ./ --auto

# Run auto mode from source
uv run python gui_main.py --auto
```

**Auto Mode Features:**
- ⚡ **Fast Commit**: No GUI interaction, one-click completion from command line
- 🤖 **Smart Detection**: Automatically validate Git repository and API configuration
- 🔄 **Complete Workflow**: Git analysis → AI generation → Auto commit
- 🛡️ **Safe Exit**: Automatically stop and show detailed information on errors
- 📝 **Real-time Feedback**: Console displays execution progress and results

#### 📋 Manual Mode (GUI Interface)

```bash
# Analyze changes in specified repository
uv run python git_diff_analyzer.py /path/to/repo 200

# Launch GUI with specified repository path
git-ai-commit-gui /path/to/repo

# Use current directory
git-ai-commit-gui ./

# Launch GUI directly (uses current directory)
uv run python gui_main.py

# View help information
git-ai-commit-gui --help
```

### Usage Examples

**Scenario 1: 🚀 Fast Auto Commit (Recommended)**
```bash
# Enter project directory and auto-commit with one command
cd /your/project/directory
git-ai-commit-gui --auto

# Output example:
# Auto mode: Starting to check repository path: /your/project/directory
# Auto mode: Repository path valid, checking API configuration...
# Starting automatic one-click processing...
# Auto processing completed: Git commit successful
```

**Scenario 2: Auto Commit with Specified Repository**
```bash
# No need to enter directory, specify path directly for auto-commit
git-ai-commit-gui /path/to/another/repo --auto
```

**Scenario 3: Quick View Changes (GUI Mode)**
```bash
# If globally installed
git-ai-commit-gui

# Or run temporarily with uv
uv run --from git-ai-commit-gui git-ai-commit-gui
```

**Scenario 4: Manual AI-Generated Commit Message (GUI Mode)**
1. Click "View Changes" in the GUI
2. Review the analysis results
3. Click "AI Summarize Changes"
4. Confirm the generated commit message
5. Click "Git Commit" to complete the commit

**Scenario 5: CI/CD Integration Auto Commit**
```bash
# Use auto mode in CI/CD scripts
#!/bin/bash
cd $PROJECT_DIR
git add .
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git-ai-commit-gui --auto
fi
```

## ⚙️ Configuration

### API Configuration
- **API URL**: API endpoint address for the AI service
- **API Key**: Key for accessing the AI service
- **Model Name**: AI model to use, default is `glm-4-flash`

### Advanced Settings
Configuration file location: `~/.git_ai_commit/config.json`

```json
{
  "api": {
    "url": "https://api.kenhong.com/v1",
    "api_key": "your-api-key",
    "model": "glm-4-flash"
  },
  "ui": {
    "window_width": 400,
    "window_height": 550,
    "last_repo_path": ""
  },
  "git": {
    "max_diff_lines": 200,
    "auto_stage": false
  }
}
```

## 🛠️ Development Guide

### Project Structure
```
git_ai_commit/
├── gui_main.py          # GUI main interface
├── git_diff_analyzer.py # Git change analyzer
├── ai_interface.py      # AI interface module
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── pyproject.toml      # Project configuration
└── README.md           # Project documentation
```

### Development Environment Setup
```bash
# Create development environment with uv
uv sync --dev

# Run tests
uv run python -m pytest

# Code formatting
uv run black .
uv run isort .
```

## 🔄 Upgrade Guide

### Quick Upgrade

**Using uv tool (Recommended):**
```bash
uv tool upgrade git-ai-commit-gui
```

**Using pip:**
```bash
pip install --upgrade git-ai-commit-gui
```

For detailed upgrade instructions, see: [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md)

## ❓ FAQ

### Q: How to get an API key?
A: Please contact the API service provider to obtain a valid API key. Ensure the key has sufficient permissions to access the GLM-4-Flash model.

### Q: What to do if the application fails to start?
A: Please check:
- Is Python version 3.12+?
- Are dependencies correctly installed: `uv sync`
- Are you running in a Git repository directory?

### Q: What to do if AI analysis fails?
A: Please check:
- Is the API key correctly configured?
- Is the network connection working?
- Is the API service available?

### Q: What Git operations are supported?
A: Currently supported:
- View uncommitted changes
- Generate commit messages
- Execute git add and git commit
- Push operations not supported (must be done manually)

### Q: How does auto mode (--auto) work?
A: Auto mode executes the following steps in sequence:
1. Check if the specified path is a valid Git repository
2. Verify API configuration is complete
3. Analyze Git change content
4. Call AI to generate commit message
5. Execute `git add .` and `git commit`
6. Automatically close the program

### Q: What to do if auto mode fails?
A: Auto mode displays detailed error information in the console:
- **Invalid Git repository**: Ensure you're running in a Git repository directory
- **API configuration error**: First run GUI mode to configure API key
- **No changes**: Ensure there are uncommitted file changes
- **Network issues**: Check network connection and API service status

### Q: What scenarios is auto mode suitable for?
A: Auto mode is particularly suitable for:
- 🚀 **Rapid Development**: Quick commits for frequent small changes
- 🤖 **CI/CD Integration**: Commits in automated build processes
- ⚡ **Command-line Workflow**: For developers who prefer not to open a GUI
- 📝 **Batch Processing**: Scripted processing of multiple repositories

## 🔧 Troubleshooting

### Dependency Installation Issues
```bash
# Clean and reinstall
rm -rf .venv
uv sync

# Or use traditional method
pip install --upgrade pip
pip install -e .
```

### GUI Interface Issues
- Ensure system supports Qt6
- On Linux, additional system packages may be required:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-pyside6

  # CentOS/RHEL
  sudo yum install python3-pyside6
  ```

### Configuration File Issues
If there are configuration problems, you can delete the config file and start over:
```bash
rm -rf ~/.git_ai_commit/config.json
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📞 Contact

For questions or suggestions, please contact us via:
- Submit a GitHub Issue
- Send email to: developer@example.com

---

⭐ If this project helps you, please give it a star!

# Donate
![alt text](image-1.png)

<!-- 测试路径解析修复 -->