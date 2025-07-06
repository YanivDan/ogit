import tempfile
import os
import subprocess
import logging
from typing import Optional

from .constants import TEMP_FILE_SUFFIX
from .config import get_config

logger = logging.getLogger(__name__)


def prompt_user_to_edit(message: str) -> str:
    """
    Opens the user's default editor to allow editing the commit message.
    
    Args:
        message: Initial commit message
        
    Returns:
        Edited commit message, or original if editing failed
    """
    config = get_config()
    editor = config.editor
    
    logger.debug(f"Opening editor: {editor}")
    
    try:
        with tempfile.NamedTemporaryFile(
            suffix=TEMP_FILE_SUFFIX, 
            mode="w+", 
            delete=False,
            encoding="utf-8"
        ) as tf:
            tf.write(message)
            tf.flush()
            temp_path = tf.name

        # Add instructions as comments
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(message + "\n\n")
            f.write("# Please edit the commit message above.\n")
            f.write("# Lines starting with '#' will be ignored.\n")
            f.write("# Save and exit to use the message.\n")
            
            if config.conventional_commits:
                f.write("#\n")
                f.write("# Conventional commit format: <type>(<scope>): <description>\n")
                f.write("# Types: feat, fix, docs, style, refactor, test, chore\n")

        # Open editor
        result = subprocess.run([editor, temp_path], check=True)
        
        if result.returncode != 0:
            logger.warning(f"Editor returned non-zero exit code: {result.returncode}")

        # Read edited content
        with open(temp_path, "r", encoding="utf-8") as f:
            edited_content = f.read()

        # Clean up temp file
        os.unlink(temp_path)
        
        # Process edited content
        edited = _process_edited_content(edited_content)
        
        if edited != message:
            logger.debug("Commit message was edited by user")
        
        return edited or message
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Editor command failed: {e}")
        return message
    except FileNotFoundError:
        logger.error(f"Editor '{editor}' not found")
        return message
    except Exception as e:
        logger.error(f"Unexpected error in editor: {e}")
        return message


def _process_edited_content(content: str) -> str:
    """
    Process the edited content from the editor.
    
    Args:
        content: Raw content from editor
        
    Returns:
        Processed commit message
    """
    lines = content.split('\n')
    
    # Remove comment lines and empty lines from the end
    message_lines = []
    for line in lines:
        if line.strip().startswith('#'):
            continue
        message_lines.append(line)
    
    # Join lines and strip whitespace
    message = '\n'.join(message_lines).strip()
    
    return message


def validate_commit_message(message: str, max_length: Optional[int] = None) -> tuple[bool, str]:
    """
    Validate commit message format.
    
    Args:
        message: Commit message to validate
        max_length: Maximum length for first line
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Commit message cannot be empty"
    
    lines = message.split('\n')
    first_line = lines[0].strip()
    
    if not first_line:
        return False, "First line of commit message cannot be empty"
    
    # Check length
    if max_length and len(first_line) > max_length:
        return False, f"First line too long ({len(first_line)} > {max_length} characters)"
    
    # Check for conventional commit format if enabled
    config = get_config()
    if config.conventional_commits:
        if not _is_conventional_commit(first_line):
            return False, "Message should follow conventional commit format: <type>(<scope>): <description>"
    
    return True, ""


def _is_conventional_commit(line: str) -> bool:
    """
    Check if line follows conventional commit format.
    
    Args:
        line: First line of commit message
        
    Returns:
        True if follows conventional commit format
    """
    from .constants import CONVENTIONAL_COMMIT_TYPES
    
    # Simple check for type: or type(scope):
    if ':' not in line:
        return False
    
    prefix = line.split(':', 1)[0].strip()
    
    # Check for type(scope) format
    if '(' in prefix and ')' in prefix:
        type_part = prefix.split('(')[0].strip()
    else:
        type_part = prefix
    
    return type_part.lower() in CONVENTIONAL_COMMIT_TYPES
