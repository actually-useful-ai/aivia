"""
Data Processing tools combining JSON conversion, OCR, and audio transcription
Enhanced with accessibility features and improved formatting
"""

import json
import yaml
import toml
import xml.dom.minidom
import csv
import io
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import whisper
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union, List
import os
import tempfile

def _convert_to_json(data: Any, indent: Optional[int] = None) -> str:
    """Convert data to JSON format"""
    return json.dumps(data, indent=indent)

def _convert_to_yaml(data: Any) -> str:
    """Convert data to YAML format"""
    return yaml.dump(data, sort_keys=False, allow_unicode=True)

def _convert_to_toml(data: Any) -> str:
    """Convert data to TOML format"""
    return toml.dumps(data)

def _convert_to_xml(data: Any) -> str:
    """Convert data to XML format"""
    def dict_to_xml(data: Dict, root_name: str = "root") -> str:
        doc = xml.dom.minidom.Document()
        root = doc.createElement(root_name)
        doc.appendChild(root)
        
        def add_element(parent, key, value):
            if isinstance(value, dict):
                child = doc.createElement(key)
                for k, v in value.items():
                    add_element(child, k, v)
                parent.appendChild(child)
            elif isinstance(value, list):
                for item in value:
                    child = doc.createElement(key)
                    if isinstance(item, dict):
                        for k, v in item.items():
                            add_element(child, k, v)
                    else:
                        child.appendChild(doc.createTextNode(str(item)))
                    parent.appendChild(child)
            else:
                child = doc.createElement(key)
                child.appendChild(doc.createTextNode(str(value)))
                parent.appendChild(child)
        
        for key, value in data.items():
            add_element(root, key, value)
        
        return doc.toprettyxml(indent="  ")
    
    return dict_to_xml(data)

def _convert_to_csv(data: Any) -> str:
    """Convert data to CSV format"""
    output = io.StringIO()
    writer = None
    
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output)
            writer.writerows(data)
    elif isinstance(data, dict):
        writer = csv.writer(output)
        writer.writerows([[k, v] for k, v in data.items()])
    
    return output.getvalue()

def _extract_text_from_image(image_path: str, language: str = "eng") -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang=language)
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def _extract_text_from_pdf(pdf_path: str, language: str = "eng") -> List[str]:
    """Extract text from PDF using OCR if needed"""
    try:
        doc = fitz.open(pdf_path)
        pages = []
        
        for page in doc:
            # Try to get text directly first
            text = page.get_text()
            
            # If no text found, try OCR
            if not text.strip():
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img, lang=language)
            
            pages.append(text.strip())
        
        return pages
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def _transcribe_audio(
    audio_path: str,
    model_name: str = "base",
    language: Optional[str] = None,
    task: str = "transcribe",
    temperature: float = 0.0,
    format: str = "text"
) -> Union[str, Dict[str, Any]]:
    """Transcribe audio using Whisper"""
    try:
        # Load model
        model = whisper.load_model(model_name)
        
        # Set up options
        options = {}
        if language:
            options["language"] = language
        
        # Transcribe
        result = model.transcribe(
            audio_path,
            task=task,
            temperature=temperature,
            **options
        )
        
        # Format output
        if format == "text":
            return result["text"]
        elif format == "json":
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result["language"]
            }
        elif format in ["srt", "vtt"]:
            writer = whisper.utils.get_writer(format, ".")
            return writer(result, audio_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")

class Tools:
    """Data processing tools with enhanced accessibility"""
    
    class Valves(BaseModel):
        TESSERACT_PATH: str = Field(
            default="",
            description="Path to Tesseract executable"
        )
        OCR_LANGUAGES: List[str] = Field(
            default=["eng"],
            description="List of installed OCR languages"
        )
        WHISPER_MODEL: str = Field(
            default="base",
            description="Default Whisper model to use"
        )
        JSON_INDENT: int = Field(
            default=2,
            description="Default indentation for JSON output"
        )

    def __init__(self):
        self.valves = self.Valves()
        if self.valves.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = self.valves.TESSERACT_PATH

    def convert_json(
        self,
        data: Union[str, Dict, List],
        target_format: str = "json",
        style: str = "pretty"
    ) -> Dict[str, Any]:
        """
        Convert data between JSON and other formats.
        
        :param data: Input data (string or Python object)
        :param target_format: Target format (json, yaml, toml, xml, csv)
        :param style: Output style (pretty, compact, single_line)
        :return: Dictionary with conversion results
        """
        try:
            # Parse input if string
            if isinstance(data, str):
                data = json.loads(data)
            
            # Convert to target format
            if target_format == "json":
                indent = self.valves.JSON_INDENT if style == "pretty" else None
                result = _convert_to_json(data, indent)
            elif target_format == "yaml":
                result = _convert_to_yaml(data)
            elif target_format == "toml":
                result = _convert_to_toml(data)
            elif target_format == "xml":
                result = _convert_to_xml(data)
            elif target_format == "csv":
                result = _convert_to_csv(data)
            else:
                raise ValueError(f"Unsupported format: {target_format}")
            
            # Apply style
            if style == "single_line":
                result = result.replace("\n", " ").strip()
            
            return {
                "status": "success",
                "data": {
                    "converted": result,
                    "format": target_format,
                    "style": style
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def process_ocr(
        self,
        file_path: str,
        language: str = "eng",
        format: str = "text"
    ) -> Dict[str, Any]:
        """
        Process image or PDF file with OCR.
        
        :param file_path: Path to image or PDF file
        :param language: OCR language
        :param format: Output format (text, json, markdown)
        :return: Dictionary with OCR results
        """
        try:
            # Check file type
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in [".pdf"]:
                pages = _extract_text_from_pdf(file_path, language)
                
                if format == "text":
                    result = "\n\n".join(pages)
                elif format == "json":
                    result = {"pages": pages}
                else:  # markdown
                    result = "\n\n".join(f"## Page {i+1}\n\n{text}" 
                                       for i, text in enumerate(pages))
                    
            elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                text = _extract_text_from_image(file_path, language)
                
                if format == "text":
                    result = text
                elif format == "json":
                    result = {"text": text}
                else:  # markdown
                    result = f"# Extracted Text\n\n{text}"
                    
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            
            return {
                "status": "success",
                "data": {
                    "result": result,
                    "format": format,
                    "language": language,
                    "pages": len(pages) if ext == ".pdf" else 1
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def transcribe_audio(
        self,
        file_path: str,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        format: str = "text"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.
        
        :param file_path: Path to audio file
        :param model: Whisper model name (optional)
        :param options: Additional options (language, task, temperature)
        :param format: Output format (text, json, srt, vtt)
        :return: Dictionary with transcription results
        """
        try:
            # Set up options
            opts = options or {}
            model_name = model or self.valves.WHISPER_MODEL
            
            # Transcribe
            result = _transcribe_audio(
                file_path,
                model_name=model_name,
                language=opts.get("language"),
                task=opts.get("task", "transcribe"),
                temperature=opts.get("temperature", 0.0),
                format=format
            )
            
            return {
                "status": "success",
                "data": {
                    "result": result,
                    "format": format,
                    "model": model_name,
                    "options": opts
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            } 