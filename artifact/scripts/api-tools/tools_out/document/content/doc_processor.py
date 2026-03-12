"""
Document management tools with enhanced accessibility and formatting
"""

import json
import os
import shutil
import logging
import hashlib
import datetime
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import requests
from bs4 import BeautifulSoup
import markdown
import html2text

class EventEmitter:
    """Event emitter for progress tracking"""
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def progress_update(self, description):
        await self.emit(description)

    async def error_update(self, description):
        await self.emit(description, "error", True)

    async def success_update(self, description):
        await self.emit(description, "success", True)

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter({
                "type": "status",
                "data": {
                    "status": status,
                    "description": description,
                    "done": done,
                }
            })

class Tools:
    """Tools for document management operations with enhanced accessibility"""
    
    class Valves(BaseModel):
        PAPERLESS_URL: str = Field(
            default="http://localhost:8000",
            description="Paperless-ngx server URL"
        )
        PAPERLESS_TOKEN: str = Field(
            default="",
            description="Paperless-ngx API token"
        )
        OCR_LANGUAGES: List[str] = Field(
            default=["eng"],
            description="Default OCR languages"
        )
        FILE_PATTERNS: Dict[str, List[str]] = Field(
            default={
                "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
                "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
                "archives": [".zip", ".tar", ".gz", ".7z", ".rar"],
                "code": [".py", ".js", ".html", ".css", ".json", ".xml"]
            },
            description="File type patterns for organization"
        )
        
    def __init__(self):
        """Initialize document management tools"""
        self.valves = self.Valves()
        
        # Configure OCR if available
        if os.getenv("TESSERACT_PATH"):
            pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
            
        # Configure Paperless if token available
        self.paperless_token = os.getenv("PAPERLESS_TOKEN")
        if self.paperless_token:
            self.valves.PAPERLESS_TOKEN = self.paperless_token
            
    async def process_ocr(self, file_path: str, options: dict = {}, __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Extract text from images and PDFs using OCR"""
        emitter = EventEmitter(__event_emitter__)
        
        try:
            await emitter.progress_update(f"Processing OCR for {file_path}")
            
            # Validate file exists
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
                
            # Process options
            language = options.get("language", self.valves.OCR_LANGUAGES[0])
            format_type = options.get("format", "text")
            include_metadata = options.get("include_metadata", False)
            
            extracted_text = ""
            metadata = {}
            
            # Handle PDFs
            if file_path.lower().endswith(".pdf"):
                pdf_document = fitz.open(file_path)
                metadata = {
                    "pages": len(pdf_document),
                    "title": pdf_document.metadata.get("title", ""),
                    "author": pdf_document.metadata.get("author", ""),
                    "creation_date": str(pdf_document.metadata.get("creationDate", ""))
                }
                
                for page_num in range(len(pdf_document)):
                    await emitter.progress_update(f"Processing page {page_num + 1}/{len(pdf_document)}")
                    
                    page = pdf_document[page_num]
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    text = pytesseract.image_to_string(img, lang=language)
                    extracted_text += f"\n\nPage {page_num + 1}:\n{text}"
                    
                pdf_document.close()
                
            # Handle images
            else:
                img = Image.open(file_path)
                metadata = {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode
                }
                
                extracted_text = pytesseract.image_to_string(img, lang=language)
                
            # Format output
            if format_type == "json":
                result = {
                    "text": extracted_text.strip(),
                    "language": language,
                    "file": file_path
                }
                if include_metadata:
                    result["metadata"] = metadata
                    
            elif format_type == "markdown":
                result = f"# OCR Results: {os.path.basename(file_path)}\n\n"
                if include_metadata:
                    result += "## Metadata\n"
                    for key, value in metadata.items():
                        result += f"- **{key}**: {value}\n"
                result += f"\n## Extracted Text\n\n{extracted_text.strip()}"
                
            else:  # text
                result = extracted_text.strip()
                
            await emitter.success_update(f"Successfully processed {file_path}")
            
            return {
                "status": "success",
                "data": {
                    "result": result,
                    "format": format_type,
                    "language": language,
                    "pages": metadata.get("pages", 1)
                }
            }
            
        except Exception as e:
            error_message = f"Error processing OCR: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
            
    async def get_paperless_documents(self, documentTypeName: Optional[str] = None,
                                    documentTagName: Optional[str] = None,
                                    correspondent: Optional[str] = None,
                                    created_year: Optional[int] = None,
                                    created_month: Optional[int] = None,
                                    __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Search and retrieve documents from Paperless"""
        emitter = EventEmitter(__event_emitter__)
        
        try:
            await emitter.progress_update("Searching Paperless documents")
            
            if not self.valves.PAPERLESS_TOKEN:
                raise ValueError("Paperless API token not configured")
                
            # Prepare API request
            headers = {
                "Authorization": f"Token {self.valves.PAPERLESS_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Build query parameters
            params = {}
            if documentTypeName:
                params["document_type__name__icontains"] = documentTypeName
            if documentTagName:
                params["tags__name__icontains"] = documentTagName
            if correspondent:
                params["correspondent__name__icontains"] = correspondent
            if created_year:
                params["created__year"] = created_year
            if created_month:
                params["created__month"] = created_month
                
            # Make API request
            response = requests.get(
                f"{self.valves.PAPERLESS_URL}/api/documents/",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Process results
            results = response.json()
            documents = []
            
            for doc in results.get("results", []):
                document = {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "created_date": doc.get("created"),
                    "modified_date": doc.get("modified"),
                    "correspondent": doc.get("correspondent_name"),
                    "document_type": doc.get("document_type_name"),
                    "tags": doc.get("tags", []),
                    "content": doc.get("content", "")
                }
                documents.append(document)
                
            await emitter.success_update(f"Found {len(documents)} documents")
            
            return {
                "status": "success",
                "data": {
                    "documents": documents,
                    "count": len(documents),
                    "query": {
                        "type": documentTypeName,
                        "tag": documentTagName,
                        "correspondent": correspondent,
                        "year": created_year,
                        "month": created_month
                    }
                }
            }
            
        except Exception as e:
            error_message = f"Error searching Paperless: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
            
    async def manage_files(self, operation: str, params: dict, __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Perform file management operations"""
        emitter = EventEmitter(__event_emitter__)
        
        try:
            await emitter.progress_update(f"Starting file operation: {operation}")
            
            source = params.get("source", "")
            if not source or not os.path.exists(source):
                raise ValueError(f"Invalid source path: {source}")
                
            # Handle different operations
            if operation == "organize":
                return await self._organize_files(source, params, emitter)
            elif operation in ["move", "copy"]:
                return await self._transfer_files(operation, source, params, emitter)
            elif operation == "archive":
                return await self._archive_files(source, params, emitter)
            elif operation == "delete":
                return await self._delete_files(source, params, emitter)
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            error_message = f"Error in file operation: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
            
    async def _organize_files(self, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Organize files by type"""
        recursive = params.get("recursive", False)
        create_dirs = params.get("create_dirs", True)
        
        organized = defaultdict(list)
        skipped = []
        
        # Walk through source directory
        for root, _, files in os.walk(source):
            if not recursive and root != source:
                continue
                
            for filename in files:
                filepath = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Determine file type
                file_type = None
                for type_name, extensions in self.valves.FILE_PATTERNS.items():
                    if file_ext in extensions:
                        file_type = type_name
                        break
                        
                if not file_type:
                    file_type = "other"
                    
                # Create type directory
                type_dir = os.path.join(source, file_type)
                if create_dirs and not os.path.exists(type_dir):
                    os.makedirs(type_dir)
                    
                # Move file
                try:
                    dest_path = os.path.join(type_dir, filename)
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        dest_path = os.path.join(type_dir, f"{base}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}")
                        
                    shutil.move(filepath, dest_path)
                    organized[file_type].append(filename)
                except Exception as e:
                    skipped.append({"file": filename, "error": str(e)})
                    
        await emitter.success_update("File organization complete")
        
        return {
            "status": "success",
            "data": {
                "organized": dict(organized),
                "skipped": skipped,
                "total_organized": sum(len(files) for files in organized.values()),
                "total_skipped": len(skipped)
            }
        }
        
    async def _transfer_files(self, operation: str, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Move or copy files"""
        destination = params.get("destination", "")
        if not destination:
            raise ValueError("Destination path required")
            
        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)
        create_dirs = params.get("create_dirs", True)
        
        if create_dirs:
            os.makedirs(destination, exist_ok=True)
            
        transferred = []
        skipped = []
        
        # Process files
        for root, _, files in os.walk(source):
            if not recursive and root != source:
                continue
                
            for filename in files:
                if not Path(filename).match(pattern):
                    continue
                    
                src_path = os.path.join(root, filename)
                dst_path = os.path.join(destination, filename)
                
                try:
                    if operation == "move":
                        shutil.move(src_path, dst_path)
                    else:  # copy
                        shutil.copy2(src_path, dst_path)
                    transferred.append(filename)
                except Exception as e:
                    skipped.append({"file": filename, "error": str(e)})
                    
        await emitter.success_update(f"File {operation} complete")
        
        return {
            "status": "success",
            "data": {
                "operation": operation,
                "transferred": transferred,
                "skipped": skipped,
                "total_transferred": len(transferred),
                "total_skipped": len(skipped)
            }
        }
        
    async def _archive_files(self, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Archive files"""
        archive_name = params.get("destination", f"archive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if not archive_name.endswith((".zip", ".tar.gz")):
            archive_name += ".zip"
            
        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)
        
        archived = []
        skipped = []
        
        # Create archive
        if archive_name.endswith(".zip"):
            with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as archive:
                for root, _, files in os.walk(source):
                    if not recursive and root != source:
                        continue
                        
                    for filename in files:
                        if not Path(filename).match(pattern):
                            continue
                            
                        filepath = os.path.join(root, filename)
                        try:
                            archive.write(filepath, os.path.relpath(filepath, source))
                            archived.append(filename)
                        except Exception as e:
                            skipped.append({"file": filename, "error": str(e)})
                            
        else:  # tar.gz
            with tarfile.open(archive_name, "w:gz") as archive:
                for root, _, files in os.walk(source):
                    if not recursive and root != source:
                        continue
                        
                    for filename in files:
                        if not Path(filename).match(pattern):
                            continue
                            
                        filepath = os.path.join(root, filename)
                        try:
                            archive.add(filepath, arcname=os.path.relpath(filepath, source))
                            archived.append(filename)
                        except Exception as e:
                            skipped.append({"file": filename, "error": str(e)})
                            
        await emitter.success_update("Archive creation complete")
        
        return {
            "status": "success",
            "data": {
                "archive": archive_name,
                "archived": archived,
                "skipped": skipped,
                "total_archived": len(archived),
                "total_skipped": len(skipped)
            }
        }
        
    async def _delete_files(self, source: str, params: dict, emitter: EventEmitter) -> Dict[str, Any]:
        """Delete files"""
        pattern = params.get("pattern", "*")
        recursive = params.get("recursive", False)
        
        deleted = []
        skipped = []
        
        # Process files
        for root, _, files in os.walk(source):
            if not recursive and root != source:
                continue
                
            for filename in files:
                if not Path(filename).match(pattern):
                    continue
                    
                filepath = os.path.join(root, filename)
                try:
                    os.remove(filepath)
                    deleted.append(filename)
                except Exception as e:
                    skipped.append({"file": filename, "error": str(e)})
                    
        await emitter.success_update("File deletion complete")
        
        return {
            "status": "success",
            "data": {
                "deleted": deleted,
                "skipped": skipped,
                "total_deleted": len(deleted),
                "total_skipped": len(skipped)
            }
        } 