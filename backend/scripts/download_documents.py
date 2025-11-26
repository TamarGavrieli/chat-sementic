from pathlib import Path
import sys
import os

print("[DEBUG] download_documents.py started running")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
print(f"[DEBUG] PROJECT_ROOT = {PROJECT_ROOT}")
sys.path.append(str(PROJECT_ROOT))
print(f"[DEBUG] sys.path includes project root? {PROJECT_ROOT in list(map(Path, sys.path))}")

try:
    from scraper.scraper import TabuVerdictScraper
    print("[DEBUG] Imported TabuVerdictScraper successfully")
except Exception as e:
    print("[ERROR] Failed to import TabuVerdictScraper:", e)
    raise


def main():
    print("[INFO] Starting download_documents main()")
    raw_dir = PROJECT_ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Raw data directory: {raw_dir}")
    existing_files = list(raw_dir.glob("*.*"))
    if existing_files:
        print(f"[INFO] Cleaning existing files from {raw_dir} ({len(existing_files)} files)...")
        for p in existing_files:
            try:
                p.unlink()
            except Exception as e:
                print(f"[WARN] Failed to delete {p}: {e}")
    scraper = TabuVerdictScraper(output_dir=str(raw_dir))
    max_pdf = 50
    max_word = 50

    print(f"[*] Gathering up to {max_pdf} PDF and {max_word} Word documents...")
    documents = scraper.gather_data(max_pdf=max_pdf, max_word=max_word)
    print(f"[DEBUG] gather_data returned {len(documents) if documents else 0} documents")
    if not documents:
        print("[!] No documents found.")
        return

    print(f"[*] Found {len(documents)} documents. Saving metadata...")
    scraper.save_data(documents)
    print("[*] Downloading files...")
    downloaded, failed = scraper.download_all(documents)
    print(f"[✓] Done! Downloaded: {downloaded}, Failed: {failed}")
    print(f"[i] Files saved into: {raw_dir}")


if __name__ == "__main__":
    print("[DEBUG] __name__ == '__main__', calling main()")
    main()
