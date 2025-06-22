#!/usr/bin/env python3
"""File processing example for DIGY.

This script demonstrates how to work with attached files.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Union

# Add parent directory to path to allow importing from digy
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from digy import digy_command  # noqa: E402


def process_files(attachments_dir: str = ".digy_attachments") -> None:
    """Process all files in the attachments directory.

    Args:
        attachments_dir: Directory containing attached files
    """
    print("\n[bold blue]Processing Attached Files[/]")
    print("=" * 30)

    # Check if attachments directory exists
    if not os.path.exists(attachments_dir):
        print("[yellow]No attachments directory found.[/]")
        print(
            "Run with: digy local . file_processor.py \
              --attach file1.txt"
        )
        return

    # List all files in the attachments directory
    attachments_path = Path(attachments_dir)
    files = list(attachments_path.glob("*"))

    if not files:
        print("[yellow]No files found in attachments directory.[/]")
        return

    # Process each file
    for file_path in files:
        try:
            print(f"\nProcessing {file_path.name}:")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"  - Size: {len(content)} bytes")
                print(f"  - Lines: {len(content.splitlines())}")
                print(f"  - Words: {len(content.split())}")
        except Exception as e:
            print(f"[red]Error processing {file_path}: {e}[/red]")


class FileProcessor:
    """Process files with various operations."""

    def __init__(self, input_dir: str = "input", output_dir: str = "output") -> None:
        """Initialize with input and output directories.

        Args:
            input_dir: Directory containing input files
            output_dir: Directory to save processed files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: Union[str, Path]) -> Dict[str, Union[int, str]]:
        """Process a single file and return statistics.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary containing file statistics or error message
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = file_path.read_text(encoding="utf-8")
            word_count = len(content.split())
            char_count = len(content)
            line_count = len(content.splitlines())

            return {
                "file": str(file_path),
                "word_count": word_count,
                "char_count": char_count,
                "line_count": line_count,
                "status": "processed",
            }
        except Exception as e:
            return {"file": str(file_path), "error": str(e)}

    def process_directory(self) -> List[Dict[str, Union[int, str]]]:
        """Process all files in the input directory and return results.

        Returns:
            List of dictionaries containing processing results for each file
        """
        if not self.input_dir.exists():
            return [{"error": f"Input directory not found: {self.input_dir}"}]

        results = []
        for file_path in self.input_dir.glob("*"):
            if file_path.is_file():
                results.append(self.process_file(file_path))

        return results


def main() -> None:
    """Main function to demonstrate file processing."""
    print("\n[bold]DIGY File Processor Example[/]")
    msg = (
        "This example shows how to work with attached files in "
        "DIGY. You can attach files using the --attach flag or "
        "--interactive-attach."
    )
    print(msg)

    # Show current working directory
    print(f"\nCurrent working directory: {os.getcwd()}")

    # Process any attached files
    process_files()

    print("\n[green]File processing complete![/]")
    print(
        "Try running with different files using the --attach or "
        "--interactive-attach options."
    )


if __name__ == "__main__":
    # When run directly, execute the command
    try:
        from rich import print  # noqa: F401
    except ImportError:
        pass  # Fall back to standard print

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        main()
    else:
        digy_command()
