"""
Interactive menu system for DIGY
Provides arrow-key navigation and command execution
"""

import os
import sys
import subprocess
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
import click

console = Console()

class InteractiveMenu:
    """Interactive menu with arrow key navigation"""

    def __init__(self, repo_path: str, deployer, readme_path: Optional[str] = None):
        self.repo_path = repo_path
        self.deployer = deployer
        self.readme_path = readme_path
        self.current_selection = 0
        self.menu_items = []
        self.setup_menu()

    def setup_menu(self):
        """Set up menu items based on discovered files"""
        self.menu_items = [
            {"title": "📋 Show Repository Info", "action": "show_info"},
            {"title": "📖 View README", "action": "view_readme"},
            {"title": "🔧 Setup Environment", "action": "setup_env"},
            {"title": "📁 List Python Files", "action": "list_files"},
            {"title": "🚀 Run Python File", "action": "run_file"},
            {"title": "🔍 Inspect File", "action": "inspect_file"},
            {"title": "💻 Interactive Shell", "action": "shell"},
            {"title": "🧹 Cleanup & Exit", "action": "exit"}
        ]

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        """Display application header"""
        header = Text()
        header.append("DIGY", style="bold blue")
        header.append(" - Dynamic Interactive Git deploY", style="dim")

        info_text = f"Repository: {os.path.basename(self.repo_path)}\n"
        info_text += f"Python files: {len(self.deployer.python_files)}"

        panel = Panel(
            info_text,
            title=header,
            border_style="blue",
            padding=(0, 1)
        )
        console.print(panel)
        console.print()

    def display_menu(self):
        """Display the interactive menu"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="", no_wrap=True)

        for i, item in enumerate(self.menu_items):
            if i == self.current_selection:
                table.add_row(f"▶ {item['title']}", style="bold cyan")
            else:
                table.add_row(f"  {item['title']}")

        console.print(table)
        console.print()
        console.print("Use ↑/↓ arrows or j/k to navigate, Enter to select, q to quit")

    def get_user_input(self) -> str:
        """Get user input for navigation"""
        try:
            # Simple input method (cross-platform)
            return input().strip().lower()
        except (KeyboardInterrupt, EOFError):
            return 'q'

    def navigate_menu(self, direction: str):
        """Navigate menu selection"""
        if direction in ['up', 'k']:
            self.current_selection = (self.current_selection - 1) % len(self.menu_items)
        elif direction in ['down', 'j']:
            self.current_selection = (self.current_selection + 1) % len(self.menu_items)

    def execute_action(self, action: str) -> bool:
        """Execute selected menu action and return whether to continue"""
        if action == "show_info":
            self.show_repository_info()
            return True
        elif action == "exit":
            self.deployer.cleanup(force=True)  # Force cleanup when exiting
            return False
        elif action == "view_readme":
            self.view_readme()
            return True
        elif action == "setup_environment":
            self.setup_environment()
            return True
        elif action == "list_python_files":
            self.list_python_files()
            return True
        elif action == "run_python_file":
            self.run_python_file()
            return True
        elif action == "inspect_file":
            self.inspect_file()
            return True
        elif action == "interactive_shell":
            self.interactive_shell()
            return True
        return True

    def show_repository_info(self):
        """Show repository information"""
        info_table = Table(title="Repository Information", box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Path", self.repo_path)
        info_table.add_row("Python Files", str(len(self.deployer.python_files)))
        info_table.add_row("Requirements", str(len(self.deployer.requirements_files)))
        info_table.add_row("Setup Files", str(len(self.deployer.setup_files)))
        info_table.add_row("Has README", "Yes" if self.readme_path else "No")

        console.print(info_table)
        self.wait_for_key()

    def view_readme(self):
        """View README file content"""
        if not self.readme_path:
            console.print("❌ No README file found")
            self.wait_for_key()
            return

        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine syntax highlighting
            syntax_lang = "markdown" if self.readme_path.endswith('.md') else "text"

            syntax = Syntax(content, syntax_lang, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="README", border_style="green"))

        except Exception as e:
            console.print(f"❌ Error reading README: {e}")

        self.wait_for_key()

    def setup_environment(self):
        """Setup deployment environment"""
        console.print("🔧 Setting up deployment environment...")

        if self.deployer.setup_environment():
            console.print("✅ Environment setup successful!")
        else:
            console.print("❌ Environment setup failed!")

        self.wait_for_key()

    def list_python_files(self):
        """List all Python files with details"""
        if not self.deployer.python_files:
            console.print("❌ No Python files found")
            self.wait_for_key()
            return

        table = Table(title="Python Files", box=None)
        table.add_column("File", style="cyan")
        table.add_column("Lines", justify="right", style="yellow")
        table.add_column("Size", justify="right", style="green")
        table.add_column("Has Main", justify="center", style="blue")

        for py_file in self.deployer.python_files:
            info = self.deployer.get_file_info(py_file)
            table.add_row(
                py_file,
                str(info["lines"]),
                f"{info['size']:,} bytes",
                "✓" if info["has_main"] else "✗"
            )

        console.print(table)
        self.wait_for_key()

    def run_python_file(self):
        """Run a selected Python file"""
        if not self.deployer.python_files:
            console.print("❌ No Python files found")
            self.wait_for_key()
            return

        # Display files for selection
        console.print("📁 Available Python files:")
        for i, py_file in enumerate(self.deployer.python_files):
            console.print(f"{i + 1}. {py_file}")

        try:
            choice = int(Prompt.ask("Select file to run (number)")) - 1
            if 0 <= choice < len(self.deployer.python_files):
                selected_file = self.deployer.python_files[choice]

                # Ask for arguments
                args_input = Prompt.ask("Enter arguments (optional)", default="")
                args = args_input.split() if args_input.strip() else []

                console.print(f"🚀 Running {selected_file}...")
                console.print("=" * 50)

                success, stdout, stderr = self.deployer.run_python_file(selected_file, args)

                if stdout:
                    console.print("📤 Output:")
                    console.print(stdout)

                if stderr:
                    console.print("⚠️ Errors:")
                    console.print(stderr, style="red")

                console.print("=" * 50)
                if success:
                    console.print("✅ Execution completed successfully")
                else:
                    console.print("❌ Execution failed")

                # Ask if user wants to run another file
                if Confirm.ask("Run another file?"):
                    self.run_python_file()
                    return
            else:
                console.print("❌ Invalid selection")

        except (ValueError, KeyboardInterrupt):
            console.print("❌ Invalid input or cancelled")

        self.wait_for_key()

    def inspect_file(self):
        """Inspect a Python file's content"""
        if not self.deployer.python_files:
            console.print("❌ No Python files found")
            self.wait_for_key()
            return

        # Display files for selection
        console.print("📁 Available Python files:")
        for i, py_file in enumerate(self.deployer.python_files):
            console.print(f"{i + 1}. {py_file}")

        try:
            choice = int(Prompt.ask("Select file to inspect (number)")) - 1
            if 0 <= choice < len(self.deployer.python_files):
                selected_file = self.deployer.python_files[choice]

                try:
                    full_path = os.path.join(self.repo_path, selected_file)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Show file info
                    info = self.deployer.get_file_info(selected_file)
                    info_text = f"File: {selected_file}\n"
                    info_text += f"Lines: {info['lines']}, Size: {info['size']} bytes\n"
                    info_text += f"Has main: {'Yes' if info['has_main'] else 'No'}"

                    console.print(Panel(info_text, title="File Information", border_style="blue"))

                    # Show imports
                    if info['imports']:
                        console.print("\n📦 Imports:")
                        for imp in info['imports'][:10]:  # Show first 10 imports
                            console.print(f"  {imp}")
                        if len(info['imports']) > 10:
                            console.print(f"  ... and {len(info['imports']) - 10} more")

                    # Show content with syntax highlighting
                    console.print("\n📄 Content:")
                    syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
                    console.print(Panel(syntax, title=selected_file, border_style="green"))

                except Exception as e:
                    console.print(f"❌ Error reading file: {e}")
            else:
                console.print("❌ Invalid selection")

        except (ValueError, KeyboardInterrupt):
            console.print("❌ Invalid input or cancelled")

        self.wait_for_key()

    def interactive_shell(self):
        """Start interactive Python shell in virtual environment"""
        if not self.deployer.venv_path:
            console.print("🔧 Setting up environment first...")
            if not self.deployer.setup_environment():
                console.print("❌ Failed to setup environment")
                self.wait_for_key()
                return

        console.print("🐍 Starting interactive Python shell...")
        console.print("Type 'exit()' to return to main menu")

        try:
            python_executable = self.deployer.get_python_executable()
            subprocess.run([python_executable, '-i'], cwd=self.repo_path)
        except Exception as e:
            console.print(f"❌ Error starting shell: {e}")

        console.print("👋 Returned to main menu")
        self.wait_for_key()

    def wait_for_key(self):
        """Wait for user to press any key"""
        console.print("\nPress Enter to continue...")
        try:
            input()
        except KeyboardInterrupt:
            pass

    def run(self):
        """Main menu loop"""
        try:
            while True:
                self.clear_screen()
                self.display_header()
                self.display_menu()

                console.print("Enter command: ", end="")
                user_input = self.get_user_input()

                if user_input == 'q' or user_input == 'quit':
                    break
                elif user_input == 'up' or user_input == 'k':
                    self.navigate_menu('up')
                elif user_input == 'down' or user_input == 'j':
                    self.navigate_menu('down')
                elif user_input == '' or user_input == 'enter':
                    # Execute current selection
                    action = self.menu_items[self.current_selection]['action']
                    if not self.execute_action(action):
                        break
                elif user_input.isdigit():
                    # Direct number selection
                    choice = int(user_input) - 1
                    if 0 <= choice < len(self.menu_items):
                        self.current_selection = choice
                        action = self.menu_items[self.current_selection]['action']
                        if not self.execute_action(action):
                            break

        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
        finally:
            self.deployer.cleanup()