#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Interface Module
Provides interaction functionality with the GLM-4-Flash AI model
"""

import json
import requests
from typing import Optional, Dict, Any
import time
import os


class GLMInterface:
    """GLM-4-Flash AI Interface class"""
    
    def __init__(self, api_key, base_url: str = "https://api.kenhong.com/v1", model: str = "glm-4-flash"):
        """
        Initialize AI interface

        Args:
            api_key: API key
            base_url: API base URL
            model: AI model name
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = 30
        self.max_retries = 3
    
    def call_ai(self, prompt: str, content: str, 
                temperature: float = 0.7, 
                max_tokens: int = 2000) -> Optional[str]:
        """
        Call AI interface for text processing
        
        Args:
            prompt: Prompt text
            content: Content to process
            temperature: Temperature parameter, controls output randomness
            max_tokens: Maximum output token count
            
        Returns:
            AI response text, or None if failed
        """
        try:
            # Build request message
            messages = [
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user", 
                    "content": content
                }
            ]
            
            # Build request data
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Set request headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Send request (with retry mechanism)
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=request_data,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Check response format
                        if "choices" in result and len(result["choices"]) > 0:
                            return result["choices"][0]["message"]["content"].strip()
                        else:
                            print(f"Warning: Abnormal response format: {result}")
                            return None
                    
                    elif response.status_code == 429:  # Rate limit
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"Rate limited, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    
                    else:
                        print(f"API request failed: {response.status_code}")
                        print(f"Response content: {response.text}")
                        return None
                
                except requests.exceptions.Timeout:
                    print(f"Request timeout, attempt {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        print("Request timeout, maximum retries reached")
                        return None
                
                except requests.exceptions.RequestException as e:
                    print(f"Network request error: {e}")
                    return None
            
            return None
            
        except Exception as e:
            print(f"AI interface call failed: {e}")
            return None
    
   
    def generate_commit_message(self, git_analysis: str, custom_prompt: str = None) -> Optional[str]:
        """
        Generate Git commit message

        Args:
            git_analysis: Git analysis result
            custom_prompt: Custom prompt, uses default prompt if None

        Returns:
            Suggested commit message
        """
        if custom_prompt:
            prompt = custom_prompt
        else:
            # Default prompt
            prompt = """You are a professional software engineer.
Carefully review the provided context and code changes that are about to be committed to the Git repository.
Generate a commit message for these changes.
The commit message must use imperative mood (e.g. "fix" not "fixed").
The commit message format should be as follows:
Use the following prefixes:
- **fix**
- **feat**
- **build**
- **chore**
- **ci**
- **docs**
- **style**
- **refactor**
- **perf**
- **test**
Just reply with the commit message itself, do not include quotes, comments, or additional explanations!
Examples:
`fix null pointer exception during user login`
`feat add user registration endpoint`
`refactor optimize order processing logic`"""
        return self.call_ai(prompt, git_analysis, temperature=0.3)
    

def create_ai_interface(api_key, base_url: str = "https://api.kenhong.com/v1", model: str = "glm-4-flash") -> GLMInterface:
    """
    Create AI interface instance

    Args:
        api_key: API key
        base_url: API base URL
        model: AI model name

    Returns:
        GLMInterface instance
    """
    return GLMInterface(api_key, base_url, model)


def test_ai_interface():
    """Test AI interface functionality"""
    # Actual API key is required here
    api_key = "your-api-key-here"
    
    if api_key == "your-api-key-here":
        print("Please set a valid API key for testing")
        return
    
    ai = create_ai_interface(api_key)
    
    # Test basic call
    test_content = """
    File: main.py (Modified)
    Changes:
    + def new_function():
    +     return "Hello World"
    - def old_function():
    -     return "Goodbye"
    """
    
    print("Testing AI summary functionality...")
    summary = ai.summarize_git_changes(test_content)
    if summary:
        print("AI summary result:")
        print(summary)
    else:
        print("AI summary failed")
    
    print("\nTesting commit message generation...")
    commit_msg = ai.generate_commit_message(test_content)
    if commit_msg:
        print("Suggested commit message:")
        print(commit_msg)
    else:
        print("Commit message generation failed")


def demo_commit_message():
    """Demo commit message generation functionality"""
    print("\n\n📝 Commit Message Generation Demo")
    print("=" * 50)
    sample_changes = """
File: src/auth.py (Modified)
- Fixed user login verification bug
- Added password strength check
- Optimized error handling logic
File: tests/test_auth.py (New)
- Added unit tests for user authentication
- Covered various edge cases
"""
    api_key = os.getenv("GLM_API_KEY", "")
    if not api_key:
        print("⚠️  API key required, skipping demo")
        return
    try:
        print("🔄 Generating commit message...")
        ai = GLMInterface(api_key)
        commit_msg = ai.generate_commit_message(sample_changes)
        if commit_msg:
            print("\n✅ Suggested commit message:")
            print("-" * 30)
            print(commit_msg)
            print("-" * 30)
        else:
            print("\n❌ Commit message generation failed")
    except Exception as e:
        print(f"\n❌ Commit message generation failed: {e}")



if __name__ == "__main__":
    demo_commit_message()
