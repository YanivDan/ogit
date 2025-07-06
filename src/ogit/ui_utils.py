"""UI utilities for ogit."""

import sys
import time
import threading
from typing import Optional


class ProgressSpinner:
    """A simple progress spinner for terminal output."""
    
    def __init__(self, message: str = "Processing", spinner_chars: str = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        """
        Initialize progress spinner.
        
        Args:
            message: Message to display with spinner
            spinner_chars: Characters to use for spinner animation
        """
        self.message = message
        self.spinner_chars = spinner_chars
        self.active = False
        self.thread: Optional[threading.Thread] = None
        self.start_time = 0
    
    def start(self) -> None:
        """Start the spinner."""
        if self.active:
            return
        
        self.active = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message: Optional[str] = None) -> None:
        """Stop the spinner."""
        if not self.active:
            return
        
        self.active = False
        if self.thread:
            self.thread.join()
        
        # Clear the spinner line
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        
        if final_message:
            elapsed = time.time() - self.start_time
            print(f"{final_message} (took {elapsed:.1f}s)")
        
        sys.stdout.flush()
    
    def _spin(self) -> None:
        """Spinner animation loop."""
        char_index = 0
        while self.active:
            char = self.spinner_chars[char_index % len(self.spinner_chars)]
            sys.stdout.write(f'\r{char} {self.message}...')
            sys.stdout.flush()
            char_index += 1
            time.sleep(0.1)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self.stop("✓ Done")
        else:
            self.stop("✗ Failed")


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Question to ask
        default: Default value if user just presses Enter
        
    Returns:
        True if user confirmed, False otherwise
    """
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        response = input(f"{message} {suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ('y', 'yes')
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return False


def display_diff_summary(diff: str) -> None:
    """
    Display a summary of the git diff.
    
    Args:
        diff: Git diff output
    """
    if not diff:
        print("No changes to display.")
        return
    
    lines = diff.split('\n')
    added_lines = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
    removed_lines = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
    
    print(f"Changes: +{added_lines} -{removed_lines} lines")
    
    # Show files changed
    files_changed = set()
    for line in lines:
        if line.startswith('diff --git'):
            # Extract filename from "diff --git a/file b/file"
            parts = line.split()
            if len(parts) >= 4:
                file_path = parts[3][2:]  # Remove "b/" prefix
                files_changed.add(file_path)
    
    if files_changed:
        print(f"Files changed: {', '.join(sorted(files_changed))}")


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"ERROR: {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print warning message to stderr."""
    print(f"WARNING: {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print info message."""
    print(f"INFO: {message}")


def print_success(message: str) -> None:
    """Print success message."""
    print(f"✓ {message}")