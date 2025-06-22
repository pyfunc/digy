"""
Tests for DIGY loader module
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from digy.loader import GitLoader, MemoryManager, digy


class TestMemoryManager:
    """Test MemoryManager functionality"""

    def test_memory_manager_initialization(self):
        """Test MemoryManager initialization"""
        manager = MemoryManager(base_size_mb=50)
        assert manager.base_size_mb == 50
        assert manager.allocated_repos == {}

    def test_check_available_memory(self):
        """Test memory availability check"""
        manager = MemoryManager()
        available = manager.check_available_memory()
        assert isinstance(available, int)
        assert available > 0

    def test_memory_allocation(self):
        """Test memory allocation and deallocation"""
        manager = MemoryManager()
        repo_url = "test_repo"

        # Test allocation
        result = manager.allocate(repo_url, 50)
        assert isinstance(result, bool)

        if result:  # If allocation successful
            assert repo_url in manager.allocated_repos
            assert manager.allocated_repos[repo_url] == 50

            # Test deallocation
            manager.deallocate(repo_url)
            assert repo_url not in manager.allocated_repos


class TestGitLoader:
    """Test GitLoader functionality"""

    def test_git_loader_initialization(self):
        """Test GitLoader initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = GitLoader(temp_dir)
            assert loader.base_path == temp_dir
            assert loader.loaded_repos == {}

    def test_parse_repo_url(self):
        """Test repository URL parsing"""
        loader = GitLoader()

        # Test different URL formats
        test_cases = [
            ("github.com/user/repo", "https://github.com/user/repo"),
            ("https://github.com/user/repo", "https://github.com/user/repo"),
            ("https://github.com/user/repo.git", "https://github.com/user/repo.git")
        ]

        for input_url, expected_url in test_cases:
            result = loader.parse_repo_url(input_url)
            assert result["url"] == expected_url
            assert "name" in result
            assert "local_path" in result

    @patch('git.Repo.clone_from')
    @patch('digy.loader.memory_manager')
    @patch('subprocess.run')
    def test_download_repo_success(self, mock_run, mock_memory_manager, mock_clone):
        """Test successful repository download"""
        # Setup mocks
        mock_memory_manager.allocate.return_value = True
        mock_repo = MagicMock()
        mock_clone.return_value = mock_repo
        mock_run.return_value.returncode = 0
        
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = GitLoader(temp_dir)
            loader._docker_client = None  # Mock no Docker available
            loader.manifest = {}  # Mock empty manifest
            loader.base_path = temp_dir  # Set base path for manifest
            loader.ram_path = temp_dir  # Set ram_path for the test
            
            # Mock the clone_from to return a repo with working_dir
            mock_repo.working_dir = os.path.join(temp_dir, "repo")
            os.makedirs(mock_repo.working_dir, exist_ok=True)
            
            result = loader.download_repo("github.com/user/repo")
    
            assert result is not None
            assert result == os.path.join(temp_dir, "repo")
            assert "github.com/user/repo" in loader.loaded_repos

    @patch('digy.loader.memory_manager')
    def test_download_repo_memory_failure(self, mock_memory_manager):
        """Test repository download failure due to insufficient memory"""
        mock_memory_manager.allocate.return_value = False

        with tempfile.TemporaryDirectory() as temp_dir:
            loader = GitLoader(temp_dir)
            result = loader.download_repo("github.com/user/repo")

            assert result is None

    def test_cleanup_repo(self):
        """Test repository cleanup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            loader = GitLoader(temp_dir)

            # Simulate loaded repository
            repo_url = "test_repo"
            repo_path = os.path.join(temp_dir, "test")
            os.makedirs(repo_path, exist_ok=True)
            loader.loaded_repos[repo_url] = repo_path

            # Test cleanup
            loader.cleanup_repo(repo_url)
            assert repo_url not in loader.loaded_repos


class TestDigyFunction:
    """Test main digy function"""

    @patch('digy.loader.InteractiveMenu')
    @patch('digy.loader.Deployer')
    @patch('digy.loader.loader_instance')
    def test_digy_function(self, mock_loader, mock_deployer_class, mock_menu_class):
        """Test main digy function"""
        # Setup mocks
        mock_loader.download_repo.return_value = "/fake/path"
        mock_deployer = MagicMock()
        mock_deployer_class.return_value = mock_deployer
        mock_menu = MagicMock()
        mock_menu_class.return_value = mock_menu

        # Test digy function
        result = digy("github.com/user/repo")

        # Verify calls
        mock_loader.download_repo.assert_called_once_with("github.com/user/repo", "main")
        mock_deployer_class.assert_called_once_with("/fake/path")
        mock_menu_class.assert_called_once()
        mock_menu.run.assert_called_once()
        mock_loader.cleanup_repo.assert_called_once_with("github.com/user/repo")

        assert result == "/fake/path"

    @patch('digy.loader.loader_instance')
    def test_digy_function_download_failure(self, mock_loader):
        """Test digy function when download fails"""
        mock_loader.download_repo.return_value = None

        result = digy("github.com/user/repo")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])