"""
AI Conversation Exporter
Export conversations from multiple AI platforms to Markdown
"""

__version__ = "0.1.0"
__author__ = "toke648"

from .core import convert, main

__all__ = ["convert", "main"]