import sys
import os

# Set environment to avoid potential execution hangs/loops
os.environ["SKIP_PDF_LOAD"] = "1"

sys.path.append(os.getcwd())
from main import app

print("--- START ROUTES ---")
for route in app.routes:
    methods = getattr(route, "methods", "N/A")
    print(f"{route.path} {methods}")
print("--- END ROUTES ---")
