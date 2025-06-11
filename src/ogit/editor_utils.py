import tempfile
import os
import subprocess

def prompt_user_to_edit(message: str) -> str:
    """
    Opens the user's default editor to allow editing the commit message.
    Falls back to nano if $EDITOR is not set.
    """
    editor = os.environ.get("EDITOR", "nano")
    with tempfile.NamedTemporaryFile(suffix=".tmp", mode="w+", delete=False) as tf:
        tf.write(message)
        tf.flush()
        temp_path = tf.name

    subprocess.call([editor, temp_path])

    with open(temp_path, "r") as f:
        edited = f.read().strip()

    os.unlink(temp_path)
    return edited or message
