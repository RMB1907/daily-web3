# Daily Web3

This project generates and publishes a new Web3 concept every day using AI. It selects a keyword from a master list, explains it simply, and archives it using MkDocs.

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/RMB1907/daily-web3.git
   cd daily-web3
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your `.env`:
   ```
   GROQ_API_KEY=your-groq-api-key
   ```

4. Add keywords to:
   ```
   docs/keywords/all.txt
   ```

## Usage

Run the script:
```bash
python daily_generator.py
```
Deploy to GitHub Pages:
```bash
mkdocs gh-deploy
```
