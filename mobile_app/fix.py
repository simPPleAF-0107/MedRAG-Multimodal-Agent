import os
import re

files_to_fix_value = [
    r"lib\screens\forms\activity_form_screen.dart",
    r"lib\screens\forms\cycle_form_screen.dart",
    r"lib\screens\forms\mood_form_screen.dart",
    r"lib\screens\register_screen.dart"
]

files_to_fix_value = [f.replace('\\', os.sep) for f in files_to_fix_value]

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    # Fix withOpacity
    new_content = re.sub(r'\.withOpacity\(([^)]+)\)', r'.withValues(alpha: \1)', content)
    
    # Fix value in specific files
    if any(filepath.endswith(fp) for fp in files_to_fix_value):
        # We replace "value: " with "initialValue: " ONLY for DropdownButtonFormField or inside those specific lines.
        # Let's just do a simple replacement of "value: " with "initialValue: " if it corresponds to those fields.
        lines = new_content.split('\n')
        for i in range(len(lines)):
            if 'DropdownButtonFormField' in lines[i-1] or 'DropdownButtonFormField' in lines[i-2] or 'DropdownButtonFormField' in lines[i-3] or 'DropdownButtonFormField' in lines[i]:
                lines[i] = re.sub(r'\bvalue: ', 'initialValue: ', lines[i])
        new_content = '\n'.join(lines)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

for root, _, files in os.walk('lib'):
    for file in files:
        if file.endswith('.dart'):
            process_file(os.path.join(root, file))
