# DIGY - Dynamic Interactive Git deploY

> **Note**: DIGY is in active development. Some features may be experimental.

[![PyPI version](https://badge.fury.io/py/digy.svg)](https://badge.fury.io/py/digy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

DIGY is a powerful tool for executing Python code in various environments with minimal setup. It provides a consistent interface for running code locally, in Docker containers, in-memory, or on remote machines.

## 🚀 Quick Links
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Examples](#-examples)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## 🌟 Features

### 🛠️ Multi-Environment Execution
- **Local**: Run code in isolated virtual environments
- **Docker**: Containerized execution for reproducibility
- **RAM**: In-memory execution for maximum performance
- **Remote**: Execute on remote machines via SSH
- **JVM**: Run Java/Scala code with Python interop

### 💻 Interactive & Scriptable
- Rich terminal interface with auto-completion
- Command-line automation support
- Scriptable execution flows
- Jupyter notebook integration

### 🔄 Flexible Code Loading
- Direct Git repository cloning
- Automatic zip download fallback
- Support for private repositories
- Branch/tag/commit selection

### 📁 File & Data Management
- Interactive file selection
- File attachment support
- Volume mounting for persistent data
- Built-in data processing utilities

### 🔒 Security & Authentication
- Multiple authentication methods
- Secure credential management
- Environment-based configuration
- Custom authentication providers

### 📊 Monitoring & Debugging
- Real-time resource usage
- Detailed logging
- Debug mode for troubleshooting
- Performance metrics

### 🔄 Integration & Extensibility
- Plugin system for custom environments
- Webhook support
- REST API
- CLI and programmatic interfaces

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git (recommended for direct Git operations)
- Docker (optional, for containerized execution)
- Poetry (for development)

### Installation

#### Using pip (recommended)
```bash
pip install digy
```

#### Development Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/digy.git
cd digy

# Install with development dependencies
pip install -e .[dev]

# Or use Poetry
poetry install
```

### Basic Usage

```bash
# Run a local script
digy local path/to/script.py

# Run in a Docker container
digy docker --image python:3.9 path/to/script.py

# Run in memory (fastest)
digy ram path/to/script.py

# Run on a remote machine
digy remote user@example.com github.com/owner/repo path/to/script.py
```

## 📚 Documentation

### Command Reference

#### `digy local <script> [args...]`
Run a script in a local environment.

**Options:**
- `--env PATH`: Path to Python virtual environment
- `--python PATH`: Path to Python interpreter
- `--cwd PATH`: Working directory
- `--debug`: Enable debug output

**Examples:**
```bash
# Basic usage
digy local script.py

# With arguments
digy local script.py arg1 arg2

# Specify Python version
digy local --python python3.9 script.py
```

#### `digy docker [options] <script> [args...]`
Run a script in a Docker container.

**Options:**
- `--image IMAGE`: Docker image to use (default: python:3.9-slim)
- `--build`: Build Docker image from Dockerfile
- `--dockerfile PATH`: Path to Dockerfile
- `--no-cache`: Disable Docker cache
- `--volume SRC:DST`: Mount a volume

**Examples:**
```bash
# Basic usage
digy docker script.py

# Specify custom image
digy docker --image tensorflow/tensorflow script.py

# Mount volumes
digy docker -v $(pwd)/data:/data script.py
```

#### `digy ram <script> [args...]`
Run a script in memory for maximum performance.

**Examples:**
```bash
# Basic usage
digy ram script.py

# With dependencies
pip install -r requirements.txt
digy ram script.py
```

#### `digy remote <user@host> <repo> <script> [args...]`
Run a script on a remote machine.

**Options:**
- `--key PATH`: SSH private key
- `--port PORT`: SSH port (default: 22)
- `--ssh-args ARGS`: Additional SSH arguments

**Examples:**
```bash
# Basic usage
digy remote user@example.com github.com/owner/repo script.py

# With custom SSH key
digy remote --key ~/.ssh/id_rsa user@example.com github.com/owner/repo script.py
```

## 📦 Configuration

DIGY can be configured using environment variables or a configuration file.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DIGY_DEBUG` | `false` | Enable debug output |
| `DIGY_CACHE_DIR` | `~/.cache/digy` | Cache directory |
| `DIGY_CONFIG` | `~/.config/digy/config.toml` | Config file path |
| `DIGY_DOCKER_IMAGE` | `python:3.9-slim` | Default Docker image |
| `DIGY_PYTHON_BIN` | `python3` | Python interpreter |

### Configuration File

Create `~/.config/digy/config.toml`:

```toml
[core]
debug = false
cache_dir = "~/.cache/digy"

[docker]
image = "python:3.9-slim"
build = false
no_cache = false

[remote]
port = 22
key = "~/.ssh/id_rsa"

[local]
python = "python3"
```
pip install -e .

# Or using Poetry
poetry install
```

### Basic Usage

#### Interactive Mode
```bash
# Clone and interact with a repository
digy local https://github.com/octocat/Hello-World.git

# Run with a specific branch
digy local https://github.com/octocat/Hello-World.git --branch main

# Attach local files (available in interactive menu)
digy local https://github.com/pyfunc/repo.git --file ./local_script.py
```

#### Non-Interactive Mode
```bash
# Run a specific script from a repository
digy local https://github.com/user/repo.git --script path/to/script.py

# With command-line arguments
digy local https://github.com/user/repo.git --script main.py -- --arg1 value1

# Using environment variables
DIGY_RAM_SIZE=4 digy local https://github.com/user/repo.git
```

#### Docker Execution
```bash
# Run in a Docker container
digy docker https://github.com/user/repo.git

# Specify custom Docker image
digy docker --image python:3.12 https://github.com/user/repo.git
```

#### RAM-Based Execution
```bash
# Run with RAM disk for temporary files
digy ram https://github.com/user/repo.git --ram-size 2  # 2GB RAM
```

#### Getting Help
```bash
# Show help
digy --help

# Show version
digy --version

# Command-specific help
digy local --help
digy docker --help
digy ram --help
```

## 🔧 Known Limitations

- Docker support requires the `docker` Python package and Docker daemon running
- Private repository access requires proper SSH/Git credentials setup
- Large repositories may require additional memory allocation
- Windows support has limited testing
- Some edge cases in error handling may need improvement

## 🔄 Fallback Behavior

DIGY implements a robust fallback mechanism for repository loading:

1. **Primary Method**: Direct Git clone (requires Git)
2. **Fallback 1**: HTTPS Git clone (if SSH fails)
3. **Fallback 2**: Download repository as zip archive
4. **Fallback 3**: Use local cache if available

This ensures maximum compatibility across different environments and network conditions.

## 🐳 Docker Support (Optional)

DIGY's Docker integration provides isolated execution environments with these benefits:

- **Isolation**: Projects run in complete isolation
- **Reproducibility**: Consistent environments across different systems
- **Security**: No host system modifications
- **Cleanup**: Automatic resource cleanup
- **Performance**: RAM-based storage for temporary files

### When to Use Docker

- When you need complete environment isolation
- For consistent testing across different systems
- When working with system dependencies
- For security-sensitive operations

### Docker Prerequisites

- Docker Engine installed and running
- Python `docker` package (`pip install docker`)
- Sufficient permissions to run Docker commands
- Minimum 2GB of available RAM (4GB recommended)
- At least 1GB of free disk space

## ⚙️ Configuration

DIGY can be configured through multiple methods (in order of precedence):

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Configuration file** (`~/.config/digy/config.toml`)
4. **Default values** (lowest priority)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DIGY_RAM_SIZE` | `1` | RAM disk size in GB |
| `DIGY_DOCKER_IMAGE` | `python:3.12-slim` | Default Docker image |
| `DIGY_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DIGY_CACHE_DIR` | `~/.cache/digy` | Cache directory |
| `DIGY_TIMEOUT` | `300` | Operation timeout in seconds |
| `DIGY_AUTO_CLEANUP` | `true` | Automatically clean up temporary files |
| `DIGY_GIT_BIN` | `git` | Path to Git executable |
| `DIGY_PYTHON_BIN` | `python3` | Path to Python interpreter |

### Configuration File Example

Create `~/.config/digy/config.toml`:

```toml
[core]
ram_size = 2
timeout = 600
auto_cleanup = true
log_level = "INFO"

[docker]
image = "python:3.12-slim"
use_sudo = false

[git]
bin = "/usr/bin/git"
timeout = 300

[cache]
enabled = true
max_size = "1GB"
path = "~/.cache/digy"
```

## 🚀 Advanced Usage

### Authentication

#### GitHub Personal Access Token
```bash
export GITHUB_TOKEN="your_github_token"
digy local https://github.com/username/private-repo.git
```

#### SSH Authentication
1. Ensure your SSH key is added to the SSH agent:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/your_private_key
   ```
2. Use SSH URL:
   ```bash
   digy local git@github.com:username/private-repo.git
   ```

### Advanced Docker Usage

#### Custom Docker Network
```bash
digy docker --network host https://github.com/user/repo.git
```

#### Volume Mounts
```bash
# Read-only mount
digy docker --mount ./config:/app/config:ro https://github.com/user/repo.git

# Read-write mount
digy docker --mount ./data:/app/data:rw https://github.com/user/repo.git
```

#### Environment Variables
```bash
# Set environment variables
digy docker -e DEBUG=1 -e API_KEY=secret https://github.com/user/repo.git

# Load from .env file
digy docker --env-file .env https://github.com/user/repo.git
```

### Resource Management

#### Memory Limits
```bash
# Set memory limit (Docker only)
digy docker --memory 4g https://github.com/user/repo.git

# CPU limits
digy docker --cpus 2 https://github.com/user/repo.git
```

#### Cleanup
```bash
# Clean all temporary files
digy clean --all

# Remove cached repositories
digy clean --cache

# Remove Docker resources
digy clean --docker
```

## 🔍 Troubleshooting

### Common Issues

#### Git Authentication Failures
```
Error: Failed to clone repository: Authentication failed
```
**Solution**:
1. Verify your SSH key is added to the SSH agent
2. For HTTPS, ensure you have a valid GitHub token
3. Check repository access permissions

#### Docker Permission Denied
```
Got permission denied while trying to connect to the Docker daemon
```
**Solution**:
1. Add your user to the `docker` group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```
2. Or use `sudo` (not recommended for security reasons)

#### Out of Memory
```
Error: Container ran out of memory
```
**Solution**:
1. Increase memory allocation:
   ```bash
   digy docker --memory 8g https://github.com/user/repo.git
   ```
2. Or reduce memory usage in your application

### Debugging

Enable debug logging:
```bash
digy --log-level DEBUG local https://github.com/user/repo.git
```

View logs:
```bash
# System logs (Linux)
journalctl -u docker.service

# Application logs
cat ~/.cache/digy/logs/digy.log
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/digy.git
   cd digy
   ```
3. Install development dependencies:
   ```bash
   poetry install --with dev
   ```
4. Run tests:
   ```bash
   pytest
   ```

5. Run linters:
   ```bash
   black .
   flake8
   mypy .
   ```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Twitter: [@yourhandle](https://twitter.com/yourhandle)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Thanks to all contributors who have helped make DIGY better
- Inspired by tools like Docker, Git, and Jupyter
- Built with ❤️ and Python

## 📄 Examples

### Basic Examples

#### Hello World
```python
# hello_world.py
print("Hello, DIGY!")
```

```bash
digy local hello_world.py
```

#### Environment Information
```python
# env_info.py
import platform
import sys

print("Python Version:", sys.version)
print("Platform:", platform.platform())
print("Current Directory:", os.getcwd())
```

```bash
digy local env_info.py
```

### Data Processing

```python
# data_analysis.py
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Process data
summary = df.describe()
print(summary)

# Save results
summary.to_csv('results/summary.csv')
```

```bash
digy local data_analysis.py
```

### Web Scraping

```python
# scraper.py
import requests
from bs4 import BeautifulSoup

def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return {
        'title': soup.title.string,
        'links': [a['href'] for a in soup.find_all('a', href=True)]
    }

if __name__ == '__main__':
    result = scrape('https://example.com')
    print(result)
```

```bash
pip install requests beautifulsoup4
digy local scraper.py
```

### Machine Learning

```python
# train.py
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Accuracy: {score:.2f}")

# Save model
joblib.dump(model, 'model.joblib')
```

```bash
pip install scikit-learn joblib
digy local train.py
```

For more examples, see the [examples](examples/) directory.

## 📦 Installation

```bash
# Install from PyPI
pip install digy

# Or install from source
git clone https://github.com/pyfunc/digy
cd digy
pip install -e .
```

### Dependencies

DIGY requires:
- Python 3.8+
- Git
- Docker (for container execution)
- SSH (for remote execution)

Install development dependencies:
```bash
pip install -e ".[dev]"
```

## 🔄 Execution Environments

DIGY supports multiple execution environments:

### 1. Local Execution
```bash
digy local github.com/pyfunc/digy
```
- Uses local Python environment
- Creates virtual environment if needed
- Supports file attachments

### 2. Remote Execution
```bash
digy remote user@host github.com/pyfunc/digy script.py
```
- Executes code on remote host via SSH
- Supports authentication
- Transfers necessary files automatically

### 3. Docker Execution
```bash
digy docker --image python:3.12 github.com/pyfunc/digy script.py
```
- Runs in isolated container
- Customizable Docker images
- Volume mounting support

### 4. RAM Execution
```bash
digy ram github.com/pyfunc/digy script.py
```
- Runs code directly in RAM for maximum performance
- No disk I/O overhead
- Ideal for high-performance computing

### 5. JVM Execution
```bash
digy jvm github.com/pyfunc/digy script.py
```
- Executes Python code on JVM using Jython
- Java integration
- Cross-platform compatibility

## 🎯 Akronim DIGY

**DIGY** = **Dynamic Interactive Git deploY**
- **Dynamic** - Dynamiczne ładowanie repozytoriów
- **Interactive** - Interaktywne menu z nawigacją strzałkami
- **Git** - Integracja z repozytoriami Git
- **deploY** - Deployment w izolowanych środowiskach

## 🚀 Funkcjonalności

- ⚡ **Szybkie ładowanie** - Pobieranie repozytoriów bezpośrednio do pamięci RAM (100MB bazowo)
- 🔒 **Izolowane środowiska** - Automatyczne tworzenie virtual environment
- 🎮 **Interaktywne menu** - Nawigacja strzałkami z pomocą
- 📊 **Zarządzanie pamięcią** - Monitoring i kontrola użycia RAM
- 🔍 **Inspekcja kodu** - Przeglądanie plików z podświetlaniem składni

## 📝 API Reference

### `digy(repo_url, branch='main')`
Główna funkcja ładująca repozytorium i uruchamiająca interaktywne menu.

**Parametry:**
- `repo_url` (str): URL repozytorium (github.com/user/repo lub pełny URL)
- `branch` (str): Gałąź do pobrania (domyślnie 'main')

**Zwraca:**
- `str | None`: Ścieżka do lokalnego repozytorium lub None przy błędzie

### Klasa `Deployer`
Zarządza deploymentem aplikacji w izolowanych środowiskach.

### Klasa `InteractiveMenu`
Zapewnia interaktywne menu z nawigacją strzałkami.

### Klasa `MemoryManager`
Zarządza alokacją pamięci dla załadowanych repozytoriów.

## 🔍 Przykłady zaawansowane

### Niestandardowa ścieżka
```python
from digy.loader import GitLoader
from digy.deployer import Deployer

loader = GitLoader("/custom/path")
local_path = loader.download_repo("github.com/user/repo")
deployer = Deployer(local_path)
```

### Programowe uruchamianie
```python
from digy import digy

# Uruchomienie z kodu Pythona
# Lokalnie
result = digy.local('github.com/user/repo', 'script.py', ['arg1', 'arg2'])

# W pamięci RAM
result = digy.ram('github.com/user/repo', 'script.py', ['arg1', 'arg2'])

# W Dockerze
result = digy.docker('github.com/user/repo', 'script.py', ['arg1', 'arg2'])

# Wynik zawiera (success, stdout, stderr)
print(f"Sukces: {result[0]}")
print(f"Wyjście: {result[1]}")
if result[2]:
    print(f"Błędy: {result[2]}")
```

## 🛠️ Rozwój

### Wymagania deweloperskie
- Python 3.8+
- Poetry
- Git

### Instalacja deweloperska
```bash
git clone https://github.com/pyfunc/digy
cd digy
poetry install
poetry run pytest
```

### Struktura projektu
```
digy/
├── digy/
│   ├── __init__.py      # Główny moduł
│   ├── loader.py        # Ładowanie repozytoriów
│   ├── deployer.py      # Deployment and execution
│   ├── interactive.py   # Interactive menu
│   ├── cli.py          # Command line interface
│   ├── environment.py   # Environment management
│   ├── auth.py         # Authentication providers
│   └── version.py      # Version information
├── tests/              # Tests
├── examples/           # Usage examples
│   ├── basic/          # Basic examples
│   ├── env/            # Environment examples
│   └── attachments/    # File attachment examples
├── pyproject.toml      # Konfiguracja Poetry
└── README.md          # Dokumentacja
```

## 📄 Licencja

Apache Software License - Zobacz plik LICENSE dla szczegółów.

## 🤝 Wkład

Zapraszamy do współpracy! Prosimy o:
1. Forkowanie repozytorium
2. Tworzenie feature branch
3. Commit zmian
4. Push do branch
5. Tworzenie Pull Request

## 📞 Wsparcie

- **Issues**: https://github.com/pyfunc/digy/issues
- **Email**: info@softreck.dev
- **Dokumentacja**: https://github.com/pyfunc/digy

---

**DIGY** - Twój interaktywny asystent do deploymentu aplikacji Python! 🚀