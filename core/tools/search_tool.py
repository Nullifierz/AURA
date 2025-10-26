"""
Web Search tool for AURA AI Assistant.
Provides web search capabilities using SearXNG API with article content fetching.
"""

import requests
from bs4 import BeautifulSoup
from core.logger import get_logger

logger = get_logger(__name__)

def _fetch_article_content(url: str, max_length: int = 2000) -> str:
    """Fetch and extract main content from a URL.
    
    Args:
        url: The URL to fetch content from
        max_length: Maximum content length in characters
        
    Returns:
        Extracted article content or error message
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script, style, and nav elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Try to find main content
            main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body
                text = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
            
            # Clean up text
            text = ' '.join(text.split())
            
            # Limit length
            if len(text) > max_length:
                text = text[:max_length] + '...'
            
            return text
        else:
            return f"[Could not fetch article - Status {response.status_code}]"
            
    except Exception as e:
        logger.warning(f"Error fetching article from {url}: {e}")
        return "[Could not fetch article content]"

# Function declaration for Gemini API (following Google's schema)
search_declaration = {
    "name": "search_web",
    "description": "Search the web and READ article contents to provide comprehensive analysis. Use this when user asks to search for something, look up information, find current news, or wants ANALYSIS of web content. Fetches full article text for deeper understanding. Perfect for: 'search for X', 'what's new about Y', 'tell me about Z'.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web. Be specific and use relevant keywords.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of articles to fetch and read. Default is 3. Use 3 for quick analysis, 5 for comprehensive research. Note: Fetching article content takes time.",
            },
            "fetch_content": {
                "type": "boolean",
                "description": "Whether to fetch full article content for analysis. Set to true when user wants analysis, summary, or conclusion. Set to false for just search results. Default is true.",
            }
        },
        "required": ["query"]
    }
}

def search_web(query: str, max_results: int = 3, fetch_content: bool = True) -> str:
    """Search the web using SearXNG API and optionally fetch article content.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 3)
        fetch_content: Whether to fetch full article content (default: True)
        
    Returns:
        A formatted string containing search results with titles, URLs, snippets, and optionally full content
    """
    try:
        logger.info(f"Searching web for: {query} (fetch_content={fetch_content})")
        
        # SearXNG API endpoint
        searxng_url = "http://localhost:8888/search"
        
        # Request parameters
        params = {
            'q': query,
            'format': 'json',
            'language': 'en',
            'safesearch': 1,  # Moderate safe search
        }
        
        response = requests.get(searxng_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return f"No search results found for '{query}'."
            
            # Limit results
            results = results[:max_results]
            
            # Format output
            output = f"Search Results for '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                url = result.get('url', '')
                snippet = result.get('content', result.get('snippet', 'No description available'))
                
                # Clean up snippet
                snippet = ' '.join(snippet.split())
                if len(snippet) > 150:
                    snippet = snippet[:150] + '...'
                
                output += f"{i}. {title}\n"
                output += f"   Summary: {snippet}\n"
                output += f"   URL: {url}\n"
                
                # Fetch full article content if requested
                if fetch_content:
                    logger.info(f"Fetching content from: {url}")
                    article_content = _fetch_article_content(url, max_length=2000)
                    output += f"   Content: {article_content}\n"
                
                output += "\n"
            
            logger.info(f"Found {len(results)} search results (fetch_content={fetch_content})")
            return output.strip()
        
        elif response.status_code == 404:
            return "SearXNG service not found. Please ensure SearXNG is running at http://localhost:8888"
        else:
            return f"Search service returned error code: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to SearXNG service")
        return "Cannot connect to search service. Please ensure SearXNG is running at http://localhost:8888"
    except requests.exceptions.Timeout:
        logger.error("SearXNG search timed out")
        return "Search request timed out. Please try again."
    except Exception as e:
        logger.error(f"Error during web search: {e}", exc_info=True)
        return f"Error performing web search: {str(e)}"

def get_search_results_data(query: str, max_results: int = 5) -> dict:
    """Get structured search results data for HUD display.
    
    This is an internal function used by the backend for HUD display.
    Not exposed as a tool to Gemini.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        A dictionary containing structured search results data
    """
    try:
        logger.info(f"Getting structured search data for: {query}")
        
        # SearXNG API endpoint
        searxng_url = "http://localhost:8888/search"
        
        # Request parameters
        params = {
            'q': query,
            'format': 'json',
            'language': 'en',
            'safesearch': 1,
        }
        
        response = requests.get(searxng_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return {
                    "error": "No results",
                    "message": f"No search results found for '{query}'."
                }
            
            # Limit results
            results = results[:max_results]
            
            # Format results for HUD
            results_list = []
            for result in results:
                title = result.get('title', 'No title')
                url = result.get('url', '')
                snippet = result.get('content', result.get('snippet', 'No description'))
                
                # Clean up snippet
                snippet = ' '.join(snippet.split())
                if len(snippet) > 200:
                    snippet = snippet[:200] + '...'
                
                results_list.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
            
            return {
                "query": query,
                "results": results_list,
                "count": len(results_list)
            }
        else:
            return {
                "error": "Search error",
                "message": f"Search service returned error code: {response.status_code}"
            }
            
    except Exception as e:
        logger.error(f"Error getting search data: {e}", exc_info=True)
        return {
            "error": "Error",
            "message": f"Error performing web search: {str(e)}"
        }
