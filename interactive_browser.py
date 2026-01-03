from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_interactive_browser():
    """Setup browser that stays open for manual interaction"""
    chrome_options = Options()
    
    # Stealth options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Keep browser open after script ends
    chrome_options.add_experimental_option("detach", True)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Hide automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

if __name__ == "__main__":
    print("🌐 Starting interactive browser...")
    driver = setup_interactive_browser()
    
    # Start with a test article
    test_url = "https://www.fbi.gov/contact-us/field-offices/stlouis/news/pair-accused-of-sexually-abusing-13-year-old-boy"
    print(f"Loading test article: {test_url}")
    driver.get(test_url)
    
    print("\n" + "="*60)
    print("🎉 Browser is ready!")
    print("The browser will stay open even after this script ends.")
    print("You can:")
    print("- Navigate to any FBI article URLs")
    print("- Test different pages manually") 
    print("- Inspect elements and content")
    print("- Close the browser window when done")
    print("="*60)
    
    # Script ends, but browser stays open due to detach=True