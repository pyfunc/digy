# DIGY Examples

This directory contains example scripts that demonstrate various features of DIGY.

## Basic Examples

### `basic/hello_world.py`
A simple "Hello, World!" example that shows basic script execution.

**Run it with:**
```bash
# Run locally
digy local examples/basic/hello_world.py

# Or run in RAM for better performance
digy ram examples/basic/hello_world.py
```

## Environment Examples

### `env/environment_info.py`
Shows information about the current execution environment, including Python version, platform, and environment variables.

**Run it with different environments:**
```bash
# Local environment
digy local examples/env/environment_info.py

# Docker environment
digy docker --image python:3.9 examples/env/environment_info.py

# RAM execution (fastest)
digy ram examples/env/environment_info.py

# Remote environment (requires SSH setup)
digy remote user@example.com github.com/yourusername/yourrepo examples/env/environment_info.py
```

## File Attachment Examples

### `attachments/file_processor.py`
Demonstrates how to work with attached files in your scripts.

**Run it with file attachments:**
```bash
# Attach specific files
digy local examples/attachments/file_processor.py --attach file1.txt --attach file2.txt

# Use interactive mode to select files
digy local examples/attachments/file_processor.py --interactive-attach

# Or run in Docker with file attachments
digy docker --image python:3.9 examples/attachments/file_processor.py --attach file1.txt
```

## Authentication Examples

To use authentication, you'll need to set up the appropriate authentication provider. Here's an example using SQL authentication:

```bash
# Run with SQL authentication
digy local --auth sql --auth-config dbconfig.json your_script.py
```

## Creating Your Own Examples

1. Create a new Python script in the appropriate directory
2. Add a descriptive docstring explaining what the example demonstrates
3. Include example commands in the docstring showing how to run it
4. Test your example with different DIGY commands and options

## Testing the Examples

To test all examples, you can use the following commands:

```bash
# Test basic example in different environments
digy local examples/basic/hello_world.py
digy ram examples/basic/hello_world.py

# Test environment info in different modes
digy local examples/env/environment_info.py
digy docker --image python:3.9 examples/env/environment_info.py

# Test file processor with a sample file
echo "Test content" > test.txt
digy local examples/attachments/file_processor.py --attach test.txt
rm test.txt
```

## Troubleshooting

- If you get permission errors, make sure the script is executable: `chmod +x examples/*/*.py`
- For Docker errors, ensure Docker is running and you have permission to use it
- For remote execution, make sure SSH is properly set up and the remote host is accessible
