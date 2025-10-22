"""
Unit tests for CLI functionality

Run with: pytest tests/test_cli.py -v
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import (
    scan_repo,
    extract_code,
    detect_language,
    render_code_blocks,
    load_adapter,
)


class TestScanRepo:
    """Tests for repository scanning"""
    
    def test_scan_empty_directory(self, tmp_path):
        """Should return empty dict for empty directory"""
        result = scan_repo(str(tmp_path))
        assert result == {}
    
    def test_scan_python_file(self, tmp_path):
        """Should extract functions and classes from Python file"""
        # Create test Python file
        py_file = tmp_path / "test.py"
        py_file.write_text("""
def hello():
    pass

class MyClass:
    def method(self):
        pass
""")
        
        result = scan_repo(str(tmp_path))
        
        assert "test.py" in result
        assert "hello" in result["test.py"]["functions"]
        assert "MyClass" in result["test.py"]["classes"]
    
    def test_scan_ignores_excluded_dirs(self, tmp_path):
        """Should skip __pycache__, .git, etc."""
        # Create excluded directories
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "test.pyc").touch()
        
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass")
        
        result = scan_repo(str(tmp_path))
        
        # Should only find main.py
        assert len(result) == 1
        assert "src/main.py" in result or "src\\main.py" in result  # Windows compatibility


class TestExtractCode:
    """Tests for code extraction from markdown"""
    
    def test_extract_single_code_block(self):
        """Should extract code from markdown fence"""
        markdown = """
Here's some code:
```python
def hello():
    print("world")
```
"""
        result = extract_code(markdown)
        assert "def hello():" in result
        assert "print(\"world\")" in result
    
    def test_extract_with_language_tag(self):
        """Should handle different language tags"""
        markdown = "```javascript\nconsole.log('test');\n```"
        result = extract_code(markdown)
        assert "console.log" in result
    
    def test_extract_no_code_blocks(self):
        """Should return original text if no code blocks"""
        text = "Just plain text"
        result = extract_code(text)
        assert result == text.strip()
    
    def test_extract_multiple_blocks_returns_first(self):
        """Should return first code block when multiple exist"""
        markdown = """
```python
first_block = 1
```

```python
second_block = 2
```
"""
        result = extract_code(markdown)
        assert "first_block" in result
        assert "second_block" not in result


class TestDetectLanguage:
    """Tests for language detection"""
    
    def test_detect_python_by_extension(self, tmp_path):
        """Should detect Python from .py extension"""
        py_file = tmp_path / "test.py"
        py_file.write_text("print('hello')")
        
        result = detect_language(str(py_file))
        assert result == "python"
    
    def test_detect_javascript_by_extension(self, tmp_path):
        """Should detect JavaScript from .js extension"""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello')")
        
        result = detect_language(str(js_file))
        assert result == "javascript"
    
    def test_detect_unknown_extension(self, tmp_path):
        """Should return unknown for unsupported extensions"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("plain text")
        
        result = detect_language(str(txt_file))
        assert result == "unknown"


class TestLoadAdapter:
    """Tests for model adapter loading"""
    
    @patch('cli.OpenRouterAdapter')
    def test_load_openrouter_adapter(self, mock_adapter):
        """Should load OpenRouter adapter by default"""
        load_adapter(model_name="openrouter", offline=False)
        mock_adapter.assert_called_once()
    
    @patch('cli.LocalAdapter')
    def test_load_local_adapter_when_offline(self, mock_adapter):
        """Should load local adapter when offline flag is set"""
        load_adapter(model_name="openrouter", offline=True)
        mock_adapter.assert_called_once()
    
    @patch('cli.OpenAIAdapter')
    def test_load_openai_adapter(self, mock_adapter):
        """Should load OpenAI adapter when specified"""
        load_adapter(model_name="openai", offline=False)
        mock_adapter.assert_called_once()


class TestRenderCodeBlocks:
    """Tests for code block rendering"""
    
    @patch('cli.console')
    def test_render_plain_text(self, mock_console):
        """Should render plain text without code blocks"""
        text = "Just some plain text"
        render_code_blocks(text)
        
        # Should call print with Markdown
        assert mock_console.print.called
    
    @patch('cli.console')
    def test_render_with_code_block(self, mock_console):
        """Should render code with syntax highlighting"""
        text = "```python\nprint('hello')\n```"
        render_code_blocks(text)
        
        # Should call print (exact assertion depends on Rich internals)
        assert mock_console.print.called


# Integration-style tests
class TestIntegration:
    """Integration tests for end-to-end workflows"""
    
    def test_scan_and_extract_workflow(self, tmp_path):
        """Should scan repo and extract metadata"""
        # Create mini project
        (tmp_path / "main.py").write_text("""
def main():
    print("Hello from BlondE")

if __name__ == "__main__":
    main()
""")
        
        (tmp_path / "utils.py").write_text("""
class Helper:
    def help(self):
        pass
""")
        
        # Scan
        result = scan_repo(str(tmp_path))
        
        # Verify structure
        assert len(result) == 2
        assert "main" in result["main.py"]["functions"]
        assert "Helper" in result["utils.py"]["classes"]


# Fixtures
@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing"""
    file = tmp_path / "sample.py"
    file.write_text("""
import os
from pathlib import Path

def calculate(x, y):
    return x + y

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
""")
    return file


@pytest.fixture
def mock_adapter():
    """Mock model adapter for testing"""
    adapter = Mock()
    adapter.chat = Mock(return_value="Mocked response")
    return adapter


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
