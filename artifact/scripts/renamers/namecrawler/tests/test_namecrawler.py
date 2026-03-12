"""Tests for namecrawler"""

import pytest
from pathlib import Path
import tempfile
import hashlib
from namecrawler.cli import sha256sum, rename_file, main


def test_sha256sum(tmp_path):
    """Test SHA256 hashing of file contents"""
    # Create test file with known content
    test_file = tmp_path / "test.txt"
    test_content = b"Hello, World!"
    test_file.write_bytes(test_content)
    
    # Expected hash
    expected_hash = hashlib.sha256(test_content).hexdigest()
    
    # Test function
    result = sha256sum(test_file)
    assert result == expected_hash


def test_rename_file(tmp_path):
    """Test renaming a file with its hash"""
    # Create test file
    test_file = tmp_path / "original.txt"
    test_content = b"Test content"
    test_file.write_bytes(test_content)
    
    # Rename it
    new_path = rename_file(test_file)
    
    # Verify new name is hash + extension
    expected_hash = hashlib.sha256(test_content).hexdigest()
    assert new_path.name == f"{expected_hash}.txt"
    assert new_path.exists()
    assert not test_file.exists()


def test_rename_preserves_extension(tmp_path):
    """Test that file extension is preserved"""
    extensions = [".pdf", ".jpg", ".docx", ".txt"]
    
    for ext in extensions:
        test_file = tmp_path / f"file{ext}"
        test_file.write_bytes(b"content")
        
        new_path = rename_file(test_file)
        assert new_path.suffix == ext


def test_same_content_same_hash(tmp_path):
    """Test that identical content produces identical hashes"""
    content = b"Identical content"
    
    # Create two files with same content
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_bytes(content)
    file2.write_bytes(content)
    
    # Get hashes
    hash1 = sha256sum(file1)
    hash2 = sha256sum(file2)
    
    assert hash1 == hash2


def test_different_content_different_hash(tmp_path):
    """Test that different content produces different hashes"""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_bytes(b"Content A")
    file2.write_bytes(b"Content B")
    
    hash1 = sha256sum(file1)
    hash2 = sha256sum(file2)
    
    assert hash1 != hash2


def test_cli_main(tmp_path, capsys):
    """Test CLI with real file"""
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"CLI test content")
    
    # Run CLI
    result = main([str(test_file)])
    
    # Check it ran successfully
    assert result == 0
    
    # Check output mentions renaming
    captured = capsys.readouterr()
    assert "Renamed" in captured.out


def test_cli_skips_nonexistent(capsys):
    """Test CLI handles nonexistent files gracefully"""
    result = main(["/nonexistent/file.txt"])
    
    captured = capsys.readouterr()
    assert "Skipping" in captured.out or "not a file" in captured.out

