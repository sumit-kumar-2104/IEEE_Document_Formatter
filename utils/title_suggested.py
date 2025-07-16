import subprocess
import re

def suggest_titles(doc_data):
    # Extract content for suggestions
    intro_text = ""
    sections = doc_data.get("sections", [])
    if sections:
        intro_text = sections[0].get("content", "")[:1500].strip()
    if not intro_text:
        intro_text = doc_data.get("abstract", "")[:1500].strip()
    
    original_title = doc_data.get("title", "").strip()
    original_abstract = doc_data.get("abstract", "").strip()
    
    # Generate suggested titles
    suggested_titles = []
    if intro_text:
        try:
            prompt = f"""You are a research assistant. Based on the content below, generate 3 IEEE-style academic paper titles. Each title must be clear, concise (max 15 words), and on a new line.

--- Content ---
{intro_text}
"""
            
            result = subprocess.run(
                ["ollama", "run", "phi3:mini"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=180
            )
            output = result.stdout.strip()
            
            # Post-process: remove bullets/numbers and trim
            lines = [re.sub(r"^[•\-–\d.]+", "", line).strip() for line in output.splitlines() if line.strip()]
            suggested_titles = [line for line in lines if 10 < len(line) < 150][:3]
            
        except Exception as e:
            print("Error running Ollama:", e)
            suggested_titles = []
    
    # Pad suggested titles if needed
    while len(suggested_titles) < 3:
        suggested_titles.append(f"AI-Generated Title {len(suggested_titles)+1}")
    
    # Generate suggested abstracts
    suggested_abstracts = []
    if intro_text:
        try:
            prompt = f"""You are a research assistant. Based on the content below, generate 3 concise academic abstracts (each 50-100 words). Each abstract should be on a new line and start with a clear topic sentence.

--- Content ---
{intro_text}
"""
            
            result = subprocess.run(
                ["ollama", "run", "phi3:mini"],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=180
            )
            output = result.stdout.strip()
            
            # Split by double newlines or numbered items
            abstracts = re.split(r'\n\n+|\n(?=\d\.)', output)
            suggested_abstracts = [re.sub(r"^[•\-–\d.]+", "", abs.strip()).strip() for abs in abstracts if abs.strip()][:3]
            
        except Exception as e:
            print("Error running Ollama:", e)
            suggested_abstracts = []
    
    # Pad suggested abstracts if needed
    while len(suggested_abstracts) < 3:
        suggested_abstracts.append(f"AI-generated abstract {len(suggested_abstracts)+1} based on the document content.")
    
    return {
        "original_title": original_title,
        "original_abstract": original_abstract,
        "suggested_titles": suggested_titles,
        "suggested_abstracts": suggested_abstracts
    }
