from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.append(str(BACKEND_DIR))

from app.ingestion.loaders import load_all_documents


def main():
    raw_dir = PROJECT_ROOT / "data" / "raw"
    docs = load_all_documents(raw_dir)
    print(f"Loaded {len(docs)} docs")
    for d in docs[:3]:
        print("----")
        print(d["path"].name)
        print(d["content"][:300])


if __name__ == "__main__":
    main()
