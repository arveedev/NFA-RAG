from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/")
    
    print("Page loaded. Waiting 10 seconds for frames to populate...")
    page.wait_for_timeout(10000)
    
    # Iterate through every frame on the page
    for i, frame in enumerate(page.frames):
        print(f"Saving content for Frame {i}...")
        try:
            content = frame.content()
            filename = f"frame_{i}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Could not save frame {i}: {e}")
            
    print("Done! Check your folder for files named frame_0.html, frame_1.html, etc.")
    browser.close()