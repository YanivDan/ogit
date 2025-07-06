"""ogit - AI-powered Git commit message generator with Ollama.

A terminal-native Git assistant that generates intelligent commit messages
using local AI models through Ollama. No cloud, no API keys - just smarter
Git workflows.
"""

__version__ = "0.2.0"
__author__ = "Yaniv Dan"
__email__ = "yanivdezan@gmail.com"

from .main import main, cli_entrypoint
from .config import get_config
from .constants import *

__all__ = [
    "main",
    "cli_entrypoint", 
    "get_config",
    "__version__"
]