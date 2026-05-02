from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
from datetime import datetime
import argparse

# Constants
BASE_URL = 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news/@@castle.cms.querylisting/9e361bf3a4174df2ad8c0e1a83906cd4?page='
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
APPROX_NUM_PAGES = 10
START_PAGE = 17
ALL_ARTICLES = {}

# Initial setup (unchanged)
url = 'https://www.fbi.gov/investigate/violent-crime/vcac/violent-crimes-against-children-news'
req = Request(url, headers=HEADERS)
webpage = urlopen(req).read()
page_soup = BeautifulSoup(webpage, 'html.parser')
total_articles = int(page_soup.find('p', {'class': 'right'}).get_text()[9:14])

# Functions (unchanged)
def get_page_links(page_num, max_retries=3):
    url = BASE_URL + str(page_num)
    
    for attempt in range(max_retries):
        try:
            # Add delay between requests (2-5 seconds)
            delay = random.uniform(2, 5)
            print(f"Waiting {delay:.1f} seconds before requesting page {page_num}...")
            time.sleep(delay)
            
            req = Request(url, headers=HEADERS)
            webpage = urlopen(req).read()
            page_soup = BeautifulSoup(webpage, 'html.parser')
            news_links = page_soup.find_all('a', {'class': 'button'}, href=True)
            all_page_links = [a['href'] for a in news_links]
            return all_page_links
            
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                wait_time = (attempt + 1) * 30  # Exponential backoff: 30, 60, 90 seconds
                print(f"Rate limited on page {page_num}, attempt {attempt + 1}. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error on page {page_num}, attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)  # Wait 10 seconds for other errors
                    
    print(f"Failed to get page {page_num} after {max_retries} attempts")
    return []

def get_all_links(start_page=START_PAGE, approx_num_pages=APPROX_NUM_PAGES):
    # Create pandas DataFrame to store results (similar to selenium_scraper.py)
    df_links = pd.DataFrame(columns=['URL', 'Page_Source'])
    failed_pages = []
    
    # Create timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/fbi_article_links_{timestamp}.csv'
    
    total_links_collected = 0
    
    for page_num in range(start_page, start_page + approx_num_pages):
        print(f"\n--- Processing page {page_num} ---")
        
        page_links = get_page_links(page_num=page_num)
        
        if page_links:
            # Add each link to DataFrame immediately (like selenium approach)
            for link in page_links:
                new_row = pd.DataFrame({
                    'URL': [link],
                    'Page_Source': [page_num]
                })
                df_links = pd.concat([df_links, new_row], ignore_index=True)
            
            total_links_collected += len(page_links)
            print(f"Got {len(page_links)} links from page {page_num}")
            print(f"TOTAL LINKS SO FAR: {total_links_collected}")
            
            # Save progress every 3 pages (more frequent saves like selenium approach)
            if (page_num - start_page + 1) % 3 == 0 or (page_num == start_page + approx_num_pages - 1):
                # Remove duplicates before saving (keep first occurrence)
                df_unique = df_links.drop_duplicates(subset=['URL'], keep='first')
                df_unique.to_csv(filename, index=False)
                print(f"💾 Saved progress: {len(df_unique)} unique links to {filename}")
        else:
            failed_pages.append(page_num)
            print(f"❌ Failed to get links from page {page_num}")
            # Save progress even on failure
            if len(df_links) > 0:
                df_unique = df_links.drop_duplicates(subset=['URL'], keep='first')
                df_unique.to_csv(filename, index=False)
                print(f"💾 Saved progress after failure: {len(df_unique)} unique links to {filename}")
    
    # Final save with deduplication
    if len(df_links) > 0:
        df_unique = df_links.drop_duplicates(subset=['URL'], keep='first')
        df_unique.to_csv(filename, index=False)
        
        print(f"\n✅ FINAL RESULTS:")
        print(f"Total links collected: {total_links_collected}")
        print(f"Unique links: {len(df_unique)}")
        print(f"Failed pages: {failed_pages}")
        print(f"Final save: {filename}")
        
        return df_unique['URL']
    else:
        print(f"\n❌ No links collected")
        return pd.Series(dtype=str)

# Modified get_articles with 3-minute timeout per article


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape FBI article links with configurable page range')
    parser.add_argument('--start_page', type=int, default=START_PAGE,
                       help=f'Starting page number (default: {START_PAGE})')
    parser.add_argument('--approx_num_pages', type=int, default=APPROX_NUM_PAGES,
                       help=f'Approximate number of pages to scrape (default: {APPROX_NUM_PAGES})')
    
    args = parser.parse_args()
    
    print(f"Starting scrape from page {args.start_page} for {args.approx_num_pages} pages")
    print(f"Total page range: {args.start_page} to {args.start_page + args.approx_num_pages - 1}")
    

    get_all_links(start_page=args.start_page, approx_num_pages=args.approx_num_pages)


            
