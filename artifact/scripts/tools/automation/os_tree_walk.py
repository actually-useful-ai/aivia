import os
import re

# Directory to scan
start_path = './'

# File to store the directory tree and dependencies
output_file = "directory_tree_with_dependencies.txt"

# Define a list of file extensions to check for dependencies
# Adjust this list based on the file types in your directory
target_extensions = ['.txt', '.md', '.py', '.html', '.js']

def find_dependencies(file_path, file_names):
    """
    Search for other file names within the content of file_path.
    This function returns a list of dependencies found in the file.
    """
    dependencies = []
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            for name in file_names:
                if re.search(rf'\b{name}\b', content):
                    dependencies.append(name)
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
    return dependencies

def generate_tree_and_dependencies(start_path):
    # Gather all file names to check for references
    file_names = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if any(file.endswith(ext) for ext in target_extensions):
                file_names.append(file)

    # Traverse and record the directory structure and dependencies
    with open(output_file, 'w') as out:
        for root, dirs, files in os.walk(start_path):
            # Print current directory level
            level = root.replace(start_path, '').count(os.sep)
            indent = ' ' * 4 * level
            out.write(f"{indent}{os.path.basename(root)}/\n")

            # Process each file in the current directory
            for file in files:
                file_path = os.path.join(root, file)
                file_indent = ' ' * 4 * (level + 1)
                out.write(f"{file_indent}{file}\n")
                
                # Find dependencies within the file
                if any(file.endswith(ext) for ext in target_extensions):
                    dependencies = find_dependencies(file_path, file_names)
                    if dependencies:
                        out.write(f"{file_indent}    Dependencies: {', '.join(dependencies)}\n")

if __name__ == "__main__":
    generate_tree_and_dependencies(start_path)
    print(f"Directory tree with dependencies saved to {output_file}")
