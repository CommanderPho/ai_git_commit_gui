#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility Functions Module
Provides utility functions for file handling, encoding detection, text processing, etc.
"""

import os
import locale
from pathlib import Path
from typing import Optional, List, Tuple
import re
import subprocess


def detect_file_encoding(file_path: str, fallback_encodings: List[str] = None) -> str:
    """
    Detect file encoding
    
    Args:
        file_path: File path
        fallback_encodings: Fallback encoding list
    
    Returns:
        Detected encoding name
    """
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    try:
        # Use chardet for detection
        with open(file_path, 'rb') as f:
            raw_data = f.read(8192)  # Read first 8KB for detection
            if raw_data:
                result = chardet.detect(raw_data)
                if result and result['encoding'] and result['confidence'] > 0.7:
                    return result['encoding']
    except (OSError, IOError):
        pass
    
    # Try fallback encodings
    for encoding in fallback_encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # Try reading part of the content
            return encoding
        except (UnicodeDecodeError, OSError, IOError):
            continue
    
    return 'utf-8'  # Default to utf-8


def is_text_file(file_path: str, max_check_bytes: int = 8192) -> bool:
    """
    Check if a file is a text file
    
    Args:
        file_path: File path
        max_check_bytes: Maximum bytes to check
    
    Returns:
        Whether it is a text file
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(max_check_bytes)
            if not chunk:
                return True  # Empty file is considered a text file
            
            # Check for null bytes (binary file characteristic)
            if b'\x00' in chunk:
                return False
            
            # Check proportion of non-printable characters
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            non_text_count = sum(1 for byte in chunk if byte not in text_chars)
            
            # If non-text characters exceed 30%, consider it a binary file
            if len(chunk) > 0 and (non_text_count / len(chunk)) > 0.30:
                return False
            
            return True
    
    except (OSError, IOError):
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB
    
    Args:
        file_path: File path
    
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except (OSError, IOError):
        return 0.0


def safe_read_file(file_path: str, encoding: str = None, max_size_mb: float = 10.0) -> Optional[str]:
    """
    Safely read file content
    
    Args:
        file_path: File path
        encoding: Specified encoding, auto-detect if None
        max_size_mb: Maximum file size limit (MB)
    
    Returns:
        File content, or None if reading fails
    """
    try:
        # Check file size
        if get_file_size_mb(file_path) > max_size_mb:
            return f"[File too large, exceeds {max_size_mb}MB limit]"
        
        # Check if it's a text file
        if not is_text_file(file_path):
            return "[Binary file, cannot display content]"
        
        # Detect encoding
        if encoding is None:
            encoding = detect_file_encoding(file_path)
        
        # Read file
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
    
    except (OSError, IOError, UnicodeDecodeError) as e:
        return f"[Failed to read file: {str(e)}]"


def truncate_text_balanced(text: str, max_lines: int, 
                          deleted_marker: str = '-', 
                          added_marker: str = '+') -> str:
    """
    Truncate text content in a balanced way, maintaining the ratio of deleted and added content
    
    Args:
        text: Original text
        max_lines: Maximum number of lines
        deleted_marker: Deleted line marker
        added_marker: Added line marker
    
    Returns:
        Truncated text
    """
    if not text:
        return text
    
    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text
    
    # Categorize lines
    deleted_lines = []
    added_lines = []
    context_lines = []
    
    for i, line in enumerate(lines):
        if line.startswith(deleted_marker) and not line.startswith('---'):
            deleted_lines.append((i, line))
        elif line.startswith(added_marker) and not line.startswith('+++'):
            added_lines.append((i, line))
        else:
            context_lines.append((i, line))
    
    # Keep all context lines
    result_lines = [line for _, line in context_lines]
    remaining_lines = max_lines - len(context_lines)
    
    if remaining_lines <= 0:
        return '\n'.join(result_lines[:max_lines])
    
    # Calculate allocation for deleted and added lines
    total_change_lines = len(deleted_lines) + len(added_lines)
    if total_change_lines == 0:
        return '\n'.join(result_lines)
    
    # Allocate remaining lines proportionally
    deleted_ratio = len(deleted_lines) / total_change_lines
    deleted_quota = int(remaining_lines * deleted_ratio)
    added_quota = remaining_lines - deleted_quota
    
    # Ensure at least one line each (if they exist)
    if len(deleted_lines) > 0 and deleted_quota == 0:
        deleted_quota = 1
        added_quota = remaining_lines - 1
    if len(added_lines) > 0 and added_quota == 0:
        added_quota = 1
        deleted_quota = remaining_lines - 1
    
    # Truncate deleted lines
    selected_deleted = deleted_lines[:deleted_quota]
    if len(deleted_lines) > deleted_quota:
        selected_deleted.append((-1, f"... ({len(deleted_lines) - deleted_quota} deleted lines omitted)"))
    
    # Truncate added lines
    selected_added = added_lines[:added_quota]
    if len(added_lines) > added_quota:
        selected_added.append((-1, f"... ({len(added_lines) - added_quota} added lines omitted)"))
    
    # Merge all lines and sort by original order
    all_selected = context_lines + selected_deleted + selected_added
    all_selected.sort(key=lambda x: x[0] if x[0] != -1 else float('inf'))
    
    return '\n'.join(line for _, line in all_selected)


def format_file_status(status: str) -> str:
    """
    Format file status display
    
    Args:
        status: Git file status
    
    Returns:
        Formatted status text
    """
    status_map = {
        'modified': 'Modified',
        'added': 'Added',
        'deleted': 'Deleted',
        'untracked': 'Untracked',
        'renamed': 'Renamed',
        'copied': 'Copied',
        'updated': 'Updated',
        'unknown': 'Unknown'
    }
    return status_map.get(status.lower(), status)


def clean_diff_output(diff_text: str) -> str:
    """
    Clean diff output, remove unnecessary information
    
    Args:
        diff_text: Original diff text
    
    Returns:
        Cleaned diff text
    """
    if not diff_text:
        return diff_text
    
    lines = diff_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip diff header info (but keep file path info)
        if line.startswith('diff --git'):
            continue
        elif line.startswith('index '):
            continue
        elif line.startswith('@@') and line.endswith('@@'):
            # Keep line number info, but simplify display
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def extract_file_extension(file_path: str) -> str:
    """
    Extract file extension
    
    Args:
        file_path: File path
    
    Returns:
        File extension (lowercase, including dot)
    """
    return Path(file_path).suffix.lower()


def safe_subprocess_run(
    cmd: List[str],
    cwd: Optional[str] = None,
    capture_output: bool = True,
    check: bool = False,
    timeout: Optional[int] = None,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Safe subprocess.run wrapper function, handles encoding issues

    Args:
        cmd: Command list to execute
        cwd: Working directory
        capture_output: Whether to capture output
        check: Whether to check return code
        timeout: Timeout in seconds
        **kwargs: Other subprocess.run parameters

    Returns:
        subprocess.CompletedProcess object

    Raises:
        subprocess.CalledProcessError: When check=True and command fails
        subprocess.TimeoutExpired: When timeout occurs
    """
    # Remove text parameter, we will handle encoding manually
    kwargs.pop('text', None)
    kwargs.pop('encoding', None)

    # List of encodings to try
    encodings_to_try = ['utf-8']

    # Add system-appropriate encodings
    try:
        system_encoding = locale.getpreferredencoding()
        if system_encoding and system_encoding.lower() not in ['utf-8', 'utf8']:
            encodings_to_try.append(system_encoding)
    except:
        pass

    # Add common encodings for Windows
    if os.name == 'nt':
        encodings_to_try.extend(['gbk', 'gb2312', 'cp936'])

    # Add fallback encoding
    encodings_to_try.append('latin-1')

    # Execute command
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture_output,
        check=False,  # We'll check manually later
        timeout=timeout,
        **kwargs
    )

    # Handle output encoding
    if capture_output:
        stdout_decoded = None
        stderr_decoded = None
        encoding_used = None

        # Try decoding stdout
        if result.stdout:
            for encoding in encodings_to_try:
                try:
                    stdout_decoded = result.stdout.decode(encoding)
                    encoding_used = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if stdout_decoded is None:
                # If all encodings fail, use errors='replace'
                stdout_decoded = result.stdout.decode('utf-8', errors='replace')
                encoding_used = 'utf-8 (with errors replaced)'

        # Try decoding stderr
        if result.stderr:
            for encoding in encodings_to_try:
                try:
                    stderr_decoded = result.stderr.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if stderr_decoded is None:
                stderr_decoded = result.stderr.decode('utf-8', errors='replace')

        # Create new result object
        result = subprocess.CompletedProcess(
            args=result.args,
            returncode=result.returncode,
            stdout=stdout_decoded,
            stderr=stderr_decoded
        )

        # If debugging is enabled, print encoding info
        if encoding_used and os.environ.get('GIT_AI_COMMIT_DEBUG'):
            print(f"DEBUG: Using encoding {encoding_used} to decode command output: {' '.join(cmd)}")

    # Check return code
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            cmd,
            output=result.stdout,
            stderr=result.stderr
        )

    return result


def is_git_repository(path: str) -> bool:
    """
    Check if path is a Git repository

    Args:
        path: Path to check

    Returns:
        Whether it is a Git repository
    """
    try:
        result = safe_subprocess_run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=path,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def normalize_path(path: str) -> str:
    """
    Normalize path
    
    Args:
        path: Original path
    
    Returns:
        Normalized path
    """
    return str(Path(path).resolve())


def split_long_lines(text: str, max_line_length: int = 120) -> str:
    """
    Split overly long lines
    
    Args:
        text: Original text
        max_line_length: Maximum line length
    
    Returns:
        Processed text
    """
    if not text:
        return text
    
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        if len(line) <= max_line_length:
            result_lines.append(line)
        else:
            # For overly long lines, try to split at appropriate positions
            while len(line) > max_line_length:
                # Find suitable split point
                split_pos = max_line_length
                for i in range(max_line_length - 20, max_line_length):
                    if i < len(line) and line[i] in ' \t,;':
                        split_pos = i + 1
                        break
                
                result_lines.append(line[:split_pos])
                line = '  ' + line[split_pos:]  # Indent continuation
            
            if line.strip():  # Add remaining part
                result_lines.append(line)
    
    return '\n'.join(result_lines)


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Test current directory
    current_dir = "."
    print(f"Is current directory a Git repository: {is_git_repository(current_dir)}")
    
    # Test path normalization
    test_path = "./test/../config.py"
    print(f"Normalized path: {normalize_path(test_path)}")
    
    # Test text truncation
    test_text = "\n".join([f"- Deleted line {i}" for i in range(10)] + 
                         [f"+ Added line {i}" for i in range(15)])
    truncated = truncate_text_balanced(test_text, 10)
    print(f"Lines after truncation: {len(truncated.split(chr(10)))}")
    
    print("Utility functions test completed")
