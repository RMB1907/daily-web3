import openai
import os
from pathlib import Path
from datetime import date
import hashlib
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Paths
KEYWORDS_DIR = Path("keywords")
OUTPUT_FILE = Path("docs/index.md")
ARCHIVE_DIR = Path("docs/concepts")
INDEX_PATH = ARCHIVE_DIR / "index.md"

# Get all keyword text files
def get_all_keyword_files():
    return list(KEYWORDS_DIR.glob("**/*.txt"))

# Choose one deterministically based on today's date
def pick_today_file(files):
    today = date.today().isoformat()
    index = int(hashlib.sha256(today.encode()).hexdigest(), 16) % len(files)
    return files[index]

# Ask GPT for the explanation
def ask_openai(concept_name, context):
    prompt = f"""You are a professional blockchain educator.

Today's keyword is: {concept_name}

Context from my notes:
\"\"\"
{context}
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

    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return res["choices"][0]["message"]["content"]

# Format file content
def format_output(title, content):
    return f"# {title}\n\n{content}"

# Add today's topic to concepts/index.md
def update_concepts_index(title, filename):
    if INDEX_PATH.exists():
        lines = INDEX_PATH.read_text(encoding="utf-8").strip().splitlines()
    else:
        lines = ["# Concept Archive", ""]

    entry = f"- [{title}]({filename})"
    if entry not in lines:
        lines.insert(2, entry)  # insert after title
        INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")
        print(f"Added to archive index: {title}")

# Main logic
def main():
    files = get_all_keyword_files()
    chosen_file = pick_today_file(files)

    concept_name = chosen_file.stem.replace("_", " ").title()
    context = chosen_file.read_text(encoding="utf-8").strip()

    explanation = ask_openai(concept_name, context)

    # Write to homepage
    OUTPUT_FILE.write_text(f"# Concept of the Day: **{concept_name}**\n\n{explanation}", encoding="utf-8")

    # Archive to concepts/YYYY-MM-DD.md
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_filename = f"{date.today().isoformat()}.md"
    archive_path = ARCHIVE_DIR / archive_filename
    archive_path.write_text(format_output(concept_name, explanation), encoding="utf-8")

    # Update concepts/index.md
    update_concepts_index(concept_name, archive_filename)

    print(f"Saved concept: {concept_name}")

if __name__ == "__main__":
    main()
