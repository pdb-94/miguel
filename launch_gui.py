"""
Simple launcher for MiGUEL Modern GUI
Run this file to start the graphical user interface
"""

import sys
import os

# Ensure the miguel directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the GUI
from modern_gui import main

if __name__ == "__main__":
    print("Starting MiGUEL Modern GUI...")
    print("=" * 50)
    print("Micro Grid User Energy Tool Library")
    print("=" * 50)
    main()
