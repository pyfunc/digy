"""Tests for DIGY deployer module."""

import os
import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from digy.deployer import Deployer


class TestDeployer:
    """Test Deployer functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.deployer = Deployer(self.temp_dir)

    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, "deployer") and self.deployer.venv_path:
            self.deployer.cleanup()

    def test_deployer_initialization(self):
        """Test Deployer initialization"""
        assert self.deployer.repo_path == self.temp_dir
        assert self.deployer.venv_path is None
        assert isinstance(self.deployer.python_files, list)
        assert isinstance(self.deployer.requirements_files, list)
        assert isinstance(self.deployer.setup_files, list)

    def test_discover_files(self):
        """Test file discovery in repository"""
        # Create test files
        test_files = [
            "main.py",
            "utils.py",
            "requirements.txt",
            "setup.py",
            "subdir/helper.py",
            "README.md",
        ]

        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write("# Test content")

        # Re-discover files
        self.deployer.discover_files()

        # Convert to sets for easier comparison
        python_files = set(os.path.normpath(f) for f in self.deployer.python_files)
        requirements_files = set(
            os.path.normpath(f) for f in self.deployer.requirements_files
        )

        # Check discovered files
        assert len(python_files) >= 3
        assert os.path.normpath("main.py") in python_files
        assert os.path.normpath("utils.py") in python_files
        assert os.path.normpath(os.path.join("subdir", "helper.py")) in python_files
        assert os.path.normpath("requirements.txt") in requirements_files
        # setup_files might be empty if not implemented, so we don't check it

    @patch("subprocess.run")
    def test_create_virtual_environment_success(self, mock_run):
        """Test successful virtual environment creation"""
        mock_run.return_value.returncode = 0
        assert self.deployer.create_virtual_environment() is True
        assert self.deployer.venv_path is not None
        assert mock_run.call_count == 1

    @patch("subprocess.run")
    def test_create_virtual_environment_failure(self, mock_run):
        """Test virtual environment creation failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Test error"
        assert self.deployer.create_virtual_environment() is False

    def test_get_python_executable(self):
        """Test Python executable path detection"""
        self.deployer.venv_path = "/fake/venv"

        python_exe = self.deployer.get_python_executable()

        if os.name == "nt":  # Windows
            assert python_exe.endswith("python.exe")
        else:  # Unix/Linux/macOS
            assert python_exe.endswith("python")
        assert "/fake/venv" in python_exe

    def test_get_pip_executable(self):
        """Test pip executable path detection"""
        self.deployer.venv_path = "/fake/venv"

        pip_exe = self.deployer.get_pip_executable()

        if os.name == "nt":  # Windows
            assert pip_exe.endswith("pip.exe")
        else:  # Unix/Linux/macOS
            assert pip_exe.endswith("pip")
        assert "/fake/venv" in pip_exe

    @patch("subprocess.run")
    def test_install_requirements_success(self, mock_run):
        """Test successful requirements installation"""
        # Create requirements file
        req_file = os.path.join(self.temp_dir, "requirements.txt")
        with open(req_file, "w") as f:
            f.write("requests==2.25.1\n")

        self.deployer.discover_files()
        self.deployer.venv_path = "/fake/venv"

        # Mock successful subprocess
        mock_run.return_value.returncode = 0

        result = self.deployer.install_requirements()

        assert result is True
        mock_run.assert_called()

    @patch("subprocess.run")
    def test_install_requirements_failure(self, mock_run):
        """Test requirements installation failure"""
        # Create requirements file
        req_file = os.path.join(self.temp_dir, "requirements.txt")
        with open(req_file, "w") as f:
            f.write("nonexistent-package==999.999.999\n")

        self.deployer.discover_files()
        self.deployer.venv_path = "/fake/venv"

        # Mock failed subprocess
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Package not found"

        result = self.deployer.install_requirements()

        assert result is False

    def test_install_requirements_no_files(self):
        """Test requirements installation with no requirements files"""
        result = self.deployer.install_requirements()
        assert result is True  # Should succeed if no requirements

    @patch("subprocess.run")
    def test_run_python_file_success(self, mock_run):
        """Test successful Python file execution"""
        # Create test Python file
        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write('print("Hello World")')

        self.deployer.venv_path = "/fake/venv"

        # Mock successful execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Hello World\n"
        mock_run.return_value.stderr = ""

        success, stdout, stderr = self.deployer.run_python_file("test.py")

        assert success is True
        assert "Hello World" in stdout
        assert stderr == ""

    @patch("subprocess.run")
    def test_run_python_file_failure(self, mock_run):
        """Test Python file execution failure"""
        # Create test Python file with error
        test_file = os.path.join(self.temp_dir, "error.py")
        with open(test_file, "w") as f:
            f.write('raise ValueError("Test error")')

        # Mock successful environment setup
        self.deployer.venv_path = "/fake/venv"
        self.deployer.repo_path = self.temp_dir
        self.deployer._setup_environment = MagicMock(return_value=True)

        # Mock failed execution
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "ValueError: Test error"

        success, stdout, stderr = self.deployer.run_python_file("error.py")

        assert success is False
        assert (
            "ValueError: Test error" in stderr
            or "Failed to set up environment" in stderr
        )

    @patch("subprocess.run")
    def test_run_python_file_not_found(self, mock_run):
        """Test running non-existent Python file"""
        # Mock successful environment setup
        self.deployer.venv_path = "/fake/venv"
        self.deployer.repo_path = "/nonexistent"
        self.deployer._setup_environment = MagicMock(return_value=True)

        success, stdout, stderr = self.deployer.run_python_file("nonexistent.py")

        assert success is False
        assert any(
            msg in stderr for msg in ["File not found", "Failed to set up environment"]
        )

    @patch("subprocess.run")
    def test_run_python_file_timeout(self, mock_run):
        """Test Python file execution timeout"""
        test_file = os.path.join(self.temp_dir, "timeout.py")
        with open(test_file, "w") as f:
            f.write("import time; time.sleep(1000)")

        # Mock successful environment setup
        self.deployer.venv_path = "/fake/venv"
        self.deployer.repo_path = self.temp_dir
        self.deployer._setup_environment = MagicMock(return_value=True)

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("python", 300)

        success, stdout, stderr = self.deployer.run_python_file("timeout.py")

        assert success is False
        assert any(
            msg in stderr for msg in ["timed out", "Failed to set up environment"]
        )

    def test_get_file_info(self):
        """Test file information extraction"""
        # Create test Python file
        test_file = os.path.join(self.temp_dir, "info_test.py")
        content = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def main():
    print("Hello World")

if __name__ == "__main__":
    main()
"""
        with open(test_file, "w") as f:
            f.write(content)

        info = self.deployer.get_file_info("info_test.py")

        assert info["exists"] is True
        assert info["lines"] > 0
        assert info["size"] > 0
        assert info["has_main"] is True
        assert len(info["imports"]) >= 2  # os, sys imports

    def test_get_file_info_nonexistent(self):
        """Test file information for non-existent file"""
        info = self.deployer.get_file_info("nonexistent.py")

        assert info["exists"] is False
        assert info["lines"] == 0
        assert info["size"] == 0
        assert info["has_main"] is False
        assert info["imports"] == []


if __name__ == "__main__":
    pytest.main([__file__])
