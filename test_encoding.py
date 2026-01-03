from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import gzip
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def get_article_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

# Test with a single FBI URL
test_url = "https://www.fbi.gov/contact-us/field-offices/stlouis/news/pair-accused-of-sexually-abusing-13-year-old-boy"

print("Testing URL:", test_url)

try:
    req = Request(test_url, headers=get_article_headers())
    response = urlopen(req, timeout=60)
    
    print("Response headers:")
    for header, value in response.info().items():
        print(f"  {header}: {value}")
    
    # Handle compressed content properly
    content = response.read()
    print(f"Raw content length: {len(content)} bytes")
    
    if response.info().get('Content-Encoding') == 'gzip':
        print("Content is gzip compressed, decompressing...")
        content = gzip.decompress(content)
        print(f"Decompressed content length: {len(content)} bytes")
    
    # Decode content with proper encoding
    try:
        html_content = content.decode('utf-8')
        print("Successfully decoded as UTF-8")
    except UnicodeDecodeError as e:
        print(f"UTF-8 decode failed: {e}")
        html_content = content.decode('latin-1', errors='replace')
        print("Fallback to latin-1 decoding")
    
    page_soup = BeautifulSoup(html_content, 'html.parser')
    
    # Test if we can find paragraphs
    p_list = page_soup.find_all('p')
    print(f"Found {len(p_list)} paragraph elements")
    
    if p_list:
        first_p = p_list[0].get_text().strip()
        print(f"First paragraph text (first 100 chars): {first_p[:100]}")
    
    # Check for title
    title = page_soup.find('title')
    if title:
        print(f"Page title: {title.get_text().strip()}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()