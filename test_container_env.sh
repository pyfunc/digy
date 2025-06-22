#!/bin/bash

# Test script to debug container environment and Git availability

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Create a test script to run inside the container
cat > "$TEMP_DIR/test_git.sh" << 'EOF'
#!/bin/bash

# Print environment information
echo "=== Environment Variables ==="
printenv | sort
echo ""

# Check PATH
echo "=== PATH ==="
echo "$PATH"
echo ""

# Check if git exists
if command -v git &> /dev/null; then
    echo "Git found at: $(which git)"
    echo "Git version: $(git --version)"
else
    echo "Git not found in PATH"
    echo "Searching for git in common locations..."
    find / -name git -type f -executable 2>/dev/null | grep -v "Permission denied" || echo "No git found"
fi

# Check Python environment
echo ""
echo "=== Python Environment ==="
which python3
python3 --version
python3 -c "import sys; print('Python path:', sys.path)"
EOF

chmod +x "$TEMP_DIR/test_git.sh"

# Run the test in the container
echo "Running test in container..."
podman run --rm -v "$TEMP_DIR:/test" localhost/digy-base:latest /test/test_git.sh

# Clean up
rm -rf "$TEMP_DIR"
echo "Cleaned up temporary directory"
