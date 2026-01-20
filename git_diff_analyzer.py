#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Diff Analyzer
Reads uncommitted file changes from local Git repository and formats them for AI summarization
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
from utils import safe_subprocess_run


class GitDiffAnalyzer:
    """Git Diff Analyzer class"""
    
    def __init__(self, repo_path: str, max_lines: int = 200):
        """
        Initialize analyzer
        
        Args:
            repo_path: Git repository path
            max_lines: Maximum line display limit
        """
        self.repo_path = Path(repo_path).resolve()
        self.max_lines = max_lines
        self.binary_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.dll', '.so',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv'
        }
    
    def validate_repo(self) -> bool:
        """Validate if it's a valid Git repository"""
        try:
            result = safe_subprocess_run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def is_binary_file(self, file_path: str) -> bool:
        """Check if a file is binary"""
        # Check by extension
        ext = Path(file_path).suffix.lower()
        if ext in self.binary_extensions:
            return True
        
        # Check via Git
        try:
            result = safe_subprocess_run(
                ['git', 'diff', '--numstat', 'HEAD', '--', file_path],
                cwd=self.repo_path,
                capture_output=True
            )
            if result.returncode == 0 and result.stdout.strip():
                # Git numstat output format: additions deletions filename
                # Binary files show as: - - filename
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2 and parts[0] == '-' and parts[1] == '-':
                    return True
        except subprocess.CalledProcessError:
            pass
        
        return False
    
    def get_unstaged_files(self) -> List[Dict[str, str]]:
        """Get list of unstaged files"""
        try:
            # Get working tree status
            result = safe_subprocess_run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                status = line[:2]
                # Git status format: XY filename, where XY is two-character status followed by a space
                file_path = line[2:].strip() if len(line) > 2 else line.strip()
                
                # Parse file status
                file_status = 'unknown'
                if status[0] == 'M' or status[1] == 'M':
                    file_status = 'modified'
                elif status[0] == 'A' or status[1] == 'A':
                    file_status = 'added'
                elif status[0] == 'D' or status[1] == 'D':
                    file_status = 'deleted'
                elif status[0] == '?' and status[1] == '?':
                    file_status = 'untracked'
                elif status[0] == 'R':
                    file_status = 'renamed'
                
                files.append({
                    'path': file_path,
                    'status': file_status,
                    'is_binary': self.is_binary_file(file_path) if file_status != 'deleted' else False
                })
            
            return files
        
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get file status: {e}")
    
    def get_file_diff(self, file_path: str, file_status: str) -> Optional[str]:
        """Get file diff content"""
        try:
            if file_status == 'untracked':
                # New file, show all content
                full_path = self.repo_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        return f"+++ New file content +++\n{content}"
                    except UnicodeDecodeError:
                        return "+++ New file (binary or encoding issue) +++"
                return None
            
            elif file_status == 'deleted':
                # Deleted file, show original content
                result = safe_subprocess_run(
                    ['git', 'show', f'HEAD:{file_path}'],
                    cwd=self.repo_path,
                    capture_output=True
                )
                if result.returncode == 0:
                    return f"--- Deleted file content ---\n{result.stdout}"
                return "--- Deleted file (unable to get original content) ---"
            
            else:
                # Modified file, get diff
                result = safe_subprocess_run(
                    ['git', 'diff', 'HEAD', '--', file_path],
                    cwd=self.repo_path,
                    capture_output=True
                )

                if result.returncode == 0 and result.stdout:
                    return result.stdout
                
                # If no diff with HEAD, might be staged changes
                result = safe_subprocess_run(
                    ['git', 'diff', '--', file_path],
                    cwd=self.repo_path,
                    capture_output=True
                )

                if result.returncode == 0:
                    return result.stdout
        
        except subprocess.CalledProcessError:
            pass
        
        return None

    def clean_diff_content(self, diff_content: str) -> str:
        """Clean diff content, remove empty lines"""
        if not diff_content:
            return diff_content

        lines = diff_content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Skip completely blank lines
            if line.strip() == '':
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def truncate_diff_content(self, diff_content: str) -> str:
        """Truncate diff content, maintaining balance between deleted and added content"""
        if not diff_content:
            return diff_content
        
        lines = diff_content.split('\n')
        if len(lines) <= self.max_lines:
            return diff_content
        
        # Separate deleted and added lines
        deleted_lines = []
        added_lines = []
        context_lines = []
        
        for line in lines:
            if line.startswith('-') and not line.startswith('---'):
                deleted_lines.append(line)
            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line)
            else:
                context_lines.append(line)
        
        # Calculate available lines (minus context lines)
        available_lines = self.max_lines - len(context_lines)
        if available_lines <= 0:
            return '\n'.join(context_lines[:self.max_lines])
        
        # Deleted and added lines each get half
        half_lines = available_lines // 2
        
        truncated_deleted = deleted_lines[:half_lines]
        truncated_added = added_lines[:half_lines]
        
        # Recombine
        result_lines = context_lines.copy()
        
        # Insert truncated deleted lines
        if truncated_deleted:
            if len(deleted_lines) > half_lines:
                truncated_deleted.append(f"... ({len(deleted_lines) - half_lines} deleted lines omitted)")
            result_lines.extend(truncated_deleted)
        
        # Insert truncated added lines
        if truncated_added:
            if len(added_lines) > half_lines:
                truncated_added.append(f"... ({len(added_lines) - half_lines} added lines omitted)")
            result_lines.extend(truncated_added)
        
        return '\n'.join(result_lines)
    
    def analyze_repository(self) -> Dict:
        """Analyze repository and return formatted results"""
        if not self.validate_repo():
            raise Exception(f"Path '{self.repo_path}' is not a valid Git repository")
        
        files = self.get_unstaged_files()
        
        # Statistics
        stats = {
            'modified': 0,
            'added': 0,
            'deleted': 0,
            'untracked': 0,
            'renamed': 0
        }
        
        file_details = []
        
        for file_info in files:
            file_path = file_info['path']
            file_status = file_info['status']
            is_binary = file_info['is_binary']
            
            stats[file_status] = stats.get(file_status, 0) + 1
            
            detail = {
                'path': file_path,
                'status': file_status,
                'is_binary': is_binary,
                'diff_content': None
            }
            
            if is_binary:
                detail['diff_content'] = f"Binary file: {file_path}"
            else:
                diff_content = self.get_file_diff(file_path, file_status)
                if diff_content:
                    detail['diff_content'] = self.truncate_diff_content(diff_content)
            
            file_details.append(detail)
        
        return {
            'repo_path': str(self.repo_path),
            'stats': stats,
            'files': file_details,
            'total_files': len(files)
        }
    
    def format_output(self, analysis_result: Dict) -> str:
        """Format output results"""
        output = []
        
        # Repository info
        output.append(f"Repository path: {analysis_result['repo_path']}")
        output.append("")
        
        # Change summary
        stats = analysis_result['stats']
        summary_parts = []
        if stats.get('modified', 0) > 0:
            summary_parts.append(f"{stats['modified']} files modified")
        if stats.get('added', 0) > 0:
            summary_parts.append(f"{stats['added']} files added")
        if stats.get('untracked', 0) > 0:
            summary_parts.append(f"{stats['untracked']} files untracked")
        if stats.get('deleted', 0) > 0:
            summary_parts.append(f"{stats['deleted']} files deleted")
        if stats.get('renamed', 0) > 0:
            summary_parts.append(f"{stats['renamed']} files renamed")
        
        if summary_parts:
            output.append(f"Change summary: {', '.join(summary_parts)}")
        else:
            output.append("Change summary: No uncommitted changes")
        
        output.append("")
        output.append("=" * 50)
        output.append("File change details")
        output.append("=" * 50)
        
        # File details
        for file_detail in analysis_result['files']:
            output.append("")
            status_map = {
                'modified': 'Modified',
                'added': 'Added',
                'deleted': 'Deleted',
                'untracked': 'Untracked',
                'renamed': 'Renamed'
            }
            status_text = status_map.get(file_detail['status'], file_detail['status'])
            output.append(f"File: {file_detail['path']} ({status_text})")
            
            if file_detail['is_binary']:
                output.append("Type: Binary file")
            elif file_detail['diff_content']:
                output.append("Changes:")
                output.append("-" * 30)
                # Clean empty lines before displaying
                cleaned_content = self.clean_diff_content(file_detail['diff_content'])
                output.append(cleaned_content)
                output.append("-" * 30)
        
        return '\n'.join(output)


if __name__ == "__main__":
    # Command line test
    if len(sys.argv) < 2:
        print("Usage: python git_diff_analyzer.py <repository_path> [max_lines]")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    max_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    
    try:
        analyzer = GitDiffAnalyzer(repo_path, max_lines)
        result = analyzer.analyze_repository()
        formatted_output = analyzer.format_output(result)
        print(formatted_output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
