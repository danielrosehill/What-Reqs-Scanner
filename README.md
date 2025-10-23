# Requirements Scanner

A tool for analyzing Python package dependencies across multiple repositories to identify common packages and inform environment management decisions.

## Overview

Requirements Scanner recursively analyzes `requirements.txt` files across your repositories and generates frequency reports showing which packages appear most often. This data can inform decisions about creating shared or reusable Python environments.

## Features

- **Frequency Analysis**: Counts package occurrences across all requirements files
- **Version Tracking**: Records version specifications for each package
- **Pattern Identification**: Identifies commonly used packages across projects

## How It Works

1. **Scans**: Recursively finds all `requirements.txt` files in your repository directory
2. **Analyzes**: Extracts and normalizes package names, tracking version specifications
3. **Ranks**: Shows you which packages appear most frequently across your projects
4. **Reports**: Generates detailed reports to help you design reusable environments

## Reports Generated

- **Unique Packages**: Alphabetically sorted, deduplicated list of all packages
- **Packages by Frequency**: Package counts with all versions found
- **Unique Packages with Versions**: Every package+version combination found
- **Packages by Frequency with Versions**: Most common version specifications
- **AI-Powered Environment Recommendations** (optional):
  - Analyzes package frequency patterns using Claude (Anthropic) or GPT-4 (OpenAI)
  - Suggests 2-5 reusable environments based on package usage patterns
  - Provides environment names, package lists, and descriptions

## Use Case Example

If the scanner finds:

- `requests`, `numpy`, and `pandas` appear in 80% of projects
- `flask` and `sqlalchemy` appear in 50% of web projects
- `pytest` and `black` appear in 90% of all projects

This data could inform creation of shared environments:

1. **base-env**: requests, numpy, pandas, pytest, black (for general Python work)
2. **web-env**: Inherits from base-env, adds flask, sqlalchemy (for web projects)
3. **ml-env**: Inherits from base-env, adds scikit-learn, tensorflow (for ML projects)

## Installation

This project uses `uv` for package management. To install:

```bash
# Clone the repository
git clone https://github.com/danielrosehill/What-Reqs-Scanner.git
cd What-Reqs-Scanner

# Create virtual environment with uv
uv venv

# Activate the environment
source .venv/bin/activate

# Install in editable mode
uv pip install -e .
```

## Configuration

The tool supports configuration via a `.env` file for convenience:

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

Available environment variables:

- `REPO_BASE`: Base directory where your code repositories are stored
- `VENV_BASE`: Preferred location for storing virtual environments (for reference)
- `ANTHROPIC_API_KEY`: API key for Claude AI analysis
- `OPENAI_API_KEY`: API key for GPT-4 AI analysis

Example `.env`:
```bash
REPO_BASE=/home/username/repos
VENV_BASE=/home/username/.venv

# AI Analysis (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

If `REPO_BASE` is set in `.env`, you can run the tool without providing a path argument.

### Getting API Keys for AI Analysis

**Anthropic (Claude):**
- Sign up at https://console.anthropic.com/
- Create an API key in your account settings

**OpenAI (GPT-4):**
- Sign up at https://platform.openai.com/
- Create an API key at https://platform.openai.com/api-keys

## Usage

### Basic Usage

Scan your repositories directory:

```bash
requirements-scanner ~/repos
```

Or use the shorter alias:

```bash
reqs-scan ~/repos
```

If you've configured `REPO_BASE` in `.env`, you can run without arguments:

```bash
reqs-scan
```

### AI-Powered Analysis

The tool can analyze your package patterns using AI to suggest environment configurations:

```bash
# Run with AI analysis (interactive prompt if API key is set)
reqs-scan ~/repos

# Force AI analysis without prompting
reqs-scan ~/repos --ai-analysis

# Use OpenAI instead of Anthropic
reqs-scan ~/repos --ai-analysis --ai-provider openai

# Skip AI analysis entirely
reqs-scan ~/repos --skip-ai
```

**AI analysis process:**
1. Reads frequency reports
2. Identifies package clusters
3. Suggests 2-5 reusable environments with names and descriptions
4. Saves recommendations to `analysis/ai_recommendations.txt`
5. Displays recommendations in terminal

### Advanced Options

```bash
# Specify custom output directory
requirements-scanner ~/repos/github --output-dir ./reports

# Customize output filenames
requirements-scanner ~/repos \
  --unique-output my_packages.txt \
  --frequency-output package_stats.txt

# Combine options with AI analysis
requirements-scanner ~/repos/github \
  --output-dir ~/analysis \
  --ai-analysis \
  --ai-provider anthropic
```

### Command-line Options

- `repo_base` (optional if set in .env): Base directory containing repositories to scan
- `--output-dir`: Directory to save output reports (default: `./analysis`)
- `--unique-output`: Filename for unique packages report (default: `unique_packages.txt`)
- `--frequency-output`: Filename for frequency report (default: `packages_by_frequency.txt`)
- `--ai-analysis`: Enable AI-powered environment recommendations (prompts if not set)
- `--ai-provider`: AI provider to use: `anthropic` (default) or `openai`
- `--skip-ai`: Skip AI analysis completely

## Output Format

The tool generates four reports (plus optional AI recommendations) in the analysis directory:

### 1. Unique Packages Report (Normalized)
`unique_packages.txt` - Package names only, no version info

```
# Unique Packages (Alphabetically Sorted)
# Total unique packages: 42

django
flask
numpy
pandas
requests
...
```

### 2. Packages by Frequency Report (Normalized)
`packages_by_frequency.txt` - Shows all versions found for each package

```
# Packages by Frequency
# Total requirements.txt files scanned: 15
# Total unique packages: 42

Package                                  Count      Versions Found
---------------------------------------- ---------- ----------------------------------------
requests                                 12         >=2.25.0, ==2.28.0, >=2.0.0
numpy                                    10         >=1.20.0, ==1.21.0
pandas                                   8          >=1.3.0, ==1.4.2
...
```

### 3. Unique Packages with Versions Report
`unique_packages_with_versions.txt` - Each package+version combination listed separately

```
# Unique Packages with Versions (Alphabetically Sorted)
# Total unique package+version combinations: 87

django==3.2.0
django==4.1.0
django>=3.0
flask==2.0.1
flask>=1.1.0
numpy==1.20.0
numpy==1.21.0
...
```

### 4. Packages by Frequency with Versions Report
`packages_by_frequency_with_versions.txt` - Package+version combinations by frequency

```
# Packages with Versions by Frequency
# Total requirements.txt files scanned: 15
# Total unique package+version combinations: 87

Package Specification                                        Count
------------------------------------------------------------ ----------
requests>=2.25.0                                             8
django==4.1.0                                                6
numpy>=1.20.0                                                5
flask>=1.1.0                                                 4
...
```

### 5. AI Recommendations Report (Optional)
`ai_recommendations.txt` - AI-generated environment suggestions

```
# AI-Generated Environment Recommendations

Generated using: ANTHROPIC

================================================================================

Based on your package usage analysis, I recommend creating 3 reusable Python
environments:

## 1. python-base (Core Development Environment)

**Packages:**
- requests (appears in 85% of projects)
- pytest (appears in 90% of projects)
- black (appears in 75% of projects)
- python-dotenv (appears in 70% of projects)

**Use for:** General Python development, testing, and formatting across most projects.

**Suggested Python version:** 3.11 or 3.12

## 2. data-science (Data Analysis Environment)

**Packages:**
- All packages from python-base, plus:
- numpy (appears in 60% of projects)
- pandas (appears in 55% of projects)
- matplotlib (appears in 40% of projects)
- jupyter (appears in 45% of projects)

**Use for:** Data analysis, visualization, and notebook-based work.

**Suggested Python version:** 3.11

## 3. web-dev (Web Development Environment)

**Packages:**
- All packages from python-base, plus:
- flask (appears in 45% of projects)
- sqlalchemy (appears in 35% of projects)
- jinja2 (appears in 40% of projects)

**Use for:** Web applications and API development.

**Suggested Python version:** 3.11

This example shows how 3 environments could serve 20+ projects.
```

## Technical Details

The scanner performs intelligent analysis of your requirements files:

1. **Scanning**: Recursively walks your repository directory tree
2. **Filtering**: Skips common directories like `.git`, `__pycache__`, `node_modules`, `.venv`
3. **Parsing**: Extracts package names and version specifications from each `requirements.txt`
4. **Normalization**: Handles package name variations (PyPI treats `-` and `_` as equivalent, case-insensitive)
5. **Frequency Analysis**: Counts how many projects use each package
6. **Reporting**: Generates detailed reports to inform your environment design decisions

## Package Normalization

The tool normalizes package names to handle variations:

- Case-insensitive: `Django` and `django` are treated as the same
- Separator normalization: `scikit-learn` and `scikit_learn` are treated as the same
- Version specs are tracked separately: `requests>=2.25.0` and `requests==2.28.0` are both recorded

## Example Workflow

```bash
# Step 1: Activate the scanner's virtual environment
source .venv/bin/activate

# Step 2: Scan your repositories
reqs-scan ~/repos/github  # Or just 'reqs-scan' if REPO_BASE is configured

# Step 3: Review the frequency report
cat analysis/packages_by_frequency.txt

# Step 4: Analyze package usage patterns
# - Packages used in 70%+ of projects
# - Packages used in specific project types

# Step 5: Create environments based on the data
# Example: Create a base environment with common packages
conda create -n python-base python=3.11 requests numpy pandas pytest black

# Step 6: Use shared environments
conda activate python-base

# Step 7: Review version-specific reports
cat analysis/packages_by_frequency_with_versions.txt
```

## License

MIT License

## Author

Daniel Rosehill
Email: public@danielrosehill.com
Website: danielrosehill.com
