from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from datetime import datetime

def setup_driver(headless=False, keep_open=False):
    """Setup Chrome driver with stealth options"""
    chrome_options = Options()
    
    # Make browser appear more human-like
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Additional stealth options
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set a realistic window size
    chrome_options.add_argument("--window-size=1920,1080")
    
    # User agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Headless mode option
    if headless:
        chrome_options.add_argument("--headless")
    
    # Keep browser open after script ends
    if keep_open:
        chrome_options.add_experimental_option("detach", True)
    
    # Install and setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute stealth script to hide webdriver properties
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def human_like_delay():
    """Add random human-like delays"""
    time.sleep(random.uniform(3, 8))

def scrape_article_content(driver, url, max_retries=1):
    """Scrape content from a single article URL"""
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}: Loading {url}")
            driver.get(url)
            
            # Wait longer for page to load (like the successful test)
            time.sleep(random.uniform(8, 12))
            
            print(f"  Page title: '{driver.title}'")
            print(f"  Current URL: {driver.current_url}")
            
            # Check for bot protection (like the test)
            page_source = driver.page_source.lower()
            if "just a moment" in driver.title.lower() or "powered and protected by" in page_source:
                print(f"  ⚠️  Bot protection detected, waiting longer...")
                time.sleep(random.uniform(25, 35))
                
                # Try refreshing once
                driver.refresh()
                time.sleep(random.uniform(12, 18))
                
                # Check again
                page_source = driver.page_source.lower()
                if "just a moment" in driver.title.lower() or "powered and protected by" in page_source:
                    print(f"  ❌ Still blocked after refresh, skipping...")
                    return ""
                else:
                    print(f"  ✅ Success after refresh!")
            else:
                print(f"  ✅ No bot detection detected!")
            
            # Extract content using same method as successful test
            try:
                paragraphs = driver.find_elements(By.TAG_NAME, "p")
                print(f"  Found {len(paragraphs)} paragraph elements")
                
                article_content = ""
                for p in paragraphs:
                    text = p.text.strip()
                    if text and len(text) > 20 and not any(skip in text.lower() for skip in [
                        'powered and protected by', 'javascript is disabled', 'just a moment',
                        'enable javascript', 'please enable cookies'
                    ]):
                        article_content += text + " "
                
                if len(article_content) > 200:
                    print(f"  ✅ Successfully extracted content ({len(article_content)} characters)")
                    return article_content.strip()
                else:
                    print(f"  ❌ Little content extracted ({len(article_content)} characters)")
                    
            except Exception as content_e:
                print(f"  ❌ Error extracting content: {content_e}")
                
        except Exception as e:
            print(f"  ❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(20, 30))
    
    return ""

def main():
    """Main scraping function"""
    # Load existing URLs from your previous scraping
    try:
        df_links = pd.read_csv("data/2025-12-30_1_6.csv")
        if df_links.columns[0] == '0' or 'Unnamed' in df_links.columns[0]:
            df_links.columns = ['URL', 'Empty_Content']
        
        urls = df_links['URL'].tolist()
        print(f"Loaded {len(urls)} URLs from previous scraping")
        
    except Exception as e:
        print(f"Error loading URLs: {e}")
        return
    
    # Setup browser - set keep_open=True to prevent auto-closing
    print("Setting up Chrome browser...")
    driver = setup_driver(headless=False, keep_open=True)  # Change keep_open to True
    
    try:
        # Don't visit other pages first - go straight to articles like the successful test
        print("Starting article content extraction...")
        
        # Create pandas DataFrame to store results
        df_results = pd.DataFrame(columns=['URL', 'Article_Text'])
        successful_scrapes = 0
        filename = f"data/fbi_articles_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Limit to first 5 URLs for initial testing (remove this limit for full scraping)
        test_urls = urls  # Change to urls for full scraping
        
        for i, url in enumerate(test_urls):
            print(f"\nProcessing article {i + 1}/{len(test_urls)}: {url}")
            
            # Much longer delay between articles (like human reading time)
            if i > 0:
                delay = random.uniform(30, 60)  # 30-60 seconds between articles
                print(f"Waiting {delay:.1f} seconds before next article...")
                time.sleep(delay)
            
            content = scrape_article_content(driver, url)
            
            # Add article to DataFrame immediately
            new_row = pd.DataFrame({
                'URL': [url],
                'Article_Text': [content if content else 'FAILED_TO_SCRAPE']
            })
            df_results = pd.concat([df_results, new_row], ignore_index=True)
            
            if content:
                successful_scrapes += 1
            
            success_rate = successful_scrapes/(i+1)*100
            print(f"Success rate so far: {successful_scrapes}/{i+1} ({success_rate:.1f}%)")
            
            # Save CSV every 10 articles or on the last article
            if (i + 1) % 10 == 0 or (i + 1) == len(test_urls):
                df_results.to_csv(filename, index=False)
                print(f"💾 Saved progress: {len(df_results)} articles to {filename}")
            
            # Stop early if success rate drops too low
            if i > 2 and success_rate < 50:
                print(f"⚠️  Low success rate ({success_rate:.1f}%), stopping to avoid further blocks")
                # Save final results before breaking
                df_results.to_csv(filename, index=False)
                print(f"💾 Final save: {len(df_results)} articles to {filename}")
                break
        
        # Final save (in case loop completed without hitting save interval)
        if len(df_results) > 0:
            df_results.to_csv(filename, index=False)
            print(f"\n✅ Final save: {len(df_results)} articles to {filename}")
            print(f"Successfully scraped content: {successful_scrapes}/{len(df_results)}")
        
        # Keep browser open for inspection
        print("\n" + "="*50)
        print("🌐 Browser will stay open for inspection")
        print("You can:")
        print("- Manually navigate to other articles")
        print("- Inspect the page source")
        print("- Test other URLs")
        print("- Press Ctrl+C in terminal when done")
        print("="*50)
        
        try:
            # Keep the browser open until user interrupts
            while True:
                time.sleep(10)
                print("Browser still open... (Press Ctrl+C to close)")
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")
        
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()