def suggest_titles(doc_data):
    intro_text = ""
    if doc_data.get("sections"):
        intro_text = doc_data["sections"][0]["content"][:1000]

    # Replace this with a call to LLM (via llama.cpp / Ollama)
    # Example: prompt the LLM to suggest 3 IEEE-style titles
    dummy_prompt = f"Based on this intro, suggest 3 IEEE-style titles:\n{intro_text}"
    
    # Placeholder response
    return [
        # "A Novel Approach to IEEE Document Formatting",
        # "Offline AI-Powered Tool for Academic Paper Structuring",
        # "Enhancing Scientific Manuscripts with Local LLMs"
    ]
