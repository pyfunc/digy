# DIGY - Dynamic Interactive Git deploY

**DIGY** to narzędzie do deploymentu aplikacji Python z repozytoriów Git w izolowanych środowiskach z interaktywnym menu nawigacyjnym.

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

## 🎯 Użycie

### Podstawowe użycie

```python
from digy import digy

# Załaduj repozytorium i uruchom interaktywne menu
digy('github.com/pyfunc/free-on-pypi')
```

### Wiersz poleceń

```bash
# Proste uruchomienie (automatycznie wykrywa repo URL)
digy github.com/pyfunc/free-on-pypi

# Lub z komendą start
digy start github.com/pyfunc/free-on-pypi

# Z określoną gałęzią
digy start github.com/user/repo --branch develop

# Szybkie uruchomienie konkretnego pliku
digy run github.com/pyfunc/free-on-pypi pypi.py --args "from_file"

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

# Załaduj repozytorium
digy('github.com/pyfunc/free-on-pypi')
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
from digy.deployer import Deployer

# Załaduj bez menu
deployer = Deployer("/path/to/repo")
deployer.setup_environment()

# Uruchom konkretny plik
success, stdout, stderr = deployer.run_python_file("script.py", ["arg1", "arg2"])
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
│   ├── deployer.py      # Deployment i uruchamianie
│   ├── interactive.py   # Interaktywne menu
│   ├── cli.py          # Interface wiersza poleceń
│   └── version.py      # Informacje o wersji
├── tests/              # Testy
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