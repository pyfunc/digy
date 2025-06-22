"""
Application deployer for DIGY
Handles Python application deployment in isolated environments
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from virtualenv import cli_run
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Deployer:
    """Deploys Python applications in isolated virtual environments"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.venv_path = None
        self.python_files = []
        self.requirements_files = []
        self.setup_files = []
        self.discover_files()

    def discover_files(self):
        """Discover Python files and configuration files in repository"""
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if
                       not d.startswith('.') and d not in ['__pycache__', 'build', 'dist', 'node_modules']]

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)

                if file.endswith('.py'):
                    self.python_files.append(rel_path)
                elif file in ['requirements.txt', 'requirements-dev.txt', 'requirements-test.txt']:
                    self.requirements_files.append(rel_path)
                elif file in ['setup.py', 'setup.cfg', 'pyproject.toml']:
                    self.setup_files.append(rel_path)

    def create_virtual_environment(self) -> bool:
        """Create isolated virtual environment"""
        try:
            self.venv_path = tempfile.mkdtemp(prefix="digy_venv_")

            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
            ) as progress:
                task = progress.add_task("Creating virtual environment...", total=None)

                # Create virtual environment using the new API
                cli_run([self.venv_path])
                progress.update(task, description="✅ Virtual environment created")

            console.print(f"🐍 Virtual environment: {self.venv_path}")
            return True

        except Exception as e:
            console.print(f"❌ Failed to create virtual environment: {e}")
            return False

    def get_python_executable(self) -> str:
        """Get Python executable path in virtual environment"""
        if os.name == 'nt':  # Windows
            return os.path.join(self.venv_path, 'Scripts', 'python.exe')
        else:  # Unix/Linux/macOS
            return os.path.join(self.venv_path, 'bin', 'python')

    def get_pip_executable(self) -> str:
        """Get pip executable path in virtual environment"""
        if os.name == 'nt':  # Windows
            return os.path.join(self.venv_path, 'Scripts', 'pip.exe')
        else:  # Unix/Linux/macOS
            return os.path.join(self.venv_path, 'bin', 'pip')

    def install_requirements(self) -> bool:
        """Install requirements in virtual environment"""
        if not self.requirements_files:
            console.print("ℹ️ No requirements files found")
            return True

        try:
            pip_executable = self.get_pip_executable()

            for req_file in self.requirements_files:
                req_path = os.path.join(self.repo_path, req_file)
                console.print(f"📦 Installing requirements from: {req_file}")

                result = subprocess.run([
                    pip_executable, 'install', '-r', req_path
                ], capture_output=True, text=True, cwd=self.repo_path)

                if result.returncode != 0:
                    console.print(f"❌ Failed to install {req_file}:")
                    console.print(result.stderr)
                    return False
                else:
                    console.print(f"✅ Installed requirements from {req_file}")

            return True

        except Exception as e:
            console.print(f"❌ Error installing requirements: {e}")
            return False

    def install_package(self) -> bool:
        """Install package if setup files exist"""
        if not self.setup_files:
            return True

        try:
            pip_executable = self.get_pip_executable()

            console.print("📦 Installing package in development mode...")
            result = subprocess.run([
                pip_executable, 'install', '-e', '.'
            ], capture_output=True, text=True, cwd=self.repo_path)

            if result.returncode != 0:
                console.print("❌ Failed to install package:")
                console.print(result.stderr)
                return False
            else:
                console.print("✅ Package installed successfully")

            return True

        except Exception as e:
            console.print(f"❌ Error installing package: {e}")
            return False

    def run_python_file(self, file_path: str, args: List[str] = None) -> Tuple[bool, str, str]:
        """Run a Python file in the virtual environment"""
        # Ensure environment is properly set up
        if not self.setup_environment():
            return False, "", "Failed to set up environment"

        python_executable = self.get_python_executable()
        full_path = os.path.join(self.repo_path, file_path)

        if not os.path.exists(full_path):
            return False, "", f"File not found: {file_path}"

        # Prepare command
        cmd = [python_executable, full_path]
        if args:
            cmd.extend(args)

        console.print(f"🚀 Running: {' '.join(cmd)}")

        try:
            # Run the file
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=300  # 5-minute timeout
            )

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", "Process timed out after 5 minutes"
        except Exception as e:
            return False, "", f"Error running file: {e}"

    def setup_environment(self) -> bool:
        """Set up the complete deployment environment"""
        console.print("🔧 Setting up deployment environment...")

        if not self.create_virtual_environment():
            return False

        if not self.install_requirements():
            return False

        if not self.install_package():
            return False

        console.print("✅ Environment setup complete!")
        return True

    def get_file_info(self, file_path: str) -> Dict:
        """Get information about a Python file"""
        full_path = os.path.join(self.repo_path, file_path)
        info = {
            "path": file_path,
            "full_path": full_path,
            "exists": os.path.exists(full_path),
            "size": 0,
            "lines": 0,
            "has_main": False,
            "imports": []
        }

        if info["exists"]:
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    info["size"] = len(content)
                    info["lines"] = len(content.splitlines())
                    info["has_main"] = 'if __name__ == "__main__"' in content

                    # Simple import detection
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith(('import ', 'from ')):
                            info["imports"].append(line)
            except Exception:
                pass

        return info

    def cleanup(self, force: bool = False):
        """Clean up virtual environment
        
        Args:
            force: If True, clean up even if the environment is still active
        """
        if not force and self.venv_path and os.path.exists(self.venv_path):
            # Don't clean up if there are active processes
            python_executable = self.get_python_executable()
            if os.path.exists(python_executable):
                try:
                    # Check if any processes are using the Python executable
                    for proc in psutil.process_iter(['pid', 'name', 'exe']):
                        if proc.info['exe'] and proc.info['exe'].startswith(self.venv_path):
                            console.print("⚠️ Virtual environment is still in use")
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        if self.venv_path and os.path.exists(self.venv_path):
            try:
                shutil.rmtree(self.venv_path)
                console.print(f"🗑️ Cleaned up virtual environment: {self.venv_path}")
            except Exception as e:
                console.print(f"⚠️ Error cleaning up virtual environment: {e}")
        self.venv_path = None