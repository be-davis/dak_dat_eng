from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import random

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

# Test the main page first
print("=== Testing Main Page ===")
url = 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news'
try:
    req = Request(url, headers=get_headers())
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, 'html.parser')
    
    print(f"Page title: {page_soup.title.text if page_soup.title else 'No title'}")
    print(f"Page length: {len(str(page_soup))}")
    
    # Look for different possible elements that might contain article count
    possible_elements = [
        page_soup.find('p', {'class': 'right'}),
        page_soup.find('div', {'class': 'right'}),
        page_soup.find_all('p', string=lambda text: text and 'of' in text.lower()),
        page_soup.find_all('div', string=lambda text: text and 'of' in text.lower()),
    ]
    
    print("\n=== Looking for article count elements ===")
    for i, elem in enumerate(possible_elements):
        if elem:
            if isinstance(elem, list):
                print(f"Element type {i} (list): {[e.get_text().strip() for e in elem[:3]]}")
            else:
                print(f"Element type {i}: {elem.get_text().strip()}")
        else:
            print(f"Element type {i}: None")
            
except Exception as e:
    print(f"Error accessing main page: {e}")

# Test the first pagination page
print("\n=== Testing First Pagination Page ===")
BASE_URL = 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news/@@castle.cms.querylisting/9e361bf3a4174df2ad8c0e1a83906cd4?page='
url = BASE_URL + '1'
try:
    req = Request(url, headers=get_headers())
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, 'html.parser')
    
    print(f"Pagination page title: {page_soup.title.text if page_soup.title else 'No title'}")
    print(f"Pagination page length: {len(str(page_soup))}")
    
    # Look for links with different selectors
    button_links = page_soup.find_all('a', {'class': 'button'})
    all_links = page_soup.find_all('a', href=True)
    
    print(f"\nFound {len(button_links)} links with class 'button'")
    print(f"Found {len(all_links)} total links")
    
    if button_links:
        print("First few button links:")
        for link in button_links[:3]:
            print(f"  - {link.get('href', 'No href')}")
    
    # Look for other possible link patterns
    article_links = []
    for link in all_links:
        href = link.get('href', '')
        if 'news' in href and 'field-offices' in href:
            article_links.append(href)
    
    print(f"\nFound {len(article_links)} potential article links")
    if article_links:
        print("First few article links:")
        for link in article_links[:3]:
            print(f"  - {link}")
            
except Exception as e:
    print(f"Error accessing pagination page: {e}")