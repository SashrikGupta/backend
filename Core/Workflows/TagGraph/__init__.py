"""
TagGraph package initialization.
Exposes the main auto-tagging graph builder.
"""

from .Graph.builder import get_auto_tagging_graph

__all__ = ["get_auto_tagging_graph"]
