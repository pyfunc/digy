.PHONY: help install test lint format build publish clean dev-setup docker-run docker-build

help:
	@echo "🔥 DIGY - Make commands"
	@echo ""
	@echo "📦 Package commands:"
	@echo "  install     Install dependencies"
	@echo "  build       Build package"
	@echo "  publish     Publish to PyPI"
	@echo ""
	@echo "🐳 Docker commands:"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container (port 8080)"
	@echo ""
	@echo "🧪 Development commands:"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  dev-setup   Setup development environment"
	@echo ""
	@echo "🧹 Utility commands:"
	@echo "  clean       Clean build artifacts"

# Package commands
install:
	poetry install

build:
	poetry version patch
	poetry build

publish: build
	poetry publish

# Docker commands
docker-build:
	docker build -t digy .

docker-run:
	@echo "Starting DIGY on http://localhost:8080"
	docker run --rm -p 8080:80 digy

# Development commands
test:
	poetry run pytest

lint:
	@echo "Running flake8..."
	poetry run flake8 digy tests examples
	@echo "\nRunning mypy..."
	poetry run mypy digy

format:
	@echo "Running black..."
	poetry run black digy tests examples
	@echo "\nRunning isort..."
	poetry run isort digy tests examples

# Utility commands
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ htmlcov/ .mypy_cache/
	@echo "Removing Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.py[co]" -delete
	find . -type f -name "*.so" -delete
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

dev-setup:
	@if [ -f "./scripts/dev_setup.sh" ]; then \
		./scripts/dev_setup.sh; \
	else \
		echo "dev_setup.sh not found. Running basic setup..."; \
		pip install --upgrade pip; \
		pip install -e .[dev]; \
	fi


# Build and push git changes
push: bump-version
	@echo "🚀 Preparing to push changes..."
	git add .
	git commit -m "📦 Bump version to $(shell poetry version -s)" || true
	git push

# Bump version (patch by default, use VERSION=minor for minor bump)
bump-version:
	@echo "🔄 Bumping version..."
	poetry version $(or $(VERSION), patch)
	@echo "✅ New version: $(shell poetry version -s)"

# Generate changelog
changelog:
	@echo "📝 Generating changelog..."
	git-chglog -o CHANGELOG.md && \
	git add CHANGELOG.md && \
	git commit -m "📝 Update changelog" || true
