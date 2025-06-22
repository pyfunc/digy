#!/usr/bin/env python3
"""
A simple hello world example for DIGY.
Run this with: digy run . hello_world.py
"""

def main():
    print("Hello, DIGY!")
    print("This is a basic example running in the local environment.")
    print("You can pass arguments to this script after the filename.")
    
    import sys
    if len(sys.argv) > 1:
        print("\nArguments received:", sys.argv[1:])

if __name__ == "__main__":
    main()
