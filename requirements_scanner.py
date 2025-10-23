#!/usr/bin/env python3
"""
Requirements Scanner CLI
Scans a repository base directory for all requirements.txt files,
extracts packages, and generates reports with optional AI analysis.
"""

import os
import re
import argparse
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional


def load_env_file(env_path: Path = None) -> Dict[str, str]:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file (defaults to .env in script directory)

    Returns:
        Dictionary of environment variables
    """
    if env_path is None:
        # Look for .env in the script's directory
        script_dir = Path(__file__).parent
        env_path = script_dir / '.env'

    env_vars = {}

    if not env_path.exists():
        return env_vars

    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")

    return env_vars


class PackageNormalizer:
    """Handles package name normalization and version extraction."""

    @staticmethod
    def parse_requirement(line: str) -> Tuple[str, str]:
        """
        Parse a requirement line and extract package name and version spec.

        Returns:
            Tuple of (normalized_package_name, version_spec)
        """
        # Remove comments
        line = line.split('#')[0].strip()

        # Skip empty lines
        if not line:
            return None, None

        # Skip lines that are just URLs or git references
        if line.startswith(('http://', 'https://', 'git+', '-e ')):
            return None, None

        # Extract package name and version specification
        # Handle various formats: package, package==1.0, package>=1.0, package[extra]>=1.0
        match = re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?)', line)

        if not match:
            return None, None

        package_name = match.group(1)

        # Normalize package name (PyPI treats - and _ as equivalent, lowercase)
        normalized_name = package_name.lower().replace('_', '-')

        # Extract version spec if present
        version_match = re.search(r'([=<>!]+.*?)(?:\s|$)', line[match.end():])
        version_spec = version_match.group(1).strip() if version_match else ''

        return normalized_name, version_spec


class RequirementsScanner:
    """Scans directories for requirements.txt files and extracts packages."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).expanduser().resolve()
        self.normalizer = PackageNormalizer()

    def scan_requirements_files(self) -> List[Path]:
        """
        Recursively find all requirements.txt files in the base path.

        Returns:
            List of Path objects for each requirements.txt file
        """
        requirements_files = []

        for root, dirs, files in os.walk(self.base_path):
            # Skip common directories that shouldn't be scanned
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env'}]

            for file in files:
                if file == 'requirements.txt':
                    requirements_files.append(Path(root) / file)

        return requirements_files

    def extract_packages(self, requirements_files: List[Path]) -> Dict[str, List[str]]:
        """
        Extract all packages from requirements files.

        Returns:
            Dictionary mapping normalized package names to list of version specs found
        """
        packages = {}

        for req_file in requirements_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        package_name, version_spec = self.normalizer.parse_requirement(line)

                        if package_name:
                            if package_name not in packages:
                                packages[package_name] = []
                            if version_spec and version_spec not in packages[package_name]:
                                packages[package_name].append(version_spec)
            except Exception as e:
                print(f"Warning: Could not read {req_file}: {e}")

        return packages

    def extract_packages_with_versions(self, requirements_files: List[Path]) -> Dict[str, int]:
        """
        Extract all package+version combinations from requirements files.

        Returns:
            Dictionary mapping "package==version" to occurrence count
        """
        package_versions = {}

        for req_file in requirements_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    seen_in_file = set()
                    for line in f:
                        package_name, version_spec = self.normalizer.parse_requirement(line)

                        if package_name:
                            # Create full package spec
                            if version_spec:
                                full_spec = f"{package_name}{version_spec}"
                            else:
                                full_spec = package_name

                            if full_spec not in seen_in_file:
                                package_versions[full_spec] = package_versions.get(full_spec, 0) + 1
                                seen_in_file.add(full_spec)
            except Exception as e:
                print(f"Warning: Could not read {req_file}: {e}")

        return package_versions

    def generate_unique_packages_report(self, packages: Dict[str, List[str]], output_file: str):
        """Generate alphabetically sorted, deduplicated package list."""
        sorted_packages = sorted(packages.keys())

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Unique Packages (Alphabetically Sorted)\n")
            f.write(f"# Total unique packages: {len(sorted_packages)}\n\n")

            for package in sorted_packages:
                f.write(f"{package}\n")

        print(f"✓ Unique packages report saved to: {output_file}")

    def generate_frequency_report(self, packages: Dict[str, List[str]],
                                  requirements_files: List[Path], output_file: str):
        """Generate package list sorted by frequency of occurrence."""
        # Count occurrences of each package
        package_counts = {}

        for req_file in requirements_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    seen_in_file = set()
                    for line in f:
                        package_name, _ = self.normalizer.parse_requirement(line)
                        if package_name and package_name not in seen_in_file:
                            package_counts[package_name] = package_counts.get(package_name, 0) + 1
                            seen_in_file.add(package_name)
            except Exception as e:
                print(f"Warning: Could not read {req_file}: {e}")

        # Sort by frequency (descending)
        sorted_by_freq = sorted(package_counts.items(), key=lambda x: (-x[1], x[0]))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Packages by Frequency\n")
            f.write(f"# Total requirements.txt files scanned: {len(requirements_files)}\n")
            f.write(f"# Total unique packages: {len(package_counts)}\n\n")
            f.write(f"{'Package':<40} {'Count':<10} {'Versions Found'}\n")
            f.write(f"{'-'*40} {'-'*10} {'-'*40}\n")

            for package, count in sorted_by_freq:
                versions = ', '.join(packages[package]) if packages[package] else 'any'
                f.write(f"{package:<40} {count:<10} {versions}\n")

        print(f"✓ Frequency report saved to: {output_file}")

    def generate_unique_packages_with_versions_report(self, package_versions: Dict[str, int], output_file: str):
        """Generate alphabetically sorted, version-aware package list."""
        sorted_packages = sorted(package_versions.keys())

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Unique Packages with Versions (Alphabetically Sorted)\n")
            f.write(f"# Total unique package+version combinations: {len(sorted_packages)}\n\n")

            for package_spec in sorted_packages:
                f.write(f"{package_spec}\n")

        print(f"✓ Unique packages with versions report saved to: {output_file}")

    def generate_frequency_with_versions_report(self, package_versions: Dict[str, int],
                                                requirements_files: List[Path], output_file: str):
        """Generate version-aware package list sorted by frequency."""
        # Sort by frequency (descending)
        sorted_by_freq = sorted(package_versions.items(), key=lambda x: (-x[1], x[0]))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Packages with Versions by Frequency\n")
            f.write(f"# Total requirements.txt files scanned: {len(requirements_files)}\n")
            f.write(f"# Total unique package+version combinations: {len(package_versions)}\n\n")
            f.write(f"{'Package Specification':<60} {'Count':<10}\n")
            f.write(f"{'-'*60} {'-'*10}\n")

            for package_spec, count in sorted_by_freq:
                f.write(f"{package_spec:<60} {count:<10}\n")

        print(f"✓ Frequency with versions report saved to: {output_file}")


def main():
    """Main CLI entry point."""
    # Load environment variables from .env file
    env_vars = load_env_file()

    parser = argparse.ArgumentParser(
        description='Scan repositories for requirements.txt files and analyze package usage.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/repos
  %(prog)s ~/repos/github --output-dir ./reports
  %(prog)s  # Uses REPO_BASE from .env if no argument provided
        """
    )

    parser.add_argument(
        'repo_base',
        nargs='?',  # Make it optional
        default=env_vars.get('REPO_BASE'),
        help='Base directory containing repositories to scan (default: REPO_BASE from .env)'
    )

    parser.add_argument(
        '--output-dir',
        default='./analysis',
        help='Directory to save output reports (default: ./analysis)'
    )

    parser.add_argument(
        '--unique-output',
        default='unique_packages.txt',
        help='Filename for unique packages report (default: unique_packages.txt)'
    )

    parser.add_argument(
        '--frequency-output',
        default='packages_by_frequency.txt',
        help='Filename for frequency report (default: packages_by_frequency.txt)'
    )

    parser.add_argument(
        '--ai-analysis',
        action='store_true',
        help='Enable AI-powered environment recommendations (recommended, requires API key)'
    )

    parser.add_argument(
        '--ai-provider',
        choices=['anthropic', 'openai'],
        default='anthropic',
        help='AI provider to use for analysis (default: anthropic)'
    )

    parser.add_argument(
        '--skip-ai',
        action='store_true',
        help='Skip AI analysis (not recommended - you may miss valuable insights)'
    )

    args = parser.parse_args()

    # Validate repo base path is provided
    if not args.repo_base:
        print("Error: No repository base path provided.")
        print("Either provide a path as an argument or set REPO_BASE in .env file.")
        return 1

    # Validate repo base path
    repo_base = Path(args.repo_base).expanduser().resolve()
    if not repo_base.exists():
        print(f"Error: Repository base path does not exist: {repo_base}")
        return 1

    if not repo_base.is_dir():
        print(f"Error: Repository base path is not a directory: {repo_base}")
        return 1

    # Create output directory if needed
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning repository base: {repo_base}")

    # Initialize scanner
    scanner = RequirementsScanner(repo_base)

    # Find all requirements.txt files
    print("\nSearching for requirements.txt files...")
    requirements_files = scanner.scan_requirements_files()

    if not requirements_files:
        print("No requirements.txt files found.")
        return 0

    print(f"Found {len(requirements_files)} requirements.txt file(s)")

    # Extract packages (normalized - no versions)
    print("\nExtracting packages (normalized)...")
    packages = scanner.extract_packages(requirements_files)
    print(f"Extracted {len(packages)} unique package(s)")

    # Extract packages with versions
    print("\nExtracting packages with versions...")
    package_versions = scanner.extract_packages_with_versions(requirements_files)
    print(f"Extracted {len(package_versions)} unique package+version combination(s)")

    # Generate reports
    print("\nGenerating reports...")

    # Normalized reports (no versions)
    unique_output = output_dir / args.unique_output
    frequency_output = output_dir / args.frequency_output

    scanner.generate_unique_packages_report(packages, unique_output)
    scanner.generate_frequency_report(packages, requirements_files, frequency_output)

    # Version-aware reports
    unique_with_versions_output = output_dir / "unique_packages_with_versions.txt"
    frequency_with_versions_output = output_dir / "packages_by_frequency_with_versions.txt"

    scanner.generate_unique_packages_with_versions_report(package_versions, unique_with_versions_output)
    scanner.generate_frequency_with_versions_report(package_versions, requirements_files, frequency_with_versions_output)

    print("\n✓ Scan complete!")
    print(f"\nReports saved to: {output_dir}")
    print("  Normalized (package names only):")
    print(f"    - {unique_output.name}")
    print(f"    - {frequency_output.name}")
    print("  Version-aware (package+version):")
    print(f"    - {unique_with_versions_output.name}")
    print(f"    - {frequency_with_versions_output.name}")

    # AI Analysis (optional but recommended)
    run_ai_analysis = False

    if args.skip_ai:
        print("\n⚠️  AI analysis skipped (not recommended)")
    elif args.ai_analysis:
        run_ai_analysis = True
    else:
        # Prompt user if they want AI analysis (recommended)
        print("\n" + "=" * 80)
        print("🤖 AI-POWERED ENVIRONMENT RECOMMENDATIONS")
        print("=" * 80)
        print("\nWould you like AI to analyze your package usage and suggest")
        print("optimal reusable environments? (Recommended)")
        print(f"\nThis will use {args.ai_provider.upper()} to generate intelligent recommendations")
        print("based on your package frequency patterns.")

        # Check if API key is available
        api_key_var = f"{args.ai_provider.upper()}_API_KEY"
        if os.environ.get(api_key_var):
            print(f"\n✓ {api_key_var} detected")
            response = input("\nRun AI analysis? [Y/n]: ").strip().lower()
            run_ai_analysis = response in ['', 'y', 'yes']
        else:
            print(f"\n⚠️  {api_key_var} not found in environment")
            print(f"Set {api_key_var} to enable AI analysis, or use --skip-ai to suppress this prompt")
            run_ai_analysis = False

    if run_ai_analysis:
        try:
            from ai_analyzer import AIAnalyzer

            analyzer = AIAnalyzer(provider=args.ai_provider)
            ai_output = output_dir / "ai_recommendations.txt"

            recommendations = analyzer.analyze(output_dir, output_file=ai_output)

            print("\n" + "=" * 80)
            print("AI RECOMMENDATIONS")
            print("=" * 80 + "\n")
            print(recommendations)
            print("\n" + "=" * 80)

        except ImportError as e:
            print(f"\n⚠️  Could not import AI analyzer: {e}")
            print("Make sure you've installed the package with AI dependencies:")
            print("  uv pip install -e .")
        except Exception as e:
            print(f"\n⚠️  AI analysis failed: {e}")
            print("Continuing with basic reports only...")

    return 0


if __name__ == '__main__':
    exit(main())
