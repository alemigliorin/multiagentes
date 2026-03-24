import os
import sys

# Add the current directory to path
sys.path.append(os.getcwd())

from main import app

for route in app.routes:
    # Use getattr to safely access methods and path
    path = getattr(route, "path", None)
    name = getattr(route, "name", None)
    methods = getattr(route, "methods", None)
    print(f"Path: {path} | Name: {name} | Methods: {methods}")
