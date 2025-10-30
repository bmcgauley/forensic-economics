#!/usr/bin/env python
"""
Forensic Economics - Development Server Launcher

Quick launcher for the development server.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api.app import main

if __name__ == '__main__':
    main()
