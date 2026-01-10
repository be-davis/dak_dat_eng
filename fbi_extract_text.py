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
import argparse

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

def scrape_article_content(driver, url, max_retries=2):
    """Scrape content from a single article URL"""
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}: Loading {url}")
            driver.get(url)
            
            # Wait longer for page to load
            time.sleep(random.uniform(8, 12))
            
            print(f"  Page title: '{driver.title}'")
            print(f"  Current URL: {driver.current_url}")
            
            # Check for bot protection
            page_source = driver.page_source.lower()
            if "just a moment" in driver.title.lower() or "powered and protected by" in page_source:
                print(f"  🚨 BOT PROTECTION DETECTED!")
                print(f"  🛑 Killing script to avoid getting blocked further")
                print(f"  🔄 You can resume later by running the same command")
                raise SystemExit("Bot protection detected - script terminated")
            else:
                print(f"  ✅ No bot detection detected!")
            
            # Extract content using paragraph elements
            try:
                paragraphs = driver.find_elements(By.TAG_NAME, "p")
                print(f"  Found {len(paragraphs)} paragraph elements")
                
                article_content = ""
                for p in paragraphs:
                    text = p.text.strip()
                    if text and len(text) > 20 and not any(skip in text.lower() for skip in [
                        'powered and protected by', 'javascript is disabled', 'just a moment',
                        'enable javascript', 'please enable cookies', 'cookie policy',
                        'privacy policy', 'terms of service'
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
    parser = argparse.ArgumentParser(description='Extract text content from FBI article URLs using Selenium')
    parser.add_argument('--input_file', type=str, default='data/fbi_article_links_combined_20260102_170044.csv',
                       help='Input CSV file containing URLs (default: data/fbi_article_links_combined_20260102_170044.csv)')
    parser.add_argument('--headless', action='store_true', default=False,
                       help='Run browser in headless mode')
    parser.add_argument('--keep_open', action='store_true', default=False,
                       help='Keep browser open after scraping')
    parser.add_argument('--max_articles', type=int, default=None,
                       help='Maximum number of articles to process (for testing)')
    
    args = parser.parse_args()
    
    # Load URLs from CSV file
    try:
        df_links = pd.read_csv(args.input_file)
        print(f"Loaded CSV file: {args.input_file}")
        print(f"Columns: {list(df_links.columns)}")
        print(f"Total rows in CSV: {len(df_links)}")
        
        # Ensure we have a URL column
        if 'URL' not in df_links.columns:
            print("❌ No URL column found in CSV file")
            return
        
        # Add 'text' column if it doesn't exist
        if 'text' not in df_links.columns:
            df_links['text'] = ''
            print("✅ Added 'text' column to DataFrame")
        
        # Find where to resume - look for first empty text field
        resume_index = 0
        for i, text_val in enumerate(df_links['text']):
            if pd.isna(text_val) or text_val == '' or text_val == 'FAILED_TO_SCRAPE':
                resume_index = i
                break
        else:
            print("✅ All articles already have text extracted!")
            return
        
        print(f"🔄 Resuming from row {resume_index + 1} (URL: {df_links.iloc[resume_index]['URL']})")
        
        # Get URLs to process (starting from resume point)
        urls_to_process = df_links.iloc[resume_index:].copy()
        if args.max_articles:
            urls_to_process = urls_to_process.head(args.max_articles)
            print(f"Limited to {len(urls_to_process)} URLs for testing")
        
        print(f"URLs to process: {len(urls_to_process)}")
        
    except Exception as e:
        print(f"❌ Error loading URLs from {args.input_file}: {e}")
        return
    
    # Setup browser
    print("Setting up Chrome browser...")
    driver = setup_driver(headless=args.headless, keep_open=args.keep_open)
    
    try:
        print("Starting article content extraction...")
        
        successful_scrapes = 0
        
        for i, (idx, row) in enumerate(urls_to_process.iterrows()):
            url = row['URL']
            print(f"\n{'='*80}")
            print(f"Processing article {i + 1}/{len(urls_to_process)} (Row {idx + 1}): {url}")
            
            # Skip video or MP4 links
            if ".mp4" in url.lower() or "video-repository" in url.lower():
                print(f"  ⏭️  Skipping video/MP4 link")
                df_links.at[idx, 'text'] = 'SKIPPED_VIDEO_LINK'
                print(f"  ✅ Marked as skipped in row {idx + 1}")
                continue
            
            # Human-like delay between articles
            if i > 0:
                delay = random.uniform(10, 20)  # 10-20 seconds between articles
                print(f"Waiting {delay:.1f} seconds before next article...")
                time.sleep(delay)
            
            content = scrape_article_content(driver, url)
            
            # Update the original DataFrame with the extracted content
            if content:
                df_links.at[idx, 'text'] = content
                successful_scrapes += 1
                print(f"  ✅ Content added to row {idx + 1}")
            else:
                df_links.at[idx, 'text'] = 'FAILED_TO_SCRAPE'
                print(f"  ❌ Failed to scrape content for row {idx + 1}")
            
            success_rate = successful_scrapes/(i+1)*100
            print(f"Success rate so far: {successful_scrapes}/{i+1} ({success_rate:.1f}%)")
            
            # Save CSV every 5 articles or on the last article
            if (i + 1) % 5 == 0 or (i + 1) == len(urls_to_process):
                df_links.to_csv(args.input_file, index=False)
                print(f"💾 Saved progress to {args.input_file}")
            
            # Stop early if success rate drops too low (after at least 5 attempts)
            if i > 4 and success_rate < 20:
                print(f"⚠️  Low success rate ({success_rate:.1f}%), stopping to avoid further blocks")
                df_links.to_csv(args.input_file, index=False)
                print(f"💾 Final save to {args.input_file}")
                print(f"🔄 You can resume later by running the same command")
                break
        
        # Final save and summary
        df_links.to_csv(args.input_file, index=False)
        print(f"\n{'='*80}")
        print(f"✅ EXTRACTION COMPLETE!")
        print(f"📊 Final Results:")
        
        # Calculate statistics
        total_processed = len(urls_to_process)
        total_with_text = len(df_links[df_links['text'].notna() & (df_links['text'] != '') & (df_links['text'] != 'FAILED_TO_SCRAPE') & (df_links['text'] != 'SKIPPED_VIDEO_LINK')])
        total_failed = len(df_links[df_links['text'] == 'FAILED_TO_SCRAPE'])
        total_skipped = len(df_links[df_links['text'] == 'SKIPPED_VIDEO_LINK'])
        total_empty = len(df_links[(df_links['text'].isna()) | (df_links['text'] == '')])
        
        print(f"   - Articles processed this session: {total_processed}")
        print(f"   - Successfully scraped this session: {successful_scrapes}")
        print(f"   - Total articles with text: {total_with_text}")
        print(f"   - Total failed scrapes: {total_failed}")
        print(f"   - Total skipped (video/MP4): {total_skipped}")
        print(f"   - Total empty/pending: {total_empty}")
        print(f"   - Overall success rate: {total_with_text/len(df_links)*100:.1f}%")
        print(f"💾 Updated CSV saved to: {args.input_file}")
        
        # Show sample of extracted content
        successful_content = df_links[(df_links['text'].notna()) & (df_links['text'] != '') & (df_links['text'] != 'FAILED_TO_SCRAPE') & (df_links['text'] != 'SKIPPED_VIDEO_LINK')]
        if len(successful_content) > 0:
            avg_length = successful_content['text'].str.len().mean()
            print(f"📝 Average content length: {avg_length:.0f} characters")
            print(f"📋 Sample extracted content (first 200 chars):")
            sample_content = successful_content.iloc[-1]['text'][:200]  # Use last successful one
            print(f"   \"{sample_content}...\"")
        
        # Keep browser open for inspection if requested
        if args.keep_open:
            print(f"\n{'='*80}")
            print("🌐 Browser will stay open for inspection")
            print("Press Ctrl+C in terminal when done")
            print('='*80)
            
            try:
                while True:
                    time.sleep(10)
                    print("Browser still open... (Press Ctrl+C to close)")
            except KeyboardInterrupt:
                print("\n👋 Closing browser...")
        
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        df_links.to_csv(args.input_file, index=False)
        print(f"💾 Saved progress to {args.input_file}")
        print(f"🔄 You can resume by running the same command again")
    
    except SystemExit as e:
        print(f"\n🚨 {e}")
        df_links.to_csv(args.input_file, index=False)
        print(f"💾 Saved progress to {args.input_file}")
        print(f"🔄 Resume by running: python fbi_extract_text.py --input_file {args.input_file}")
        print(f"💡 Consider using --headless flag or waiting before resuming")
    
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()
