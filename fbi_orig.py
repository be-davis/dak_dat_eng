#%%
from urllib.request import Request, urlopen, HTTPCookieProcessor, build_opener
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime
import random
import gzip
import io
import http.cookiejar

# Constants
BASE_URL = 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news/@@castle.cms.querylisting/9e361bf3a4174df2ad8c0e1a83906cd4?page='

# Rotate between different User-Agent strings for article scraping only
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

def get_article_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news'
    }p original headers for link discovery (since it works)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def initialize_session():
    """Initialize session by visiting the main FBI page first"""
    global SESSION_INITIALIZED
    if SESSION_INITIALIZED:
        return
    
    print("Initializing session by visiting main FBI page...")
    try:
        main_url = 'https://www.fbi.gov/'
        req = Request(main_url, headers=HEADERS)
        response = opener.open(req, timeout=30)
        
        # Just read and discard the response
        response.read()
        SESSION_INITIALIZED = True
        print("Session initialized successfully")
        
        # Wait a bit before continuing
        time.sleep(random.uniform(3, 7))
        
    except Exception as e:
        print(f"Session initialization failed: {e}")
        SESSION_INITIALIZED = False
cookie_jar = http.cookiejar.CookieJar()
cookie_processor = HTTPCookieProcessor(cookie_jar)
opener = build_opener(cookie_processor)

# Global session state
SESSION_INITIALIZED = False
APPROX_NUM_PAGES = 2
START_PAGE = 1
ALL_ARTICLES = {}

# Initial setup (unchanged)
url = 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news'
req = Request(url, headers=HEADERS)
webpage = urlopen(req).read()
page_soup = BeautifulSoup(webpage, 'html.parser')
total_articles = int(page_soup.find('p', {'class': 'right'}).get_text()[9:14])

# Functions (unchanged)
def get_page_links(page_num):
    url = BASE_URL + str(page_num)
    req = Request(url, headers=HEADERS)
    webpage = urlopen(req).read()
    page_soup = BeautifulSoup(webpage, 'html.parser')
    news_links = page_soup.find_all('a', {'class': 'button'}, href=True)
    all_page_links = [a['href'] for a in news_links]
    return all_page_links

def get_all_links():
    all_links = []
    for page_num in range(START_PAGE, START_PAGE + APPROX_NUM_PAGES):
        try:
            page_links = get_page_links(page_num=page_num)
            all_links += page_links
            print("LENGTH ALL LINKS " f"{len(all_links)}")
        except Exception as e:
            print(f'scrape error on page {page_num}: {e}')
            continue
    return all_links

# Modified get_articles with 3-minute timeout per article
def get_articles():
    all_links = get_all_links()
    print("LENGTH ALL LINKS " f"{len(all_links)}")
    
    for i, url in enumerate(all_links):
        if i == len(all_links) - 3:  # Stop 3 articles before the end (your original logic)
            break
        print(f"Processing article {i + 1}/{len(all_links)}: {url}")
        
        try:
            # Initialize session on first request
            initialize_session()
            
            # Much longer delay between requests (simulate human reading time)
            if i > 0:  # Don't delay on first article
                read_time = random.uniform(45, 90)  # 45-90 seconds between articles
                print(f"Waiting {read_time:.1f} seconds before next request...")
                time.sleep(read_time)
            
            # Use session-based request with cookies
            headers = get_article_headers()
            req = Request(url, headers=headers)
            start_time = time.time()
            
            # Use the session opener instead of urlopen
            response = opener.open(req, timeout=60)
            
            # Handle compressed content properly
            content = response.read()
            if response.info().get('Content-Encoding') == 'gzip':
                content = gzip.decompress(content)
            
            # Decode content with proper encoding
            try:
                html_content = content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1 if utf-8 fails
                html_content = content.decode('latin-1', errors='replace')
            
            # Check elapsed time after fetching
            elapsed_time = time.time() - start_time
            if elapsed_time > 180:  # If somehow took longer than 3 minutes
                print(f"Article {url} took too long ({elapsed_time:.2f}s), skipping...")
                continue
            
            page_soup = BeautifulSoup(html_content, 'html.parser')
            
            # Debug: Check if we got the right page
            title = page_soup.find('title')
            if title:
                page_title = title.get_text().strip()
                print(f"Page title: {page_title}")
                if "powered and protected" in page_title.lower() or not page_title:
                    print("WARNING: Got Akamai protection page instead of article content")
                    print("This article is protected by bot detection. Skipping...")
                    continue
            
            # Check if we got an Akamai protection page
            akamai_check = page_soup.find('p', string=lambda text: text and 'powered and protected by' in text.lower())
            if akamai_check:
                print("WARNING: Detected Akamai bot protection. Trying longer delay...")
                time.sleep(random.uniform(30, 60))  # Much longer delay
                
                # Try once more with different headers
                try:
                    headers2 = get_article_headers()
                    headers2['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                    req2 = Request(url, headers=headers2)
                    response2 = opener.open(req2, timeout=60)  # Use session opener
                    
                    content2 = response2.read()
                    if response2.info().get('Content-Encoding') == 'gzip':
                        content2 = gzip.decompress(content2)
                    
                    try:
                        html_content2 = content2.decode('utf-8')
                    except UnicodeDecodeError:
                        html_content2 = content2.decode('latin-1', errors='replace')
                    
                    page_soup = BeautifulSoup(html_content2, 'html.parser')
                    
                    # Check again for Akamai protection
                    akamai_check2 = page_soup.find('p', string=lambda text: text and 'powered and protected by' in text.lower())
                    if akamai_check2:
                        print("Still getting Akamai protection after retry. Skipping...")
                        continue
                    else:
                        print("Retry successful - got past Akamai protection!")
                        
                except Exception as retry_e:
                    print(f"Retry failed: {retry_e}")
                    continue
            
            # Remove the debug print and breakpoint for normal operation
            # print(page_soup)  
            # breakpoint()
            p_list = page_soup.find_all('p')
            st = ''
            article_content_found = False
            for p in p_list:
                text = p.get_text().strip()
                # Skip "powered and protected by" and other generic content
                if text and not any(skip_phrase in text.lower() for skip_phrase in [
                    'powered and protected by',
                    'javascript is disabled',
                    'enable javascript',
                    'please enable cookies'
                ]):
                    st += text + " "
                    article_content_found = True
            
            st = st.strip().replace("\n", " ")
            
            if not article_content_found or len(st) < 100:
                print(f"WARNING: Little or no article content found. Content length: {len(st)}")
                print(f"Sample content: {st[:200]}...")
                continue
                
            ALL_ARTICLES[url] = st
            print(f"ARTICLE TEXT LENGTH: {len(st)}")
            print(f"Successfully scraped article {i + 1}")
            
        except Exception as e:
            if "401" in str(e) or "Unauthorized" in str(e):
                print(f"401 Unauthorized error for {url}. Trying with longer delay...")
                # If we get 401, wait longer and try once more
                time.sleep(random.uniform(15, 25))
                try:
                    req = Request(url, headers=get_article_headers())
                    response = opener.open(req, timeout=60)  # Use session opener
                    
                    # Handle compressed content properly for retry
                    content = response.read()
                    if response.info().get('Content-Encoding') == 'gzip':
                        content = gzip.decompress(content)
                    
                    # Decode content with proper encoding
                    try:
                        html_content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        html_content = content.decode('latin-1', errors='replace')
                    
                    page_soup = BeautifulSoup(html_content, 'html.parser')
                    p_list = page_soup.find_all('p')
                    st = ''
                    for p in p_list:
                        text = p.get_text().strip()
                        st += text
                        st = st.replace("\n", "")
                    ALL_ARTICLES[url] = st
                    print(f"Retry successful for article {i + 1}")
                except Exception as retry_e:
                    print(f"Retry also failed for {url}: {retry_e}")
                    continue
            else:
                print(f"Scrape error for {url}: {e}")
                continue
    
    # Save to CSV with proper column structure
    filename = f"data/{datetime.now().strftime('%Y-%m-%d')}_{START_PAGE}_{START_PAGE+APPROX_NUM_PAGES}.csv"
    
    # Create DataFrame with two columns: 'URL' and 'Article_Text'
    df = pd.DataFrame(list(ALL_ARTICLES.items()), columns=['URL', 'Article_Text'])
    df.to_csv(filename, index=False)
    print(f"Saved {len(ALL_ARTICLES)} articles to {filename}")
    print(f"CSV format: URL column and Article_Text column")
get_articles()
#%%
if __name__ == '__main__':
    get_articles()

#%%
import pandas as pd
pd.read_csv("data/2025-12-30_1_6.csv")
#%%