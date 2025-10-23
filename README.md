# Requirements Scanner

Stop creating countless single-use Python virtual environments. Use this tool to identify your most common package dependencies and create a few reusable environments instead.

## The Problem

Many Python developers end up with dozens of project-specific virtual environments, each containing largely the same packages. This leads to:

- Wasted disk space with duplicate packages across environments
- Slower environment creation and setup times
- Difficulty maintaining consistent package versions across projects
- Environment sprawl that's hard to manage

## The Solution

Requirements Scanner recursively analyzes all `requirements.txt` files across your repositories, identifies patterns in your package usage, and shows you which packages you use most frequently. With this information, you can create a few well-designed reusable environments that serve multiple projects instead of creating bespoke environments for each one.

## Why This Matters

When you discover that 15 of your 20 projects all use `requests`, `numpy`, and `pytest`, you realize you don't need 15 separate environments with these same packages. You need one solid base environment that all these projects can share. The scanner reveals these patterns by:

- **Frequency Analysis**: Shows which packages appear in most of your projects
- **Version Tracking**: Identifies if you're consistently using similar versions (or if there's version fragmentation)
- **Data-Driven Decisions**: Takes the guesswork out of environment design

## How It Works

1. **Scans**: Recursively finds all `requirements.txt` files in your repository directory
2. **Analyzes**: Extracts and normalizes package names, tracking version specifications
3. **Ranks**: Shows you which packages appear most frequently across your projects
4. **Reports**: Generates detailed reports to help you design reusable environments

## Key Features

- Recursive scanning of your entire repository directory tree
- Smart package name normalization (handles case, separators like `-` vs `_`)
- Tracks both package names and version specifications
- Generates four comprehensive reports:
  - **Unique Packages**: Alphabetically sorted, deduplicated list of all packages
  - **Packages by Frequency**: Shows which packages you use most often
  - **Unique Packages with Versions**: Every package+version combination found
  - **Packages by Frequency with Versions**: Most common version specifications
- **🤖 AI-Powered Environment Recommendations** (optional but recommended):
  - Analyzes your package frequency patterns using Claude (Anthropic) or GPT-4 (OpenAI)
  - Suggests 2-5 discrete, reusable environments based on your actual usage
  - Provides environment names, package lists, and descriptions
  - Saves you hours of manual analysis and decision-making

## Use Case Example

Let's say you run the scanner and discover:

- `requests`, `numpy`, and `pandas` appear in 80% of your projects
- `flask` and `sqlalchemy` appear in 50% of your web projects
- `pytest` and `black` appear in 90% of all projects

Instead of creating 20 separate environments, you could create:

1. **base-env**: requests, numpy, pandas, pytest, black (for general Python work)
2. **web-env**: Inherits from base-env, adds flask, sqlalchemy (for web projects)
3. **ml-env**: Inherits from base-env, adds scikit-learn, tensorflow (for ML projects)

This reduces 20 environments down to 3 reusable ones that serve most of your needs.

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
- `ANTHROPIC_API_KEY`: API key for Claude AI analysis (recommended)
- `OPENAI_API_KEY`: API key for GPT-4 AI analysis (alternative)

Example `.env`:
```bash
REPO_BASE=/home/username/repos
VENV_BASE=/home/username/.venv

# AI Analysis (optional but recommended)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

If `REPO_BASE` is set in `.env`, you can run the tool without providing a path argument.

### Getting API Keys for AI Analysis

**Anthropic (Claude) - Recommended:**
- Sign up at https://console.anthropic.com/
- Create an API key in your account settings
- Claude provides excellent analysis of package patterns

**OpenAI (GPT-4) - Alternative:**
- Sign up at https://platform.openai.com/
- Create an API key at https://platform.openai.com/api-keys
- GPT-4 offers strong reasoning about environment design

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

The tool can analyze your package patterns using AI to suggest optimal environments:

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

**AI analysis will:**
1. Read your frequency reports
2. Identify natural package clusters
3. Suggest 2-5 reusable environments with names and descriptions
4. Save recommendations to `analysis/ai_recommendations.txt`
5. Display recommendations in the terminal

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
- `--skip-ai`: Skip AI analysis completely (not recommended)

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

This reduces your 20+ project-specific environments to just 3 reusable ones!
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

# Step 3: Review the frequency report to identify common packages
cat analysis/packages_by_frequency.txt

# Step 4: Design your reusable environments based on the data
# Look for natural clusters:
# - Packages used in 70%+ of projects → base environment
# - Packages used in specific project types → specialized environments

# Step 5: Create your reusable environments
# Example: Create a base environment with your most common packages
conda create -n python-base python=3.11 requests numpy pandas pytest black

# Step 6: Use these environments across multiple projects
# Instead of creating new environments, activate an existing one:
conda activate python-base

# Step 7: Review version-aware reports for consistency
cat analysis/packages_by_frequency_with_versions.txt
# This helps you identify if you need specific version pinning
```

## License

MIT License

## Author

Daniel Rosehill
Email: public@danielrosehill.com
Website: danielrosehill.com
