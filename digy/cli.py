"""
Command Line Interface for DIGY
Provides CLI commands for the deployment tool
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .loader import digy, memory_manager
from .version import __version__

console = Console()

@click.group()
@click.version_option(version=__version__, prog_name="DIGY")
def main():
    """
    DIGY - Dynamic Interactive Git deploY

    Deploy Python applications from Git repositories in isolated environments
    with interactive menu support.
    """
    pass

@main.command()
@click.argument('repo_url')
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
@click.option('--no-interactive', is_flag=True, help='Skip interactive menu')
def start(repo_url: str, branch: str, no_interactive: bool):
    """
    Start DIGY with a repository from Git

    REPO_URL can be:
    - github.com/user/repo
    - https://github.com/user/repo
    - Any valid Git URL
    """
    if no_interactive:
        console.print("🚀 Loading repository in non-interactive mode...")
        # TODO: Implement non-interactive mode
        console.print("❌ Non-interactive mode not yet implemented")
        return

    digy(repo_url, branch)

# Make 'digy' default to 'digy start' for easier usage
@main.command(hidden=True)
@click.argument('repo_url')
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
def default(repo_url: str, branch: str):
    """Default command when just 'digy <repo>' is used"""
    digy(repo_url, branch)

@main.command()
def status():
    """Show current DIGY status and memory usage"""

    # Memory information
    available_mb = memory_manager.check_available_memory()
    allocated_repos = memory_manager.allocated_repos

    status_table = Table(title="DIGY Status", box=None)
    status_table.add_column("Property", style="cyan")
    status_table.add_column("Value", style="white")

    status_table.add_row("Available Memory", f"{available_mb:,} MB")
    status_table.add_row("Base Memory Allocation", f"{memory_manager.base_size_mb} MB")
    status_table.add_row("Loaded Repositories", str(len(allocated_repos)))

    console.print(status_table)

    if allocated_repos:
        console.print("\n📦 Loaded Repositories:")
        repo_table = Table(box=None)
        repo_table.add_column("Repository", style="green")
        repo_table.add_column("Memory (MB)", justify="right", style="yellow")

        for repo_url, memory_mb in allocated_repos.items():
            repo_table.add_row(repo_url, str(memory_mb))

        console.print(repo_table)

@main.command()
def examples():
    """Show usage examples"""

    examples_text = """
# Load a repository from GitHub
digy start github.com/pyfunc/free-on-pypi

# Load with specific branch
digy start github.com/user/repo --branch develop

# Quick shorthand (same as 'digy start')
digy github.com/pyfunc/free-on-pypi

# Using the direct digy function in Python
from digy import digy
digy('github.com/pyfunc/free-on-pypi')

# Check current status
digy status
"""

    syntax_panel = Panel(
        examples_text.strip(),
        title="Usage Examples",
        border_style="green"
    )
    console.print(syntax_panel)

@main.command()
@click.argument('repo_url')
@click.argument('python_file')
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
@click.option('--args', help='Arguments to pass to the Python file')
def run(repo_url: str, python_file: str, branch: str, args: str):
    """
    Quick run: Load repository and execute a specific Python file

    REPO_URL: Repository to load
    PYTHON_FILE: Python file to execute (relative path)
    """
    from .loader import GitLoader
    from .deployer import Deployer

    console.print(f"🚀 Quick run: {repo_url}/{python_file}")

    # Load repository
    loader = GitLoader()
    local_path = loader.download_repo(repo_url, branch)

    if not local_path:
        console.print("❌ Failed to load repository")
        return

    try:
        # Setup deployer
        deployer = Deployer(local_path)

        # Setup environment
        if not deployer.setup_environment():
            console.print("❌ Failed to setup environment")
            return

        # Run file
        file_args = args.split() if args else []
        success, stdout, stderr = deployer.run_python_file(python_file, file_args)

        console.print("=" * 50)
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

    finally:
        # Cleanup
        loader.cleanup_repo(repo_url)

@main.command()
def info():
    """Show information about DIGY"""

    info_text = f"""
DIGY v{__version__}
Dynamic Interactive Git deploY

A Python package for deploying applications from Git repositories 
in isolated environments with interactive menu support.

Features:
• Load repositories directly into RAM
• Isolated virtual environments
• Interactive menu navigation
• Real-time code execution
• Memory management
• Cross-platform support

Repository: https://github.com/yourusername/digy
"""

    info_panel = Panel(
        info_text.strip(),
        title="About DIGY",
        border_style="blue"
    )
    console.print(info_panel)

if __name__ == '__main__':
    main()