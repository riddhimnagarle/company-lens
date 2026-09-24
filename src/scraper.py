import os
import time
import urllib.robotparser
from urllib.parse import urljoin
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class CompanyScraper:
    def __init__(self, base_url: str, output_dir: str = "data/raw_scraped"):
        self.base_url = base_url.rstrip("/")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self._check_robots_txt()

    def _check_robots_txt(self):
        """1. Respects robots.txt before crawling."""
        robots_url = urljoin(self.base_url, "/robots.txt")
        print(f"[ROBOTS.TXT] Checking crawl permissions at: {robots_url}")
        try:
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
            print("[ROBOTS.TXT] Successfully parsed permissions.")
        except Exception as e:
            print(f"[ROBOTS.TXT] Notice: robots.txt not reachable ({e}). Proceeding politely.")

    def is_allowed(self, url: str) -> bool:
        """Verifies if robots.txt allows this specific page."""
        try:
            allowed = self.robot_parser.can_fetch(HEADERS["User-Agent"], url)
            return True if allowed is None else allowed
        except Exception:
            return True

    def fetch_page(self, url: str, max_retries: int = 3) -> str:
        """
        2. Retries & Graceful Failure Handling:
        Never crashes on network drops or 404 errors.
        """
        if not self.is_allowed(url):
            print(f"[SKIP] Blocked by robots.txt: {url}")
            return ""

        for attempt in range(1, max_retries + 1):
            try:
                print(f"[FETCH] (Attempt {attempt}/{max_retries}) Downloading: {url}")
                time.sleep(1.0)  # Polite crawl delay
                
                response = requests.get(url, headers=HEADERS, timeout=10)
                
                # Graceful failure handling on missing pages
                if response.status_code == 404:
                    print(f"[WARN] 404 Not Found on {url} - Skipping gracefully.")
                    return ""
                
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.RequestException as e:
                print(f"[WARN] Network issue on {url}: {e}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 2s, 4s backoff
                    print(f"[RETRY] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"[FAIL] Retries exhausted for {url}. Skipping page.")
                    return ""
        return ""

    def clean_html(self, html_content: str) -> tuple[str, str]:
        """
        3. Strips scripts, styles, headers, menus, and footers.
        """
        if not html_content:
            return "", ""
            
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Page"
        
        # Decompose non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
            tag.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        return title, "\n".join(clean_lines)

    def scrape_company(self, pages: dict[str, str]) -> dict[str, str]:
        """
        4. Scrapes all target pages and writes them to data/raw_scraped/ with metadata.
        """
        saved_files = {}
        scrape_date = datetime.now().strftime("%Y-%m-%d")
        
        print("\n=======================================================")
        print(f"  Starting Multi-Page Scrape for: {self.base_url}")
        print("=======================================================\n")
        
        for page_type, path in pages.items():
            full_url = urljoin(self.base_url, path)
            print(f"---> Processing: [{page_type.upper()}] from {full_url}")
            
            raw_html = self.fetch_page(full_url)
            if not raw_html:
                print(f"[-] No text retrieved for {page_type}.\n")
                continue
                
            title, clean_text = self.clean_html(raw_html)
            
            if len(clean_text) < 100:
                print(f"[WARN] Text suspiciously short ({len(clean_text)} chars). Skipping.\n")
                continue

            # Official metadata header for RAG citations
            file_content = (
                f"SOURCE_URL: {full_url}\n"
                f"PAGE_TYPE: {page_type}\n"
                f"SCRAPE_DATE: {scrape_date}\n"
                f"TITLE: {title}\n"
                f"========================================\n\n"
                f"{clean_text}\n"
            )
            
            filename = f"{page_type}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_content)
                
            print(f"[OK] Saved {len(clean_text)} characters to: {filepath}\n")
            saved_files[page_type] = filepath
            
        return saved_files


if __name__ == "__main__":
    company_url = "https://posthog.com"
    target_pages = {
        "about": "/about",
        "careers": "/careers",
        "blog": "/blog",
        "changelog": "/changelog"
    }
    
    scraper = CompanyScraper(base_url=company_url)
    results = scraper.scrape_company(target_pages)
    
    print("=======================================================")
    print(f"SCRAPING COMPLETE! Successfully created {len(results)} clean data files:")
    for p_type, path in results.items():
        print(f"  - {p_type.capitalize()}: {path}")
    print("=======================================================")