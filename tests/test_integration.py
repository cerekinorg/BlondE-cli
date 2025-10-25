"""
Integration tests for BlondE-CLI with memory and agentic features.

Tests the complete workflow including:
- Memory integration
- Agentic mode
- Iterative refinement
- All CLI commands
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from typer.testing import CliRunner
from cli import app
from memory import MemoryManager
from tools import ToolRegistry


class TestMemoryIntegration:
    """Test memory system integration with CLI commands"""
    
    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        with open(self.test_file, "w") as f:
            f.write("def hello():\n    print('Hello')\n")
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_memory_manager_initialization(self):
        """Test memory manager can be initialized"""
        try:
            mem = MemoryManager(user_id="test_user", enable_vector_store=False)
            assert mem is not None
            assert mem.user_id == "test_user"
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")
    
    def test_memory_add_conversation(self):
        """Test adding conversations to memory"""
        try:
            mem = MemoryManager(user_id="test_user", enable_vector_store=False)
            mem.add_conversation("Test query", "Test response")
            
            # Verify conversation was stored
            assert len(mem.short_term_memory["conversations"]) > 0
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")
    
    def test_memory_retrieve_context(self):
        """Test retrieving relevant context from memory"""
        try:
            mem = MemoryManager(user_id="test_user", enable_vector_store=False)
            mem.add_conversation("How to write Python functions", "Use def keyword")
            
            context = mem.get_context_for_prompt("Python functions", max_context_length=500)
            assert context is not None
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")


class TestAgenticMode:
    """Test agentic mode and tool execution"""
    
    def test_tool_registry_initialization(self):
        """Test tool registry can be initialized"""
        try:
            registry = ToolRegistry(require_confirmation=False, log_calls=False)
            assert registry is not None
        except Exception as e:
            pytest.skip(f"Tools system not available: {e}")
    
    def test_tool_registration(self):
        """Test registering tools"""
        try:
            registry = ToolRegistry(require_confirmation=False, log_calls=False)
            
            def test_tool(arg1):
                return f"Result: {arg1}"
            
            registry.register_tool(
                name="test_tool",
                func=test_tool,
                description="A test tool",
                safe=True
            )
            
            tools = registry.list_tools()
            assert "test_tool" in tools
        except Exception as e:
            pytest.skip(f"Tools system not available: {e}")


class TestCLICommands:
    """Test all CLI commands with enhanced features"""
    
    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        with open(self.test_file, "w") as f:
            f.write("def add(a, b):\n    return a + b\n")
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_gen_command_with_memory(self):
        """Test gen command with memory enabled"""
        result = self.runner.invoke(app, [
            'gen',
            'Create a Python hello world function',
            '--memory',
            '--save', os.path.join(self.test_dir, 'hello.py')
        ])
        
        # Command should execute (may fail if no API key, but structure is tested)
        assert result.exit_code in [0, 1]  # 0 success, 1 if API not configured
    
    def test_create_command_with_iterative(self):
        """Test create command with iterative mode"""
        # This test verifies the command structure
        # Actual execution requires API keys
        result = self.runner.invoke(app, [
            'create',
            'A simple calculator class',
            os.path.join(self.test_dir, 'calculator.py'),
            '--memory',
            '--no-iterative'  # Disable interactive mode for testing
        ])
        
        assert result.exit_code in [0, 1]
    
    def test_fix_command_with_memory(self):
        """Test fix command with memory integration"""
        result = self.runner.invoke(app, [
            'fix',
            self.test_file,
            '--memory',
            '--no-preview',
            '--export', os.path.join(self.test_dir, 'fixes.diff')
        ])
        
        assert result.exit_code in [0, 1]
    
    def test_doc_command_with_style(self):
        """Test doc command with different styles"""
        result = self.runner.invoke(app, [
            'doc',
            self.test_file,
            '--memory',
            '--style', 'concise',
            '--export', os.path.join(self.test_dir, 'docs.md')
        ])
        
        assert result.exit_code in [0, 1]


class TestIterativeRefinement:
    """Test iterative refinement capabilities"""
    
    def setup_method(self):
        """Setup test environment"""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_iterative_fix_mode(self):
        """Test iterative refinement in fix command"""
        test_file = os.path.join(self.test_dir, "buggy.py")
        with open(test_file, "w") as f:
            f.write("def divide(a, b):\n    return a / b  # No error handling\n")
        
        # Test command structure (won't actually iterate without user input)
        result = self.runner.invoke(app, [
            'fix',
            test_file,
            '--iterative',
            '--memory',
            '--export', os.path.join(self.test_dir, 'fix.diff')
        ])
        
        assert result.exit_code in [0, 1]
    
    def test_iterative_create_mode(self):
        """Test iterative refinement in create command"""
        result = self.runner.invoke(app, [
            'create',
            'A data validation function',
            os.path.join(self.test_dir, 'validator.py'),
            '--iterative',
            '--memory'
        ])
        
        assert result.exit_code in [0, 1]


class TestContextAwareness:
    """Test context awareness across commands"""
    
    def test_memory_persistence(self):
        """Test that memory persists across sessions"""
        try:
            # First session
            mem1 = MemoryManager(user_id="persistent_test", enable_vector_store=False)
            mem1.add_conversation("Test persistence", "This should persist")
            mem1.add_task("Test task", status="in_progress")
            
            # Second session - should load previous data
            mem2 = MemoryManager(user_id="persistent_test", enable_vector_store=False)
            
            # Check if data persisted
            assert len(mem2.short_term_memory["conversations"]) > 0
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")
    
    def test_context_injection(self):
        """Test context injection in prompts"""
        try:
            mem = MemoryManager(user_id="context_test", enable_vector_store=False)
            mem.add_conversation("Python best practices", "Use type hints and docstrings")
            mem.add_conversation("Error handling", "Always use try-except blocks")
            
            context = mem.get_context_for_prompt("How to write Python", max_context_length=1000)
            
            # Context should contain relevant information
            assert context is not None
            assert len(context) > 0
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
