# Light Novel Scraper

A Python script designed to scrape text content from chapter-based online novel websites, automating the process of navigating from a starting chapter to an ending chapter and saving the combined text.

**⚠️ IMPORTANT DISCLAIMER ⚠️**

*   **Check Website Terms:** Always check the target website's `robots.txt` file and Terms of Service before using this script. Scraping may be against their terms.
*   **Copyright:** Downloading copyrighted material without permission is illegal in most jurisdictions. This script is provided for educational purposes only. **You are solely responsible for using this script legally and ethically.**
*   **Website Changes:** Websites frequently change their structure. This script (including the default NovelBin selectors) will likely break if the target website updates its HTML layout, requiring updates to the CSS selectors.
*   **Rate Limiting/Blocking:** Running the script too frequently or too quickly can lead to your IP address being blocked by the website. Use the `delay_between_requests` setting responsibly.

## Features

*   Scrapes novel chapters sequentially from a defined start URL to an end URL.
*   Automatically finds and follows the "Next Chapter" link on each page.
*   Extracts the primary text content from each chapter page.
*   Combines the text from all scraped chapters into a single output `.txt` file.
*   Configurable CSS selectors to adapt to different website structures (defaults set for NovelBin).
*   Configurable delay between requests to avoid overloading the server or getting blocked.
*   Basic error handling for common network issues (Timeouts, HTTP errors like 404).
*   Includes `User-Agent` header to mimic a browser visit.
*   Includes basic check for Cloudflare/JS challenge pages (adds delay, but may not bypass).
*   Adds chapter separators to the output file for readability.
*   Includes a startup check to prevent running with default placeholder URLs/filename.

## Prerequisites

*   **Python 3.x** (Recommended: 3.7+) - Download from [python.org](https://www.python.org/)
*   **pip** (Python package installer - usually included with Python 3)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git # Replace with your repo URL
    cd your-repo-name
    ```
    *Alternatively, download the ZIP file from GitHub and extract it.*

2.  **Install required Python libraries:**
    ```bash
    pip install requests beautifulsoup4
    ```
    *(Consider creating a `requirements.txt` file for easier dependency management)*

## Configuration (Crucial!)

This script requires configuration before its first run. Edit the `novel_scraper.py` file and modify the variables in the configuration section near the top.

**Default Settings (NovelBin):**
The script comes with default CSS selectors (`content_selector` and `next_page_selector`) that are configured for **NovelBin.com** *(as of the last update to this script)*. These might need updating if NovelBin changes its website structure.

**Required Configuration (Must Be Changed):**
You **MUST** always set the following for your specific scraping task:

*   `start_url`: (String) The full URL of the *first* chapter you want to scrape from the specific novel. **Replace the placeholder value.**
    ```python
    # --- EXAMPLE - MUST BE CHANGED FOR YOUR NOVEL ---
    start_url = 'https://novelbin.com/b/your-novel-name/chapter-1'
    ```
*   `end_url`: (String) The full URL of the *last* chapter you want to scrape from that novel. The script stops *after* scraping this chapter. **Replace the placeholder value.**
    ```python
    # --- EXAMPLE - MUST BE CHANGED FOR YOUR NOVEL ---
    end_url = 'https://novelbin.com/b/your-novel-name/chapter-50'
    ```
*   `output_filename`: (String) The desired name for the output text file (e.g., `my_novel.txt`). **Replace the placeholder value.**
    ```python
    output_filename = 'my_novel_chapters_1_to_50.txt'
    ```
    *(The script includes a check to prevent running if these default placeholder values are detected).*

**Optional Configuration / Adapting to Other Sites:**
If you want to scrape a different website, OR if the NovelBin structure changes, you will likely need to change these:

*   `content_selector`: (String) **The CSS Selector for the HTML element containing the main novel text.**
    *   **How to find:** Use your browser's "Inspect Element" tool on a chapter page to find the unique ID or class of the `div`, `article`, etc., holding the text.
    ```python
    # --- Default for NovelBin (MAY NEED UPDATING) ---
    content_selector = '#chr-content'
    ```
*   `next_page_selector`: (String) **The CSS Selector for the link (`<a>` tag) that points to the *next* chapter.**
    *   **How to find:** Use "Inspect Element" on the "Next Chapter" link to find its unique ID, class, or other attributes.
    ```python
    # --- Default for NovelBin (MAY NEED UPDATING) ---
    next_page_selector = '#next_chap'
    ```
*   `delay_between_requests`: (Integer/Float) Seconds to pause between requests. **Increase if you get `429 Too Many Requests` errors.** Values from 5 to 15+ seconds are recommended depending on the site.
    ```python
    delay_between_requests = 6 # Default setting
    ```
*   `headers`: (Dictionary) Can be modified if needed, but the default `User-Agent` is usually sufficient. Changing the `Referer` might be necessary for other sites.

## Usage

1.  Ensure you have configured the script (changed `start_url`, `end_url`, `output_filename`).
2.  Open your terminal or command prompt.
3.  Navigate to the directory where you saved `novel_scraper.py`.
4.  Run the script using Python:
    ```bash
    python novel_scraper.py
    ```
5.  The script will print its progress and any warnings or errors.

## Output

Upon successful completion, a text file (named according to `output_filename`) will be created in the same directory. This file will contain the concatenated text of all scraped chapters, with separators like `--- Chapter from: [URL] ---`.

## Troubleshooting

*   **Script exits immediately with ERROR:** You forgot to change the placeholder values for `start_url`, `end_url`, or `output_filename`.
*   **Script fails immediately (Python errors):** Check Python installation and required libraries (`pip show requests beautifulsoup4`).
*   **`403 Forbidden` or `429 Too Many Requests` errors:** Increase `delay_between_requests` significantly (10-20 seconds or more). The site might be blocking you based on request frequency or headers.
*   **No text scraped / Empty output file / `Content selector... not found` error:**
    *   The CSS selector (`content_selector`) is likely incorrect for the website or has changed. Re-inspect the page structure carefully using browser dev tools.
    *   The website might require JavaScript to load content (this script won't work easily).
*   **Script stops early / `Next page selector... not found` error:**
    *   The CSS selector (`next_page_selector`) is likely incorrect or has changed. Re-inspect the "Next Chapter" link.
    *   You might have reached the actual last chapter available on the site, or the link is missing/broken on that specific page.
*   **`404 Not Found` error:** The specific chapter URL being requested doesn't exist on the server (could be a typo in the URL generated *by the website*, or the chapter was removed). The script should skip this chapter and attempt to continue if a next link is found later.
*   **Other Python errors (`AttributeError`, `TypeError`, etc.):** Often caused by selectors failing unexpectedly on a particular page. Note the URL being scraped when the error occurs and inspect that page's HTML structure for differences.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
