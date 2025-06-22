"""
File utilities for DIGY
Handles file selection, attachment, and management
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def select_files_interactive(start_path: str = None) -> List[str]:
    """
    Interactive file selection using a simple text-based interface
    
    Args:
        start_path: Starting directory for file selection
        
    Returns:
        List of selected file paths
    """
    if start_path is None:
        start_path = os.getcwd()
    
    selected_files = []
    current_dir = Path(start_path).resolve()
    
    while True:
        # List directory contents
        items = []
        for item in current_dir.iterdir():
            if item.is_dir():
                items.append((item.name + '/', 'dir'))
            else:
                items.append((item.name, 'file'))
        
        # Sort directories first, then files
        items.sort(key=lambda x: (x[1] != 'dir', x[0].lower()))
        
        # Display current directory and contents
        console.print(f"\n[bold blue]Current directory: {current_dir}[/]")
        for i, (name, typ) in enumerate(items, 1):
            prefix = "📁 " if typ == 'dir' else "📄 "
            console.print(f"  {i:2d}. {prefix}{name}")
        
        # Navigation options
        console.print("\n[bold]Options:[/]")
        console.print("  [bold]1-N[/] Select file/directory")
        console.print("  [bold]u[/]p - Go up one directory")
        console.print("  [bold]h[/]ome - Go to home directory")
        console.print("  [bold]d[/]one - Finish selection")
        console.print("  [bold]q[/]uit - Cancel")
        
        choice = Prompt.ask("\nSelect an option", default="")
        
        if choice.lower() == 'q':
            return []
        elif choice.lower() == 'd':
            break
        elif choice.lower() == 'u':
            current_dir = current_dir.parent
        elif choice.lower() == 'h':
            current_dir = Path.home()
        elif choice.isdigit() and 1 <= int(choice) <= len(items):
            selected_item = items[int(choice) - 1]
            item_path = current_dir / selected_item[0].rstrip('/')
            
            if selected_item[1] == 'dir':
                current_dir = item_path
            else:
                selected_files.append(str(item_path))
                console.print(f"\n✅ Added: {item_path}")
                
                if not Confirm.ask("Select another file?", default=True):
                    break
    
    return selected_files

def attach_files(files: List[str], target_dir: str, overwrite: bool = False) -> Dict[str, str]:
    """
    Attach files to the target directory
    
    Args:
        files: List of source file paths
        target_dir: Target directory to copy files to
        overwrite: Whether to overwrite existing files
        
    Returns:
        Dict mapping source paths to destination paths
    """
    attached = {}
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    for src in files:
        src_path = Path(src)
        dst_path = target_path / src_path.name
        
        if dst_path.exists() and not overwrite:
            # Handle filename conflicts
            counter = 1
            while True:
                new_name = f"{src_path.stem}_{counter}{src_path.suffix}"
                new_dst = target_path / new_name
                if not new_dst.exists():
                    dst_path = new_dst
                    break
                counter += 1
        
        try:
            shutil.copy2(src_path, dst_path)
            attached[str(src_path)] = str(dst_path)
            console.print(f"📎 Attached: {src_path} -> {dst_path}")
        except Exception as e:
            console.print(f"[red]Error attaching {src_path}: {e}[/red]")
    
    return attached

def preview_file(file_path: str, max_lines: int = 20) -> None:
    """
    Preview file contents in the console
    
    Args:
        file_path: Path to the file to preview
        max_lines: Maximum number of lines to show
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [next(f) for _ in range(max_lines)]
            
        content = ''.join(lines)
        lexer = "python" if file_path.endswith('.py') else "text"
        
        console.print(Panel(
            Syntax(content, lexer, line_numbers=True, word_wrap=True),
            title=f"Preview: {file_path}",
            border_style="blue"
        ))
    except StopIteration:
        console.print(f"[yellow]File is empty: {file_path}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")

if __name__ == "__main__":
    # Simple test of the file selector
    selected = select_files_interactive()
    if selected:
        print("\nSelected files:")
        for f in selected:
            print(f"- {f}")
    else:
        print("No files selected")
