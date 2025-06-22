"""
Environment management for DIGY
Handles different execution environments (local, docker, jvm, remote)
"""
import os
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path

from rich.console import Console

console = Console()

class EnvironmentManager:
    """Manages different execution environments"""
    
    def __init__(self, env_type: str = "local", **kwargs):
        """Initialize environment manager
        
        Args:
            env_type: Type of environment ('local', 'docker', 'jvm', 'remote')
            **kwargs: Additional environment-specific parameters
        """
        self.env_type = env_type
        self.kwargs = kwargs
        self.venv_path = kwargs.get('venv_path')
        self.venv_python = None
        
        if self.venv_path:
            self.venv_python = os.path.join(self.venv_path, 'bin', 'python')
            if not os.path.exists(self.venv_python):
                self.venv_python = os.path.join(self.venv_path, 'Scripts', 'python.exe')
    
    @classmethod
    def from_cli(cls, ctx: 'click.Context') -> 'EnvironmentManager':
        """Create EnvironmentManager from CLI context"""
        env_type = ctx.params.get('env_type', 'local')
        return cls(
            env_type=env_type,
            venv_path=ctx.params.get('venv_path'),
            docker_image=ctx.params.get('docker_image'),
            remote_host=ctx.params.get('remote_host'),
            jvm_options=ctx.params.get('jvm_options')
        )
    
    def create_virtualenv(self, path: str = None, python: str = None) -> bool:
        """Create a new virtual environment
        
        Args:
            path: Path where to create the virtual environment
            python: Python interpreter to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        path = path or self.venv_path
        if not path:
            console.print("[red]No path specified for virtual environment[/red]")
            return False
            
        cmd = [sys.executable, "-m", "venv"]
        if python:
            cmd.extend(["--python", python])
        cmd.append(path)
        
        try:
            subprocess.run(cmd, check=True)
            self.venv_path = path
            self.venv_python = os.path.join(path, 'bin', 'python')
            if not os.path.exists(self.venv_python):
                self.venv_python = os.path.join(path, 'Scripts', 'python.exe')
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to create virtual environment: {e}[/red]")
            return False
    
    def install_requirements(self, requirements: List[str] = None, requirements_file: str = None) -> bool:
        """Install Python packages in the environment
        
        Args:
            requirements: List of package specifications
            requirements_file: Path to requirements file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.venv_python:
            console.print("[red]No virtual environment active[/red]")
            return False
            
        cmd = [self.venv_python, "-m", "pip", "install", "--upgrade", "pip"]
        
        try:
            subprocess.run(cmd, check=True)
            
            if requirements_file:
                cmd = [self.venv_python, "-m", "pip", "install", "-r", requirements_file]
                subprocess.run(cmd, check=True)
            
            if requirements:
                cmd = [self.venv_python, "-m", "pip", "install"] + requirements
                subprocess.run(cmd, check=True)
                
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to install requirements: {e}[/red]")
            return False
    
    def execute_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Execute a command in the environment
        
        Args:
            command: Command to execute as list of strings
            **kwargs: Additional arguments to subprocess.run()
            
        Returns:
            subprocess.CompletedProcess: Result of the command execution
        """
        if self.env_type == 'docker':
            return self._execute_in_docker(command, **kwargs)
        elif self.env_type == 'jvm':
            return self._execute_in_jvm(command, **kwargs)
        elif self.env_type == 'remote':
            return self._execute_remote(command, **kwargs)
        else:  # local
            return self._execute_local(command, **kwargs)
    
    def _execute_local(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Execute command in local environment"""
        env = os.environ.copy()
        if self.venv_python:
            # Add virtual environment's bin/Scripts to PATH
            venv_bin = os.path.dirname(self.venv_python)
            env['PATH'] = f"{venv_bin}{os.pathsep}{env['PATH']}"
        
        return subprocess.run(
            command,
            env=env,
            **kwargs
        )
    
    def _execute_in_docker(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Execute command in Docker container"""
        image = self.kwargs.get('docker_image', 'python:3.9')
        volumes = self.kwargs.get('volumes', [])
        
        docker_cmd = ["docker", "run", "--rm"]
        
        # Add volume mounts
        for vol in volumes:
            docker_cmd.extend(["-v", vol])
        
        docker_cmd.append(image)
        docker_cmd.extend(command)
        
        return subprocess.run(docker_cmd, **kwargs)
    
    def _execute_in_jvm(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Execute command using Jython"""
        jython_cmd = ["jython"]
        jython_cmd.extend(command)
        return subprocess.run(jython_cmd, **kwargs)
    
    def _execute_remote(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Execute command on remote host via SSH"""
        host = self.kwargs.get('remote_host')
        if not host:
            raise ValueError("Remote host not specified")
            
        ssh_cmd = ["ssh", host]
        # Properly escape and quote command arguments for SSH
        escaped_args = []
        for arg in command:
            # First escape backslashes, then escape quotes
            escaped = arg.replace('\\', '\\\\').replace('"', '\\"')
            escaped_args.append(f'"{escaped}"')
        ssh_cmd.append(" ".join(escaped_args))
        
        return subprocess.run(" ".join(ssh_cmd), shell=True, **kwargs)


def select_virtualenv() -> Optional[str]:
    """Interactively select a virtual environment"""
    # Common virtual environment locations
    common_paths = [
        os.path.expanduser("~/.virtualenvs"),
        os.path.join(os.getcwd(), ".venv"),
        os.path.join(os.getcwd(), "venv"),
    ]
    
    envs = []
    for path in common_paths:
        if os.path.isdir(path):
            if os.path.basename(path) in ('venv', '.venv'):
                envs.append((path, os.path.dirname(path)))
            else:
                for name in os.listdir(path):
                    env_path = os.path.join(path, name)
                    if os.path.isdir(env_path):
                        envs.append((env_path, name))
    
    if not envs:
        console.print("[yellow]No virtual environments found[/yellow]")
        return None
    
    console.print("\n[bold]Available virtual environments:[/bold]")
    for i, (path, name) in enumerate(envs, 1):
        console.print(f"  {i}. {name} ({path})")
    
    try:
        choice = int(input("\nSelect environment (number) or 0 to skip: "))
        if 1 <= choice <= len(envs):
            return envs[choice - 1][0]
    except (ValueError, IndexError):
        pass
    
    return None
