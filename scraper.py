#!/usr/bin/env python3
"""
Main UVic LIM Job Scraper
Entry point for the organized project structure
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

print("UVic LIM Job Scraper")
print("=" * 60)
print("\nThis is the main entry point.")
print("Run './run.sh' for the interactive menu.")
print("\nOr use directly:")
print("  python scraper.py --help")
print("  python cookie_scraper.py --help")
