import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Base paths
BASE_DIR = Path(__file__).resolve().parent
KEYWORDS_FILE = BASE_DIR / "keywords" / "all.txt"
OUTPUT_FILE = BASE_DIR / "docs" / "index.md"
ARCHIVE_DIR = BASE_DIR / "docs" / "concepts"
INDEX_PATH = ARCHIVE_DIR / "index.md"

# Load all keywords
def load_keywords():
    if not KEYWORDS_FILE.exists():
        print("❌ keywords/all.txt not found.")
        sys.exit(0)
    lines = KEYWORDS_FILE.read_text(encoding="utf-8").strip().splitlines()
    return [line.strip() for line in lines if line.strip()]

# Pick keyword and remove it from the list
def pick_keyword_and_remove(keywords):
    if not keywords:
        print("🎉 All keywords used.")
        sys.exit(0)

    now = datetime.now()
    rounded_minute = now.minute - (now.minute % 5)
    time_key = now.strftime(f"%Y-%m-%d-%H-{rounded_minute:02d}")

    index = int(hashlib.sha256(time_key.encode()).hexdigest(), 16) % len(keywords)
    concept = keywords[index]

    # Remove the used keyword
    del keywords[index]
    KEYWORDS_FILE.write_text("\n".join(keywords), encoding="utf-8")

    return concept

# Ask Groq (Mixtral) for the explanation
def ask_groq(concept_name):
    prompt = f"""
You are a professional blockchain educator.

Today's keyword is: {concept_name}

Context from my notes:
\"\"\"
{concept_name}
\"\"\"

Write in the following format:

### 📘 Concept: {concept_name}

#### 🧩 ELI5 Allegory:
Start with a simple real-world analogy or story that makes the concept intuitive for a beginner. Use plain language. Avoid jargon and technical terms. Keep the tone clear and relatable.

#### 📖 Standard Definition:
Provide a clear and concise explanation of the concept using simple language. Do not include code. Do not use bullet points. Do not use parentheses. Do not use hyphens or dashes of any kind. Use full sentences. The tone should be beginner-friendly and professional.

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
    response = requests.post(url, headers=headers, json=data)

    # Log detailed error if not OK
    if response.status_code != 200:
        print("❌ Groq API Error:")
        print("Status:", response.status_code)
        print("Details:", response.text)  # This will explain *why* Groq rejected it

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Archive format
def format_output(title, content):
    return f"# {title}\n\n{content}"

# Update concepts index
def update_concepts_index(title, filename):
    if INDEX_PATH.exists():
        lines = INDEX_PATH.read_text(encoding="utf-8").strip().splitlines()
    else:
        lines = ["# Concept Archive", ""]

    entry = f"- [{title}]({filename})"
    if entry not in lines:
        lines.insert(2, entry)
        INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
        print(f"🗂️  Added to archive index: {title}")

# Main
def main():
    keywords = load_keywords()
    print(f"🧠 Remaining keywords: {len(keywords)}")

    concept_name = pick_keyword_and_remove(keywords)
    print(f"📌 Generating explanation for: {concept_name}")

    explanation = ask_groq(concept_name)

    # Write to homepage
    OUTPUT_FILE.write_text(f"# Concept of the Day: **{concept_name}**\n\n{explanation}", encoding="utf-8")

    # Archive
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    archive_filename = f"{timestamp}.md"
    archive_path = ARCHIVE_DIR / archive_filename
    archive_path.write_text(format_output(concept_name, explanation), encoding="utf-8")

    # Update index
    update_concepts_index(concept_name, archive_filename)

    print(f"✅ Saved concept: {concept_name}")

if __name__ == "__main__":
    main()
