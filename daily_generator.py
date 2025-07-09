import os
import sys
import hashlib
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Paths
BASE_DIR = Path(__file__).resolve().parent
KEYWORDS_FILE = BASE_DIR / "keywords" / "all.txt"
USED_KEYWORDS_FILE = BASE_DIR / "keywords" / "used.txt"
OUTPUT_FILE = BASE_DIR / "docs" / "index.md"
ARCHIVE_DIR = BASE_DIR / "docs" / "concepts"
INDEX_PATH = ARCHIVE_DIR / "index.md"

def ask_groq(concept_name, context=""):
    prompt = f"""
You are a professional blockchain educator.

Today's keyword is: {concept_name}

Context from my notes:
\"\"\"{context}\"\"\"

Write in the following format:

### 📘 Concept: {concept_name}

#### 🧩 ELI5 Allegory:
Start with a simple real-world analogy or story that makes the concept intuitive for a beginner. Use plain language. Avoid jargon and technical terms. Keep the tone clear and relatable.

#### 📖 Standard Definition:
Provide a clear and concise explanation of the concept using simple language. Do not include code. Do not use bullet points. Do not use parentheses or dashes. Use full sentences. The tone should be beginner-friendly and professional.

End with:
**Keywords**: list the main keywords related to the concept, separated by commas

Return only this formatted explanation. Do not include anything else.
"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 800
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"❌ Groq API Error {response.status_code}")
        print(response.text)
        response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def format_output(title, content):
    return f"# {title}\n\n{content}"

def update_concepts_index(title, filename):
    if INDEX_PATH.exists():
        lines = INDEX_PATH.read_text(encoding="utf-8").strip().splitlines()
    else:
        lines = ["# Concept Archive", ""]
    entry = f"- [{title}]({filename})"
    if entry not in lines:
        lines.insert(1, entry)
        INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
        print(f"🗂️  Added to archive index: {title}")

def load_keywords(path):
    if path.exists():
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return []

def main():
    # Load all keywords
    keywords = load_keywords(KEYWORDS_FILE)

    # If empty, recycle used.txt
    if not keywords:
        used = load_keywords(USED_KEYWORDS_FILE)
        if not used:
            print("🎉 All keywords completed. Nothing left to restore.")
            OUTPUT_FILE.write_text("# 🎉 All Topics Covered!\n\nYou've reached the end of the archive.", encoding="utf-8")
            return
        random.shuffle(used)
        KEYWORDS_FILE.write_text("\n".join(used), encoding="utf-8")
        USED_KEYWORDS_FILE.write_text("", encoding="utf-8")
        keywords = used
        print(f"♻️ Recycled {len(keywords)} keywords from used.txt")

    print(f"🧠 Remaining keywords: {len(keywords)}")

    # Randomly pick one keyword
    today = datetime.now().strftime("%Y-%m-%d")
    index = int(hashlib.sha256(today.encode()).hexdigest(), 16) % len(keywords)
    keyword = keywords[index].strip().title()

    print(f"📌 Generating explanation for: {keyword}")
    explanation = ask_groq(keyword)

    # Write to homepage
    OUTPUT_FILE.write_text(f"# Concept of the Day: **{keyword}**\n\n{explanation}", encoding="utf-8")

    # Archive
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    archive_filename = f"{timestamp}.md"
    archive_path = ARCHIVE_DIR / archive_filename
    archive_path.write_text(format_output(keyword, explanation), encoding="utf-8")

    # Index
    update_concepts_index(keyword, archive_filename)

    # Remove used word and log it
    del keywords[index]
    KEYWORDS_FILE.write_text("\n".join(keywords), encoding="utf-8")
    with USED_KEYWORDS_FILE.open("a", encoding="utf-8") as f:
        f.write(keyword + "\n")

    print(f"✅ Saved concept: {keyword}")

if __name__ == "__main__":
    main()
