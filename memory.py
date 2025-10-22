"""
Memory Management System for BlondE-CLI

Provides:
1. Short-term memory (session state, goals, tasks)
2. Long-term memory (semantic search via ChromaDB)
3. Context injection for LLM prompts
4. Task tracking and goal persistence

Usage:
    mem = MemoryManager(user_id="default")
    mem.add_conversation(user_msg, ai_response)
    relevant = mem.retrieve_relevant_context(query, n_results=5)
    mem.add_task("Implement user authentication")
    mem.show_session_state()
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
logger = logging.getLogger("blonde")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not installed. Long-term memory disabled. Install with: pip install chromadb")


class MemoryManager:
    """Manages short-term and long-term memory for context-aware AI"""
    
    def __init__(self, user_id: str = "default", enable_vector_store: bool = True):
        """
        Initialize memory manager.
        
        Args:
            user_id: Unique identifier for user session
            enable_vector_store: Use ChromaDB for semantic search (requires chromadb package)
        """
        self.user_id = user_id
        self.cache_dir = Path.home() / ".blonde" / "memory"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Vector store for long-term semantic memory
        self.vector_store_enabled = enable_vector_store and CHROMADB_AVAILABLE
        if self.vector_store_enabled:
            try:
                self.chroma = chromadb.PersistentClient(
                    path=str(self.cache_dir / "chroma"),
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.chroma.get_or_create_collection(
                    name=f"conversations_{user_id}",
                    metadata={"description": "Conversation history with semantic search"}
                )
                logger.info(f"Vector store initialized with {self.collection.count()} memories")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB: {e}")
                self.vector_store_enabled = False
        
        # JSON for short-term/session memory
        self.session_file = self.cache_dir / f"session_{user_id}.json"
        self.session = self.load_session()
    
    def load_session(self) -> Dict:
        """Load active session state (goals, tasks, context)"""
        if self.session_file.exists():
            try:
                return json.loads(self.session_file.read_text())
            except json.JSONDecodeError:
                logger.error(f"Corrupted session file: {self.session_file}")
                return self._create_new_session()
        return self._create_new_session()
    
    def _create_new_session(self) -> Dict:
        """Create a new session structure"""
        return {
            "user_id": self.user_id,
            "goals": [],
            "completed_tasks": [],
            "active_task": None,
            "context_variables": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def save_session(self):
        """Persist session state to disk"""
        self.session["last_updated"] = datetime.now().isoformat()
        try:
            self.session_file.write_text(json.dumps(self.session, indent=2))
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def add_conversation(self, user_msg: str, ai_response: str):
        """
        Add conversation to long-term memory for semantic retrieval.
        
        Args:
            user_msg: User's input message
            ai_response: AI's response
        """
        if not self.vector_store_enabled:
            return
        
        timestamp = datetime.now().isoformat()
        doc_id = f"msg_{timestamp.replace(':', '-').replace('.', '-')}"
        
        try:
            self.collection.add(
                ids=[doc_id],
                documents=[f"User: {user_msg}\n\nAssistant: {ai_response}"],
                metadatas=[{
                    "timestamp": timestamp,
                    "type": "conversation",
                    "user_msg_length": len(user_msg),
                    "ai_response_length": len(ai_response)
                }]
            )
            logger.debug(f"Added conversation to vector store: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to add conversation to vector store: {e}")
    
    def retrieve_relevant_context(self, query: str, n_results: int = 5) -> List[str]:
        """
        Semantic search for relevant past interactions.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant conversation snippets
        """
        if not self.vector_store_enabled:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            if results and results["documents"] and len(results["documents"]) > 0:
                return results["documents"][0]
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def add_task(self, task_description: str, priority: str = "medium"):
        """
        Add a task/goal to the session.
        
        Args:
            task_description: Description of the task
            priority: Priority level (low, medium, high)
        """
        task = {
            "id": len(self.session["goals"]),
            "description": task_description,
            "priority": priority,
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        self.session["goals"].append(task)
        self.save_session()
        logger.info(f"Added task: {task_description}")
    
    def mark_task_complete(self, task_index: int):
        """
        Move task to completed list.
        
        Args:
            task_index: Index of task in goals list
        """
        if 0 <= task_index < len(self.session["goals"]):
            task = self.session["goals"].pop(task_index)
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat()
            self.session["completed_tasks"].append(task)
            self.save_session()
            logger.info(f"Completed task: {task['description']}")
            return True
        return False
    
    def set_context_variable(self, key: str, value: str):
        """
        Store a context variable (e.g., current project path, language).
        
        Args:
            key: Variable name
            value: Variable value
        """
        self.session["context_variables"][key] = value
        self.save_session()
    
    def get_context_variable(self, key: str) -> Optional[str]:
        """Retrieve a context variable"""
        return self.session["context_variables"].get(key)
    
    def get_session_context(self) -> str:
        """
        Generate a text summary of current session state for LLM injection.
        
        Returns:
            Formatted string with goals, context variables, and recent tasks
        """
        context_parts = []
        
        # Active tasks
        if self.session["goals"]:
            context_parts.append("## Current Goals:")
            for i, goal in enumerate(self.session["goals"]):
                context_parts.append(f"{i+1}. [{goal['priority'].upper()}] {goal['description']} (Status: {goal['status']})")
        
        # Recently completed tasks
        if self.session["completed_tasks"]:
            recent = self.session["completed_tasks"][-3:]  # Last 3
            context_parts.append("\n## Recently Completed:")
            for task in recent:
                context_parts.append(f"- {task['description']}")
        
        # Context variables
        if self.session["context_variables"]:
            context_parts.append("\n## Context Variables:")
            for key, value in self.session["context_variables"].items():
                context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts) if context_parts else "No active session context."
    
    def show_session_state(self):
        """Display current session state in terminal"""
        # Goals table
        if self.session["goals"]:
            table = Table(title="Active Goals & Tasks", show_lines=True)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Priority", style="yellow")
            table.add_column("Description", style="white")
            table.add_column("Status", style="green")
            
            for i, goal in enumerate(self.session["goals"]):
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(goal["priority"], "⚪")
                status_emoji = {"pending": "⏳", "in_progress": "⚙️", "completed": "✅"}.get(goal["status"], "❓")
                table.add_row(
                    str(i),
                    f"{priority_emoji} {goal['priority'].upper()}",
                    goal["description"],
                    f"{status_emoji} {goal['status']}"
                )
            
            console.print(table)
        else:
            console.print("[yellow]No active goals.[/yellow]")
        
        # Context variables
        if self.session["context_variables"]:
            context_text = "\n".join(
                f"[cyan]{k}[/cyan]: {v}"
                for k, v in self.session["context_variables"].items()
            )
            console.print(Panel(context_text, title="Context Variables", border_style="blue"))
        
        # Recently completed
        if self.session["completed_tasks"]:
            recent = self.session["completed_tasks"][-5:]
            completed_text = "\n".join(f"✅ {task['description']}" for task in recent)
            console.print(Panel(completed_text, title="Recently Completed", border_style="green"))
        
        # Memory stats
        if self.vector_store_enabled:
            stats = f"💾 Vector Store: {self.collection.count()} memories"
            console.print(f"[dim]{stats}[/dim]")
    
    def clear_session(self):
        """Reset session state (keeps vector store)"""
        self.session = self._create_new_session()
        self.save_session()
        logger.info("Session cleared")
    
    def clear_all_memory(self):
        """Delete all memory (session + vector store)"""
        self.clear_session()
        
        if self.vector_store_enabled:
            try:
                self.chroma.delete_collection(f"conversations_{self.user_id}")
                self.collection = self.chroma.get_or_create_collection(
                    name=f"conversations_{self.user_id}",
                    metadata={"description": "Conversation history with semantic search"}
                )
                logger.info("Vector store cleared")
            except Exception as e:
                logger.error(f"Failed to clear vector store: {e}")
    
    def export_memory(self, output_file: str):
        """
        Export all memory to JSON file.
        
        Args:
            output_file: Path to output JSON file
        """
        export_data = {
            "session": self.session,
            "vector_store": []
        }
        
        if self.vector_store_enabled:
            try:
                # Get all documents
                all_docs = self.collection.get()
                export_data["vector_store"] = [
                    {
                        "id": all_docs["ids"][i],
                        "document": all_docs["documents"][i],
                        "metadata": all_docs["metadatas"][i]
                    }
                    for i in range(len(all_docs["ids"]))
                ]
            except Exception as e:
                logger.error(f"Failed to export vector store: {e}")
        
        try:
            Path(output_file).write_text(json.dumps(export_data, indent=2))
            console.print(f"[green]Memory exported to {output_file}[/green]")
        except Exception as e:
            logger.error(f"Failed to export memory: {e}")
            console.print(f"[red]Export failed: {e}[/red]")


# CLI commands for memory management
if __name__ == "__main__":
    import typer
    app = typer.Typer()
    
    @app.command()
    def show():
        """Show current session state"""
        mem = MemoryManager()
        mem.show_session_state()
    
    @app.command()
    def clear():
        """Clear session state"""
        mem = MemoryManager()
        mem.clear_session()
        console.print("[green]Session cleared.[/green]")
    
    @app.command()
    def clear_all():
        """Clear all memory including vector store"""
        mem = MemoryManager()
        if typer.confirm("This will delete ALL memory. Continue?"):
            mem.clear_all_memory()
            console.print("[green]All memory cleared.[/green]")
    
    @app.command()
    def export(output: str = "memory_export.json"):
        """Export memory to JSON file"""
        mem = MemoryManager()
        mem.export_memory(output)
    
    app()
