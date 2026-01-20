#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git AI Commit GUI Main Interface
Provides a graphical interface for managing Git change analysis and AI commit message generation
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QFormLayout, QSplitter, QGroupBox, QProgressBar, QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from config import config_manager
from git_diff_analyzer import GitDiffAnalyzer
from ai_interface import create_ai_interface
from utils import is_git_repository, normalize_path, safe_subprocess_run


class GitAnalysisWorker(QThread):
    """Git analysis worker thread"""
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, repo_path: str, max_lines: int = 200):
        super().__init__()
        self.repo_path = repo_path
        self.max_lines = max_lines
    
    def run(self):
        try:
            analyzer = GitDiffAnalyzer(self.repo_path, self.max_lines)
            result = analyzer.analyze_repository()
            formatted_output = analyzer.format_output(result)
            self.finished.emit(formatted_output)
        except Exception as e:
            self.error.emit(str(e))


class AIAnalysisWorker(QThread):
    """AI analysis worker thread"""
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, git_analysis: str, api_config: dict):
        super().__init__()
        self.git_analysis = git_analysis
        self.api_config = api_config
    
    def run(self):
        try:
            ai = create_ai_interface(
                self.api_config["api_key"],
                self.api_config["url"],
                self.api_config["model"]
            )
            # Use custom prompt if available
            custom_prompt = self.api_config.get("prompt", "").strip()
            result = ai.generate_commit_message(
                self.git_analysis,
                custom_prompt if custom_prompt else None
            )
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("AI analysis failed: no result returned")
        except Exception as e:
            self.error.emit(f"AI analysis failed: {str(e)}")


class GitAnalyzerGUI(QMainWindow):
    """Git analyzer main interface"""

    def __init__(self, repo_path: str = "./", auto_mode: bool = False):
        super().__init__()
        self.current_repo_path = ""
        self.git_analysis_result = ""
        self.initial_repo_path = repo_path
        self.auto_mode = auto_mode

        # Worker threads
        self.git_worker = None
        self.ai_worker = None

        # Auto process state management
        self.auto_process_state = "IDLE"  # IDLE, GIT_ANALYSIS, AI_ANALYSIS, COMMIT

        self.init_ui()
        self.load_settings()
        self.setup_auto_path()

        # If in auto mode, setup timer for auto execution
        if self.auto_mode:
            self.setup_auto_execution()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Git AI Commit - Intelligent Commit Assistant WeChat:261077")
        self.setMinimumSize(400, 500)  # Reduce minimum window size
        self.resize(400, 550)  # Set default window size
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Repository path selection area
        self.create_repo_selection_area(main_layout)
        
        # Create tab widget
        self.create_tab_widget(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_repo_selection_area(self, parent_layout):
        """Create repository selection area"""
        repo_group = QGroupBox("Repository Selection")
        repo_layout = QHBoxLayout(repo_group)
        
        # Path input field
        self.repo_path_edit = QLineEdit()
        self.repo_path_edit.setPlaceholderText("Please select Git repository path...")
        self.repo_path_edit.textChanged.connect(self.on_repo_path_changed)
        
        # Browse button
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_repo_path)
        
        repo_layout.addWidget(QLabel("Repository Path:"))
        repo_layout.addWidget(self.repo_path_edit)
        repo_layout.addWidget(browse_btn)
        
        parent_layout.addWidget(repo_group)
    
    def create_tab_widget(self, parent_layout):
        """Create tab widget"""
        self.tab_widget = QTabWidget()
        
        # Code tab
        self.create_code_tab()
        
        # Settings tab
        self.create_settings_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_code_tab(self):
        """Create code tab"""
        code_widget = QWidget()
        code_layout = QVBoxLayout(code_widget)
        
        # Button area
        button_layout = QHBoxLayout()

        self.view_changes_btn = QPushButton("View Changes")
        self.view_changes_btn.clicked.connect(self.view_git_changes)

        self.ai_summary_btn = QPushButton("AI Summarize")
        self.ai_summary_btn.clicked.connect(self.ai_analyze_changes)

        self.commit_btn = QPushButton("Git Commit")
        self.commit_btn.clicked.connect(self.git_commit)
        self.commit_btn.setEnabled(False)

        self.auto_process_btn = QPushButton("Auto Process")
        self.auto_process_btn.clicked.connect(self.auto_process)
        self.auto_process_btn.setEnabled(False)

        button_layout.addWidget(self.view_changes_btn)
        button_layout.addWidget(self.ai_summary_btn)
        button_layout.addWidget(self.commit_btn)
        button_layout.addWidget(self.auto_process_btn)

        code_layout.addLayout(button_layout)
        
        # Text display area (vertical layout)
        # Git changes text box
        changes_group = QGroupBox("Git Changes")
        changes_layout = QVBoxLayout(changes_group)
        self.changes_text = QTextEdit()
        self.changes_text.setFont(QFont("Monaco", 9))  # Use system monospace font, smaller size
        self.changes_text.setPlaceholderText("Click 'View Changes' button to view Git changes...")
        self.changes_text.setMaximumHeight(200)  # Limit height
        changes_layout.addWidget(self.changes_text)

        # AI analysis result text box
        ai_group = QGroupBox("AI Analysis Result")
        ai_layout = QVBoxLayout(ai_group)
        self.ai_result_text = QTextEdit()
        self.ai_result_text.setFont(QFont("Monaco", 9))  # Use system monospace font, smaller size
        self.ai_result_text.setPlaceholderText("Click 'AI Summarize' button to get AI analysis...")
        self.ai_result_text.setMaximumHeight(150)  # Limit height, AI results are usually shorter
        ai_layout.addWidget(self.ai_result_text)

        code_layout.addWidget(changes_group)
        code_layout.addWidget(ai_group)
        
        self.tab_widget.addTab(code_widget, "Code")
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(20)

        # API settings group
        api_group = QGroupBox("OpenAI API Settings")
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(15)

        # Use grid layout for better width control
        api_grid = QGridLayout()
        api_grid.setColumnStretch(1, 1)  # Allow second column (input field) to stretch

        # API URL
        api_url_label = QLabel("API URL:")
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("https://api.kenhong.com/v1")
        self.api_url_edit.setMinimumWidth(300)
        api_grid.addWidget(api_url_label, 0, 0)
        api_grid.addWidget(self.api_url_edit, 0, 1)

        # API Key
        api_key_label = QLabel("API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Please enter API key...")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setMinimumWidth(300)
        api_grid.addWidget(api_key_label, 1, 0)
        api_grid.addWidget(self.api_key_edit, 1, 1)

        # Model name
        model_label = QLabel("Model Name:")
        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("glm-4-flash")
        self.model_name_edit.setMinimumWidth(300)
        api_grid.addWidget(model_label, 2, 0)
        api_grid.addWidget(self.model_name_edit, 2, 1)

        api_layout.addLayout(api_grid)

        # Prompt settings
        prompt_label = QLabel("AI Prompt:")
        prompt_label.setAlignment(Qt.AlignTop)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Please enter AI prompt for generating commit message...")
        self.prompt_edit.setMaximumHeight(120)  # Limit height
        self.prompt_edit.setMinimumHeight(80)   # Minimum height

        # Create grid layout for prompt
        prompt_grid = QGridLayout()
        prompt_grid.addWidget(prompt_label, 0, 0)
        prompt_grid.addWidget(self.prompt_edit, 0, 1)
        prompt_grid.setColumnStretch(1, 1)  # Allow text box to stretch

        api_layout.addLayout(prompt_grid)

        # Save button area
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        save_btn = QPushButton("Save Settings")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()

        settings_layout.addWidget(api_group)
        settings_layout.addLayout(button_layout)
        settings_layout.addStretch()

        self.tab_widget.addTab(settings_widget, "Settings")
    
    def setup_auto_path(self):
        """Auto setup path"""
        current_dir = os.getcwd()

        # Use the passed path parameter
        input_path = self.initial_repo_path
        # If relative path "./", convert to absolute path
        if input_path == "./":
            resolved_path = normalize_path(current_dir)
        else:
            resolved_path = normalize_path(input_path)

        # Set path
        self.repo_path_edit.setText(resolved_path)
        self.current_repo_path = resolved_path

    def setup_auto_execution(self):
        """Setup auto execution"""
        # Use timer to delay execution, ensuring GUI is fully initialized
        self.auto_timer = QTimer()
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(self.auto_execute)
        self.auto_timer.start(1000)  # Execute after 1 second

    def auto_execute(self):
        """Auto execute one-click processing"""
        print(f"Auto mode: Starting to check repository path: {self.current_repo_path}")

        # Check if repository path is valid
        if not self.current_repo_path or not is_git_repository(self.current_repo_path):
            print(f"Error: Invalid Git repository path: {self.current_repo_path}")
            QApplication.quit()
            return

        print("Auto mode: Repository path is valid, checking API configuration...")

        # Check API configuration
        api_config = config_manager.get_api_config()
        if not api_config["api_key"]:
            print("Error: API key not configured, please configure in settings first")
            QApplication.quit()
            return

        print("Starting auto execution of one-click processing...")
        # Trigger auto process
        self.auto_process()

    def load_settings(self):
        """Load settings"""
        # Load API settings
        api_config = config_manager.get_api_config()
        self.api_url_edit.setText(api_config["url"])
        self.api_key_edit.setText(api_config["api_key"])
        self.model_name_edit.setText(api_config["model"])
        self.prompt_edit.setPlainText(api_config["prompt"])

        # Load UI settings
        ui_config = config_manager.get_ui_config()
        self.resize(ui_config["window_width"], ui_config["window_height"])

        # Load last repository path
        last_repo = ui_config["last_repo_path"]
        if last_repo and not self.current_repo_path:
            self.repo_path_edit.setText(last_repo)
            self.current_repo_path = last_repo

    def save_settings(self):
        """Save settings"""
        # Save API settings
        config_manager.set_api_config(
            self.api_url_edit.text().strip(),
            self.api_key_edit.text().strip(),
            self.model_name_edit.text().strip(),
            self.prompt_edit.toPlainText().strip()
        )

        # Save UI settings
        config_manager.set_ui_config(
            window_width=self.width(),
            window_height=self.height(),
            last_repo_path=self.current_repo_path
        )

        QMessageBox.information(self, "Settings", "Settings saved")

    def browse_repo_path(self):
        """Browse repository path"""
        current_path = self.repo_path_edit.text() or os.getcwd()
        repo_path = QFileDialog.getExistingDirectory(
            self, "Select Git Repository", current_path
        )

        if repo_path:
            self.repo_path_edit.setText(repo_path)

    def on_repo_path_changed(self, path: str):
        """Handle repository path change"""
        self.current_repo_path = path.strip()

        # Check if it's a valid Git repository
        if self.current_repo_path and is_git_repository(self.current_repo_path):
            self.statusBar().showMessage(f"Git repository: {self.current_repo_path}")
            self.view_changes_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)
        else:
            self.statusBar().showMessage("Please select a valid Git repository")
            self.view_changes_btn.setEnabled(False)
            self.ai_summary_btn.setEnabled(False)
            self.commit_btn.setEnabled(False)
            self.auto_process_btn.setEnabled(False)

    def view_git_changes(self):
        """View Git changes"""
        if not self.current_repo_path:
            QMessageBox.warning(self, "Warning", "Please select a Git repository path first")
            return

        if not is_git_repository(self.current_repo_path):
            QMessageBox.warning(self, "Warning", "The selected path is not a valid Git repository")
            return

        # Disable buttons, show progress
        self.view_changes_btn.setEnabled(False)
        self.statusBar().showMessage("Analyzing Git changes...")

        # Start Git analysis worker thread
        git_config = config_manager.get_git_config()
        self.git_worker = GitAnalysisWorker(
            self.current_repo_path,
            git_config["max_diff_lines"]
        )
        self.git_worker.finished.connect(self.on_git_analysis_finished)
        self.git_worker.error.connect(self.on_git_analysis_error)
        self.git_worker.start()

    def on_git_analysis_finished(self, result: str):
        """Git analysis completed"""
        self.git_analysis_result = result
        self.changes_text.setPlainText(result)

        # Check if in auto process
        if self.auto_process_state == "GIT_ANALYSIS":
            # Auto process: continue with AI analysis
            self.auto_process_state = "AI_ANALYSIS"
            self.statusBar().showMessage("Auto process: Running AI analysis...")
            self.ai_analyze_changes()
        else:
            # Manual operation: restore button states
            self.view_changes_btn.setEnabled(True)
            self.ai_summary_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)
            self.statusBar().showMessage("Git change analysis completed")

    def on_git_analysis_error(self, error: str):
        """Git analysis error"""
        # Reset auto process state
        if self.auto_process_state != "IDLE":
            self.auto_process_state = "IDLE"
            self.statusBar().showMessage("Auto process failed: Git change analysis failed")

            # If in auto mode, print error and quit
            if self.auto_mode:
                print(f"Auto process failed: Git change analysis failed: {error}")
                QApplication.quit()
                return
        else:
            self.statusBar().showMessage("Git change analysis failed")

        # Restore button states
        self.view_changes_btn.setEnabled(True)
        self.ai_summary_btn.setEnabled(False)
        self.commit_btn.setEnabled(False)
        self.auto_process_btn.setEnabled(True)

        QMessageBox.critical(self, "Error", f"Git analysis failed: {error}")

    def ai_analyze_changes(self):
        """AI analyze changes"""
        if not self.git_analysis_result:
            QMessageBox.warning(self, "Warning", "Please view Git changes first")
            return

        # Check API configuration
        api_config = config_manager.get_api_config()
        if not api_config["api_key"]:
            QMessageBox.warning(self, "Warning", "Please configure API key in settings first")
            self.tab_widget.setCurrentIndex(1)  # Switch to settings tab
            return

        # Disable buttons, show progress
        self.ai_summary_btn.setEnabled(False)
        self.statusBar().showMessage("Running AI analysis...")

        # Start AI analysis worker thread
        self.ai_worker = AIAnalysisWorker(self.git_analysis_result, api_config)
        self.ai_worker.finished.connect(self.on_ai_analysis_finished)
        self.ai_worker.error.connect(self.on_ai_analysis_error)
        self.ai_worker.start()

    def on_ai_analysis_finished(self, result: str):
        """AI analysis completed"""
        self.ai_result_text.setPlainText(result)

        # Check if in auto process
        if self.auto_process_state == "AI_ANALYSIS":
            # Auto process: continue with Git commit
            self.auto_process_state = "COMMIT"
            self.statusBar().showMessage("Auto process: Executing Git commit...")
            self.git_commit()
        else:
            # Manual operation: restore button states
            self.ai_summary_btn.setEnabled(True)
            self.commit_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)
            self.statusBar().showMessage("AI analysis completed")

    def on_ai_analysis_error(self, error: str):
        """AI analysis error"""
        # Reset auto process state
        if self.auto_process_state != "IDLE":
            self.auto_process_state = "IDLE"
            self.statusBar().showMessage("Auto process failed: AI analysis failed")

            # If in auto mode, print error and quit
            if self.auto_mode:
                print(f"Auto process failed: AI analysis failed: {error}")
                QApplication.quit()
                return
        else:
            self.statusBar().showMessage("AI analysis failed")

        # Restore button states
        self.view_changes_btn.setEnabled(True)
        self.ai_summary_btn.setEnabled(True)
        self.commit_btn.setEnabled(False)
        self.auto_process_btn.setEnabled(True)

        QMessageBox.critical(self, "Error", f"AI analysis failed: {error}")

    def auto_process(self):
        """Auto process: automatically execute view changes → AI analysis → Git commit"""
        # Check repository path
        if not self.current_repo_path:
            QMessageBox.warning(self, "Warning", "Please select a Git repository path first")
            return

        if not is_git_repository(self.current_repo_path):
            QMessageBox.warning(self, "Warning", "The selected path is not a valid Git repository")
            return

        # Check API configuration
        api_config = config_manager.get_api_config()
        if not api_config["api_key"]:
            QMessageBox.warning(self, "Warning", "Please configure API key in settings first")
            self.tab_widget.setCurrentIndex(1)  # Switch to settings tab
            return

        # Start auto process
        self.auto_process_state = "GIT_ANALYSIS"
        self.statusBar().showMessage("Auto process: Analyzing Git changes...")

        # Disable all buttons
        self.view_changes_btn.setEnabled(False)
        self.ai_summary_btn.setEnabled(False)
        self.commit_btn.setEnabled(False)
        self.auto_process_btn.setEnabled(False)

        # Start Git analysis
        self.view_git_changes()

    def git_commit(self):
        """Execute Git commit"""
        if not self.current_repo_path:
            QMessageBox.warning(self, "Warning", "Please select a Git repository path first")
            return

        commit_message = self.ai_result_text.toPlainText().strip()
        if not commit_message:
            QMessageBox.warning(self, "Warning", "No commit message")
            return

        try:
            # Execute git add .
            safe_subprocess_run(
                ["git", "add", "."],
                cwd=self.current_repo_path,
                check=True
            )

            # Execute git commit
            safe_subprocess_run(
                ["git", "commit", "-m", commit_message],
                cwd=self.current_repo_path,
                check=True
            )

            # Check if in auto process
            if self.auto_process_state == "COMMIT":
                self.statusBar().showMessage("Auto process completed: Git commit successful")
                self.auto_process_state = "IDLE"

                # If in auto mode, close automatically after completion
                if self.auto_mode:
                    print("Auto process completed: Git commit successful")
                    QApplication.quit()
                    return
            else:
                self.statusBar().showMessage("Git commit successful")

            # Clear text boxes
            self.changes_text.clear()
            self.ai_result_text.clear()
            self.git_analysis_result = ""

            # Restore button states
            self.view_changes_btn.setEnabled(True)
            self.ai_summary_btn.setEnabled(False)
            self.commit_btn.setEnabled(False)
            self.auto_process_btn.setEnabled(True)

        except subprocess.CalledProcessError as e:
            # Reset auto process state
            if self.auto_process_state != "IDLE":
                self.auto_process_state = "IDLE"
                self.statusBar().showMessage("Auto process failed: Git commit failed")

                # If in auto mode, print error and quit
                if self.auto_mode:
                    print(f"Auto process failed: Git commit failed: {e}")
                    QApplication.quit()
                    return
            else:
                self.statusBar().showMessage("Git commit failed")

            # Restore button states
            self.view_changes_btn.setEnabled(True)
            self.ai_summary_btn.setEnabled(True)
            self.commit_btn.setEnabled(True)
            self.auto_process_btn.setEnabled(True)

            QMessageBox.critical(self, "Error", f"Git commit failed: {e}")
        

    def closeEvent(self, event):
        """Window close event"""
        # Save window size and position
        config_manager.set_ui_config(
            window_width=self.width(),
            window_height=self.height(),
            last_repo_path=self.current_repo_path
        )
        event.accept()


def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Git AI Commit - Intelligent Commit Assistant")
    parser.add_argument("repo_path", nargs="?", default="./",
                       help="Git repository path (default: current directory)")
    parser.add_argument("--auto", action="store_true",
                       help="Automatically execute one-click processing and close window")
    args = parser.parse_args()

    # Create QApplication with only program name to avoid Qt parsing our custom arguments
    app = QApplication([sys.argv[0]])
    app.setApplicationName("Git AI Commit")
    app.setApplicationVersion("1.0.0")

    # Create main window with parsed arguments
    window = GitAnalyzerGUI(repo_path=args.repo_path, auto_mode=args.auto)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
