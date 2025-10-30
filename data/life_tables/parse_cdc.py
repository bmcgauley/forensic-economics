#!/usr/bin/env python3
"""
CDC Life Tables PDF Parser - Simple Wrapper

This is a convenience wrapper that calls the robust parser.

Usage:
    python parse_cdc.py

    Or simply:
    python parse_cdc.py
"""

from pathlib import Path
import sys

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the robust parser
try:
    from parse_cdc_pdf_robust import main
    sys.exit(main())
except ImportError as e:
    print(f"ERROR: Could not import robust parser: {e}")
    sys.exit(1)
