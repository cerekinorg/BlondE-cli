"""
Unit tests for Memory Management System

Run with: pytest tests/test_memory.py -v
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import MemoryManager


class TestMemoryManager:
    """Tests for MemoryManager class"""
    
    def test_init_creates_directories(self, tmp_path, monkeypatch):
        """Should create .blonde/memory directory on init"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        
        assert (tmp_path / ".blonde" / "memory").exists()
    
    def test_new_session_structure(self, tmp_path, monkeypatch):
        """Should create proper session structure"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        
        assert "goals" in mem.session
        assert "completed_tasks" in mem.session
        assert "context_variables" in mem.session
        assert isinstance(mem.session["goals"], list)
    
    def test_add_task(self, tmp_path, monkeypatch):
        """Should add task to goals"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        mem.add_task("Build feature X", priority="high")
        
        assert len(mem.session["goals"]) == 1
        assert mem.session["goals"][0]["description"] == "Build feature X"
        assert mem.session["goals"][0]["priority"] == "high"
        assert mem.session["goals"][0]["status"] == "pending"
    
    def test_mark_task_complete(self, tmp_path, monkeypatch):
        """Should move task to completed_tasks"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        mem.add_task("Task 1")
        mem.add_task("Task 2")
        
        # Complete first task
        result = mem.mark_task_complete(0)
        
        assert result is True
        assert len(mem.session["goals"]) == 1
        assert len(mem.session["completed_tasks"]) == 1
        assert mem.session["completed_tasks"][0]["status"] == "completed"
        assert "completed_at" in mem.session["completed_tasks"][0]
    
    def test_mark_invalid_task(self, tmp_path, monkeypatch):
        """Should return False for invalid task index"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        result = mem.mark_task_complete(99)
        
        assert result is False
    
    def test_context_variables(self, tmp_path, monkeypatch):
        """Should store and retrieve context variables"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        
        mem.set_context_variable("project_path", "/home/user/project")
        mem.set_context_variable("language", "python")
        
        assert mem.get_context_variable("project_path") == "/home/user/project"
        assert mem.get_context_variable("language") == "python"
        assert mem.get_context_variable("nonexistent") is None
    
    def test_session_persistence(self, tmp_path, monkeypatch):
        """Should persist and load session from disk"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        # Create and save session
        mem1 = MemoryManager(user_id="test", enable_vector_store=False)
        mem1.add_task("Persistent task")
        mem1.set_context_variable("key", "value")
        mem1.save_session()
        
        # Load in new instance
        mem2 = MemoryManager(user_id="test", enable_vector_store=False)
        
        assert len(mem2.session["goals"]) == 1
        assert mem2.session["goals"][0]["description"] == "Persistent task"
        assert mem2.get_context_variable("key") == "value"
    
    def test_clear_session(self, tmp_path, monkeypatch):
        """Should clear session state"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        mem.add_task("Task 1")
        mem.set_context_variable("key", "value")
        
        mem.clear_session()
        
        assert len(mem.session["goals"]) == 0
        assert len(mem.session["context_variables"]) == 0
    
    def test_get_session_context(self, tmp_path, monkeypatch):
        """Should generate formatted context string"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=False)
        mem.add_task("Task 1", priority="high")
        mem.set_context_variable("project", "blonde-cli")
        
        context = mem.get_session_context()
        
        assert "Current Goals" in context
        assert "Task 1" in context
        assert "Context Variables" in context
        assert "blonde-cli" in context


class TestVectorStore:
    """Tests for ChromaDB integration (if available)"""
    
    @pytest.mark.skipif(
        "chromadb" not in sys.modules,
        reason="ChromaDB not installed"
    )
    def test_add_conversation(self, tmp_path, monkeypatch):
        """Should add conversation to vector store"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=True)
        
        if mem.vector_store_enabled:
            mem.add_conversation("Hello", "Hi there!")
            
            # Should have 1 memory
            assert mem.collection.count() > 0
    
    @pytest.mark.skipif(
        "chromadb" not in sys.modules,
        reason="ChromaDB not installed"
    )
    def test_retrieve_relevant_context(self, tmp_path, monkeypatch):
        """Should retrieve relevant conversations"""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        mem = MemoryManager(user_id="test", enable_vector_store=True)
        
        if mem.vector_store_enabled:
            mem.add_conversation("How do I use Python?", "Python is easy...")
            mem.add_conversation("What's the weather?", "It's sunny today")
            
            # Search for Python-related content
            results = mem.retrieve_relevant_context("Python programming", n_results=1)
            
            assert len(results) > 0
            assert "Python" in results[0]


# Fixtures
@pytest.fixture
def temp_memory_manager(tmp_path, monkeypatch):
    """Create temporary MemoryManager for testing"""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return MemoryManager(user_id="test", enable_vector_store=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
