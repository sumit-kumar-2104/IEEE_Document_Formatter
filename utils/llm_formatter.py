# utils/llm_formatter.py

import subprocess
import json

def generate_ieee_markdown(parsed_data, model="llama3", temperature=0.3):
    """
    Uses Ollama to generate IEEE-formatted Markdown text from parsed document JSON.
    """
    system_prompt = (
        "You are an expert in academic formatting. Reformat the given academic paper into IEEE format.\n\n"
        "Requirements:\n"
        "- Use IEEE structure: Title, Abstract, Keywords, numbered sections (1. Introduction, 2. Methodology, etc.).\n"
        "- Keep original meaning, don't invent content.\n"
        "- Format in clean, well-structured Markdown for readability and easy LaTeX/DOCX conversion.\n"
        "- Use proper IEEE-style tone.\n"
    )

    # Create input prompt for the LLM
    user_prompt = f"{system_prompt}\n\nParsed Data:\n{json.dumps(parsed_data, indent=2)}"

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=user_prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )
        if result.returncode != 0:
            return {"error": result.stderr.decode("utf-8")}

        return {
            "formatted_markdown": result.stdout.decode("utf-8").strip()
        }

    except subprocess.TimeoutExpired:
        return {"error": "Ollama model timed out. Try reducing input size or switching model."}
    except Exception as e:
        return {"error": str(e)}
