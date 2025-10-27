"""
Enhanced Agentic Tools for BlondE-CLI

Provides comprehensive capabilities similar to Windsurf/Claude:
- Code editing and refactoring
- Task decomposition and planning
- File system operations
- Git integration
- Terminal command execution
- Multi-step task execution
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.table import Table
import difflib

console = Console()


class TaskPlanner:
    """Decomposes complex tasks into executable steps"""
    
    def __init__(self, llm_adapter):
        self.llm = llm_adapter
        self.current_plan = []
        self.completed_steps = []
    
    def decompose_task(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Break down a complex task into actionable steps.
        
        Args:
            user_request: The user's high-level request
            
        Returns:
            List of steps with tool calls needed
        """
        planning_prompt = f"""
You are a task planner. Break down this request into specific, executable steps.

User Request: {user_request}

For each step, identify:
1. What needs to be done
2. Which tool to use (read_file, write_file, edit_file, run_command, etc.)
3. What parameters are needed

Return a JSON array of steps like:
[
  {{"step": 1, "action": "Read file", "tool": "read_file", "params": {{"path": "file.py"}}, "reason": "Need to see current code"}},
  {{"step": 2, "action": "Edit code", "tool": "edit_file", "params": {{"path": "file.py", "changes": "..."}}, "reason": "Fix the bug"}}
]

Be specific and actionable. Only return the JSON array.
"""
        
        try:
            response = self.llm.chat(planning_prompt)
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                steps = json.loads(json_match.group())
                self.current_plan = steps
                return steps
            else:
                # Fallback: create a simple plan
                return [{
                    "step": 1,
                    "action": user_request,
                    "tool": "manual",
                    "params": {},
                    "reason": "Direct execution"
                }]
        except Exception as e:
            console.print(f"[yellow]Planning error: {e}. Using direct execution.[/yellow]")
            return [{
                "step": 1,
                "action": user_request,
                "tool": "manual",
                "params": {},
                "reason": "Fallback"
            }]
    
    def display_plan(self):
        """Display the current execution plan"""
        if not self.current_plan:
            console.print("[yellow]No plan created yet[/yellow]")
            return
        
        table = Table(title="📋 Execution Plan", show_header=True, header_style="bold cyan")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Action", style="white")
        table.add_column("Tool", style="green")
        table.add_column("Status", style="yellow")
        
        for step in self.current_plan:
            status = "✅ Done" if step["step"] in self.completed_steps else "⏳ Pending"
            table.add_row(
                str(step["step"]),
                step["action"],
                step["tool"],
                status
            )
        
        console.print(table)


class EnhancedToolRegistry:
    """Extended tool registry with code editing and advanced capabilities"""
    
    def __init__(self, require_confirmation: bool = True):
        self.require_confirmation = require_confirmation
        self.tools = {}
        self.register_all_tools()
    
    def register_all_tools(self):
        """Register all available tools"""
        # File operations
        self.tools["read_file"] = self.read_file
        self.tools["write_file"] = self.write_file
        self.tools["edit_file"] = self.edit_file
        self.tools["delete_file"] = self.delete_file
        self.tools["rename_file"] = self.rename_file
        
        # Directory operations
        self.tools["list_dir"] = self.list_dir
        self.tools["create_dir"] = self.create_dir
        self.tools["search_files"] = self.search_files
        
        # Code operations
        self.tools["replace_in_file"] = self.replace_in_file
        self.tools["insert_at_line"] = self.insert_at_line
        self.tools["remove_lines"] = self.remove_lines
        
        # Git operations
        self.tools["git_status"] = self.git_status
        self.tools["git_diff"] = self.git_diff
        self.tools["git_add"] = self.git_add
        self.tools["git_commit"] = self.git_commit
        
        # Terminal
        self.tools["run_command"] = self.run_command
        
        # Analysis
        self.tools["count_lines"] = self.count_lines
        self.tools["search_in_files"] = self.search_in_files
    
    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool with confirmation if needed"""
        if tool_name not in self.tools:
            return f"❌ Tool '{tool_name}' not found"
        
        # Show what we're doing
        console.print(f"\n[cyan]🔧 Calling tool: {tool_name}[/cyan]")
        console.print(f"[dim]Parameters: {kwargs}[/dim]")
        
        # Ask for confirmation for destructive operations
        destructive = tool_name in ["write_file", "edit_file", "delete_file", "git_commit", "run_command"]
        if destructive and self.require_confirmation:
            if not Confirm.ask("Execute this tool?", default=True):
                return "❌ Cancelled by user"
        
        try:
            result = self.tools[tool_name](**kwargs)
            console.print(f"[green]✅ Tool executed successfully[/green]")
            return result
        except Exception as e:
            error_msg = f"❌ Tool error: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg
    
    # ============= File Operations =============
    
    def read_file(self, path: str) -> str:
        """Read a file"""
        file_path = Path(path)
        if not file_path.exists():
            return f"❌ File not found: {path}"
        
        try:
            content = file_path.read_text()
            return f"📄 {path} ({len(content)} chars):\n\n{content}"
        except Exception as e:
            return f"❌ Read error: {e}"
    
    def write_file(self, path: str, content: str) -> str:
        """Write content to a file"""
        file_path = Path(path)
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"✅ Written {len(content)} chars to {path}"
        except Exception as e:
            return f"❌ Write error: {e}"
    
    def edit_file(self, path: str, old_text: str, new_text: str) -> str:
        """Edit file by replacing text"""
        file_path = Path(path)
        
        if not file_path.exists():
            return f"❌ File not found: {path}"
        
        try:
            content = file_path.read_text()
            
            if old_text not in content:
                return f"❌ Text not found in file:\n{old_text}"
            
            # Show diff
            old_lines = content.split('\n')
            new_content = content.replace(old_text, new_text)
            new_lines = new_content.split('\n')
            
            diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
            if diff:
                console.print("\n[yellow]📝 Changes:[/yellow]")
                for line in diff[:20]:  # Show first 20 lines of diff
                    if line.startswith('+'):
                        console.print(f"[green]{line}[/green]")
                    elif line.startswith('-'):
                        console.print(f"[red]{line}[/red]")
                    else:
                        console.print(f"[dim]{line}[/dim]")
            
            file_path.write_text(new_content)
            return f"✅ File edited: {path}"
        except Exception as e:
            return f"❌ Edit error: {e}"
    
    def delete_file(self, path: str) -> str:
        """Delete a file"""
        file_path = Path(path)
        
        if not file_path.exists():
            return f"❌ File not found: {path}"
        
        try:
            file_path.unlink()
            return f"✅ Deleted: {path}"
        except Exception as e:
            return f"❌ Delete error: {e}"
    
    def rename_file(self, old_path: str, new_path: str) -> str:
        """Rename/move a file"""
        old = Path(old_path)
        new = Path(new_path)
        
        if not old.exists():
            return f"❌ File not found: {old_path}"
        
        try:
            old.rename(new)
            return f"✅ Renamed: {old_path} → {new_path}"
        except Exception as e:
            return f"❌ Rename error: {e}"
    
    # ============= Directory Operations =============
    
    def list_dir(self, path: str = ".") -> str:
        """List directory contents"""
        dir_path = Path(path)
        
        if not dir_path.exists():
            return f"❌ Directory not found: {path}"
        
        items = []
        for item in sorted(dir_path.iterdir()):
            icon = "📁" if item.is_dir() else "📄"
            items.append(f"{icon} {item.name}")
        
        return f"📂 {path}:\n" + "\n".join(items)
    
    def create_dir(self, path: str) -> str:
        """Create a directory"""
        dir_path = Path(path)
        
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return f"✅ Created directory: {path}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def search_files(self, pattern: str, path: str = ".") -> str:
        """Search for files matching pattern"""
        dir_path = Path(path)
        matches = list(dir_path.rglob(pattern))
        
        if not matches:
            return f"❌ No files matching '{pattern}'"
        
        results = [str(m) for m in matches[:50]]
        return f"🔍 Found {len(matches)} matches:\n" + "\n".join(results)
    
    # ============= Code Operations =============
    
    def replace_in_file(self, path: str, pattern: str, replacement: str, regex: bool = False) -> str:
        """Replace text in file with pattern"""
        file_path = Path(path)
        
        if not file_path.exists():
            return f"❌ File not found: {path}"
        
        try:
            content = file_path.read_text()
            
            if regex:
                new_content = re.sub(pattern, replacement, content)
            else:
                new_content = content.replace(pattern, replacement)
            
            if content == new_content:
                return f"⚠️ No changes made (pattern not found)"
            
            file_path.write_text(new_content)
            return f"✅ Replaced in {path}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def insert_at_line(self, path: str, line_number: int, text: str) -> str:
        """Insert text at specific line"""
        file_path = Path(path)
        
        if not file_path.exists():
            return f"❌ File not found: {path}"
        
        try:
            lines = file_path.read_text().split('\n')
            lines.insert(line_number - 1, text)
            file_path.write_text('\n'.join(lines))
            return f"✅ Inserted at line {line_number}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def remove_lines(self, path: str, start_line: int, end_line: int) -> str:
        """Remove lines from file"""
        file_path = Path(path)
        
        if not file_path.exists():
            return f"❌ File not found: {path}"
        
        try:
            lines = file_path.read_text().split('\n')
            del lines[start_line-1:end_line]
            file_path.write_text('\n'.join(lines))
            return f"✅ Removed lines {start_line}-{end_line}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    # ============= Git Operations =============
    
    def git_status(self) -> str:
        """Get git status"""
        try:
            result = subprocess.run(["git", "status", "--short"], 
                                  capture_output=True, text=True, timeout=5)
            return f"📊 Git status:\n{result.stdout or 'Clean working tree'}"
        except Exception as e:
            return f"❌ Git error: {e}"
    
    def git_diff(self, file: str = None) -> str:
        """Show git diff"""
        try:
            cmd = ["git", "diff"]
            if file:
                cmd.append(file)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return f"📝 Git diff:\n{result.stdout or 'No changes'}"
        except Exception as e:
            return f"❌ Git error: {e}"
    
    def git_add(self, files: str) -> str:
        """Stage files for commit"""
        try:
            subprocess.run(["git", "add", files], check=True)
            return f"✅ Staged: {files}"
        except Exception as e:
            return f"❌ Git error: {e}"
    
    def git_commit(self, message: str) -> str:
        """Commit changes"""
        try:
            subprocess.run(["git", "commit", "-m", message], check=True)
            return f"✅ Committed: {message}"
        except Exception as e:
            return f"❌ Git error: {e}"
    
    # ============= Terminal =============
    
    def run_command(self, command: str) -> str:
        """Execute shell command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            output = result.stdout if result.returncode == 0 else result.stderr
            return f"💻 Command output:\n{output}"
        except Exception as e:
            return f"❌ Command error: {e}"
    
    # ============= Analysis =============
    
    def count_lines(self, path: str) -> str:
        """Count lines in file/directory"""
        file_path = Path(path)
        
        if not file_path.exists():
            return f"❌ Path not found: {path}"
        
        if file_path.is_file():
            lines = len(file_path.read_text().split('\n'))
            return f"📊 {lines} lines in {path}"
        
        # Directory
        total = 0
        files = 0
        for item in file_path.rglob('*.py'):
            try:
                total += len(item.read_text().split('\n'))
                files += 1
            except:
                pass
        
        return f"📊 {total} lines across {files} Python files in {path}"
    
    def search_in_files(self, pattern: str, path: str = ".", file_pattern: str = "*") -> str:
        """Search for text in files"""
        dir_path = Path(path)
        matches = []
        
        for file in dir_path.rglob(file_pattern):
            if file.is_file():
                try:
                    content = file.read_text()
                    if pattern in content:
                        # Find line numbers
                        lines = content.split('\n')
                        line_nums = [i+1 for i, line in enumerate(lines) if pattern in line]
                        matches.append(f"{file}: lines {', '.join(map(str, line_nums))}")
                except:
                    pass
        
        if not matches:
            return f"❌ No matches for '{pattern}'"
        
        return f"🔍 Found {len(matches)} files:\n" + "\n".join(matches[:20])


class AgenticExecutor:
    """Autonomous execution engine that can plan and execute multi-step tasks"""
    
    def __init__(self, llm_adapter, tool_registry: EnhancedToolRegistry, 
                 planner: TaskPlanner):
        self.llm = llm_adapter
        self.tools = tool_registry
        self.planner = planner
    
    def execute_task(self, user_request: str, auto_confirm: bool = False) -> str:
        """
        Execute a complex task autonomously.
        
        1. Plan the task (decompose into steps)
        2. Execute each step
        3. Handle errors and retry
        4. Return final result
        """
        console.print(Panel(f"[bold cyan]🤖 Agentic Mode: {user_request}[/bold cyan]", 
                          border_style="cyan"))
        
        # Step 1: Plan
        console.print("\n[yellow]📋 Planning task...[/yellow]")
        steps = self.planner.decompose_task(user_request)
        self.planner.display_plan()
        
        if not auto_confirm:
            if not Confirm.ask("\nExecute this plan?", default=True):
                return "❌ Cancelled by user"
        
        # Step 2: Execute
        console.print("\n[yellow]⚙️ Executing plan...[/yellow]")
        results = []
        
        for step in steps:
            console.print(f"\n[cyan]Step {step['step']}: {step['action']}[/cyan]")
            
            tool_name = step.get("tool")
            params = step.get("params", {})
            
            if tool_name == "manual":
                # Ask LLM to handle it
                response = self.llm.chat(step["action"])
                results.append(response)
            elif tool_name in self.tools.tools:
                # Execute tool
                result = self.tools.call_tool(tool_name, **params)
                results.append(result)
                
                # Mark as completed
                self.planner.completed_steps.append(step["step"])
            else:
                results.append(f"⚠️ Unknown tool: {tool_name}")
        
        # Step 3: Summarize
        console.print("\n[green]✅ Task completed![/green]")
        summary = "\n\n".join([f"Step {i+1}: {r}" for i, r in enumerate(results)])
        
        return summary
    
    def parse_tool_calls_from_response(self, response: str) -> List[Tuple[str, Dict]]:
        """
        Parse tool calls from LLM response.
        Format: <tool:tool_name param1="value1" param2="value2"/>
        """
        pattern = r'<tool:(\w+)\s+([^/>]+)/>'
        matches = re.findall(pattern, response)
        
        tool_calls = []
        for tool_name, params_str in matches:
            # Parse parameters
            param_pattern = r'(\w+)="([^"]*)"'
            params = dict(re.findall(param_pattern, params_str))
            tool_calls.append((tool_name, params))
        
        return tool_calls


# Standalone testing
if __name__ == "__main__":
    console.print("[cyan]Testing Enhanced Agentic Tools[/cyan]")
    
    tools = EnhancedToolRegistry(require_confirmation=False)
    
    # Test file operations
    console.print("\n[yellow]Test 1: File operations[/yellow]")
    console.print(tools.call_tool("write_file", path="test.txt", content="Hello World"))
    console.print(tools.call_tool("read_file", path="test.txt"))
    console.print(tools.call_tool("delete_file", path="test.txt"))
    
    # Test directory operations
    console.print("\n[yellow]Test 2: Directory operations[/yellow]")
    console.print(tools.call_tool("list_dir", path="."))
    
    # Test code operations
    console.print("\n[yellow]Test 3: Search[/yellow]")
    console.print(tools.call_tool("search_files", pattern="*.py", path="."))
    
    console.print("\n[green]✅ All tests completed![/green]")
