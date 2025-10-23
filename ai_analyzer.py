#!/usr/bin/env python3
"""
AI Analyzer Module
Uses Anthropic or OpenAI to analyze package frequency data and suggest reusable environments.
"""

import os
from pathlib import Path
from typing import Dict, Optional, List


class AIAnalyzer:
    """Analyzes package frequency data using AI to suggest reusable environments."""

    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        """
        Initialize the AI analyzer.

        Args:
            provider: AI provider to use ("anthropic" or "openai")
            api_key: API key for the provider (uses environment variable if not provided)
        """
        self.provider = provider.lower()
        self.api_key = api_key

        if self.provider not in ["anthropic", "openai"]:
            raise ValueError(f"Unsupported AI provider: {provider}. Use 'anthropic' or 'openai'.")

        # Get API key from environment if not provided
        if not self.api_key:
            if self.provider == "anthropic":
                self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            else:  # openai
                self.api_key = os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                f"No API key provided for {self.provider}. "
                f"Set {self.provider.upper()}_API_KEY environment variable or pass api_key parameter."
            )

    def read_analysis_files(self, analysis_dir: Path) -> Dict[str, str]:
        """
        Read the generated analysis files.

        Args:
            analysis_dir: Directory containing the analysis reports

        Returns:
            Dictionary with file contents
        """
        files_to_read = {
            "unique_packages": "unique_packages.txt",
            "frequency": "packages_by_frequency.txt",
            "unique_with_versions": "unique_packages_with_versions.txt",
            "frequency_with_versions": "packages_by_frequency_with_versions.txt",
        }

        contents = {}
        for key, filename in files_to_read.items():
            file_path = analysis_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents[key] = f.read()
                except Exception as e:
                    print(f"Warning: Could not read {filename}: {e}")
                    contents[key] = ""
            else:
                contents[key] = ""

        return contents

    def generate_prompt(self, analysis_data: Dict[str, str]) -> str:
        """
        Generate the prompt for the AI model.

        Args:
            analysis_data: Dictionary containing analysis file contents

        Returns:
            Formatted prompt string
        """
        prompt = """I have analyzed Python package usage across multiple repositories. Based on the frequency analysis below, please suggest a small number of discrete, reusable Python virtual environments (typically 2-5 environments) that would cover most use cases.

For each suggested environment, provide:
1. A descriptive name (e.g., "python-base", "data-science", "web-dev")
2. The core packages to include (focus on the most frequently used packages)
3. A brief description of what types of projects would use this environment
4. Suggested Python version

Guidelines:
- Focus on packages that appear in 30%+ of projects
- Group related packages together (e.g., web frameworks, data analysis, testing)
- Start with a "base" environment containing the most universal packages
- Keep specialized environments lean - only add what's truly needed
- Consider version compatibility when grouping packages

FREQUENCY ANALYSIS:
{frequency}

UNIQUE PACKAGES (for reference):
{unique}

Please provide your recommendations in a clear, structured format."""

        return prompt.format(
            frequency=analysis_data.get("frequency", "Not available"),
            unique=analysis_data.get("unique_packages", "Not available")
        )

    def analyze_with_anthropic(self, prompt: str) -> str:
        """
        Call Anthropic API to analyze the data.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Analysis response
        """
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")

        client = anthropic.Anthropic(api_key=self.api_key)

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {e}")

    def analyze_with_openai(self, prompt: str) -> str:
        """
        Call OpenAI API to analyze the data.

        Args:
            prompt: The prompt to send to GPT

        Returns:
            Analysis response
        """
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        client = openai.OpenAI(api_key=self.api_key)

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a Python environment design expert who helps developers create efficient, reusable virtual environments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {e}")

    def analyze(self, analysis_dir: Path, output_file: Optional[Path] = None) -> str:
        """
        Analyze the package frequency data and generate environment recommendations.

        Args:
            analysis_dir: Directory containing the analysis reports
            output_file: Optional file to save the recommendations

        Returns:
            AI-generated recommendations
        """
        print(f"\n🤖 Analyzing package usage with {self.provider.upper()} AI...")

        # Read analysis files
        analysis_data = self.read_analysis_files(analysis_dir)

        if not analysis_data.get("frequency"):
            raise ValueError("Could not read frequency analysis file")

        # Generate prompt
        prompt = self.generate_prompt(analysis_data)

        # Call appropriate AI provider
        if self.provider == "anthropic":
            recommendations = self.analyze_with_anthropic(prompt)
        else:  # openai
            recommendations = self.analyze_with_openai(prompt)

        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("# AI-Generated Environment Recommendations\n\n")
                    f.write(f"Generated using: {self.provider.upper()}\n\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(recommendations)
                print(f"\n✓ AI recommendations saved to: {output_file}")
            except Exception as e:
                print(f"Warning: Could not save recommendations to file: {e}")

        return recommendations


def main():
    """Simple test function."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <analysis_dir> [provider]")
        print("  provider: 'anthropic' (default) or 'openai'")
        sys.exit(1)

    analysis_dir = Path(sys.argv[1])
    provider = sys.argv[2] if len(sys.argv) > 2 else "anthropic"

    try:
        analyzer = AIAnalyzer(provider=provider)
        recommendations = analyzer.analyze(
            analysis_dir,
            output_file=analysis_dir / "ai_recommendations.txt"
        )
        print("\n" + "=" * 80)
        print("AI RECOMMENDATIONS")
        print("=" * 80 + "\n")
        print(recommendations)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
