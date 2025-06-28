import subprocess
import re

def suggest_titles(doc_data):
    # Step 1: Get intro text (first section content)
    intro_text = doc_data.get("sections", [{}])[0].get("content", "")[:1000].strip()

    if not intro_text:
        return ["No introduction found to suggest titles."]

    # Step 2: Create prompt
    prompt = f"""
Suggest 4 IEEE-style research paper titles based on the introduction below.
Please return them clearly as a bullet list or numbered list.

Introduction:
{intro_text}
"""

    try:
        # Step 3: Run Ollama with a local model (replace with what works)
        result = subprocess.run(
            ["ollama", "run", "phi3:mini"],  # ← change model name if needed
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60
        )
        output = result.stdout.strip()

        # Step 4: Extract titles from output using regex (handles bullet or numbered)
        titles = re.findall(r"[-•\d.]*\s*(.+)", output)
        clean_titles = [title.strip() for title in titles if len(title.strip()) > 15]

        # Return exactly 4 titles, pad if needed
        while len(clean_titles) < 4:
            clean_titles.append(f"Generated Title {len(clean_titles)+1}")

        return clean_titles[:4]

    except Exception as e:
        print("Error running Ollama:", e)
        return [
            "Fallback Title 1",
            "Fallback Title 2",
            "Fallback Title 3",
            "Fallback Title 4"
        ]
