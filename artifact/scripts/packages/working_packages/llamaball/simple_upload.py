#!/usr/bin/env python3
"""
Simple PyPI upload script for llamaball
File Purpose: Upload package to PyPI without twine dependency issues
Primary Functions: Upload wheel and source distribution to PyPI
Inputs: Distribution files and API token
Outputs: Upload status and package URL
"""

import os
import sys
import requests
import hashlib
from pathlib import Path

def get_file_hash(filepath):
    """Calculate SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_to_pypi(token, dist_files, repository_url="https://upload.pypi.org/legacy/"):
    """Upload distribution files to PyPI"""
    
    print("🦙 Llamaball PyPI Upload")
    print("=" * 25)
    
    for dist_file in dist_files:
        if not os.path.exists(dist_file):
            print(f"❌ Error: File {dist_file} not found")
            return False
            
        print(f"📦 Uploading {os.path.basename(dist_file)}...")
        
        # Prepare file data
        with open(dist_file, 'rb') as f:
            file_content = f.read()
        
        # Prepare form data
        files = {
            'content': (os.path.basename(dist_file), file_content, 'application/octet-stream')
        }
        
        data = {
            ':action': 'file_upload',
            'protocol_version': '1',
            'name': 'llamaball',
            'version': '1.1.1',
            'filetype': 'bdist_wheel' if dist_file.endswith('.whl') else 'sdist',
            'pyversion': 'py3' if dist_file.endswith('.whl') else 'source',
            'md5_digest': '',
            'sha256_digest': get_file_hash(dist_file),
        }
        
        # Upload
        response = requests.post(
            repository_url,
            data=data,
            files=files,
            auth=('__token__', token)
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully uploaded {os.path.basename(dist_file)}")
        else:
            print(f"❌ Failed to upload {os.path.basename(dist_file)}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    return True

def main():
    # Get version from __init__.py
    version = "1.1.1"  # Current version
    
    # Check for distribution files
    dist_files = [
        f"dist/llamaball-{version}-py3-none-any.whl",
        f"dist/llamaball-{version}.tar.gz"
    ]
    
    missing_files = [f for f in dist_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Error: Missing distribution files:")
        for f in missing_files:
            print(f"   {f}")
        print("\nRun 'python -m build' first.")
        return 1
    
    print("📦 Found distribution files:")
    for f in dist_files:
        size = os.path.getsize(f) / 1024  # KB
        print(f"   {f} ({size:.1f} KB)")
    
    # Get API token
    print("\n🔑 PyPI Authentication")
    print("=" * 25)
    print("Please enter your PyPI API token (starts with 'pypi-'):")
    print("You can get this from: https://pypi.org/manage/account/token/")
    
    token = input("\nAPI Token: ").strip()
    
    if not token.startswith('pypi-'):
        print("❌ Error: Invalid token format. Token should start with 'pypi-'")
        return 1
    
    print("✅ Token format looks correct")
    
    # Upload to PyPI
    print("\n🚀 Uploading to PyPI...")
    if upload_to_pypi(token, dist_files):
        print("\n🎉 Upload complete!")
        print("🔗 View your package at: https://pypi.org/project/llamaball/")
        print("📦 Install with: pip install llamaball")
        return 0
    else:
        print("\n❌ Upload failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 