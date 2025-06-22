"""
Tests for DIGY interactive module
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from io import StringIO

from digy.interactive import InteractiveMenu


class TestInteractiveMenu:
    """Test InteractiveMenu functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_deployer = MagicMock()
        self.mock_deployer.python_files = ["main.py", "utils.py"]
        self.mock_deployer.requirements_files = ["requirements.txt"]
        self.mock_deployer.setup_files = ["setup.py"]

        self.readme_path = os.path.join(self.temp_dir, "README.md")
        with open(self.readme_path, 'w') as f:
            f.write("# Test README\nThis is a test repository.")

        self.menu = InteractiveMenu(
            self.temp_dir,
            self.mock_deployer,
            self.readme_path
        )

    def test_interactive_menu_initialization(self):
        """Test InteractiveMenu initialization"""
        assert self.menu.repo_path == self.temp_dir
        assert self.menu.deployer == self.mock_deployer
        assert self.menu.readme_path == self.readme_path
        assert self.menu.current_selection == 0
        assert len(self.menu.menu_items) == 8  # 8 menu items

    def test_setup_menu(self):
        """Test menu setup"""
        expected_actions = [
            "show_info", "view_readme", "setup_env", "list_files",
            "run_file", "inspect_file", "shell", "exit"
        ]

        actual_actions = [item["action"] for item in self.menu.menu_items]
        assert actual_actions == expected_actions

    def test_navigate_menu_up(self):
        """Test menu navigation up"""
        self.menu.current_selection = 3
        self.menu.navigate_menu('up')
        assert self.menu.current_selection == 2

        # Test wrap around
        self.menu.current_selection = 0
        self.menu.navigate_menu('up')
        assert self.menu.current_selection == len(self.menu.menu_items) - 1

    def test_navigate_menu_down(self):
        """Test menu navigation down"""
        self.menu.current_selection = 2
        self.menu.navigate_menu('down')
        assert self.menu.current_selection == 3

        # Test wrap around
        self.menu.current_selection = len(self.menu.menu_items) - 1
        self.menu.navigate_menu('down')
        assert self.menu.current_selection == 0

    def test_navigate_menu_k_j(self):
        """Test vim-style navigation"""
        self.menu.current_selection = 2
        self.menu.navigate_menu('k')
        assert self.menu.current_selection == 1

        self.menu.navigate_menu('j')
        assert self.menu.current_selection == 2

    @patch('digy.interactive.console')
    def test_show_repository_info(self, mock_console):
        """Test repository information display"""
        with patch.object(self.menu, 'wait_for_key'):
            self.menu.show_repository_info()
            mock_console.print.assert_called()

    @patch('digy.interactive.console')
    def test_view_readme_success(self, mock_console):
        """Test README viewing success"""
        with patch.object(self.menu, 'wait_for_key'):
            self.menu.view_readme()
            mock_console.print.assert_called()

    @patch('digy.interactive.console')
    def test_view_readme_no_file(self, mock_console):
        """Test README viewing with no file"""
        menu_no_readme = InteractiveMenu(
            self.temp_dir,
            self.mock_deployer,
            None
        )

        with patch.object(menu_no_readme, 'wait_for_key'):
            menu_no_readme.view_readme()
            # Should print error message
            mock_console.print.assert_called()

    @patch('digy.interactive.console')
    def test_setup_environment_success(self, mock_console):
        """Test environment setup success"""
        self.mock_deployer.setup_environment.return_value = True

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.setup_environment()
            self.mock_deployer.setup_environment.assert_called_once()
            mock_console.print.assert_called()

    @patch('digy.interactive.console')
    def test_setup_environment_failure(self, mock_console):
        """Test environment setup failure"""
        self.mock_deployer.setup_environment.return_value = False

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.setup_environment()
            self.mock_deployer.setup_environment.assert_called_once()
            mock_console.print.assert_called()

    @patch('digy.interactive.console')
    def test_list_python_files_success(self, mock_console):
        """Test Python files listing"""
        # Mock file info
        self.mock_deployer.get_file_info.side_effect = [
            {"lines": 50, "size": 1200, "has_main": True},
            {"lines": 30, "size": 800, "has_main": False}
        ]

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.list_python_files()
            mock_console.print.assert_called()
            assert self.mock_deployer.get_file_info.call_count == 2

    @patch('digy.interactive.console')
    def test_list_python_files_empty(self, mock_console):
        """Test Python files listing when no files found"""
        self.mock_deployer.python_files = []

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.list_python_files()
            mock_console.print.assert_called()

    @patch('digy.interactive.Prompt.ask')
    @patch('digy.interactive.Confirm.ask')
    @patch('digy.interactive.console')
    def test_run_python_file_success(self, mock_console, mock_confirm, mock_prompt):
        """Test running Python file successfully"""
        # Setup mocks
        mock_prompt.side_effect = ["1", "arg1 arg2"]  # Select file 1, provide args
        mock_confirm.return_value = False  # Don't run another file
        self.mock_deployer.run_python_file.return_value = (True, "Output", "")

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.run_python_file()

            self.mock_deployer.run_python_file.assert_called_once_with(
                "main.py", ["arg1", "arg2"]
            )
            mock_console.print.assert_called()

    @patch('digy.interactive.Prompt.ask')
    @patch('digy.interactive.console')
    def test_run_python_file_invalid_selection(self, mock_console, mock_prompt):
        """Test running Python file with invalid selection"""
        mock_prompt.return_value = "999"  # Invalid selection

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.run_python_file()
            mock_console.print.assert_called()

    @patch('digy.interactive.Prompt.ask')
    @patch('digy.interactive.console')
    def test_run_python_file_no_files(self, mock_console, mock_prompt):
        """Test running Python file when no files available"""
        self.mock_deployer.python_files = []

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.run_python_file()
            mock_console.print.assert_called()

    @patch('digy.interactive.Prompt.ask')
    @patch('digy.interactive.console')
    def test_inspect_file_success(self, mock_console, mock_prompt):
        """Test file inspection success"""
        mock_prompt.return_value = "1"  # Select first file

        # Create test file for inspection
        test_file = os.path.join(self.temp_dir, "main.py")
        with open(test_file, 'w') as f:
            f.write('import os\nprint("Hello")\nif __name__ == "__main__":\n    print("Main")')

        # Mock file info
        self.mock_deployer.get_file_info.return_value = {
            "lines": 4,
            "size": 65,
            "has_main": True,
            "imports": ["import os"]
        }

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.inspect_file()
            self.mock_deployer.get_file_info.assert_called_once_with("main.py")
            mock_console.print.assert_called()

    @patch('digy.interactive.Prompt.ask')
    @patch('digy.interactive.console')
    def test_inspect_file_invalid_selection(self, mock_console, mock_prompt):
        """Test file inspection with invalid selection"""
        mock_prompt.return_value = "999"  # Invalid selection

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.inspect_file()
            mock_console.print.assert_called()

    @patch('subprocess.run')
    @patch('digy.interactive.console')
    def test_interactive_shell_success(self, mock_console, mock_subprocess):
        """Test interactive shell launch"""
        self.mock_deployer.venv_path = "/fake/venv"
        self.mock_deployer.get_python_executable.return_value = "/fake/venv/bin/python"
        mock_subprocess.return_value = None

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.interactive_shell()
            mock_subprocess.assert_called_once()
            mock_console.print.assert_called()

    @patch('digy.interactive.console')
    def test_interactive_shell_no_venv(self, mock_console):
        """Test interactive shell when no virtual environment exists"""
        self.mock_deployer.venv_path = None
        self.mock_deployer.setup_environment.return_value = False

        with patch.object(self.menu, 'wait_for_key'):
            self.menu.interactive_shell()
            self.mock_deployer.setup_environment.assert_called_once()
            mock_console.print.assert_called()

    def test_execute_action_show_info(self):
        """Test executing show_info action"""
        with patch.object(self.menu, 'show_repository_info') as mock_method:
            result = self.menu.execute_action("show_info")
            mock_method.assert_called_once()
            assert result is True

    def test_execute_action_exit(self):
        """Test executing exit action"""
        result = self.menu.execute_action("exit")
        assert result is False

    def test_execute_action_all_actions(self):
        """Test all menu actions can be executed"""
        actions_to_test = [
            "show_repository_info", "view_readme", "setup_environment",
            "list_python_files", "run_python_file", "inspect_file",
            "interactive_shell"
        ]

        for action in actions_to_test:
            with patch.object(self.menu, action) as mock_method:
                continue_execution = self.menu.execute_action(action)
                mock_method.assert_called_once()
                if action != "exit":
                    assert continue_execution is True

    @patch('builtins.input')
    def test_get_user_input_normal(self, mock_input):
        """Test normal user input"""
        mock_input.return_value = "test input"
        result = self.menu.get_user_input()
        assert result == "test input"

    @patch('builtins.input')
    def test_get_user_input_keyboard_interrupt(self, mock_input):
        """Test user input with keyboard interrupt"""
        mock_input.side_effect = KeyboardInterrupt()
        result = self.menu.get_user_input()
        assert result == "q"

    @patch('builtins.input')
    def test_get_user_input_eof_error(self, mock_input):
        """Test user input with EOF error"""
        mock_input.side_effect = EOFError()
        result = self.menu.get_user_input()
        assert result == "q"

    @patch('builtins.input')
    def test_wait_for_key(self, mock_input):
        """Test wait for key functionality"""
        mock_input.return_value = ""
        self.menu.wait_for_key()
        mock_input.assert_called_once()

    @patch('builtins.input')
    def test_wait_for_key_keyboard_interrupt(self, mock_input):
        """Test wait for key with keyboard interrupt"""
        mock_input.side_effect = KeyboardInterrupt()
        # Should not raise exception
        self.menu.wait_for_key()


if __name__ == "__main__":
    pytest.main([__file__])