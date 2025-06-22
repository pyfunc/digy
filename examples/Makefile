.PHONY: all hello env file auth clean test

# Default target: run all examples
all: hello env file auth

# Run basic hello world example
hello:
	@echo "\n=== Running Hello World Example ==="
	digy run basic/hello_world.py

# Run environment info example (local only)
env:
	@echo "\n=== Running Environment Info Example ==="
	digy run env/environment_info.py

# Run file processor example with a test file
file: test.txt
	@echo "\n=== Running File Processor Example ==="
	digy run attachments/file_processor.py --attach test.txt

# Run authentication demo (will show not authenticated without auth params)
auth:
	@echo "\n=== Running Authentication Demo ==="
	digy run auth/auth_demo.py

# Create a test file for the file processor
test.txt:
	@echo "This is a test file for DIGY examples." > test.txt

# Clean up generated files
clean:
	rm -f test.txt

# Run all tests (same as 'all' target)
test: all
