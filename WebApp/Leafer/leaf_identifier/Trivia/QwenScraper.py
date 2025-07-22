from playwright.sync_api import sync_playwright
import random
import time
from .promptGen import generate_trivia_prompt

prompt=generate_trivia_prompt()
def scrape_with_input():
    with sync_playwright() as p:
        # Launch browser with persistent context to mimic a real user
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = p.chromium.launch_persistent_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            user_data_dir="./user_profile",  # stores cookies/cache
            headless=False
        )
        page = context.new_page()

        # Stealth script to remove navigator.__proto__.webdriver flag
        page.add_init_script("""
            delete navigator.__proto__.webdriver;
        """)

        # Go to the target URL
        page.goto("https://chat.qwen.ai/")    
        selector = r'img.h-\[2rem\].w-\[2rem\].rounded-full.object-cover[alt="User profile"]'
        
    # Check if the image exists
        # time.sleep(1000000)
        page.wait_for_selector("#chat-input")
        if page.locator(selector).is_visible(timeout=30000):
                print("✅Logged in ")
                page.wait_for_selector("#chat-input")
                page.fill('#chat-input', prompt+"dont output anything but the trivia facts.")
                page.press("#chat-input", "Enter")
               
                page.wait_for_selector("#send-message-button",timeout=650000000)
                
                items = page.locator("#response-content-container > div.svelte-1c06zsf > ol > li")
                # Get the number of items
                count = items.count()
                # Create a list of text from each item
                item_list = [items.nth(i).inner_text() for i in range(count)]

                print(item_list)
                print("done")
        else:
            print("no login")
            # Click login button
            page.click("button[aria-label='Log in']")

            # Wait for Google login then click it        
            page.wait_for_selector("button:has-text('Continue with Google')", timeout=10000)
            print("waited for google")            
            page.click("button:has-text('Continue with Google')")          
            print("clicked google")
            
            
            try:     
                    page.wait_for_selector("#chat-input", state="visible", timeout=30000)
                    print("Now Logged In")
                    page.wait_for_selector("#chat-input")
                    page.fill('#chat-input', prompt+"dont output anything but the trivia facts.")
                    page.press("#chat-input", "Enter")
                    page.wait_for_selector("#send-message-button",timeout=650000000)
                        
                    items = page.locator("#response-content-container > div.svelte-1c06zsf > ol > li")
                    # Get the number of items
                    count = items.count()
                    # Create a list of text from each item
                    item_list = [items.nth(i).inner_text() for i in range(count)]

                    print(item_list)
            except:     
                    print("logging in")

                    # Wait for email page then fill it 
                    page.wait_for_selector('#identifierId')
                    page.fill('#identifierId', 'jauyboy.14@gmail.com')
                    time.sleep(10)
                    print("sleeped 10")

                    # Click next 
                    page.wait_for_selector("#identifierNext")
                    page.click("#identifierNext")


                    page.fill("input[type=password][name=Passwd]", 'G2STLKM.N1')
                    page.press("input[type=password][name=Passwd]", "Enter")

                    page.wait_for_selector("#chat-input")
                    page.fill('#chat-input', prompt+"dont output anything but the trivia facts.")
                    page.press("#chat-input", "Enter")
                    page.wait_for_selector("#send-message-button",timeout=650000000)
                        
                    items = page.locator("#response-content-container > div.svelte-1c06zsf > ol > li")
                    # Get the number of items
                    count = items.count()
                    # Create a list of text from each item
                    item_list = [items.nth(i).inner_text() for i in range(count)]

                    print(item_list)
                    print("done")
                
                
        context.close()
    return item_list
# try :
#     print(scrape_with_input())
# except:
#     print("Enter prompt to the LLM :",prompt)
#     print("---------------------------------------------------------------------")
#     from .Local_LLM_Zeph import generate_trivia
#     import io
#     #for the input prompt
#     lines = []
#     trivia_string = generate_trivia(prompt)
#     lines = [line.strip() for line in trivia_string.split('\n') if line.strip()]
#     print(lines)

    