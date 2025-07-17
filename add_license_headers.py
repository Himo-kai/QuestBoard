#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Script to add MPL 2.0 license headers to Python files.
"""
import os
import sys

LICENSE_HEADER = """# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""

def should_skip_file(filepath):
    """Check if file should be skipped."""
    skip_dirs = [
        'venv',
        '__pycache__',
        '.git',
        'migrations',
        'tests',
        'node_modules',
        'build',
        'dist'
    ]
    
    for skip_dir in skip_dirs:
        if f'/{skip_dir}/' in filepath or filepath.startswith(f'{skip_dir}/'):
            return True
    
    # Skip files that already have the license header
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(200)  # Only check first 200 chars for performance
            if 'Mozilla Public' in content and 'License, v. 2.0' in content:
                return True
    except (UnicodeDecodeError, PermissionError):
        return True
    
    return False

def add_license_to_file(filepath):
    """Add license header to a single file."""
    try:
        with open(filepath, 'r+', encoding='utf-8') as f:
            content = f.read()
            
            # Skip if file starts with shebang
            if content.startswith('#!'):
                lines = content.split('\n', 1)
                new_content = f"{lines[0]}\n\n{LICENSE_HEADER}{lines[1] if len(lines) > 1 else ''}"
            else:
                new_content = f"{LICENSE_HEADER}{content}"
            
            # Write back to file
            f.seek(0)
            f.write(new_content)
            f.truncate()
            
        print(f"Added license to: {filepath}")
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return False

def main():
    """Main function to process all Python files."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    processed = 0
    errors = 0
    
    print("Adding MPL 2.0 license headers to Python files...")
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if not should_skip_file(filepath):
                    if add_license_to_file(filepath):
                        processed += 1
                    else:
                        errors += 1
    
    print(f"\nDone! Processed {processed} files with {errors} errors.")
    if errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
