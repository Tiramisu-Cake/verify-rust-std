#!/usr/bin/env python3
"""Same ghost byte rules; isolated import without dormant C2 proof runner."""
import re

GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/(?:\r?\n)?", re.S)

GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")

def strip_ghost(source: bytes) -> bytes:
    """Match the project capture's byte-preserving ghost stripper."""
    return GHOST_LINE.sub(b"", GHOST_BLOCK.sub(b"", source))
