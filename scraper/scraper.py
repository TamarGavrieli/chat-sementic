import requests
import json
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TabuVerdictScraper:
    def __init__(self, output_dir="downloads"):
        self.base_url = "https://www.gov.il"
        self.search_url = "https://www.gov.il/he/Departments/DynamicCollectors/tabu_search_verdict?skip=0"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })




    def save_data(self, documents):
        data_file = self.output_dir / "documents_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        return data_file

    def download_all(self, documents):
        if not documents:
            print("[!] No documents to download.")
            return 0, 0

        driver = self._init_download_driver()
        downloaded = 0
        failed = 0

        try:
            for doc in documents:
                url = doc["url"]
                print(f"[DOWNLOAD] Opening in browser: {url}")
                try:
                    driver.get(url)
                    time.sleep(5)
                    downloaded += 1
                except Exception as e:
                    print(f"[ERROR] Failed to open {url} in browser: {e}")
                    failed += 1

        finally:
            driver.quit()

        print(f"[INFO] Finished downloads. Downloaded={downloaded}, Failed={failed}")
        return downloaded, failed


    def run(self, max_pdf=50, max_word=50):
        documents = self.gather_data(max_pdf=max_pdf, max_word=max_word)

        if not documents:
            return

        self.save_data(documents)

        self.download_all(documents)
        
        
    def gather_data(self, max_pdf: int = 50, max_word: int = 50): 
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        documents = []
        seen_urls = set()
        pdf_count = 0
        word_count = 0

        try:
            max_pages = 20 

            for page_idx in range(max_pages):
                if pdf_count >= max_pdf and word_count >= max_word:
                    break

                skip = page_idx * 20
                if "skip=" in self.search_url:
                    base = self.search_url.split("skip=")[0]
                    page_url = f"{base}skip={skip}"
                else:
                    page_url = self.search_url

                print(f"[INFO] Loading search page with skip={skip}: {page_url}")
                driver.get(page_url)
                time.sleep(5)

                if page_idx == 0:
                    with open("page_source.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)

                links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
                print(f"[DEBUG] Found {len(links)} <a> tags with href on page skip={skip}")

                for link in links:
                    href = link.get_attribute("href")
                    text = (link.text or "").strip()

                    if not href:
                        continue
                    if (
                        "free-justice.openapi.gov.il" not in href
                        or "SearchPredefinedApi/Documents" not in href
                    ):
                        continue
                    kind = None
                    if "/Documents/TabuSrc/" in href:
                        kind = "word"
                    elif "/Documents/Tabu/" in href:
                        kind = "pdf"
                    else:
                        continue
                    if kind == "pdf" and pdf_count >= max_pdf:
                        continue
                    if kind == "word" and word_count >= max_word:
                        continue
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    if kind == "pdf":
                        pdf_count += 1
                        idx = pdf_count
                        filename = f"pdf_{idx:03d}.pdf"
                    else:  # word
                        word_count += 1
                        idx = word_count
                        filename = f"word_{idx:03d}.docx"

                    doc_number = len(documents) + 1

                    documents.append({
                        "doc_number": doc_number,
                        "url": href,
                        "name": text or filename,
                        "filename": filename,
                        "kind": kind,
                    })

                    print(f"[DOC] #{doc_number} kind={kind} ({filename}) : {href} | text='{text}'")
                    if pdf_count >= max_pdf and word_count >= max_word:
                        break

            print(f"[INFO] Total documents gathered: {len(documents)} "
                  f"(pdf={pdf_count}, word={word_count})")

        except Exception as e:
            import traceback
            traceback.print_exc()

        finally:
            driver.quit()

        return documents

    
    def _init_download_driver(self) -> webdriver.Chrome:
        download_dir = str(self.output_dir.resolve())
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        prefs = {
            "download.default_directory": download_dir,   
            "download.prompt_for_download": False,             
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,        
        }
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=chrome_options)
        return driver




