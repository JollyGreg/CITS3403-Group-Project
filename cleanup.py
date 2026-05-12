import os

files_to_remove = [
    '__init__.py',           # No longer needed, Flask app is in app.py
    '__init__.py.bak',       # Backup file
    'install.bat',           # Redundant with setup.bat
    'install_deps.py',       # Redundant with setup.bat
]

for file in files_to_remove:
    filepath = os.path.join(os.path.dirname(__file__), file)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"✓ Removed: {file}")
    else:
        print(f"✗ Not found: {file}")

print("\nCleanup complete!")
print("\nRemaining essential files:")
print("  - app.py          (Main Flask application)")
print("  - models.py       (Database models)")
print("  - db.py           (Database utilities)")
print("  - requirements.txt (Python dependencies)")
print("  - setup.bat       (Setup script for Windows)")
print("  - setup.sh        (Setup script for Linux/Mac)")
print("  - .env.example    (Environment configuration template)")
