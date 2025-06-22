# Changelog

All notable changes to DIGY project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Non-interactive mode support
- Configuration file support
- Plugin system for custom deployers
- Docker container deployment
- Remote repository authentication
- Advanced memory management options

## [0.1.0] - 2025-06-22

### Added
- Initial release of DIGY (Dynamic Interactive Git deploY)
- Core repository loading functionality from Git URLs
- Memory-based repository caching (100MB base allocation)
- Interactive menu system with arrow key navigation
- Isolated virtual environment creation and management
- Python file discovery and execution
- Real-time console output display
- File inspection with syntax highlighting
- README parsing and display
- Memory management and monitoring
- CLI interface with multiple commands
- Support for requirements.txt and setup.py installation
- Cross-platform compatibility (Windows, macOS, Linux)
- Rich console output with colors and formatting

### Features
- `load()` function for repository deployment
- `digy load` command for CLI usage
- `digy run` for quick file execution
- `digy status` for memory and repository monitoring
- `digy info` for application information
- Interactive menu with 8 core functions:
  - Repository information display
  - README viewing
  - Environment setup
  - Python file listing
  - File execution with arguments
  - Code inspection
  - Interactive Python shell
  - Cleanup and exit

### Technical Details
- Built with Poetry for dependency management
- Uses GitPython for repository operations
- Rich library for enhanced console output
- Click for CLI interface
- PSUtil for memory monitoring
- Virtual environment isolation
- Automatic cleanup on exit
- Error handling and timeout protection

### Supported Formats
- GitHub repositories (github.com/user/repo)
- Full Git URLs (https://github.com/user/repo.git)
- Multiple branch support
- Requirements.txt parsing
- Setup.py/pyproject.toml recognition
- README files (.md, .txt, .rst)

### Documentation
- Complete README with usage examples
- API documentation
- CLI help system
- Interactive help in menu system