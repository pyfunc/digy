# DIGY Examples

This directory contains example scripts that demonstrate various features of DIGY. Each example is designed to work with DIGY's execution environments (local, docker, ram, remote).

## 📋 Table of Contents
- [Basic Examples](#basic-examples)
- [Environment Examples](#environment-examples)
- [Data Processing](#data-processing-example)
- [Web Scraping](#web-scraping-example)
- [Machine Learning](#machine-learning-example)
- [File Operations](#file-attachment-examples)
- [Authentication](#authentication-examples)
- [Creating Your Own Examples](#creating-your-own-examples)
- [Testing the Examples](#testing-the-examples)
- [Troubleshooting](#troubleshooting)

## Basic Examples

### `basic/hello_world.py`
A simple "Hello, World!" example that shows basic script execution.

**Dependencies**: None (uses standard library only)

**Run it with:**
```bash
# Run locally
digy local examples/basic/hello_world.py

# Run in RAM for better performance
digy ram examples/basic/hello_world.py

# Run with debug output
digy --debug local examples/basic/hello_world.py
```

**Expected Output**:
```
Hello, DIGY!
This is a basic example running in the local environment.
You can pass arguments to this script after the filename.
```

## Environment Examples

### `env/environment_info.py`
Shows detailed information about the current execution environment, including:
- Python version and paths
- Platform information
- Environment variables
- Process information
- Execution context

**Dependencies**: None (uses standard library only)

**Run it with different environments:**
```bash
# Local environment (default)
digy local examples/env/environment_info.py

# Docker environment (isolated)
digy docker --image python:3.9 examples/env/environment_info.py

# RAM execution (fastest, no disk I/O)
digy ram examples/env/environment_info.py

# Remote execution (via SSH)
digy remote user@example.com github.com/pyfunc/yourrepo examples/env/environment_info.py
```

**Example Output**:
```
DIGY Environment Information
==============================

Python Version
--------------
  3.12.9 | packaged by Anaconda, Inc. | (main, Feb  6 2025, 18:56:27) [GCC 11.2.0]

Platform
--------
  Linux-6.14.11-300.fc42.x86_64-x86_64-with-glibc2.41

Current Directory
-----------------
  /home/user/digy

Environment Variables
---------------------
  PATH: /usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
  PYTHONPATH: /app
  VIRTUAL_ENV: /venv

Process Info
------------
  Process ID: 12345
  Parent Process ID: 67890
  User: user
  Effective User: 1000

Environment check complete!
```

## Data Processing Example

### `data_processing/data_analyzer.py`
Demonstrates data analysis with pandas and matplotlib. This example:
- Loads data from a CSV file
- Performs basic statistical analysis
- Generates visualizations
- Saves results to the specified output directory

**Dependencies**:
- pandas
- matplotlib
- numpy (automatically installed with pandas)

**Run it with sample data:**
```bash
# Install dependencies
pip install pandas matplotlib

# Run with the included sample data
digy local examples/data_processing/data_analyzer.py --input-file examples/data_processing/sample_data.csv

# Save output to a specific directory
digy local examples/data_processing/data_analyzer.py --input-file examples/data_processing/sample_data.csv --output-dir my_results

# Run in Docker with all dependencies included
digy docker --image python:3.9-slim examples/data_processing/data_analyzer.py --input-file /app/examples/data_processing/sample_data.csv
```

**Example Output**:
```
📊 Loading data from examples/data_processing/sample_data.csv
✅ Loaded 10 rows
📊 Columns: id, value, category, score

📈 Basic Statistics:
             id      value      score
count  10.00000  10.000000  10.000000
mean    5.50000  14.490000  86.000000
std     3.02765   3.926675   6.146363
min     1.00000   9.800000  76.000000
25%     3.25000  11.675000  82.500000
50%     5.50000  13.750000  86.500000
75%     7.75000  16.625000  90.500000
max    10.00000  22.100000  95.000000

📊 Generating plots for numeric columns...
✅ Saved id distribution plot to analysis_output/id_distribution.png
✅ Saved value distribution plot to analysis_output/value_distribution.png
✅ Saved score distribution plot to analysis_output/score_distribution.png

✅ Analysis complete! Results saved to /path/to/analysis_output/
```

## Web Scraping Example

### `web_scraping/website_scraper.py`
Demonstrates web scraping with requests and BeautifulSoup. This example:
- Fetches a webpage
- Extracts links and metadata
- Saves results to a JSON file
- Handles errors and timeouts

**Dependencies**:
- requests
- beautifulsoup4
- lxml (recommended for better parsing)

**Install dependencies:**
```bash
pip install requests beautifulsoup4 lxml
```

**Run it to scrape a website:**
```bash
# Basic usage (scrapes example.com)
digy local examples/web_scraping/website_scraper.py --url https://example.com

# Scrape a different website
digy local examples/web_scraping/website_scraper.py --url https://pypi.org

# Save results to a custom directory
digy local examples/web_scraping/website_scraper.py --url https://example.com --output-dir scrape_results

# Limit number of links to extract
digy local examples/web_scraping/website_scraper.py --url https://example.com --max-links 10

# Run in Docker with all dependencies included
digy docker --image python:3.9-slim examples/web_scraping/website_scraper.py --url https://example.com
```

**Example Output**:
```
🔍 Starting web scraping of https://example.com
📂 Output directory: scrape_results
🔗 Maximum links to extract: 20
🌐 Fetching https://example.com
💾 Results saved to scrape_results/scrape_example_com_20230622_123456.json
✅ Scraping complete! Results saved to scrape_results/scrape_example_com_20230622_123456.json

📊 Scraping Results:
🌐 URL: https://example.com
📝 Title: Example Domain
🔗 Links found: 1
📄 Description: No description

🔗 Top links:
  1. https://www.iana.org/domains/example
     More information...
```

## Machine Learning Example

### `machine_learning/iris_classifier.py`
A complete machine learning workflow example using scikit-learn. This script:
- Loads the Iris dataset
- Trains a Random Forest classifier
- Evaluates the model
- Saves the trained model and metrics

**Dependencies**:
- scikit-learn
- numpy
- joblib (for model serialization)

**Installation and Setup:**
```bash
# Create and activate a virtual environment (recommended)
python -m venv ml_env
source ml_env/bin/activate  # On Windows: ml_env\Scripts\activate

# Install required packages
pip install scikit-learn numpy joblib
```

**Running the Example:**
```bash
# Run the script directly with Python
python -m examples.machine_learning.iris_classifier

# Or navigate to the examples directory and run:
cd examples/machine_learning
python iris_classifier.py
```

**Example Output:**
```
Loading Iris dataset...
Splitting data into training and test sets...
Training Random Forest classifier...
Evaluating model...
Saving model...

Training complete!
Model saved to: output/iris_classifier.joblib

Metrics:
accuracy: 0.9
setosa_precision: 1.0
setosa_recall: 1.0
setosa_f1-score: 1.0
...
```

**Key Features:**
- Simple, self-contained script with no external dependencies beyond scikit-learn
- Saves the trained model to disk for later use
- Provides detailed classification metrics
- Works in any Python 3.8+ environment with the required dependencies

**Note:** This is a standalone Python script that demonstrates a complete ML workflow. For DIGY integration examples, see the other examples in this directory.

## File Attachment Examples

### `attachments/file_processor.py`
Demonstrates how to work with attached files in your scripts. This example shows:
- How to specify files to attach
- Interactive file selection
- File processing in different environments
- Working with file metadata

**Dependencies**: None (uses standard library only)

**Run it with file attachments:**
```bash
# Create some test files
echo "Test content 1" > test1.txt
echo "Test content 2" > test2.txt

# Attach specific files
digy local examples/attachments/file_processor.py --attach test1.txt --attach test2.txt

# Use interactive mode to select files
digy local examples/attachments/file_processor.py --interactive-attach

# Run in Docker with file attachments
digy docker --image python:3.9-slim examples/attachments/file_processor.py --attach test1.txt

# Clean up test files
rm test1.txt test2.txt
```

**Example Output**:
```
📁 Processing 2 attached files:

📄 File 1: test1.txt
   Size: 14 bytes
   Type: text/plain
   Content: Test content 1

📄 File 2: test2.txt
   Size: 14 bytes
   Type: text/plain
   Content: Test content 2

✅ Processed 2 files successfully!
```

**Note**: When using Docker, make sure to:
1. Use absolute paths for files outside the current directory
2. Mount volumes if you need to access files from the host system:
   ```bash
   digy docker --image python:3.9-slim -v $(pwd):/data examples/attachments/file_processor.py --attach /data/test1.txt
   ```

## Authentication Examples

DIGY supports various authentication methods for secure access to resources. Here are some examples:

### SQL Authentication
```bash
# Run with SQL authentication
digy local --auth sql --auth-config dbconfig.json your_script.py

# Example dbconfig.json:
# {
#   "database": "mydb",
#   "user": "user",
#   "password": "password",
#   "host": "localhost",
#   "port": 5432
# }
```

### Web Authentication
```bash
# Web-based OAuth2 authentication
digy local --auth oauth2 --auth-config oauth_config.json your_script.py
```

### Environment-based Authentication
```bash
# Load credentials from environment variables
digy local --auth env your_script.py

# Required environment variables:
# DIGY_AUTH_USERNAME
# DIGY_AUTH_PASSWORD
```

### Custom Authentication
You can implement custom authentication by creating a Python module that implements the `authenticate()` function.

```python
# custom_auth.py
def authenticate(config):
    # Your authentication logic here
    return {"token": "your_auth_token"}
```

```bash
digy local --auth custom:custom_auth --auth-config auth_config.json your_script.py
```

## Creating Your Own Examples

1. Create a new Python script in the appropriate directory
2. Add a descriptive docstring explaining what the example demonstrates
3. Include example commands in the docstring showing how to run it
4. Test your example with different DIGY commands and options

## Testing the Examples

To test all examples, you can use the following commands:

### Basic Testing
```bash
# Test basic example in different environments
digy local examples/basic/hello_world.py
digy ram examples/basic/hello_world.py

# Test environment info in different modes
digy local examples/env/environment_info.py
digy docker --image python:3.9-slim examples/env/environment_info.py
```

### Data Processing Example
```bash
# Test data analyzer with sample data
digy local examples/data_processing/data_analyzer.py --input-file examples/data_processing/sample_data.csv

# Check output in analysis_output/
ls -l analysis_output/
```

### Web Scraping Example
```bash
# Test web scraper with example.com
digy local examples/web_scraping/website_scraper.py --url https://example.com

# Check output in scrape_results/
ls -l scrape_results/
```

### Machine Learning Example
```bash
# Create virtual environment for ML dependencies
python -m venv ml_env
source ml_env/bin/activate  # On Windows: ml_env\Scripts\activate
pip install scikit-learn pandas matplotlib joblib scipy

# Run ML example
digy local examples/machine_learning/iris_classifier.py --output-dir ml_output

# Check output in ml_output/
ls -l ml_output/
```

### File Processing Example
```bash
# Create test files
echo "Test content 1" > test1.txt
echo "Test content 2" > test2.txt

# Test file processor
digy local examples/attachments/file_processor.py --attach test1.txt --attach test2.txt

# Clean up
deactivate  # Exit virtual environment
rm test1.txt test2.txt
```

## Troubleshooting

### Common Issues and Solutions

#### Permission Errors
```bash
# Make scripts executable
chmod +x examples/*/*.py

# If running with Docker, ensure your user is in the docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Missing Dependencies
```bash
# Check if package is installed
pip list | grep package_name

# Install missing dependencies
pip install package_name

# For ML examples, create a virtual environment
python -m venv ml_env
source ml_env/bin/activate  # On Windows: ml_env\Scripts\activate
pip install -r requirements.txt  # Or install packages individually
```

#### Docker Issues
```bash
# Check if Docker is running
docker info

# Pull the latest image
docker pull python:3.9-slim

# Run with more verbose output
digy --debug docker --image python:3.9-slim examples/your_script.py
```

#### Web Scraping Issues
- If you get SSL errors, try:
  ```bash
  pip install --upgrade certifi
  ```
- If the target website blocks your requests, try adding headers or using a proxy

#### ML Example Issues
- If you get memory errors, reduce the dataset size or model complexity
- For visualization issues, ensure you have a display server running or use a non-interactive backend:
  ```python
  import matplotlib
  matplotlib.use('Agg')  # Non-interactive backend
  ```

#### Getting Help
- Check the logs in `~/.cache/digy/logs/`
- Run with `--debug` flag for more verbose output
- Open an issue on GitHub with the error message and steps to reproduce
