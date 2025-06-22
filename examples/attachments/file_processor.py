#!/usr/bin/env python3
"""File processing example for DIGY.

This script demonstrates how to work with attached files.

Run with file attachments:
  digy local . file_processor.py --attach file1.txt --attach file2.txt

Or use interactive mode:
  digy local . file_processor.py --interactive-attach

Or from a GitHub repo:
  digy local github.com/pyfunc/digy file_processor.py --attach file1.txt
"""
import os
from pathlib import Path


def process_files(attachments_dir='.digy_attachments'):
    """Process all files in the attachments directory.

    Args:
        attachments_dir (str): Directory containing attached files
    """
    print("\n[bold blue]Processing Attached Files[/bold blue]")
    print("=" * 30)

    # Check if attachments directory exists
    if not os.path.exists(attachments_dir):
        print("[yellow]No attachments directory found.[/yellow]")
        print("Run with: digy local . file_processor.py --attach file1.txt")
        return

    # List all files in the attachments directory
    attachments_path = Path(attachments_dir)
    files = list(attachments_path.glob('*'))

    if not files:
        print("[yellow]No files found in attachments directory.[/yellow]")
        return

    print(f"Found {len(files)} attached file(s):")

    # Process each file
    for i, file_path in enumerate(files, 1):
        try:
            # Get file info
            file_size = file_path.stat().st_size
            file_type = "directory" if file_path.is_dir() else "file"
            header = (
                f"\n[{i}] {file_path.name} "
                f"({file_type}, {file_size} bytes)"
            )
            print(header)
            print("-" * len(header))

            # For text files, show a preview
            if file_path.is_file() and file_size < 1024 * 10:  # < 10KB
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(500)  # First 500 chars
                        if content.strip():
                            print("Preview:")
                            print("```")
                            print(content)
                            if len(content) < 500:
                                print("```")
                            else:
                                print("... (truncated)")
                except (UnicodeDecodeError, PermissionError) as e:
                    msg = f"(Binary file - {str(e)}"[:80] + ")"
                    print(msg)

        except Exception as e:
            print(f"[red]Error processing {file_path}: {e}[/red]")


def main():
    """Main function to demonstrate file processing."""
    print("\n[bold]DIGY File Processor Example[/bold]")
    msg = (
        "This example shows how to work with attached files in DIGY. "
        "You can attach files using the --attach flag or "
        "--interactive-attach."
    )
    print(msg)

    # Show current working directory
    print(f"\nCurrent working directory: {os.getcwd()}")

    # Process any attached files
    process_files()

    print("\n[green]File processing complete![/green]")
    print(
        "Try running with different files using the "
        "--attach or --interactive-attach options."
    )


if __name__ == "__main__":
    try:
        from rich import print  # noqa: F401
    except ImportError:
        pass  # Fall back to standard print if rich is not available

    main()
