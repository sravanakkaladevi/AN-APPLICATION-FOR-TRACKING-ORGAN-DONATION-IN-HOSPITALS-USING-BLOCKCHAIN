#!/usr/bin/env python
import os
import sys
import subprocess

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, 'backend')
    
    # Path to the virtual environment python executable
    venv_python = os.path.join(root_dir, 'venv', 'Scripts', 'python.exe')
    
    # Fallback to the current python executable if the venv one doesn't exist
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    
    manage_py_path = os.path.join(backend_dir, 'manage.py')
    
    # Build the command
    cmd = [python_exe, manage_py_path] + sys.argv[1:]
    
    # Run the command with the backend directory as the current working directory
    try:
        sys.exit(subprocess.call(cmd, cwd=backend_dir))
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()
