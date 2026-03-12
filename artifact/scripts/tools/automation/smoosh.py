import os
import datetime
import json
import logging
import shutil #yikes

# Set up logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smoosh.log'),
        logging.StreamHandler()
    ]
)

def crawl_directory(base_path):
    file_types = ('.py', '.sh', '.html', '.css', '.js')
    found_files = {ext: [] for ext in file_types}

    logging.info('Starting directory crawl...')
    
    try:
        for dirpath, dirnames, filenames in os.walk(base_path):
            # Skip hidden directories and Python packages
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and 
                          not os.path.exists(os.path.join(dirpath, d, '__init__.py'))]
            
            for filename in filenames:
                if filename.endswith(file_types):
                    ext = os.path.splitext(filename)[1]  # More reliable extension extraction
                    full_path = os.path.join(dirpath, filename)
                    found_files[ext].append(full_path)
                    logging.debug(f'Found file: {full_path}')

        for ext, files in found_files.items():
            logging.info(f'Found {len(files)} {ext} files')
            
        return found_files
        
    except Exception as e:
        logging.error(f'Error during directory crawl: {str(e)}')
        raise

def create_timestamped_directory(base_path, found_files):
    # Create a human-readable timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_at_%H-%M-%S')
    smoosh_dir = os.path.join(base_path, 'smoosh', timestamp)
    
    try:
        os.makedirs(smoosh_dir, exist_ok=True)
        logging.info(f'Created directory: {smoosh_dir}')

        for ext, files in found_files.items():
            if not files:
                continue
                
            # Create the file listing
            listing_path = os.path.join(smoosh_dir, f'file_list{ext}.txt')
            with open(listing_path, 'w') as f:
                for file in files:
                    f.write(file + '\n')
            logging.info(f'Created file listing: {listing_path}')

            # Create the concatenated file
            concat_path = os.path.join(smoosh_dir, f'all_content{ext}')
            with open(concat_path, 'w', encoding='utf-8') as outfile:
                for file_path in files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(f'\n\n{"="*80}\n')
                            outfile.write(f'File: {file_path}\n')
                            outfile.write(f'{"="*80}\n\n')
                            outfile.write(infile.read())
                            logging.debug(f'Concatenated: {file_path}')
                    except Exception as e:
                        error_msg = f'Error reading {file_path}: {str(e)}'
                        logging.error(error_msg)
                        outfile.write(f'\n\n{error_msg}\n\n')
            
            logging.info(f'Created concatenated file: {concat_path}')

        return smoosh_dir
        
    except Exception as e:
        logging.error(f'Error creating smoosh directory: {str(e)}')
        raise

def create_structure_diagram(base_path, smoosh_dir):
    logging.info('Creating directory structure diagram...')
    structure = {}

    try:
        for root, dirs, files in os.walk(base_path):
            # Skip smoosh directory and hidden folders
            relative_root = os.path.relpath(root, base_path)
            if 'smoosh' in relative_root.split(os.sep) or any(part.startswith('.') for part in relative_root.split(os.sep)):
                continue

            # Build the directory structure
            parts = relative_root.split(os.sep)
            current_level = structure

            # Walk down the directory tree, creating entries for each directory level
            for part in parts:
                if part == '.':
                    continue
                current_level = current_level.setdefault(part, {})

            # Add files to the current directory
            for f in files:
                if not f.startswith('.') and f != '__init__.py':
                    current_level[f] = None

        # Save the structure to a JSON file
        structure_path = os.path.join(smoosh_dir, 'directory_structure.json')
        with open(structure_path, 'w') as f:
            json.dump(structure, f, indent=2)
            
        logging.info(f'Created structure diagram: {structure_path}')
        
    except Exception as e:
        logging.error(f'Error creating structure diagram: {str(e)}')
        raise

def main():
    try:
        base_directory = '.'
        logging.info('Starting smoosh script...')
        
        found_files = crawl_directory(base_directory)
        smoosh_dir = create_timestamped_directory(base_directory, found_files)
        create_structure_diagram(base_directory, smoosh_dir)
        
        logging.info('Smoosh completed successfully!')
        logging.info(f'Results can be found in: {smoosh_dir}')
        
    except Exception as e:
        logging.error(f'Fatal error: {str(e)}')
        raise

if __name__ == "__main__":
    main()