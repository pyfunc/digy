"""
DIGY - Dynamic Interactive Git deploY

A Python package for deploying applications from Git repositories 
in isolated environments with interactive menu support.
"""

__version__ = "0.1.0"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"

from .loader import digy, digy_command
from .cli import main
from .interactive import InteractiveMenu
from .deployer import Deployer

__all__ = ["digy", "digy_command", "main", "InteractiveMenu", "Deployer"]