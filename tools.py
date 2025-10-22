"""
Tool Registry for Agentic AI Capabilities

Provides safe, controlled access to file operations, terminal commands,
and other system functions for AI agents.

Features:
- Whitelisted command execution
- File operations with confirmations
- Tool call logging
- Safety checks and sandboxing

Usage:
    registry = ToolRegistry()
    result = registry.call("read_file", path="config.yml")
    available = registry.list_tools()
"""

import os
import subprocess
import logging
import json
from pathlib import Path
from typing import Callable, Dict, Any, Optional, List
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

console = Console()
logger = logging.getLogger("blonde")


class ToolRegistry:
    """Safe tool execution framework for agentic AI"""
    
    def __init__(self, require_confirmation: bool = True, log_calls: bool = True):
        """
        Initialize tool registry.
        
        Args:
            require_confirmation: Ask user before executing tools
            log_calls: Log all tool calls to file
        """
        self.require_confirmation = require_confirmation
        self.log_calls = log_calls
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict] = {}
        self.call_history: List[Dict] = []
        
        self.log_dir = Path.home() / ".blonde" / "tool_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.register_default_tools()
    
    def register_default_tools(self):
        """Register built-in safe tools"""
        
        # File operations
        self.register_tool(
            name="read_file",
            func=self.read_file,
            description="Read contents of a file",
            params={"path": "str - Path to file"},
            safe=True
        )
        
        self.register_tool(
            name="write_file",
            func=self.write_file,
            description="Write content to a new file (fails if file exists)",
            params={"path": "str - Path to file", "content": "str - Content to write"},
            safe=False  # Requires confirmation
        )
        
        self.register_tool(
            name="list_directory",
            func=self.list_directory,
            description="List contents of a directory",
            params={"path": "str - Directory path (default: current)"},
            safe=True
        )
        
        self.register_tool(
            name="search_files",
            func=self.search_files,
            description="Search for files matching a pattern",
            params={"pattern": "str - Glob pattern", "path": "str - Directory to search"},
            safe=True
        )
        
        # Terminal commands (whitelist only)
        self.register_tool(
            name="run_command",
            func=self.run_command_safe,
            description="Execute a whitelisted terminal command",
            params={"cmd": "str - Command to execute"},
            safe=False
        )
        
        # Code analysis
        self.register_tool(
            name="count_lines",
            func=self.count_lines,
            description="Count lines of code in a file or directory",
            params={"path": "str - File or directory path"},
            safe=True
        )
        
        # Git operations
        self.register_tool(
            name="git_status",
            func=self.git_status,
            description="Get git repository status",
            params={},
            safe=True
        )
    
    def register_tool(self, name: str, func: Callable, description: str, 
                     params: Dict[str, str], safe: bool = True):
        """
        Register a new tool.
        
        Args:
            name: Tool name
            func: Function to execute
            description: Tool description
            params: Parameter descriptions
            safe: Whether tool requires confirmation
        """
        self.tools[name] = func
        self.tool_metadata[name] = {
            "description": description,
            "params": params,
            "safe": safe
        }
        logger.debug(f"Registered tool: {name}")
    
    def call(self, tool_name: str, **kwargs) -> str:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result as string
        """
        if tool_name not in self.tools:
            return f"ERROR: Tool '{tool_name}' not found. Use list_tools() to see available tools."
        
        metadata = self.tool_metadata[tool_name]
        
        # Confirmation for unsafe tools
        if not metadata["safe"] and self.require_confirmation:
            console.print(f"[yellow]Tool: {tool_name}[/yellow]")
            console.print(f"[yellow]Args: {kwargs}[/yellow]")
            if not Confirm.ask("Execute this tool?", default=False):
                return "CANCELLED: User declined to execute tool."
        
        # Execute tool
        try:
            result = self.tools[tool_name](**kwargs)
            
            # Log call
            if self.log_calls:
                self._log_call(tool_name, kwargs, result, success=True)
            
            return result
        except Exception as e:
            error_msg = f"ERROR: Tool execution failed: {e}"
            logger.error(f"Tool {tool_name} failed: {e}")
            
            if self.log_calls:
                self._log_call(tool_name, kwargs, error_msg, success=False)
            
            return error_msg
    
    def _log_call(self, tool_name: str, args: Dict, result: str, success: bool):
        """Log tool call to history and file"""
        from datetime import datetime
        
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "args": args,
            "result": result[:500] if len(result) > 500 else result,  # Truncate
            "success": success
        }
        
        self.call_history.append(call_record)
        
        # Write to log file
        log_file = self.log_dir / f"tool_calls_{datetime.now().strftime('%Y-%m-%d')}.json"
        try:
            existing = []
            if log_file.exists():
                existing = json.loads(log_file.read_text())
            existing.append(call_record)
            log_file.write_text(json.dumps(existing, indent=2))
        except Exception as e:
            logger.error(f"Failed to write tool log: {e}")
    
    def list_tools(self) -> str:
        """List all available tools with descriptions"""
        table = Table(title="Available Tools", show_lines=True)
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Safe", style="green")
        
        for name, metadata in self.tool_metadata.items():
            safe_emoji = "✅" if metadata["safe"] else "⚠️"
            table.add_row(name, metadata["description"], safe_emoji)
        
        console.print(table)
        return f"Found {len(self.tools)} tools"
    
    # ==================== Tool Implementations ====================
    
    def read_file(self, path: str) -> str:
        """Read a file safely"""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                return f"ERROR: File not found: {path}"
            
            if file_path.stat().st_size > 1_000_000:  # 1MB limit
                return f"ERROR: File too large (>1MB): {path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return f"SUCCESS: Read {len(content)} characters from {path}\n\n{content}"
        except UnicodeDecodeError:
            return f"ERROR: File is not text (binary): {path}"
        except Exception as e:
            return f"ERROR: Failed to read file: {e}"
    
    def write_file(self, path: str, content: str) -> str:
        """Write to a file (fails if exists)"""
        try:
            file_path = Path(path).expanduser()
            
            if file_path.exists():
                return f"ERROR: File already exists: {path}. Use overwrite_file to replace."
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"SUCCESS: Written {len(content)} characters to {path}"
        except Exception as e:
            return f"ERROR: Failed to write file: {e}"
    
    def list_directory(self, path: str = ".") -> str:
        """List directory contents"""
        try:
            dir_path = Path(path).expanduser()
            
            if not dir_path.exists():
                return f"ERROR: Directory not found: {path}"
            
            if not dir_path.is_dir():
                return f"ERROR: Not a directory: {path}"
            
            items = []
            for item in sorted(dir_path.iterdir()):
                item_type = "📁" if item.is_dir() else "📄"
                size = item.stat().st_size if item.is_file() else ""
                items.append(f"{item_type} {item.name} {f'({size} bytes)' if size else ''}")
            
            return f"SUCCESS: Contents of {path}:\n" + "\n".join(items)
        except Exception as e:
            return f"ERROR: Failed to list directory: {e}"
    
    def search_files(self, pattern: str, path: str = ".") -> str:
        """Search for files matching a glob pattern"""
        try:
            dir_path = Path(path).expanduser()
            matches = list(dir_path.rglob(pattern))
            
            if not matches:
                return f"No files matching '{pattern}' found in {path}"
            
            results = [str(m.relative_to(dir_path)) for m in matches[:50]]  # Limit to 50
            return f"SUCCESS: Found {len(matches)} matches:\n" + "\n".join(results)
        except Exception as e:
            return f"ERROR: Search failed: {e}"
    
    def run_command_safe(self, cmd: str) -> str:
        """Execute whitelisted commands only"""
        # Whitelist of safe commands
        safe_commands = [
            "git status",
            "git log",
            "git diff",
            "git branch",
            "ls",
            "ls -la",
            "pwd",
            "whoami",
            "date",
            "echo",
            "cat",
            "head",
            "tail",
            "wc",
            "grep",
        ]
        
        # Check if command is whitelisted (exact match or starts with safe prefix)
        is_safe = any(cmd.strip().startswith(safe) for safe in safe_commands)
        
        if not is_safe:
            return f"ERROR: Command '{cmd}' not in whitelist. Safe commands: {', '.join(safe_commands)}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.getcwd()
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            return f"SUCCESS (exit {result.returncode}):\n{output}"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timeout (>10 seconds)"
        except Exception as e:
            return f"ERROR: Command execution failed: {e}"
    
    def count_lines(self, path: str) -> str:
        """Count lines of code in file or directory"""
        try:
            file_path = Path(path).expanduser()
            
            if not file_path.exists():
                return f"ERROR: Path not found: {path}"
            
            total_lines = 0
            file_count = 0
            
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                return f"SUCCESS: {lines} lines in {path}"
            
            # Directory: count all code files
            code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb'}
            
            for item in file_path.rglob('*'):
                if item.is_file() and item.suffix in code_extensions:
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                        file_count += 1
                    except:
                        pass  # Skip unreadable files
            
            return f"SUCCESS: {total_lines} lines across {file_count} files in {path}"
        except Exception as e:
            return f"ERROR: Line counting failed: {e}"
    
    def git_status(self) -> str:
        """Get git repository status"""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return "ERROR: Not a git repository or git not installed"
            
            status = result.stdout.strip()
            if not status:
                return "SUCCESS: Working tree clean (no changes)"
            
            return f"SUCCESS: Git status:\n{status}"
        except Exception as e:
            return f"ERROR: Git status failed: {e}"


# Standalone CLI for testing tools
if __name__ == "__main__":
    import typer
    app = typer.Typer()
    
    @app.command()
    def list():
        """List available tools"""
        registry = ToolRegistry(require_confirmation=False)
        registry.list_tools()
    
    @app.command()
    def test(tool: str):
        """Test a tool interactively"""
        registry = ToolRegistry(require_confirmation=True)
        
        if tool not in registry.tools:
            console.print(f"[red]Tool '{tool}' not found[/red]")
            registry.list_tools()
            return
        
        metadata = registry.tool_metadata[tool]
        console.print(f"[cyan]Tool: {tool}[/cyan]")
        console.print(f"[white]Description: {metadata['description']}[/white]")
        console.print(f"[yellow]Parameters:[/yellow]")
        
        for param, desc in metadata['params'].items():
            console.print(f"  - {param}: {desc}")
        
        # Prompt for parameters
        kwargs = {}
        for param in metadata['params'].keys():
            value = typer.prompt(f"Enter {param}")
            kwargs[param] = value
        
        # Execute
        result = registry.call(tool, **kwargs)
        console.print(f"\n[bold green]Result:[/bold green]\n{result}")
    
    app()
