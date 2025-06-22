"""
Git repository loader for DIGY
Handles downloading and caching repositories in RAM
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import yaml
from dotenv import load_dotenv
from git import Repo  # type: ignore
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Make docker import optional
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

from .deployer import Deployer
from .interactive import InteractiveMenu

console = Console()

class MemoryManager:
    """Manages memory allocation for loaded repositories."""

    def __init__(self, base_size_mb: int = 100):
        """Initialize memory manager with base size in MB."""
        self.base_size_mb = base_size_mb
        self.allocated_repos: Dict[str, int] = {}

    def check_available_memory(self) -> int:
        """Check available RAM in MB."""
        if sys.platform == 'linux' or sys.platform == 'linux2':
            with open('/proc/meminfo', 'r') as mem:
                mem.readline()  # Skip first line
                mem_available = int(mem.readline().split()[1]) / 1024
                return int(mem_available)
        elif sys.platform == 'darwin':
            mem = subprocess.check_output(['vm_stat']).decode('ascii')
            pages_free = int(re.search(r'Pages free:[\s]+(\d+)', mem).group(1))
            pages_inactive = int(re.search(r'Pages inactive:[\s]+(\d+)', mem).group(1))
            page_size = os.sysconf('hw.pagesize')
            return int((pages_free + pages_inactive) * page_size / (1024 * 1024))
        return 2000  # Default to 2GB if we can't determine available memory

    def can_allocate(self, size_mb: int) -> bool:
        """Check if we can allocate memory for repository."""
        available = self.check_available_memory()
        return available >= size_mb

    def allocate(self, repo_url: str, size_mb: int) -> bool:
        """Allocate memory for repository."""
        if self.can_allocate(size_mb):
            self.allocated_repos[repo_url] = size_mb
            return True
        return False

    def deallocate(self, repo_url: str) -> None:
        """Deallocate memory for repository."""
        self.allocated_repos.pop(repo_url, None)

memory_manager = MemoryManager()

class GitLoader:
    """Loads Git repositories into memory-based temporary directories"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or tempfile.mkdtemp(prefix="digy_")
        self.loaded_repos: Dict[str, str] = {}
        self.manifest = self.load_manifest()
        self.ram_path = ""  # Initialize ram_path
        self.repo_path = ""  # Initialize repo_path
        self.load_env_config()
        self._docker_client = None

    @property
    def docker_client(self) -> Optional[Any]:
        """Get a Docker client instance if available."""
        if not DOCKER_AVAILABLE:
            return None
            
        try:
            # Test if Docker is actually available and responding
            client = docker.from_env()
            client.ping()  # Simple API call to test connection
            return client
        except Exception as e:
            console.print(f"⚠️ Docker is not available: {e}", style="yellow")
            return None

    def download_repo(self, repo_url: str, branch: str = "main") -> Optional[str]:
        """Download repository to memory-based location"""
        try:
            repo_info = self.parse_repo_url(repo_url)
            local_path = repo_info["local_path"]
            project_name = repo_info['name']

            # Skip RAM disk if we can't create it
            use_ram_disk = os.getenv('DIGY_USE_RAM_DISK', 'true').lower() == 'true'
            ram_disk = None
            
            if use_ram_disk:
                try:
                    ram_size = int(os.getenv('DIGY_RAM_SIZE', 
                                        self.manifest.get('config', {}).get('ram_size', 2)))
                    ram_disk = self.create_ram_disk(ram_size)
                except Exception as e:
                    console.print(f"⚠️ Warning: Could not create RAM disk: {e}")
                    console.print("⚠️ Falling back to temporary directory")
                    ram_disk = None

            # Get volume configuration
            volumes = self.get_volume_config(project_name)
            
            # Try direct Git clone first (bypassing Docker)
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Cloning repository...", total=1)
                try:
                    # Try local Git clone first
                    import shutil
                    import tempfile
                    import os
                    
                    if shutil.which('git') is None:
                        raise Exception("Git is not installed locally")
                        
                    # Create a temporary directory for the clone
                    temp_dir = tempfile.mkdtemp(prefix='digy_')
                    repo_dir = os.path.join(temp_dir, project_name)
                    
                    # Clone the repository locally
                    clone_cmd = [
                        'git', 'clone',
                        '--depth', '1'
                    ]
                    
                    # Add branch if specified
                    if branch:
                        clone_cmd.extend(['--branch', branch])
                    
                    # Add repository URL and target directory
                    clone_cmd.extend([repo_info['url'], repo_dir])
                    
                    progress.print(f"Running: {' '.join(clone_cmd)}")
                    
                    # Execute the Git command
                    result = subprocess.run(
                        clone_cmd,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        error_msg = f"Git clone failed with return code {result.returncode}"
                        if result.stderr:
                            error_msg += f": {result.stderr.strip()}"
                        if result.stdout:
                            error_msg += f"\nOutput: {result.stdout.strip()}"
                        raise Exception(error_msg)
                    
                    progress.update(task, advance=1, description="✅ Repository cloned with Git")
                    return f"file://{repo_dir}"
                    
                except Exception as e:
                    progress.print(f"❌ Git clone failed: {e}")
                    progress.print("⚠️ Falling back to direct download")
                    
                    # Ensure we have a clean state
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    # Create a new temporary directory for the zip download
                    temp_dir = tempfile.mkdtemp(prefix='digy_zip_')
                    progress.print("Attempting to download repository as zip...")
                    
                    try:
                        # Construct the zip URL based on the repository URL format
                        if 'github.com' in repo_info['url']:
                            # GitHub format: https://github.com/owner/repo/archive/refs/heads/branch.zip
                            repo_path = repo_info['url'].replace('https://', '').replace('git@github.com:', '').replace('.git', '')
                            zip_url = f"https://github.com/{repo_path}/archive/refs/heads/{branch if branch else 'main'}.zip"
                        else:
                            # Fallback for other Git providers that support zip downloads
                            zip_url = f"{repo_info['url'].replace('.git', '')}/archive/refs/heads/{branch if branch else 'main'}.zip"
                        
                        zip_path = os.path.join(temp_dir, 'repo.zip')
                        progress.print(f"Downloading {zip_url}...")
                        
                        # Download the zip file
                        response = requests.get(zip_url, stream=True)
                        response.raise_for_status()
                        
                        # Write the zip file
                        with open(zip_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        # Extract the zip file
                        progress.print("Extracting repository...")
                        import zipfile
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        
                        # Get the extracted directory name
                        extracted_dirs = [d for d in os.listdir(temp_dir) 
                                       if os.path.isdir(os.path.join(temp_dir, d)) 
                                       and d != os.path.basename(local_path)]
                        
                        if not extracted_dirs:
                            raise Exception("No directories found in downloaded zip")
                        
                        extracted_path = os.path.join(temp_dir, extracted_dirs[0])
                        
                        # Move the extracted directory to the target location
                        if os.path.exists(local_path):
                            shutil.rmtree(local_path, ignore_errors=True)
                        shutil.move(extracted_path, local_path)
                        
                        progress.update(task, advance=1, description="✅ Repository downloaded and extracted")
                        return f"file://{local_path}"
                        
                    except ImportError:
                        raise Exception("The 'requests' package is required for downloading repositories")
                    except Exception as e:
                        raise Exception(f"Failed to download repository: {e}")
                    finally:
                        # Clean up temporary files
                        if 'zip_path' in locals() and os.path.exists(zip_path):
                            os.remove(zip_path)
                        if 'temp_dir' in locals() and os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir, ignore_errors=True)

                        script_content = f'''#!/bin/bash
set -e
echo "=== Container Environment ==="
echo "PATH: $PATH"
echo "PWD: $(pwd)"
echo "Git: $(which git 2>/dev/null || echo 'git not found')"
echo "Git version: $(git --version 2>/dev/null || echo 'git not available')"

# Clone the repository
echo "Cloning repository..."
git clone --depth 1 --branch {shlex.quote(branch)} {shlex.quote(repo_url)} /app

# Fix permissions
chmod -R a+rw /app
echo "Repository cloned successfully"
'''

                        script_path = os.path.join(temp_dir, 'clone_repo.sh')
                        with open(script_path, 'w', encoding='utf-8') as f:
                            f.write(script_content)
                        
                        # Make the script executable
                        os.chmod(script_path, 0o755)
                        
                        # Generate a unique container name
                        container_name = f"digy-clone-{os.getpid()}"
                        
                        try:
                            # Build the docker run command to clone the repo using our custom image
                            docker_cmd = [
                                'docker', 'run',
                                '--rm',
                                '--name', container_name,
                                '-v', f'{temp_dir}:/app:Z',  # :Z for SELinux compatibility
                                'localhost/digy-base:latest',  # Use our custom image with Git pre-installed
                                '/app/clone_repo.sh',  # Run our script
                                branch,  # Pass branch as first argument
                                repo_info["url"]  # Pass URL as second argument
                            ]
                            
                            # Run the docker command
                            progress.print("Running docker command:", ' '.join(docker_cmd))
                            result = subprocess.run(
                                docker_cmd,
                                capture_output=True,
                                text=True
                            )
                            
                            if result.returncode != 0:
                                error_msg = f"Docker command failed with return code {result.returncode}"
                                if result.stderr:
                                    error_msg += f": {result.stderr.strip()}"
                                if result.stdout:
                                    error_msg += f"\nOutput: {result.stdout.strip()}"
                                progress.print(f"❌ {error_msg}")
                                raise Exception(error_msg)
                            
                            # Get the container ID
                            container_id = result.stdout.strip()
                            progress.update(task, advance=1, description="✅ Repository cloned with Docker")
                            return f"docker://{container_id}"
                            
                        except subprocess.CalledProcessError as e:
                            error_msg = f"Docker command failed with return code {e.returncode}"
                            if e.stderr:
                                error_msg += f": {e.stderr.decode().strip()}"
                            if e.stdout:
                                error_msg += f"\nOutput: {e.stdout.decode().strip()}"
                            progress.print(f"❌ {error_msg}")
                            raise Exception(error_msg) from e
                            
                        except Exception as e:
                            progress.print(f"❌ Error: {e}")
                            # Clean up temp directory and any containers
                            try:
                                if os.path.exists(temp_dir):
                                    shutil.rmtree(temp_dir, ignore_errors=True)
                                subprocess.run(
                                    ['docker', 'rm', '-f', container_name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    check=False
                                )
                            except Exception as cleanup_error:
                                progress.print(f"⚠️ Warning during cleanup: {cleanup_error}")
                            return None

        except Exception as e:
            console.print(f"❌ Error loading repository: {e}")
            return None

    def load_env_config(self) -> None:
        """Load environment variables from .env file"""
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    def load_manifest(self) -> dict:
        """Load manifest file from repository"""
        manifest_path = os.path.join(self.base_path, 'manifest.yml')
        
        try:
            if not os.path.exists(manifest_path):
                console.print("⚠️ Warning: Manifest file not found")
                return {}

            with open(manifest_path, 'r') as f:
                try:
                    return yaml.safe_load(f) or {}
                except yaml.YAMLError as e:
                    console.print(f"⚠️ Warning: Invalid YAML in manifest: {e}")
                    return {}
        except Exception as e:
            console.print(f"⚠️ Warning: Could not load manifest: {e}")
            return {}

    def get_volume_config(self, project_name: str) -> Dict:
        """Get volume configuration for a project"""
        config = self.manifest.get('config', {})
        project_config = self.manifest.get('projects', {}).get(project_name, {})
        
        # Initialize with default volumes
        volumes = {}
        
        # Add default volume from config if it exists
        config_volumes = config.get('volumes', [])
        if config_volumes and len(config_volumes) > 0:
            vol = config_volumes[0]
            volumes[vol.get('path', '/tmp')] = {
                'bind': vol.get('path', '/tmp'),
                'mode': 'rw'
            }
        
        # Add project-specific volumes
        for volume in project_config.get('volumes', []):
            if volume['type'] == 'local':
                volumes[volume['path']] = {
                    'bind': volume['path'],
                    'mode': 'ro' if volume.get('readonly', False) else 'rw'
                }
            elif volume['type'] == 'ram':
                volumes[volume['path']] = {
                    'bind': volume['path'],
                    'mode': 'rw'
                }
        
        return volumes

    def create_ram_disk(self, size_gb: int = 2) -> str:
        """Create RAM disk mount point"""
        ram_disk = "/tmp/digy_ram"
        os.makedirs(ram_disk, exist_ok=True)
        os.system(f"mount -t tmpfs -o size={size_gb}G tmpfs {ram_disk}")
        return ram_disk

    def parse_repo_url(self, url: str) -> Dict[str, str]:
        """Parse repository URL and extract components.
        
        Args:
            url: Repository URL to parse
            
        Returns:
            Dict containing URL components and local path
        """
        # Handle SSH format (git@github.com:user/repo.git)
        if url.startswith('git@'):
            url = url.replace('git@', 'https://').replace(':', '/')
        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        # Extract repo name for local directory
        repo_name = url.split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        return {
            "url": url,
            "name": repo_name,
            "local_path": str(Path(self.base_path) / repo_name)
        }

    def _clone_repository(self, repo_info: Dict[str, str], branch: str) -> Optional[str]:
        """Clone a repository with branch fallback logic.
        
        Args:
            repo_info: Dictionary containing repository info
            branch: Preferred branch to checkout
            
        Returns:
            str: Path to cloned repository or None if failed
        """
        local_path = repo_info["local_path"]
        project_name = repo_info['name']

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Cloning {project_name}...", total=None)

            try:
                branches_to_try = [branch, "main", "master"]
                repo = None

                for branch_name in branches_to_try:
                    try:
                        repo = Repo.clone_from(
                            repo_info["url"],
                            local_path,
                            branch=branch_name,
                            depth=1  # Shallow clone to save memory
                        )
                        break
                    except Exception:
                        continue

                if repo is None:
                    raise Exception("Failed to clone with any branch")

                progress.update(task, description=f"✅ Cloned {project_name}")
                return local_path

            except Exception as e:
                console.print(f"❌ Failed to clone repository: {e}")
                return None

    def download_repo(self, repo_url: str, branch: str = "main") -> Optional[str]:
        """Download repository to memory-based location.
        
        Args:
            repo_url: URL of the repository to download
            branch: Branch to checkout (default: main)
            
        Returns:
            str: Path to the downloaded repository or None if failed
        """
        try:
            repo_info = self.parse_repo_url(repo_url)
            project_name = repo_info['name']

            if repo_url in self.loaded_repos:
                console.print(f"✅ Repository already loaded: {project_name}")
                return self.loaded_repos[repo_url]

            if not memory_manager.allocate(repo_url, memory_manager.base_size_mb):
                console.print("❌ Insufficient memory to load repository")
                return None

            # Create RAM disk with configured size
            ram_size = int(os.getenv(
                'DIGY_RAM_SIZE',
                self.manifest.get('config', {}).get('ram_size', 2)
            ))
            self.create_ram_disk(ram_size)

            local_path = self._clone_repository(repo_info, branch)
            if local_path:
                self.loaded_repos[repo_url] = local_path
                console.print(f"📦 Repository loaded to: {local_path}")
                return local_path
            
            memory_manager.deallocate(repo_url)
            return None

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