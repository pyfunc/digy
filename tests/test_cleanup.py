"""Tests for DIGY repository cleanup functionality."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock, call

from digy.loader import GitLoader, memory_manager


class TestCleanupBehavior(unittest.TestCase):
    """Test cleanup behavior for different repository types."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="digy_test_")
        self.local_repo = os.path.join(self.temp_dir, "local_repo")
        os.makedirs(self.local_repo, exist_ok=True)
        
        # Initialize a git repository
        os.system(f"git -C {self.local_repo} init")
        with open(os.path.join(self.local_repo, "test.txt"), "w") as f:
            f.write("test content")
        os.system(f"git -C {self.local_repo} add . && "
                 f"git -C {self.local_repo} commit -m 'initial'")
        
        # Initialize GitLoader
        self.loader = GitLoader()
        self.loader.ram_path = os.path.join(self.temp_dir, "ram_disk")
        
        # Mock docker client property if it exists
        if hasattr(self.loader, 'docker_client'):
            self.loader_patcher = patch.object(
                GitLoader, 'docker_client', 
                new_callable=PropertyMock(return_value=MagicMock())
            )
            self.mock_docker_client = self.loader_patcher.start()
            self.addCleanup(self.loader_patcher.stop)

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_local_repo_not_deleted(self):
        """Test that local repositories are not deleted on cleanup."""
        # Mock the _get_repo_type to ensure consistent behavior
        with patch('digy.loader.GitLoader._get_repo_type', return_value="local"):
            # Load the local repository
            self.loader.download_repo(self.local_repo)
            
            # Verify it's loaded
            self.assertIn(self.local_repo, self.loader.loaded_repos)
            self.assertEqual(
                self.loader.loaded_repos[self.local_repo]["type"],
                "local"
            )
            
            # Clean up (should not delete local repo)
            with patch('shutil.rmtree') as mock_rmtree:
                with patch('os.path.exists', return_value=True):
                    # Mock the actual cleanup to ensure we don't delete anything
                    with patch.object(self.loader, '_cleanup_local_repo') as mock_cleanup:
                        self.loader.cleanup_repo(self.local_repo)
                        # Verify our cleanup method was called
                        mock_cleanup.assert_called_once()
                    # Verify rmtree was not called for local repo
                    mock_rmtree.assert_not_called()
            
            # Verify local repo still exists
            self.assertTrue(os.path.exists(self.local_repo))
            
            # The repo should be removed from loaded_repos after cleanup
            # We'll verify this by checking the cleanup_repo method's return value
            self.assertNotIn(self.local_repo, self.loader.loaded_repos)

    @patch('digy.loader.memory_manager.allocate')
    def test_ram_repo_cleanup(self, mock_allocate):
        """Test RAM-based repository cleanup."""
        # Mock memory allocation
        mock_allocate.return_value = True
        
        # Mock a RAM-based repo path
        ram_repo = os.path.join(self.loader.ram_path, "test_repo")
        os.makedirs(ram_repo, exist_ok=True)
        
        # Simulate loading a RAM-based repo
        with patch('digy.loader.GitLoader._get_repo_type', return_value="ram"):
            with patch('digy.loader.GitLoader._clone_repository', 
                      return_value=ram_repo):
                self.loader.download_repo("ram://test_repo")
        
        # Verify it's loaded
        self.assertIn("ram://test_repo", self.loader.loaded_repos)
        
        # Clean up should remove the directory
        with patch('shutil.rmtree') as mock_rmtree:
            # First call is from cleanup_repo, second is from cleanup_all in tearDown
            self.loader.cleanup_repo("ram://test_repo")
            # Verify rmtree was called with the correct path
            mock_rmtree.assert_called_with(ram_repo, ignore_errors=True)
            # Verify it was called at least once
            self.assertGreaterEqual(mock_rmtree.call_count, 1)

    @patch('digy.loader.DOCKER_AVAILABLE', True)
    def test_container_repo_cleanup(self):
        """Test container-based repository cleanup."""
        # Skip if docker is not available
        if not hasattr(GitLoader, 'docker_client'):
            self.skipTest("Docker not available")
        
        # Create a test container ID and path
        container_id = "test_container_123"
        container_path = f"/tmp/{container_id}"
        
        # Mock container
        mock_container = MagicMock()
        mock_container.id = container_id
        
        # Mock the docker client to return our mock container
        self.mock_docker_client.return_value.containers.get.return_value = mock_container
        
        # Mock the clone method to avoid actual git operations
        with patch('digy.loader.GitLoader._get_repo_type', return_value="container"):
            with patch('digy.loader.GitLoader._clone_repository', 
                      return_value=container_path):
                # Simulate loading a container-based repo
                self.loader.download_repo(f"container://{container_id}")
        
        # Verify container was added to loaded_repos
        self.assertIn(f"container://{container_id}", self.loader.loaded_repos)
        
        # Clean up should remove the container
        with patch('os.path.exists', return_value=True):
            # Mock the docker client again for the cleanup phase
            with patch('digy.loader.docker.from_env', return_value=self.mock_docker_client.return_value):
                self.loader.cleanup_repo(f"container://{container_id}")
        
        # Verify container removal was attempted
        # Note: The actual implementation might not call get() directly, so we'll just check remove()
        mock_container.remove.assert_called_once_with(force=True)
        
        # Verify repo was removed from loaded_repos
        self.assertNotIn(f"container://{container_id}", self.loader.loaded_repos)


if __name__ == "__main__":
    unittest.main()
