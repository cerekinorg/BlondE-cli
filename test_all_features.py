#!/usr/bin/env python3
"""
Comprehensive test suite for BlondE-CLI
Tests all commands, memory system, and agentic tools
"""

import sys
import os
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_imports():
    """Test all critical imports"""
    print(f"\n{BLUE}Testing imports...{RESET}")
    try:
        import typer
        print(f"{GREEN}✓ typer{RESET}")
        
        import rich
        print(f"{GREEN}✓ rich{RESET}")
        
        from memory import MemoryManager
        print(f"{GREEN}✓ memory.MemoryManager{RESET}")
        
        from tools import ToolRegistry
        print(f"{GREEN}✓ tools.ToolRegistry{RESET}")
        
        import chromadb
        print(f"{GREEN}✓ chromadb{RESET}")
        
        from cli import load_adapter, detect_language, scan_repo
        print(f"{GREEN}✓ cli functions{RESET}")
        
        return True
    except Exception as e:
        print(f"{RED}✗ Import failed: {e}{RESET}")
        return False

def test_memory_system():
    """Test memory management system"""
    print(f"\n{BLUE}Testing Memory System...{RESET}")
    try:
        from memory import MemoryManager
        
        # Create memory manager
        mem = MemoryManager(user_id="test_user", enable_vector_store=True)
        print(f"{GREEN}✓ MemoryManager initialized{RESET}")
        
        # Test adding conversation
        mem.add_conversation("Test question", "Test answer")
        print(f"{GREEN}✓ add_conversation{RESET}")
        
        # Test retrieving context
        context = mem.retrieve_relevant_context("test", n_results=1)
        print(f"{GREEN}✓ retrieve_relevant_context (found {len(context)} results){RESET}")
        
        # Test get_context_for_prompt
        ctx = mem.get_context_for_prompt("test query", max_context_length=500)
        print(f"{GREEN}✓ get_context_for_prompt (length: {len(ctx)}){RESET}")
        
        # Test task management
        mem.add_task("Test task", priority="high")
        print(f"{GREEN}✓ add_task{RESET}")
        
        # Test context variables
        mem.set_context_variable("test_var", "test_value")
        value = mem.get_context_variable("test_var")
        assert value == "test_value"
        print(f"{GREEN}✓ context variables{RESET}")
        
        # Clean up
        mem.clear_all_memory()
        print(f"{GREEN}✓ clear_all_memory{RESET}")
        
        return True
    except Exception as e:
        print(f"{RED}✗ Memory test failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

def test_tools_system():
    """Test agentic tools system"""
    print(f"\n{BLUE}Testing Tools System...{RESET}")
    try:
        from tools import ToolRegistry
        
        # Create registry
        registry = ToolRegistry(require_confirmation=False, log_calls=False)
        print(f"{GREEN}✓ ToolRegistry initialized{RESET}")
        
        # Test read_file
        result = registry.call('read_file', path='requirements.txt')
        assert 'SUCCESS' in result
        print(f"{GREEN}✓ read_file tool{RESET}")
        
        # Test list_directory
        result = registry.call('list_directory', path='.')
        assert 'SUCCESS' in result
        print(f"{GREEN}✓ list_directory tool{RESET}")
        
        # Test count_lines
        result = registry.call('count_lines', path='cli.py')
        assert 'SUCCESS' in result
        print(f"{GREEN}✓ count_lines tool{RESET}")
        
        # Test git_status
        result = registry.call('git_status')
        assert 'SUCCESS' in result or 'ERROR' in result
        print(f"{GREEN}✓ git_status tool{RESET}")
        
        # Test list_tools
        tools_list = registry.list_tools()
        print(f"{GREEN}✓ list_tools{RESET}")
        
        return True
    except Exception as e:
        print(f"{RED}✗ Tools test failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_helpers():
    """Test CLI helper functions"""
    print(f"\n{BLUE}Testing CLI Helper Functions...{RESET}")
    try:
        from cli import detect_language, scan_repo, extract_code
        
        # Test detect_language
        lang = detect_language("test.py")
        assert lang == "python"
        print(f"{GREEN}✓ detect_language{RESET}")
        
        # Test scan_repo
        repo_map = scan_repo(".")
        assert isinstance(repo_map, dict)
        assert len(repo_map) > 0
        print(f"{GREEN}✓ scan_repo (found {len(repo_map)} files){RESET}")
        
        # Test extract_code
        code_block = "```python\nprint('hello')\n```"
        extracted = extract_code(code_block)
        assert "print" in extracted
        print(f"{GREEN}✓ extract_code{RESET}")
        
        return True
    except Exception as e:
        print(f"{RED}✗ CLI helpers test failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

def test_model_adapters():
    """Test model adapter loading"""
    print(f"\n{BLUE}Testing Model Adapters...{RESET}")
    try:
        from cli import load_adapter
        
        # Note: We won't actually make API calls, just test imports
        print(f"{YELLOW}⚠ Skipping actual API calls (would require API keys){RESET}")
        
        # Check if model files exist
        from pathlib import Path
        models_dir = Path("models")
        
        if (models_dir / "openrouter.py").exists():
            print(f"{GREEN}✓ models/openrouter.py exists{RESET}")
        
        if (models_dir / "openai.py").exists():
            print(f"{GREEN}✓ models/openai.py exists{RESET}")
        
        if (models_dir / "local.py").exists():
            print(f"{GREEN}✓ models/local.py exists{RESET}")
        
        if (models_dir / "hf.py").exists():
            print(f"{GREEN}✓ models/hf.py exists{RESET}")
        
        return True
    except Exception as e:
        print(f"{RED}✗ Model adapters test failed: {e}{RESET}")
        return False

def test_cli_commands_exist():
    """Test that all CLI commands are properly registered"""
    print(f"\n{BLUE}Testing CLI Commands Registration...{RESET}")
    try:
        from cli import app
        
        # Get command names - typer stores commands differently
        commands = []
        if hasattr(app, 'registered_commands'):
            for command in app.registered_commands:
                if hasattr(command, 'name'):
                    commands.append(command.name)
                elif hasattr(command, 'callback') and hasattr(command.callback, '__name__'):
                    commands.append(command.callback.__name__)
        
        # Alternative: check by function names directly
        import cli
        expected_functions = ['set_key', 'chat', 'gen', 'create', 'fix', 'doc']
        
        for func_name in expected_functions:
            if hasattr(cli, func_name):
                print(f"{GREEN}✓ Command '{func_name}' exists{RESET}")
            else:
                print(f"{RED}✗ Command '{func_name}' NOT found{RESET}")
                return False
        
        return True
    except Exception as e:
        print(f"{RED}✗ CLI commands test failed: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}BlondE-CLI Comprehensive Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Memory System", test_memory_system()))
    results.append(("Tools System", test_tools_system()))
    results.append(("CLI Helpers", test_cli_helpers()))
    results.append(("Model Adapters", test_model_adapters()))
    results.append(("CLI Commands", test_cli_commands_exist()))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✓ All tests passed! BlondE-CLI is ready!{RESET}")
        return 0
    else:
        print(f"\n{RED}✗ Some tests failed. Please review the errors above.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
