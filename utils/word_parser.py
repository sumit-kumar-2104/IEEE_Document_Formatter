import docx
import re

COMMON_SECTIONS = [
    "introduction", "literature review", "related work", "methodology",
    "methods", "results", "discussion", "experiments", "evaluation",
    "conclusion", "future work", "acknowledgment", "acknowledgement"
]
KEYWORD_HEADERS = ["keywords", "index terms"]
REFERENCE_HEADERS = ["references"]

def is_author_line(text):
    return bool(re.search(r'@\w+\.\w+', text)) or 'tcs' in text.lower() or 'university' in text.lower()

def is_possible_heading(text):
    text = text.strip()
    if not text or len(text.split()) > 15:
        return False
    if text.lower() in COMMON_SECTIONS:
        return True
    if re.match(r'^\d+(\.\d+)*[\.\)]?\s+[A-Z]', text):
        return True
    if re.match(r'^[A-Z][A-Za-z\s\-]{3,}$', text) and len(text.split()) <= 6:
        return True
    return False

def extract_heading_level(text):
    match = re.match(r'^(\d+(\.\d+)*)(\.|\))?\s+', text)
    return match.group(1) if match else None

def parse_docx(path):
    doc = docx.Document(path)

    result = {
        "title": "",
        "abstract": "",
        "keywords": "",
        "sections": [],
        "references": []
    }

    current_section = None
    current_subsection = None
    in_references = False
    in_abstract = False
    title_found = False
    abstract_started = False
    author_block_ended = False
    author_detected = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # --- Title ---
        if not title_found:
            if para.style.name.lower().startswith("title"):
                result["title"] = text
                title_found = True
                continue
            elif not re.match(r'(abstract|keywords?|index terms|references?)', text, re.IGNORECASE):
                result["title"] = text
                title_found = True
                continue

        # --- Skip Author Block ---
        if not author_block_ended:
            if is_author_line(text):
                author_detected = True
                continue
            if author_detected:
                author_block_ended = True
                continue
            continue

        # --- Abstract Detection ---
        if re.match(r'^abstract\b', text, re.IGNORECASE):
            in_abstract = True
            result["abstract"] = ""
            continue

        if in_abstract:
            if re.match(r'^(keywords?|index terms|references?)\b', text, re.IGNORECASE) or is_possible_heading(text) or is_author_line(text):
                in_abstract = False
            else:
                result["abstract"] += text + " "
                continue  # remain inside abstract block


        # --- Keywords ---
        if any(text.lower().startswith(k) for k in KEYWORD_HEADERS):
            parts = re.split(r'[:\-]', text, 1)
            result["keywords"] = parts[1].strip() if len(parts) > 1 else text
            continue

        # --- References ---
        if any(text.lower().startswith(r) for r in REFERENCE_HEADERS):
            in_references = True
            if current_subsection and current_section:
                current_section["subsections"].append(current_subsection)
                current_subsection = None
            if current_section:
                result["sections"].append(current_section)
                current_section = None
            continue

        if in_references:
            result["references"].append(text)
            continue

        # --- Skip leftover author lines ---
        if is_author_line(text):
            continue

        # --- Sections / Subsections ---
        level = extract_heading_level(text)
        if is_possible_heading(text) and not in_abstract and not in_references:
            if level and '.' in level:
                # Subsection
                if current_subsection:
                    current_section["subsections"].append(current_subsection)
                current_subsection = {
                    "heading": text,
                    "content": ""
                }
            else:
                # New Section
                if current_subsection and current_section:
                    current_section["subsections"].append(current_subsection)
                    current_subsection = None
                if current_section:
                    result["sections"].append(current_section)
                current_section = {
                    "heading": text,
                    "content": "",
                    "subsections": []
                }
            continue

        # --- Content Appending ---
        if current_subsection:
            current_subsection["content"] += text + " "
        elif current_section:
            current_section["content"] += text + " "

    # --- Finalize Remaining ---
    if current_subsection and current_section:
        current_section["subsections"].append(current_subsection)
    if current_section:
        result["sections"].append(current_section)

    return result
