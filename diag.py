from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/")
    
    print("Page loaded. Detecting frame sources...")
    page.wait_for_timeout(5000)
    
    # Iterate through every frame and print its src attribute
    for i, frame in enumerate(page.frames):
        url = frame.url
        print(f"Frame {i}: {url}")
        
    browser.close()