"""
Git repository loader for DIGY
Handles downloading and caching repositories in RAM
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import git
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import psutil

from .deployer import Deployer
from .interactive import InteractiveMenu

console = Console()

class MemoryManager:
    """Manages memory allocation for loaded repositories"""

    def __init__(self, base_size_mb: int = 100):
        self.base_size_mb = base_size_mb
        self.allocated_repos: Dict[str, int] = {}

    def check_available_memory(self) -> int:
        """Check available RAM in MB"""
        memory = psutil.virtual_memory()
        return memory.available // (1024 * 1024)

    def can_allocate(self, size_mb: int) -> bool:
        """Check if we can allocate memory for repository"""
        available = self.check_available_memory()
        return available > size_mb + 200  # Keep 200MB buffer

    def allocate(self, repo_url: str, size_mb: int) -> bool:
        """Allocate memory for repository"""
        if self.can_allocate(size_mb):
            self.allocated_repos[repo_url] = size_mb
            return True
        return False

    def deallocate(self, repo_url: str):
        """Deallocate memory for repository"""
        if repo_url in self.allocated_repos:
            del self.allocated_repos[repo_url]

memory_manager = MemoryManager()

class GitLoader:
    """Loads Git repositories into memory-based temporary directories"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or tempfile.mkdtemp(prefix="digy_")
        self.loaded_repos: Dict[str, str] = {}

    def parse_repo_url(self, url: str) -> Dict[str, str]:
        """Parse repository URL and extract components"""
        if url.startswith("github.com/"):
            url = f"https://{url}"
        elif not url.startswith(("http://", "https://")):
            url = f"https://github.com/{url}"

        # Extract repo name for local directory
        repo_name = url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        return {
            "url": url,
            "name": repo_name,
            "local_path": os.path.join(self.base_path, repo_name)
        }

    def download_repo(self, repo_url: str, branch: str = "main") -> Optional[str]:
        """Download repository to memory-based location"""
        try:
            repo_info = self.parse_repo_url(repo_url)
            local_path = repo_info["local_path"]

            # Check if already loaded
            if repo_url in self.loaded_repos:
                console.print(f"✅ Repository already loaded: {repo_info['name']}")
                return self.loaded_repos[repo_url]

            # Check memory availability
            if not memory_manager.allocate(repo_url, memory_manager.base_size_mb):
                console.print("❌ Insufficient memory to load repository")
                return None

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Cloning {repo_info['name']}...", total=None)

                try:
                    # Try different branch names
                    branches_to_try = [branch, "main", "master"]
                    repo = None

                    for branch_name in branches_to_try:
                        try:
                            repo = git.Repo.clone_from(
                                repo_info["url"],
                                local_path,
                                branch=branch_name,
                                depth=1  # Shallow clone to save memory
                            )
                            break
                        except git.GitCommandError:
                            continue

                    if repo is None:
                        raise git.GitCommandError("Failed to clone with any branch")

                    progress.update(task, description=f"✅ Cloned {repo_info['name']}")

                except git.GitCommandError as e:
                    console.print(f"❌ Failed to clone repository: {e}")
                    memory_manager.deallocate(repo_url)
                    return None

            self.loaded_repos[repo_url] = local_path
            console.print(f"📦 Repository loaded to: {local_path}")
            return local_path

        except Exception as e:
            console.print(f"❌ Error loading repository: {e}")
            memory_manager.deallocate(repo_url)
            return None

    def cleanup_repo(self, repo_url: str):
        """Clean up loaded repository"""
        if repo_url in self.loaded_repos:
            local_path = self.loaded_repos[repo_url]
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            del self.loaded_repos[repo_url]
            memory_manager.deallocate(repo_url)
            console.print(f"🗑️ Cleaned up repository: {repo_url}")

    def cleanup_all(self):
        """Clean up all loaded repositories"""
        for repo_url in list(self.loaded_repos.keys()):
            self.cleanup_repo(repo_url)

        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)

loader_instance = GitLoader()

def digy(repo_url: str, branch: str = "main") -> Optional[str]:
    """
    Main digy function - downloads repository and starts interactive menu

    Args:
        repo_url: Repository URL (github.com/user/repo or full URL)
        branch: Branch to checkout (default: main)

    Returns:
        Local path to loaded repository or None if failed
    """
    console.print(f"🚀 DIGY - Loading repository: {repo_url}")

    # Download repository
    local_path = loader_instance.download_repo(repo_url, branch)
    if not local_path:
        return None

    # Check for README
    readme_path = None
    for readme_name in ["README.md", "README.txt", "README.rst", "readme.md"]:
        potential_path = os.path.join(local_path, readme_name)
        if os.path.exists(potential_path):
            readme_path = potential_path
            break

    if not readme_path:
        console.print("⚠️ No README file found")

    # Create deployer and interactive menu
    deployer = Deployer(local_path)
    menu = InteractiveMenu(local_path, deployer, readme_path)

    try:
        # Start interactive session
        menu.run()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
    finally:
        # Cleanup - only clean up the repo, not the virtual environment
        loader_instance.cleanup_repo(repo_url)
        # Force cleanup of virtual environment if it exists
        if deployer.venv_path:
            deployer.cleanup(force=True)

    return local_path

def digy_command():
    """Command-line entry point for digy"""
    if len(sys.argv) < 2:
        console.print("Usage: digy <repository_url> [branch]")
        sys.exit(1)

    repo_url = sys.argv[1]
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"

    digy(repo_url, branch)

# Backward compatibility
load = digy
load_command = digy_command