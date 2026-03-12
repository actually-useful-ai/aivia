# Web Search Tool Documentation

## Overview
The web search tool provides advanced web search capabilities using multiple search engines and APIs. It's designed to deliver comprehensive, relevant results while handling rate limiting, caching, and error management.

## Required Credentials
```python
SERPER_API_KEY="your_serper_api_key"  # Required for Google Search API
BING_API_KEY="your_bing_api_key"      # Optional for Bing search
```

## Input Parameters

### Required Parameters
- `query` (str): The search query to execute
- `num_results` (int): Number of results to return (default: 10)

### Optional Parameters
- `search_type` (str): Type of search ('web', 'news', 'images')
- `region` (str): Geographic region for results
- `language` (str): Preferred language for results
- `safe_search` (bool): Whether to enable safe search
- `time_period` (str): Time range for results ('day', 'week', 'month', 'year')

## Output Format
```json
{
    "results": [
        {
            "title": "Result title",
            "link": "https://result.url",
            "snippet": "Result description or excerpt",
            "position": 1,
            "source": "search_engine_name",
            "date_published": "ISO datetime",
            "additional_links": ["related_url1", "related_url2"]
        }
    ],
    "metadata": {
        "total_results": 100,
        "search_time": 0.5,
        "engine": "google",
        "query": "original query"
    }
}
```

## Rate Limits
- Serper API: 1000 requests/month (free tier)
- Bing API: Varies by subscription
- Built-in rate limiting: 60 requests/minute

## Error Handling
```python
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Detailed error message",
        "suggestion": "Suggested fix"
    }
}
```

Common error codes:
- `RATE_LIMIT_EXCEEDED`
- `API_KEY_INVALID`
- `QUERY_TOO_LONG`
- `NO_RESULTS_FOUND`
- `SERVICE_UNAVAILABLE`

## Example Usage

### Basic Search
```python
from tools.web_search import WebSearch

searcher = WebSearch()
results = searcher.search("ActuallyUsefulAI documentation")
```

### Advanced Search
```python
results = searcher.search(
    query="machine learning tutorials",
    num_results=20,
    search_type="web",
    region="US",
    language="en",
    time_period="month"
)
```

## Common Applications

### Research Workflows
1. Initial broad search
2. Filtering results by date/relevance
3. Extracting key information
4. Following related links

### Content Aggregation
1. Collecting articles on a topic
2. Monitoring news updates
3. Gathering reference materials
4. Finding primary sources

### Data Collection
1. Market research
2. Competitive analysis
3. Trend monitoring
4. Source verification

## Integration Examples

### With Infinite Search
```python
from tools.infinite_search import InfiniteSearch
from tools.web_search import WebSearch

def deep_research(topic):
    initial_results = WebSearch().search(topic)
    deep_results = InfiniteSearch().explore(initial_results)
    return deep_results
```

### With Content Analysis
```python
from tools.web_search import WebSearch
from tools.tool_advanced_web_scrape import WebScraper

def analyze_topic(query):
    search_results = WebSearch().search(query)
    detailed_content = []
    for result in search_results:
        content = WebScraper().scrape(result['link'])
        detailed_content.append(content)
    return detailed_content
```

## Best Practices

### Query Optimization
1. Use specific keywords
2. Include relevant filters
3. Consider region/language
4. Use time period constraints

### Resource Management
1. Cache frequent searches
2. Implement rate limiting
3. Handle errors gracefully
4. Log search patterns

### Result Processing
1. Validate URLs
2. Check content relevance
3. Extract key information
4. Store useful metadata

## Troubleshooting

### Common Issues
1. Rate limit exceeded
   - Solution: Implement exponential backoff
2. No results found
   - Solution: Broaden search terms
3. Invalid results
   - Solution: Add more specific keywords
4. API errors
   - Solution: Check credentials and quotas

### Performance Optimization
1. Use async requests
2. Implement caching
3. Batch similar queries
4. Filter results server-side 