import requests
import time
import random
from bs4 import BeautifulSoup

# Try using requests library instead of urllib - sometimes handles things better
session = requests.Session()

# Set up session with realistic headers
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
})

def test_with_requests():
    print("Testing with requests library...")
    
    try:
        # Start with FBI homepage
        print("1. Visiting FBI homepage...")
        response = session.get('https://www.fbi.gov/', timeout=30)
        print(f"   Status: {response.status_code}, Content-Length: {len(response.content)}")
        
        time.sleep(random.uniform(3, 7))
        
        # Visit news section
        print("2. Visiting news section...")
        session.headers.update({'Referer': 'https://www.fbi.gov/'})
        response = session.get('https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news', timeout=30)
        print(f"   Status: {response.status_code}, Content-Length: {len(response.content)}")
        
        time.sleep(random.uniform(5, 12))
        
        # Try the article
        print("3. Attempting to access article...")
        session.headers.update({'Referer': 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news'})
        
        test_url = "https://www.fbi.gov/contact-us/field-offices/stlouis/news/pair-accused-of-sexually-abusing-13-year-old-boy"
        response = session.get(test_url, timeout=60)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Length: {len(response.content)}")
        
        # Check response headers
        print("   Response headers:")
        for header, value in response.headers.items():
            if header.lower() in ['content-type', 'content-encoding', 'server', 'set-cookie']:
                print(f"     {header}: {value}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        
        if title:
            print(f"   Page title: '{title.get_text().strip()}'")
        
        # Check for Akamai
        akamai_check = soup.find('p', string=lambda text: text and 'powered and protected by' in text.lower())
        if akamai_check:
            print("   ❌ Still blocked by Akamai")
        else:
            print("   ✅ Success! Content retrieved")
            paragraphs = soup.find_all('p')
            print(f"   Found {len(paragraphs)} paragraphs")
            
            for i, p in enumerate(paragraphs[:3]):
                text = p.get_text().strip()
                if text and len(text) > 10:
                    print(f"   P{i+1}: {text[:100]}...")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_with_requests()