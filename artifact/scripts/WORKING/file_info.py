#!/usr/bin/env python3
"""
File Information CLI
Simple tool to display detailed information about files and directories.
"""

import sys
import os
import argparse
import hashlib
from pathlib import Path
from datetime import datetime


def format_size(bytes_size):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_timestamp(timestamp):
    """Format timestamp to readable date"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def calculate_hash(filepath, algorithm='sha256'):
    """Calculate file hash"""
    try:
        hash_func = getattr(hashlib, algorithm)()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"


def get_file_type(filepath):
    """Get file type information"""
    path = Path(filepath)
    suffix = path.suffix.lower()
    
    # Common file type categories
    categories = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp', '.heic', '.heif'],
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'document': ['.pdf', '.doc', '.docx', '.odt', '.txt', '.rtf'],
        'spreadsheet': ['.xls', '.xlsx', '.ods', '.csv'],
        'presentation': ['.ppt', '.pptx', '.odp'],
        'archive': ['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'],
        'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.html', '.css', '.php', '.rb', '.go', '.rs'],
        'data': ['.json', '.xml', '.yaml', '.yml', '.toml', '.ini'],
    }
    
    for category, extensions in categories.items():
        if suffix in extensions:
            return f"{category.capitalize()} file"
    
    return "Unknown type" if suffix else "No extension"


def get_file_info(filepath, show_hash=False, hash_algorithm='sha256'):
    """Get detailed file information"""
    try:
        path = Path(filepath)
        
        if not path.exists():
            return None, f"File not found: {filepath}"
        
        stat = path.stat()
        
        info = {
            'name': path.name,
            'path': str(path.absolute()),
            'type': get_file_type(filepath),
            'size': stat.st_size,
            'size_formatted': format_size(stat.st_size),
            'created': format_timestamp(stat.st_ctime),
            'modified': format_timestamp(stat.st_mtime),
            'accessed': format_timestamp(stat.st_atime),
            'permissions': oct(stat.st_mode)[-3:],
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'is_symlink': path.is_symlink(),
            'extension': path.suffix,
        }
        
        if show_hash and path.is_file():
            info['hash'] = calculate_hash(filepath, hash_algorithm)
            info['hash_algorithm'] = hash_algorithm
        
        return info, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"


def get_directory_info(dirpath):
    """Get directory statistics"""
    try:
        path = Path(dirpath)
        
        if not path.exists():
            return None, f"Directory not found: {dirpath}"
        
        if not path.is_dir():
            return None, f"Not a directory: {dirpath}"
        
        total_size = 0
        file_count = 0
        dir_count = 0
        file_types = {}
        
        for item in path.rglob('*'):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
                ext = item.suffix.lower() or 'no_extension'
                file_types[ext] = file_types.get(ext, 0) + 1
            elif item.is_dir():
                dir_count += 1
        
        info = {
            'name': path.name,
            'path': str(path.absolute()),
            'total_size': total_size,
            'total_size_formatted': format_size(total_size),
            'file_count': file_count,
            'dir_count': dir_count,
            'file_types': file_types,
        }
        
        return info, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"


def print_file_info(info):
    """Print file information in a formatted way"""
    print("\n" + "="*70)
    print("📄 File Information")
    print("="*70)
    print(f"Name:         {info['name']}")
    print(f"Path:         {info['path']}")
    print(f"Type:         {info['type']}")
    print(f"Extension:    {info['extension'] or 'None'}")
    print(f"Size:         {info['size_formatted']} ({info['size']:,} bytes)")
    print(f"Permissions:  {info['permissions']}")
    print(f"Created:      {info['created']}")
    print(f"Modified:     {info['modified']}")
    print(f"Accessed:     {info['accessed']}")
    
    if info.get('hash'):
        print(f"{info['hash_algorithm'].upper()}:      {info['hash']}")
    
    print("="*70)


def print_directory_info(info):
    """Print directory information in a formatted way"""
    print("\n" + "="*70)
    print("📁 Directory Information")
    print("="*70)
    print(f"Name:         {info['name']}")
    print(f"Path:         {info['path']}")
    print(f"Total Size:   {info['total_size_formatted']} ({info['total_size']:,} bytes)")
    print(f"Files:        {info['file_count']:,}")
    print(f"Directories:  {info['dir_count']:,}")
    
    if info['file_types']:
        print(f"\nFile Types:")
        sorted_types = sorted(info['file_types'].items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:10]:  # Show top 10
            print(f"  {ext:20s} {count:>6,} files")
        if len(info['file_types']) > 10:
            print(f"  ... and {len(info['file_types']) - 10} more types")
    
    print("="*70)


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Display detailed file and directory information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show file information
  %(prog)s document.pdf
  
  # Show file with hash
  %(prog)s image.jpg --hash
  
  # Directory statistics
  %(prog)s /path/to/directory --dir
  
  # Multiple files
  %(prog)s file1.txt file2.pdf file3.jpg
        """
    )
    
    parser.add_argument("paths", nargs="+", help="File or directory path(s)")
    parser.add_argument("--hash", action="store_true", help="Calculate file hash")
    parser.add_argument("--hash-algorithm", default="sha256", 
                        choices=["md5", "sha1", "sha256", "sha512"],
                        help="Hash algorithm (default: sha256)")
    parser.add_argument("-d", "--dir", action="store_true", help="Show directory statistics")
    
    args = parser.parse_args()
    
    for filepath in args.paths:
        if args.dir:
            info, error = get_directory_info(filepath)
            if error:
                print(f"❌ {error}")
            else:
                print_directory_info(info)
        else:
            info, error = get_file_info(filepath, args.hash, args.hash_algorithm)
            if error:
                print(f"❌ {error}")
            else:
                print_file_info(info)
        
        if len(args.paths) > 1:
            print()  # Add spacing between multiple files


if __name__ == "__main__":
    main()
