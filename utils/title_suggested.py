import subprocess
import re

def suggest_titles(doc_data):
    # Step 1: Extract intro or fallback to abstract/first section
    intro_text = ""
    sections = doc_data.get("sections", [])
    if sections:
        intro_text = sections[0].get("content", "")[:1500].strip()
    if not intro_text:
        intro_text = doc_data.get("abstract", "")[:1500].strip()
    if not intro_text:
        return ["No sufficient content found to suggest titles."]

    # Step 2: Create structured prompt
    prompt = f"""You are a research assistant. Based on the content below, generate 4 IEEE-style academic paper titles. Each title must be clear, concise (max 15 words), and on a new line.

--- Content ---
{intro_text}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "phi3:mini"],  # Use your model name here
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60
        )
        output = result.stdout.strip()

        # Step 3: Post-process: remove bullets/numbers and trim
        lines = [re.sub(r"^[•\-–\d.]+", "", line).strip() for line in output.splitlines() if line.strip()]
        titles = [line for line in lines if 10 < len(line) < 150]

        # Step 4: Pad or trim to 4 titles
        while len(titles) < 4:
            titles.append(f"Generated Title {len(titles)+1}")
        return titles[:4]

    except Exception as e:
        print("Error running Ollama:", e)
        return [f"Fallback Title {i}" for i in range(1, 5)]
