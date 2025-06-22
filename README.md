# DIGY - Dynamic Interactive Git deploY

## 🌟 Features

- **Multi-Environment Execution**
  - Local execution with virtual environments
  - Docker container isolation
  - Remote execution over SSH
  - JVM-based execution
  - RAM-based execution for maximum performance

- **Interactive Development**
  - Rich terminal interface
  - Code inspection with syntax highlighting
  - Interactive file selection
  - Memory usage monitoring

- **Flexible Configuration**
  - Multiple authentication methods (SQL, Web, IO, Socket)
  - Custom virtual environments
  - File attachments for execution
  - Environment-specific settings

## 🚀 Quick Start

### Basic Usage

```bash
# Run a repository locally
digy local github.com/username/repo

# Run a specific Python file from a repository
digy local github.com/username/repo script.py --arg1 value1

# Run on a remote host via SSH
digy remote user@host github.com/username/repo script.py

# Run in a Docker container
digy docker --image python:3.12 github.com/username/repo script.py
```

## 🐳 Docker Configuration

DIGY supports running projects in isolated Docker containers with RAM-based storage for maximum performance. This ensures that:
- Projects run in complete isolation
- No local filesystem changes are made
- Resources are cleaned up automatically
- Execution is as fast as possible using RAM storage

### Configuration

DIGY uses a manifest file (`digy/manifest.yml`) to configure Docker settings. You can override these settings either:
1. In the manifest file
2. Using environment variables
3. Through command-line arguments

### Volume Types

DIGY supports two types of volumes:

1. **RAM Volumes**
   - Stored in RAM for maximum speed
   - Automatically cleaned up after use
   - Size configurable in GB
   - Example: `/tmp/digy_ram`

2. **Local Volumes**
   - Mount local directories into containers
   - Can be read-only or read-write
   - Useful for:
     - Persistent data storage
     - Local development
     - Configuration files

### Usage Examples

1. **Basic Usage**
```bash
# Run a repository from GitHub
digy local github.com/pyfunc/digy

# Run with 4GB RAM
digy local --ram-size 4 github.com/pyfunc/digy
```

2. **Local File Mount**
```bash
# Mount local directory into container
digy docker --mount ./data:/app/data:ro github.com/pyfunc/digy
```

3. **Custom Docker Configuration**
```bash
# Build and run with custom Dockerfile
digy build -f Dockerfile .
digy docker --image myapp:latest github.com/pyfunc/digy

# Or in one command
digy docker --build -f Dockerfile github.com/pyfunc/digy
```

### Performance Tips

1. **RAM Size**
   - Default: 2GB (`--ram-size 2`)
   - Adjust based on project needs
   - Example: `digy local --ram-size 4 github.com/user/repo`

2. **Volume Mounts**
   - Read-only mount: `--mount ./config:/app/config:ro`
   - Read-write mount: `--mount ./data:/app/data:rw`
   - RAM disk: `--ram-disk /cache`

3. **Cleanup**
   - Automatic cleanup: `--cleanup`
   - Remove all data: `digy clean --all`
   - List resources: `digy ls`

### Environment Configuration

DIGY supports configuration through environment variables. You can create a `.env` file in your project root based on the example:

```bash
# Initialize with default configuration
digy init
```

Key environment variables:

- `DIGY_RAM_SIZE`: RAM disk size in GB (default: 1)
- `DIGY_RAM_PATH`: RAM disk mount path (default: /tmp/digy_ram)
- `DIGY_DOCKER_IMAGE`: Default Docker image (default: python:3.12-slim)
- `DIGY_LOCAL_VOLUMES`: Local volume mounts (format: host:container:mode)
- `DIGY_RAM_VOLUMES`: RAM volume mounts
- `DIGY_ENV_VARS`: Default environment variables
- `DIGY_AUTO_CLEANUP`: Automatic cleanup after execution (true/false)
- `DIGY_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

Example `.env` file:
```bash
DIGY_RAM_SIZE=2
DIGY_DOCKER_IMAGE=python:3.12-slim
DIGY_LOCAL_VOLUMES=/app:/app:rw
DIGY_LOG_LEVEL=INFO
```

### Security

- All execution happens in isolated containers
- No changes are made to the host system
- RAM volumes are ephemeral
- Local mounts can be made read-only
- Environment variables can be configured per project

### Troubleshooting

1. **Not enough RAM**
   - Increase RAM size in manifest
   - Use `--ram-size` flag
   - Monitor container memory usage

2. **Volume permissions**
   - Check Docker volume permissions
   - Use `--user` flag to match UID
   - Verify mount points are accessible

3. **Resource cleanup**
   - Use `--cleanup` flag
   - Check Docker volume usage
   - Monitor RAM disk usage

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
digy local github.com/username/repo
```
- Uses local Python environment
- Creates virtual environment if needed
- Supports file attachments

### 2. Remote Execution
```bash
digy remote user@host github.com/username/repo script.py
```
- Executes code on remote host via SSH
- Supports authentication
- Transfers necessary files automatically

### 3. Docker Execution
```bash
digy docker --image python:3.12 github.com/username/repo script.py
```
- Runs in isolated container
- Customizable Docker images
- Volume mounting support

### 4. JVM Execution
```bash
digy jvm github.com/username/repo script.py
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
- 🐍 **Uruchamianie kodu** - Wykonywanie plików Python z wyświetlaniem wyników
- 📊 **Zarządzanie pamięcią** - Monitoring i kontrola użycia RAM
- 🔍 **Inspekcja kodu** - Przeglądanie plików z podświetlaniem składni

## 📦 Instalacja

```bash
# Instalacja z pip (gdy będzie dostępne)
pip install digy

# Lub instalacja z źródeł
git clone https://github.com/pyfunc/digy
cd digy
poetry install
```

## 🛠️ Advanced Usage

### Command Reference

#### `digy local` - Run Python files locally
```bash
# Basic usage
digy local github.com/username/repo script.py

# With arguments
digy local github.com/username/repo script.py --arg1 value1 --arg2 value2
```

#### `digy remote` - Run Python files on a remote host via SSH
```bash
digy remote user@host github.com/username/repo script.py
```

#### `digy docker` - Run Python files in a Docker container
```bash
digy docker --image python:3.12 github.com/username/repo script.py
```

#### `digy jvm` - Run Python files on JVM
```bash
digy jvm github.com/username/repo script.py
```

#### `digy local` - Run locally with interactive menu
```bash
digy local github.com/username/repo

# Specify branch
digy local github.com/username/repo --branch develop

# Attach local files
digy local github.com/username/repo --file config.json
```

#### Environment Management
```bash
# List available environments
digy env list

# Create new environment
digy env create myenv --python=3.10

# Activate environment
digy env activate myenv
```

```bash
# Uruchomienie w środowisku lokalnym
digy local github.com/pyfunc/free-on-pypi

# Uruchomienie w pamięci RAM (najszybsze)
digy ram github.com/pyfunc/free-on-pypi

# Uruchomienie w kontenerze Docker
digy docker github.com/pyfunc/free-on-pypi

# Dodatkowe opcje
# Z określoną gałęzią
digy local github.com/user/repo --branch develop

# Szybkie uruchomienie konkretnego pliku
digy ram github.com/pyfunc/free-on-pypi pypi.py --args "from_file"

# Status i informacje
digy status
digy info
```

## 📋 Interaktywne Menu

Po załadowaniu repozytorium DIGY wyświetli interaktywne menu z opcjami:

```
📋 Show Repository Info    - Informacje o repozytorium
📖 View README            - Wyświetl plik README
🔧 Setup Environment      - Skonfiguruj środowisko
📁 List Python Files      - Lista plików Python
🚀 Run Python File        - Uruchom plik Python
🔍 Inspect File           - Zbadaj zawartość pliku
💻 Interactive Shell      - Interaktywna powłoka Python
🧹 Cleanup & Exit         - Wyczyść i wyjdź
```

### Nawigacja

- **↑/↓** lub **j/k** - Poruszanie się po menu
- **Enter** - Wybór opcji
- **1-8** - Bezpośredni wybór numerem
- **q** - Wyjście

## 🔧 Przykład użycia z repozytorium free-on-pypi

```python
from digy import digy

# Załaduj repozytorium lokalnie
digy.local('github.com/pyfunc/free-on-pypi')

# Lub w pamięci RAM
digy.ram('github.com/pyfunc/free-on-pypi')

# Albo w Dockerze
digy.docker('github.com/pyfunc/free-on-pypi')
```

Po załadowaniu zobaczysz menu z opcjami uruchomienia:
1. `pypi.py from_file` - Sprawdzenie nazw z pliku
2. `pypi.py generator` - Generator kombinacji nazw
3. `github.py from_file` - Sprawdzenie nazw na GitHub

Każde uruchomienie pokaże:
- Pełne wyjście konsoli
- Błędy (jeśli wystąpią)
- Pytanie o uruchomienie kolejnej komendy

## 🎮 Funkcje interaktywne

### Uruchamianie plików Python
- Wybór pliku z listy
- Podanie argumentów
- Wyświetlenie pełnego wyjścia
- Monitoring czasu wykonania

### Inspekcja kodu
- Podświetlanie składni
- Informacje o pliku (linie, rozmiar)
- Lista importów
- Wykrywanie bloku `if __name__ == "__main__"`

### Zarządzanie środowiskiem
- Automatyczne tworzenie virtual environment
- Instalacja requirements.txt
- Instalacja pakietu w trybie deweloperskim
- Monitoring pamięci RAM

## 🔧 Konfiguracja

### Zmienne środowiskowe

```bash
export DIGY_MEMORY_BASE=100    # Bazowa alokacja pamięci w MB
export DIGY_TIMEOUT=300        # Timeout wykonania w sekundach
```

### Programowa konfiguracja

```python
from digy.loader import memory_manager

# Zmień bazową alokację pamięci
memory_manager.base_size_mb = 200

# Sprawdź dostępną pamięć
available = memory_manager.check_available_memory()
print(f"Dostępne: {available} MB")
```

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