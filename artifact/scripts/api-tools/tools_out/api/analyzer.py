from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ...base import BaseTool
import json
import re

@dataclass
class APIService:
    """Represents an API service with accessibility information."""
    name: str
    key: str
    category: str
    requires_payment: bool
    accessibility_features: List[str]
    documentation_url: Optional[str] = None

class APIAnalyzer(BaseTool):
    """Tool for analyzing API services with focus on accessibility features."""
    
    def __init__(self):
        super().__init__()
        self.services: Dict[str, APIService] = {}
        self.free_apis = {
            "semantic_scholar": "https://api.semanticscholar.org/",
            "arxiv": "https://arxiv.org/help/api/",
            "unpaywall": "https://unpaywall.org/products/api",
            "open_library": "https://openlibrary.org/developers/api",
            "gutendex": "https://gutendex.com/",
            "courtlistener": "https://www.courtlistener.com/api/",
            "federal_election": "https://api.open.fec.gov/",
            "healthcare_gov": "https://www.healthcare.gov/developers/",
            "open_food_facts": "https://world.openfoodfacts.org/data",
            "google_scholar": "https://scholar.google.com/",
            "github": "https://api.github.com/",
            "reddit": "https://www.reddit.com/dev/api/",
            "news_api": "https://newsapi.org/",
            "guardian": "https://open-platform.theguardian.com/",
            "nyt": "https://developer.nytimes.com/apis",
            "wayback_machine": "https://archive.org/help/wayback_api.php",
            "free_dictionary": "https://dictionaryapi.dev/",
            "open_trivia": "https://opentdb.com/api_config.php",
        }

    def categorize_api(self, name: str) -> str:
        """
        Categorize an API based on its name and known patterns.
        
        Args:
            name (str): The name of the API service
            
        Returns:
            str: The category of the API
        """
        name_lower = name.lower()
        
        categories = {
            "accessibility": ["text to speech", "tts", "alt", "aria", "screen reader", "voice", "speech"],
            "research": ["scholar", "research", "academic", "arxiv", "library", "dictionary"],
            "healthcare": ["health", "medical", "clinical", "therapy", "food"],
            "education": ["education", "learning", "teaching", "trivia"],
            "media": ["media", "audio", "video", "image", "news", "guardian", "nyt"],
            "development": ["api", "code", "git", "dev", "github"],
            "analysis": ["analysis", "data", "processing", "stats"],
            "government": ["gov", "federal", "election", "court"],
        }
        
        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        return "other"

    def analyze_accessibility_features(self, name: str, description: str = "") -> List[str]:
        """
        Analyze potential accessibility features of an API.
        
        Args:
            name (str): The name of the API service
            description (str, optional): Additional description of the API
            
        Returns:
            List[str]: List of identified accessibility features
        """
        features = []
        text = f"{name} {description}".lower()
        
        if any(term in text for term in ["speech", "tts", "voice"]):
            features.append("text_to_speech")
        if any(term in text for term in ["alt", "image", "description"]):
            features.append("alt_text")
        if any(term in text for term in ["aria", "semantic"]):
            features.append("semantic_markup")
        if "audio" in text:
            features.append("audio_processing")
        if any(term in text for term in ["translate", "language"]):
            features.append("translation")
            
        return features

    def analyze_api_keys(self, api_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze API keys from structured data.
        
        Args:
            api_data (List[Dict[str, str]]): List of API service data
            
        Returns:
            Dict[str, Any]: Analysis results including categorized services
        """
        for item in api_data:
            service_name = item.get("service", "")
            api_key = item.get("key", "")
            
            if not service_name or not api_key:
                continue
            
            category = self.categorize_api(service_name)
            requires_payment = service_name.lower() not in self.free_apis
            accessibility_features = self.analyze_accessibility_features(service_name)
            
            self.services[service_name] = APIService(
                name=service_name,
                key=api_key,
                category=category,
                requires_payment=requires_payment,
                accessibility_features=accessibility_features,
                documentation_url=self.free_apis.get(service_name.lower())
            )
            
        return self.generate_analysis()

    def generate_analysis(self) -> Dict[str, Any]:
        """
        Generate a structured analysis of API services.
        
        Returns:
            Dict[str, Any]: Structured analysis results
        """
        categories: Dict[str, List[Dict[str, Any]]] = {}
        free_apis: List[Dict[str, Any]] = []
        
        for service in self.services.values():
            service_data = {
                "name": service.name,
                "category": service.category,
                "requires_payment": service.requires_payment,
                "accessibility_features": service.accessibility_features,
                "documentation_url": service.documentation_url
            }
            
            if service.category not in categories:
                categories[service.category] = []
            categories[service.category].append(service_data)
            
            if not service.requires_payment:
                free_apis.append(service_data)
        
        return {
            "categories": categories,
            "free_apis": free_apis,
            "total_services": len(self.services),
            "total_free": len(free_apis),
            "accessibility_focused": len([s for s in self.services.values() 
                                       if s.accessibility_features])
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the API analyzer tool.
        
        Args:
            api_data (List[Dict[str, str]]): List of API service data to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        api_data = kwargs.get('api_data', [])
        if not api_data:
            return {
                'success': False,
                'error': 'No API data provided'
            }
            
        try:
            analysis = self.analyze_api_keys(api_data)
            return {
                'success': True,
                'data': analysis
            }
        except Exception as e:
            self.logger.error(f"Error analyzing API data: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }

    @property
    def tool_name(self) -> str:
        return "api_analyzer"

    @property
    def description(self) -> str:
        return "Analyzes API services with focus on accessibility features"

    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "api_data": {
                "type": "array",
                "description": "List of API service data to analyze",
                "items": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string"},
                        "key": {"type": "string"}
                    }
                },
                "required": True
            }
        } 