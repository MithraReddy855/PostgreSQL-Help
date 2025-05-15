import re
import requests
import logging
from bs4 import BeautifulSoup
from config import POSTGRESQL_DOC_BASE_URL, DOCUMENTATION_SECTIONS
from utils.doc_parser import fetch_doc_page, extract_content

logger = logging.getLogger(__name__)

def search_documentation(search_term):
    """
    Search PostgreSQL documentation for a given term
    
    Args:
        search_term (str): The term to search for in the documentation
        
    Returns:
        list: A list of dict containing search results with title, url, and snippet
    """
    logger.debug(f"Searching documentation for: {search_term}")
    
    # Use PostgreSQL's search function via their website
    search_url = f"https://www.postgresql.org/search/?q={search_term}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract search results from the page
        result_elements = soup.select('.search-results li')
        
        for element in result_elements[:10]:  # Limit to top 10 results
            link = element.find('a')
            if not link:
                continue
                
            url = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Get a snippet of text if available
            snippet = ""
            paragraph = element.find('p')
            if paragraph:
                snippet = paragraph.get_text(strip=True)
            
            # Only include documentation results
            if '/docs/' in url:
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching documentation: {str(e)}")
        return []

def get_doc_content(doc_path):
    """
    Get the full content of a specific documentation page
    
    Args:
        doc_path (str): The path to the documentation page
        
    Returns:
        dict: A dictionary containing the title and content of the documentation
    """
    logger.debug(f"Getting documentation content for: {doc_path}")
    
    try:
        # Make sure we have a valid doc path
        if not doc_path.endswith('.html'):
            doc_path = f"{doc_path}.html"
            
        full_url = f"{POSTGRESQL_DOC_BASE_URL}{doc_path}"
        html_content = fetch_doc_page(full_url)
        
        if not html_content:
            return {'title': 'Not Found', 'content': 'Documentation page could not be loaded.'}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title_elem = soup.find('title')
        title = title_elem.get_text() if title_elem else 'PostgreSQL Documentation'
        
        # Extract the main content
        content_elem = soup.find('div', class_='sect1') or soup.find('div', class_='chapter')
        
        if not content_elem:
            content_elem = soup.find('body')
            
        content = extract_content(content_elem) if content_elem else 'Content not available'
        
        return {
            'title': title,
            'content': content
        }
        
    except Exception as e:
        logger.error(f"Error getting doc content: {str(e)}")
        return {
            'title': 'Error',
            'content': f'Failed to retrieve documentation: {str(e)}'
        }

def get_doc_sections():
    """
    Get structured sections of PostgreSQL documentation
    
    Returns:
        dict: A dictionary of documentation sections
    """
    logger.debug("Getting documentation sections")
    
    try:
        # Get the main index page
        index_url = f"{POSTGRESQL_DOC_BASE_URL}index.html"
        html_content = fetch_doc_page(index_url)
        
        if not html_content:
            return DOCUMENTATION_SECTIONS
            
        # Parse sections from the documentation index
        soup = BeautifulSoup(html_content, 'html.parser')
        toc_div = soup.find('div', class_='toc')
        
        # If we can't parse the TOC, return the predefined sections
        if not toc_div:
            return DOCUMENTATION_SECTIONS
            
        sections = {}
        current_section = None
        
        for element in toc_div.find_all(['dt', 'dd']):
            if element.name == 'dt':
                current_section = element.get_text(strip=True)
                sections[current_section] = []
            elif element.name == 'dd' and current_section:
                link = element.find('a')
                if link:
                    url = link.get('href', '')
                    title = link.get_text(strip=True)
                    sections[current_section].append({
                        'title': title,
                        'url': url
                    })
        
        # If sections is empty, fall back to predefined sections
        return sections if sections else DOCUMENTATION_SECTIONS
        
    except Exception as e:
        logger.error(f"Error getting doc sections: {str(e)}")
        return DOCUMENTATION_SECTIONS
