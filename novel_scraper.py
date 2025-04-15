# --- START OF FILE novel_scraper.py ---

import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin
import traceback

# --- !!! IMPORTANT CONFIGURATION - CHECKED FOR NOVELBIN (BUT MAY CHANGE) !!! ---

# 1. STARTING URL: The URL of the *first* chapter/page you want to scrape.
#    >>> YOU MUST CHANGE THIS TO YOUR TARGET NOVEL'S FIRST CHAPTER <<<
start_url = 'https://novelbin.com/b/example-novel-name/chapter-1' # EXAMPLE - CHANGE ME!

# 2. ENDING URL: The URL of the *last* chapter/page you want to scrape.
#    The script will stop *after* scraping this page.
#    >>> YOU MUST CHANGE THIS TO YOUR TARGET NOVEL'S LAST CHAPTER <<<
end_url = 'https://novelbin.com/b/example-novel-name/chapter-50' # EXAMPLE - CHANGE ME!

# 3. OUTPUT FILENAME: Where the combined text will be saved.
#    >>> CHANGE THIS TO A DESCRIPTIVE NAME FOR YOUR OUTPUT <<<
output_filename = 'my_scraped_novel.txt' # EXAMPLE - CHANGE ME!

# 4. CSS SELECTOR FOR NOVEL CONTENT:
#    Default is for NovelBin (#chr-content). Change if using another site or if NovelBin updates.
content_selector = '#chr-content'

# 5. CSS SELECTOR FOR THE "NEXT CHAPTER" LINK:
#    Default is for NovelBin (#next_chap). Change if using another site or if NovelBin updates.
next_page_selector = '#next_chap'

# 6. DELAY BETWEEN REQUESTS (in seconds):
#    Increase if you encounter issues (e.g., 429 errors) or get blocked. 5-10+ is recommended.
delay_between_requests = 6

# 7. HEADERS: Mimic a real browser visit. Default includes NovelBin referer.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://novelbin.com/' # May help avoid simple blocks
}

# --- END OF CONFIGURATION ---

def scrape_chapter(url):
    """Fetches and extracts text content from a single chapter URL."""
    print(f"Scraping: {url}")
    try:
        # --- Network Request ---
        response = requests.get(url, headers=headers, timeout=25) # Timeout in seconds
        # Check specifically for 404 Not Found *before* raise_for_status
        if response.status_code == 404:
             print(f"  [Error] Received 404 Not Found for URL: {url}. Chapter may not exist or URL is incorrect.")
             return None, None # Treat as scraping failure for this URL

        response.raise_for_status() # Raise error for other bad statuses (e.g., 403, 429, 5xx)

        # --- Anti-Bot Check ---
        # Simple check for common Cloudflare/JS challenge pages
        if "Just a moment..." in response.text or "Checking if the site connection is secure" in response.text:
             print(f"  [Warning] Possible Cloudflare or anti-bot page detected at {url}. Adding delay.")
             time.sleep(10) # Extra delay might sometimes help

        # --- HTML Parsing ---
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Find Content ---
        content_element = soup.select_one(content_selector)
        if not content_element:
            # If content element isn't found, treat as failure for this chapter
            print(f"  [Error] Content selector '{content_selector}' not found on {url}.")
            return None, None

        # --- Content Cleaning (Basic) ---
        # Remove common unwanted tags like scripts, styles, iframes from within the content
        unwanted_tags = content_element.find_all(['script', 'style', 'iframe'])
        for tag in unwanted_tags:
            tag.decompose() # Remove the tag and its content

        # --- Extract Text ---
        # Get text, using newline as separator between tags, and stripping extra whitespace
        chapter_text = content_element.get_text(separator='\n', strip=True)

        # --- Find Next Link ---
        next_page_element = soup.select_one(next_page_selector)

        if next_page_element and next_page_element.has_attr('href'):
            # --- A next chapter link WAS found ---
            next_page_url_relative = next_page_element['href']
            # Construct absolute URL (handles relative paths like /path/to/next or //domain/path)
            if next_page_url_relative.startswith('//'):
                 next_page_url = 'https:' + next_page_url_relative
            elif next_page_url_relative.startswith('/'):
                 next_page_url = urljoin(url, next_page_url_relative) # urljoin handles base URL context
            else:
                 next_page_url = next_page_url_relative # Assume it's already absolute

            # --- Link Validation Removed ---
            # Previous versions had a check here like:
            # base_novel_path = '/b/specific-novel-name/'
            # if base_novel_path not in next_page_url:
            #     print(f"  [Warning] URL doesn't match expected novel path...")
            #     return chapter_text, None
            # This was removed to make the script slightly more general by default.
            # The core safety depends on the next_page_selector being accurate.
            # You could add a custom check here if you only intend to scrape one specific novel path.

            # Assume the found URL is correct if the selector matched
            return chapter_text, next_page_url

        else:
            # --- No "Next Chapter" link element was found ---
            print(f"  [Info] Next page selector '{next_page_selector}' not found or has no href on {url}.")
            # Check if this is expected because we are on the target end URL
            if url == end_url:
                print("      (This is the specified end URL, so link absence is expected).")
            else:
                print("      (This might be the actual end of the novel, or the selector/page structure changed).")
            # Signal the end of this scraping path by returning None for the next URL
            return chapter_text, None

    # --- Exception Handling ---
    except requests.exceptions.Timeout:
        print(f"  [Error] Request timed out for {url}. Try increasing the timeout setting.")
        return None, None # Indicate failure
    except requests.exceptions.HTTPError as e:
         # Handles non-404 HTTP errors raised by raise_for_status()
         status_code = e.response.status_code if e.response else 'Unknown'
         reason = e.response.reason if e.response else 'Unknown'
         print(f"  [Error] HTTP Error for {url}: {status_code} {reason}")
         # Provide specific advice for common blocking codes
         if status_code == 403: print("  [Error Details] Received 403 Forbidden. The site might be blocking the script (IP, User-Agent?).")
         elif status_code == 429: print(f"  [Error Details] Received 429 Too Many Requests. Increase 'delay_between_requests' significantly (currently {delay_between_requests}s).")
         elif status_code == 503: print("  [Error Details] Received 503 Service Unavailable. Server might be overloaded. Try again later.")
         return None, None # Indicate failure
    except requests.exceptions.RequestException as e:
        # Handles other network-related errors (DNS, connection errors)
        print(f"  [Error] Network error fetching {url}: {e}")
        return None, None # Indicate failure
    except Exception as e:
        # Catch any other unexpected errors during parsing, file I/O etc.
        print(f"  [Error] An unexpected error occurred while processing {url}:")
        traceback.print_exc() # Print detailed traceback for debugging
        return None, None # Indicate failure

# --- Main Script Logic ---
if __name__ == "__main__": # Ensure this runs only when script is executed directly
    # --- Configuration Validation (Basic) ---
    if 'example-novel-website.com' in start_url or 'example-novel-name' in start_url or \
       'example-novel-website.com' in end_url or 'example-novel-name' in end_url or \
       'my_scraped_novel.txt' == output_filename :
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: You MUST change the placeholder values for     !!!")
        print("!!!        start_url, end_url, and output_filename        !!!")
        print("!!!        in the script's configuration section before   !!!")
        print("!!!        running it.                                    !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        exit(1) # Stop execution if defaults are still present

    current_url = start_url
    all_chapters_text = []
    scraped_something = False
    previous_url = None # Initialize previous_url

    print("--- Starting Novel Scraper ---")
    print(f"Start URL: {start_url}")
    print(f"End URL:   {end_url}")
    print(f"Output:    {output_filename}")
    print(f"Content Selector: {content_selector}")
    print(f"Next Page Selector: {next_page_selector}")
    print(f"Delay: {delay_between_requests} seconds")
    print("----------------------------")

    # --- Main Scraping Loop ---
    while current_url:
        # Check if the *previous* URL scraped was the intended end URL.
        if previous_url == end_url:
             print(f"\nSuccessfully scraped the target end URL ({end_url}). Stopping.")
             break

        # Safety check: Prevent infinite loops if the next URL somehow repeats
        if current_url == previous_url and previous_url is not None:
            print(f"\n[Error] Current URL ({current_url}) is the same as the previous URL. Stopping to prevent infinite loop.")
            print(f"        Check the 'Next Page Selector' ('{next_page_selector}') or website structure on page: {previous_url}")
            break

        # Scrape the current chapter
        chapter_text, next_url = scrape_chapter(current_url)

        if chapter_text is not None:
            # Successfully scraped, add separator and text
            # Separator includes URL for reference in the output file
            all_chapters_text.append(f"\n\n--- Chapter from: {current_url} ---\n\n")
            all_chapters_text.append(chapter_text)
            scraped_something = True
        else:
            # Handle failed chapter scrape (error already printed in scrape_chapter)
            print(f"  [Warning] Failed to get content for {current_url}. Skipping this chapter.")
            # Optional: Decide whether to stop entirely if one chapter fails
            # print("Stopping script due to error.")
            # break

        # Update previous_url *before* updating current_url for the next loop iteration
        previous_url = current_url
        # Prepare for the next iteration
        current_url = next_url

        # Add delay only if we are going to scrape another page
        if current_url:
            print(f"  Waiting {delay_between_requests} seconds before next request...")
            time.sleep(delay_between_requests)

    # --- Final Check After Loop ---
    # Check if the loop finished but didn't reach the end URL (e.g., link missing on last page)
    if scraped_something and previous_url != end_url:
         # This is expected if the loop finished because next_url became None
         if current_url is None:
              print(f"\n[Info] Scraping stopped. The last URL processed was {previous_url}.")
              print(f"       This might be because the 'Next Chapter' link was not found on that page,")
              print(f"       or an error occurred on subsequent chapter attempts.")
         else: # Should not happen with current logic, but good fallback
              print(f"\n[Warning] Script finished unexpectedly. Last processed URL: {previous_url}. Target end URL: {end_url}")

    # --- Save the combined text to a file ---
    if all_chapters_text:
        num_chapters = len(all_chapters_text) // 2 # Each chapter adds 2 elements (separator + text)
        print(f"\nWriting {num_chapters} scraped chapter(s) to {output_filename}...")
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                # Join the collected strings. Add a final newline for good measure.
                f.write("\n".join(all_chapters_text) + "\n")
            print("--- Scraping Process Finished ---")
            print(f"Novel text saved to: {os.path.abspath(output_filename)}")
        except IOError as e:
            print(f"[Error] Failed to write to output file {output_filename}: {e}")
        except Exception as e:
            print(f"[Error] An unexpected error occurred during file writing: {e}")

    elif not scraped_something:
        print("\n--- No content was successfully scraped ---")
        print("Please check your configuration (URLs, selectors), network connection,")
        print("and ensure the target website structure hasn't changed or isn't blocking the script.")

# --- END OF FILE novel_scraper.py ---
