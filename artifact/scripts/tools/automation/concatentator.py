# """
# PDF Merger Script with Error Handling
# -----------------------------------

# This script combines multiple PDF files in a folder into a single PDF file,
# with enhanced error handling for common PDF issues like missing EOF markers.

# Requirements:
#     - Python 3.x
#     - PyPDF2 library (install using: pip install PyPDF2)

# Usage:
#     From command line:
#         python script.py /path/to/folder -o output.pdf
    
#     Examples:
#         python script.py C:/Documents/PDFs
#         python script.py ./my_pdfs -o combined.pdf
#         python script.py "/Users/name/Desktop/PDF Files" -o merged_result.pdf

# Arguments:
#     folder  : Required. Path to the folder containing PDF files
#     --output, -o : Optional. Name for the output file (default: merged_output.pdf)

# Notes:
#     - The script will process all files with .pdf extension in the specified folder
#     - Files are merged in alphabetical order
#     - The merged file will be saved in the same folder as the input files
#     - Progress is shown as each file is processed
#     - Handles common PDF errors including missing EOF markers
# """

import os
import argparse
from PyPDF2 import PdfMerger, PdfReader
import logging

def safe_read_pdf(file_path):
    """Safely read a PDF file with error handling."""
    try:
        # Open in binary read mode with strict=False to handle EOF errors
        with open(file_path, 'rb') as file:
            reader = PdfReader(file, strict=False)
            return reader
    except Exception as e:
        logging.error(f"Error reading {file_path}: {str(e)}")
        return None

def merge_pdfs(input_folder, output_filename):
    # Create a PdfMerger object
    merger = PdfMerger(strict=False)
    
    # Track successful and failed files
    successful_files = []
    failed_files = []
    
    try:
        # Get all PDF files from the input folder
        pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
        pdf_files.sort()
        
        if not pdf_files:
            print("No PDF files found in the specified folder.")
            return
        
        # Process each PDF file
        for pdf in pdf_files:
            file_path = os.path.join(input_folder, pdf)
            print(f"Processing: {pdf}")
            
            try:
                # Attempt to read the PDF
                reader = safe_read_pdf(file_path)
                if reader is not None:
                    merger.append(reader)
                    successful_files.append(pdf)
                    print(f"Successfully added: {pdf}")
                else:
                    failed_files.append(pdf)
                    print(f"Failed to add: {pdf}")
            
            except Exception as e:
                failed_files.append(pdf)
                print(f"Error processing {pdf}: {str(e)}")
                continue
        
        # Only write output if we have successful files
        if successful_files:
            output_path = os.path.join(input_folder, output_filename)
            merger.write(output_path)
            print(f"\nMerge completed!")
            print(f"Successfully merged {len(successful_files)} files into {output_filename}")
            print(f"Output location: {output_path}")
        
        # Report any failures
        if failed_files:
            print("\nThe following files could not be processed:")
            for failed_file in failed_files:
                print(f"- {failed_file}")
    
    except Exception as e:
        print(f"An error occurred during merging: {str(e)}")
    
    finally:
        merger.close()

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Merge PDF files in a folder')
    parser.add_argument('folder', help='Folder containing PDF files')
    parser.add_argument('--output', '-o', default='merged_output.pdf',
                      help='Output filename (default: merged_output.pdf)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.ERROR)
    
    # Run the merger
    merge_pdfs(args.folder, args.output)