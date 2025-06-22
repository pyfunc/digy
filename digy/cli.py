"""
Command Line Interface for DIGY
Provides CLI commands for the deployment tool
"""

import os
import sys
import click
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from .loader import digy, memory_manager
from .version import __version__
from .environment import EnvironmentManager, select_virtualenv
from .auth import get_auth_provider, interactive_auth_selector

# Import Deployer if it exists in the project
try:
    from .deployer import Deployer
except ImportError:
    class Deployer:
        """Dummy Deployer class if not available"""
        def __init__(self, path: str):
            self.path = path
        
        @classmethod
        def execute_python_file(cls, python_file: str, args: List[str] = None) -> subprocess.CompletedProcess:
            """Execute a Python file with arguments"""
            cmd = [sys.executable, python_file] + (args or [])
            return subprocess.run(cmd, cwd=os.getcwd())

console = Console()

# Common options for environment selection
env_options = [
    click.option(
        '--venv',
        'venv_path',
        type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
        help='Path to Python virtual environment',
    ),
    click.option(
        '--python',
        'python_path',
        type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
        help='Path to Python interpreter',
    ),
    click.option(
        '--no-venv',
        is_flag=True,
        help='Do not use a virtual environment (use system Python)',
    ),
]

def add_options(options):
    """Decorator to add common options to commands"""
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options

@click.group()
@click.version_option(version=__version__, prog_name="DIGY")
@click.option(
    '--auth',
    type=click.Choice(['sql', 'web', 'io', 'socket'], case_sensitive=False),
    help='Authentication method to use',
)
@click.option(
    '--auth-config',
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help='Path to authentication config file',
)
@click.pass_context
def main(ctx, auth: Optional[str], auth_config: Optional[str]):
    """
    DIGY - Dynamic Interactive Git deploY

    Deploy Python applications from Git repositories in isolated environments
    with interactive menu support.
    """
    # Ensure ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    
    # Store authentication info in context
    ctx.obj['auth_type'] = auth
    ctx.obj['auth_config'] = auth_config
    
    # Initialize environment manager with default values
    ctx.obj['env_manager'] = EnvironmentManager(env_type='local')

@main.group()
def env():
    """Manage execution environments"""
    pass

@env.command('list')
def list_envs():
    """List available virtual environments"""
    select_virtualenv()

@env.command('create')
@click.argument('path', type=click.Path())
@click.option('--python', help='Python interpreter to use')
def create_env(path: str, python: Optional[str]):
    """Create a new virtual environment"""
    env_manager = EnvironmentManager()
    if env_manager.create_virtualenv(path, python):
        console.print(f"✅ Created virtual environment at {path}")
    else:
        console.print("❌ Failed to create virtual environment")
        sys.exit(1)

@main.command()
@click.argument('repo_url')
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
@click.option('--no-interactive', is_flag=True, help='Skip interactive menu')
@click.option('--file', '-f', 'files', multiple=True, help='Files to attach')
@add_options(env_options)
@click.pass_context
def local(
    ctx,
    repo_url: str,
    branch: str,
    no_interactive: bool,
    files: list,
    venv_path: Optional[str],
    python_path: Optional[str],
    no_venv: bool,
):
    """
    Run a repository locally

    REPO_URL can be:
    - github.com/user/repo
    - git@github.com:user/repo.git
    - /path/to/local/repo
    - file:///path/to/local/repo
    """
    # Set environment type to local
    ctx.obj['env_manager'] = EnvironmentManager(env_type='local')
    
    # Call the original start command with the context
    ctx.invoke(start, 
              repo_url=repo_url, 
              branch=branch, 
              no_interactive=no_interactive,
              files=files,
              venv_path=venv_path,
              python_path=python_path,
              no_venv=no_venv)

@main.command()
@click.argument('repo_url')
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
@click.option('--no-interactive', is_flag=True, help='Skip interactive menu')
@click.option('--file', '-f', 'files', multiple=True, help='Files to attach')
@add_options(env_options)
@click.pass_context
def start(
    ctx,
    repo_url: str,
    branch: str,
    no_interactive: bool,
    files: list,
    venv_path: Optional[str],
    python_path: Optional[str],
    no_venv: bool,
):
    """
    Start DIGY with a repository from Git (legacy, use 'local' instead)

    REPO_URL can be:
    - github.com/user/repo
    - git@github.com:user/repo.git
    - /path/to/local/repo
    - file:///path/to/local/repo
    """
    # Initialize environment manager from context or create new
    env_manager = ctx.obj.get('env_manager', EnvironmentManager(env_type='local'))
    
    # If no virtualenv specified and not explicitly disabled, try to find one
    if not venv_path and not no_venv and not python_path:
        # Try to find or create a virtual environment
        env_path = select_virtualenv()
        if env_path:
            env_manager.venv_path = env_path
    
    if no_interactive:
        console.print("🚀 Loading repository in non-interactive mode...")
        # TODO: Implement non-interactive mode with attached files
        console.print("❌ Non-interactive mode not yet implemented")
        return
    
    # Store files in context for the interactive menu
    ctx.obj['attached_files'] = list(files)
    
    # Store environment manager in context
    ctx.obj['env_manager'] = env_manager
    
    # Start interactive mode
    digy(repo_url, branch)
    
    # Cleanup after digy completes
    if env_manager.venv_path and os.path.exists(env_manager.venv_path):
        shutil.rmtree(env_manager.venv_path, ignore_errors=True)

# Make 'digy' default to 'digy start' for easier usage
@main.command(hidden=True)
@click.argument('repo_url')
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
@click.pass_context
def default(ctx, repo_url: str, branch: str):
    """Default command when just 'digy <repo>' is used"""
    digy(repo_url, branch)

@main.command()
@click.pass_context
def status(ctx):
    """Show current DIGY status and memory usage"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim", width=20)
    table.add_column("Value")
    
    # Memory usage
    mem_stats = memory_manager.get_stats()
    table.add_row("Memory Usage", f"{mem_stats['usage_mb']:.2f} MB / {mem_stats['total_mb']:.2f} MB")
    
    # Environment info
    env_manager = ctx.obj.get('env_manager', EnvironmentManager())
    env_type = getattr(env_manager, 'env_type', 'local')
    python_path = getattr(env_manager, 'venv_python', sys.executable)
    table.add_row("Environment", f"{env_type} ({python_path})")
    
    # Authentication status
    auth_type = ctx.obj.get('auth_type', 'None')
    table.add_row("Authentication", auth_type)
    
    # Recent commands
    recent = memory_manager.get_recent_commands(limit=5)
    recent_str = "\n".join([f"{cmd['command']} ({cmd['timestamp']})" for cmd in recent])
    table.add_row("Recent Commands", recent_str or "None")
    
    console.print(Panel.fit(table, title="DIGY Status"))

@main.command()
@click.argument('repo_url')
@click.argument('python_file')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.option('--branch', '-b', default='main', help='Git branch to checkout')
@click.option('--env', '-e', 'env_type',
              type=click.Choice(['local', 'docker', 'jvm', 'remote'], case_sensitive=False),
              default='local',
              help='Execution environment')
@click.option('--docker-image', help='Docker image to use (for docker env)')
@click.option('--remote-host', help='Remote host (for remote env)')
@click.option('--attach', '-a', 'attachments', multiple=True, 
              help='Files to attach (can be specified multiple times)')
@click.option('--interactive-attach', is_flag=True, 
              help='Interactively select files to attach')
@add_options(env_options)
@click.pass_context
def run(
    ctx,
    repo_url: str,
    python_file: str,
    args: tuple,
    branch: str,
    env_type: str,
    docker_image: Optional[str],
    remote_host: Optional[str],
    attachments: List[str],
    interactive_attach: bool,
    venv_path: Optional[str],
    python_path: Optional[str],
    no_venv: bool,
):
    """
    Quick run: Load repository and execute a specific Python file

    REPO_URL: Repository to load (e.g., github.com/user/repo)
    PYTHON_FILE: Python file to execute (relative path in repository)
    ARGS: Arguments to pass to the Python file
    """
    import tempfile
    import shutil
    import git
    from urllib.parse import urlparse
    from .file_utils import select_files_interactive, attach_files

    console.print(f"🚀 Running: {python_file} with args: {args}")
    
    # Set up environment manager
    env_manager = EnvironmentManager(
        env_type=env_type,
        venv_path=venv_path,
        docker_image=docker_image,
        remote_host=remote_host,
    )
    
    # Handle authentication if needed
    if ctx.obj.get('auth_type'):
        auth_provider = get_auth_provider(
            ctx.obj['auth_type'],
            config_file=ctx.obj.get('auth_config')
        )
        if auth_provider and not auth_provider.authenticate():
            console.print("[red]Authentication failed[/red]")
            sys.exit(1)
    
    # Create a temporary directory for the repository
    temp_dir = tempfile.mkdtemp(prefix="digy_")
    try:
        console.print(f"📦 Cloning repository: {repo_url}")
        
        # Clone the repository
        repo_name = os.path.splitext(os.path.basename(repo_url))[0]
        repo_path = os.path.join(temp_dir, repo_name)
        
        # Handle different repository URL formats
        if not any(repo_url.startswith(proto) for proto in ['http://', 'https://', 'git@']):
            repo_url = f"https://{repo_url}"
        if not repo_url.endswith('.git'):
            repo_url += '.git'
            
        # Clone the repository
        try:
            repo = git.Repo.clone_from(repo_url, repo_path, branch=branch)
            console.print(f"✅ Cloned {branch} branch to {repo_path}")
        except git.GitCommandError as e:
            console.print(f"[red]Failed to clone repository: {e}[/red]")
            sys.exit(1)
        
        # Check if the Python file exists
        python_file_path = os.path.join(repo_path, python_file)
        if not os.path.exists(python_file_path):
            console.print(f"[red]Python file not found: {python_file}[/red]")
            sys.exit(1)
        
        # Handle file attachments
        files_to_attach = list(attachments)
        if interactive_attach:
            console.print("\n[bold]Select files to attach:[/]")
            interactive_files = select_files_interactive()
            files_to_attach.extend(interactive_files)
        
        if files_to_attach:
            attach_dir = os.path.join(repo_path, '.digy_attachments')
            os.makedirs(attach_dir, exist_ok=True)
            attached = attach_files(files_to_attach, attach_dir)
            console.print(f"\n📎 Attached {len(attached)} file(s) to {attach_dir}")
        
        # Create a deployer instance
        deployer = Deployer(repo_path)
        
        # Execute the Python file with the environment manager
        if env_manager.env_type == 'local':
            # For local execution, use the deployer directly
            result = deployer.execute_python_file(python_file, list(args))
        else:
            # For other environments, use the environment manager
            cmd = [sys.executable, python_file] + list(args)
            result = env_manager.execute_command(cmd, cwd=repo_path)
        
        if result.returncode == 0:
            console.print("✅ Execution completed successfully")
        else:
            console.print(f"❌ Execution failed with code {result.returncode}")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

@main.command()
def examples():
    """Show usage examples"""
    examples = """
    [bold]Basic usage:[/bold]
    $ digy start github.com/username/repo
    $ digy run github.com/username/repo script.py --arg1 value1

    [bold]With environment selection:[/bold]
    $ digy --env docker start github.com/user/repo
    $ digy --venv ~/venvs/myenv run github.com/user/repo script.py

    [bold]With authentication:[/bold]
    $ digy --auth sql --auth-config dbconfig.json start github.com/user/repo
    """
    console.print(Panel(
        examples.strip(),
        title="DIGY Examples",
        border_style="blue"
    ))

@main.command()
def info():
    """Show information about DIGY"""
    info_text = f"""
    [bold]DIGY - Dynamic Interactive Git deploY[/bold]
    Version: {__version__}
    Python: {sys.version.split()[0]}
    Platform: {sys.platform}
    """
    console.print(Panel(
        info_text.strip(),
        title="DIGY Information",
        border_style="green"
    ))

if __name__ == '__main__':
    main()