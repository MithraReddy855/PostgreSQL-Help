import os
import logging
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

logger = logging.getLogger(__name__)

# Cache for documentation pages to avoid repeated requests
DOC_CACHE = {}

def fetch_doc_page(url):
    """
    Fetch a PostgreSQL documentation page
    
    Args:
        url (str): URL of the documentation page
        
    Returns:
        str or None: HTML content of the page or None if there was an error
    """
    # Check cache first
    if url in DOC_CACHE:
        return DOC_CACHE[url]
    
    try:
        # Add a small delay to avoid overwhelming the docs server
        time.sleep(0.1)
        
        headers = {
            'User-Agent': 'PostgreSQL-Agent/1.0 (Documentation Helper)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Cache the result
        DOC_CACHE[url] = response.text
        
        return response.text
        
    except requests.RequestException as e:
        logger.error(f"Error fetching documentation page {url}: {str(e)}")
        return None

def extract_content(element):
    """
    Extract text content from HTML element, preserving some formatting
    
    Args:
        element (BeautifulSoup element): The HTML element to extract content from
        
    Returns:
        str: Extracted and formatted content
    """
    if not element:
        return ""
    
    # Use a list to build the content to avoid string concatenation in a loop
    content_parts = []
    
    for child in element.descendants:
        # Handle different tag types to preserve some formatting
        if child.name == 'h1':
            content_parts.append(f"\n\n== {child.get_text(strip=True)} ==\n\n")
        elif child.name == 'h2':
            content_parts.append(f"\n\n-- {child.get_text(strip=True)} --\n\n")
        elif child.name == 'h3':
            content_parts.append(f"\n\n* {child.get_text(strip=True)} *\n\n")
        elif child.name == 'p':
            content_parts.append(f"{child.get_text(strip=True)}\n\n")
        elif child.name == 'pre' or child.name == 'code':
            # Preserve code blocks
            content_parts.append(f"\n```\n{child.get_text()}\n```\n")
        elif child.name == 'li':
            content_parts.append(f"  * {child.get_text(strip=True)}\n")
        elif child.name == 'a' and child.has_attr('href'):
            # Include links
            text = child.get_text(strip=True)
            href = child.get('href')
            content_parts.append(f"{text} [{href}]")
        elif child.name is None and child.strip():
            # This is a text node with content
            content_parts.append(child.strip())
    
    # Join all parts and clean up
    content = "".join(content_parts)
    
    # Remove excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def extract_code_examples(html_content):
    """
    Extract code examples from documentation HTML
    
    Args:
        html_content (str): HTML content
        
    Returns:
        list: List of code examples
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        examples = []
        
        # Find code blocks
        for pre in soup.find_all('pre'):
            # Check if this is a SQL example
            text = pre.get_text()
            if any(keyword in text.lower() for keyword in ['select', 'insert', 'update', 'delete', 'create', 'alter']):
                examples.append(text)
        
        return examples
        
    except Exception as e:
        logger.error(f"Error extracting code examples: {str(e)}")
        return []

def find_related_docs(html_content, base_url):
    """
    Find related documentation links
    
    Args:
        html_content (str): HTML content
        base_url (str): Base URL for resolving relative links
        
    Returns:
        list: List of related documentation links
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        related_links = []
        
        # Look for links in the document
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filter to include only links to other documentation pages
            if (href.endswith('.html') or '/' in href) and not href.startswith(('http:', 'https:', 'mailto:')):
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                
                related_links.append({
                    'text': text,
                    'url': full_url
                })
        
        return related_links
        
    except Exception as e:
        logger.error(f"Error finding related docs: {str(e)}")
        return []
