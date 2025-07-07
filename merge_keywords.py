from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KEYWORDS_DIR = BASE_DIR / "keywords"

def merge_all_keyword_files():
    all_keywords = set()
    for file in KEYWORDS_DIR.glob("**/*.txt"):
        if file.name == "all.txt":
            continue
        lines = file.read_text(encoding="utf-8").strip().splitlines()
        all_keywords.update(line.strip() for line in lines if line.strip())

    merged_path = KEYWORDS_DIR / "all.txt"
    merged_path.write_text("\n".join(sorted(all_keywords)), encoding="utf-8")
    print(f"✅ Merged {len(all_keywords)} keywords into all.txt")

if __name__ == "__main__":
    merge_all_keyword_files()
