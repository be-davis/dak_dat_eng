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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news'
    }

# Test with the St. Louis article
test_url = "https://www.fbi.gov/contact-us/field-offices/stlouis/news/pair-accused-of-sexually-abusing-13-year-old-boy"

print("Testing URL:", test_url)

try:
    headers = get_article_headers()
    req = Request(test_url, headers=headers)
    response = urlopen(req, timeout=60)
    
    print("Response status:", response.getcode())
    
    # Handle compressed content properly
    content = response.read()
    if response.info().get('Content-Encoding') == 'gzip':
        content = gzip.decompress(content)
    
    # Decode content with proper encoding
    try:
        html_content = content.decode('utf-8')
    except UnicodeDecodeError:
        html_content = content.decode('latin-1', errors='replace')
    
    page_soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check page title
    title = page_soup.find('title')
    if title:
        print(f"Page title: {title.get_text().strip()}")
    
    # Find paragraphs
    p_list = page_soup.find_all('p')
    print(f"Found {len(p_list)} paragraph elements")
    
    if p_list:
        print("\nFirst few paragraphs:")
        for i, p in enumerate(p_list[:5]):
            text = p.get_text().strip()
            if text:  # Only show non-empty paragraphs
                print(f"P{i+1}: {text[:100]}...")
    
    # Look for main content divs
    main_content = page_soup.find('div', {'class': 'content'}) or page_soup.find('main') or page_soup.find('article')
    if main_content:
        print(f"\nFound main content area")
        content_p = main_content.find_all('p')
        print(f"Paragraphs in main content: {len(content_p)}")
        if content_p:
            print(f"First content paragraph: {content_p[0].get_text().strip()[:200]}...")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()