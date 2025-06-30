import fitz  # PyMuPDF
import re

COMMON_SECTIONS = {
    "introduction", "related work", "literature review", "methodology",
    "methods", "results", "discussion", "experiments", "evaluation",
    "conclusion", "future work", "acknowledgment", "acknowledgement"
}

EMAIL_REGEX = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b')
AFFILIATION_KEYWORDS = [
    "university", "institute", "department", "college", "school",
    "research", "tcs", "technologies", "engineering"
]

def is_possible_section_heading(text):
    text = text.strip()
    if not text or len(text.split()) > 15:
        return False
    if text.lower() in COMMON_SECTIONS:
        return True
    return bool(re.match(r'^([IVXLC]+\.|\d+[\.\)])?\s*[A-Z][A-Za-z0-9\s\-:,]{1,80}$', text))

def is_affiliation_line(text):
    text = text.lower()
    return any(kw in text for kw in AFFILIATION_KEYWORDS) or EMAIL_REGEX.search(text)

def parse_pdf(file_path):
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print("PDF open failed:", e)
        return {"error": "Could not open PDF"}

    raw_text = "\n".join([page.get_text("text") for page in doc])
    raw_text = re.sub(r'\s+\n', '\n', raw_text)
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    result = {
        "title": "",
        "abstract": "",
        "keywords": "",
        "sections": [],
        "references": []
    }

    current_section = None
    in_references = False
    title_found = False
    author_detected = False
    author_block_skipped = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        lower = line.lower()

        # Skip author lines (affiliations/emails)
        if not author_block_skipped:
            if is_affiliation_line(line):
                author_detected = True
                i += 1
                continue
            if author_detected:
                author_block_skipped = True
                i += 1
                continue
            i += 1
            continue

        # --- Title ---
        if not title_found:
            result["title"] = line
            title_found = True
            i += 1
            continue

        # --- Abstract ---
        if re.match(r'^abstract\b', lower):
            abstract = []

            inline_match = re.match(r'^abstract\b[:\-\—]?\s*(.+)', line, flags=re.I)
            if inline_match:
                abstract.append(inline_match.group(1).strip())

            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                lower_next = next_line.lower()

                if re.match(r'^(keywords?|index terms|references?)\b', lower_next) or is_affiliation_line(next_line):
                    break
                abstract.append(next_line)
                i += 1

            result["abstract"] = " ".join(abstract).strip()
            continue

        # --- Keywords ---
        if re.match(r'^(keywords|index terms)\b[:\-\—]?', lower):
            keyword_line = re.sub(r'^(keywords|index terms)[:\-\—]?', '', line, flags=re.I).strip()
            keyword_parts = [keyword_line]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if is_possible_section_heading(next_line) or next_line.lower().startswith("introduction"):
                    break
                keyword_parts.append(next_line)
                i += 1
            result["keywords"] = " ".join(keyword_parts).strip()
            continue

        # --- References ---
        if re.match(r'^references\b', lower):
            in_references = True
            if current_section:
                result["sections"].append(current_section)
                current_section = None
            i += 1
            continue

        if in_references:
            result["references"].append(line)
            i += 1
            continue

        # --- Section Heading ---
        if is_possible_section_heading(line):
            if current_section:
                result["sections"].append(current_section)
            current_section = {
                "heading": line,
                "content": "",
                "subsections": []
            }
        elif current_section:
            current_section["content"] += line + " "

        i += 1

    # Finalize last section
    if current_section:
        result["sections"].append(current_section)

    # Safety fallback
    if not result["title"] and not result["abstract"] and not result["sections"]:
        return {"error": "Unable to parse PDF content"}

    return result


    



#def parse_pdf(file_path):
#     doc = fitz.open(file_path)

#     # Step 1: Clean and normalize text
#     full_text = "\n".join([page.get_text("text") for page in doc])
#     text = re.sub(r'\s+\n', '\n', full_text)          # clean space before newline
#     text = re.sub(r'\n{2,}', '\n\n', text).strip()    # normalize paragraph breaks

#     result = {
#         "title": "",
#         "abstract": "",
#         "keywords": "",
#         "sections": [],
#         "references": []
#     }

#     # Step 2: Split into lines and basic title
#     lines = [line.strip() for line in text.splitlines() if line.strip()]
#     if lines:
#         result["title"] = lines[0]

#     # Step 3: Extract Abstract
#     abstract_match = re.search(
#         r'\babstract\b[:\s\-–]*([\s\S]*?)(?=\n{2,}|\bkeywords\b|\bindex terms\b|\breferences\b|\b1[\.\s])',
#         text, re.IGNORECASE
#     )
#     if abstract_match:
#         result["abstract"] = re.sub(r'\n+', ' ', abstract_match.group(1)).strip()

#     # Step 4: Extract Keywords
#     keyword_match = re.search(r'\b(keywords|index terms)\b[:\s\-–]*([^\n]+)', text, re.IGNORECASE)
#     if keyword_match:
#         result["keywords"] = keyword_match.group(2).strip()

#     # Step 5: Extract References
#     ref_match = re.search(r'\breferences\b', text, re.IGNORECASE)
#     if ref_match:
#         content_text = text[:ref_match.start()]
#         ref_text = text[ref_match.end():]
#         # Matches: [1] something, 1. something, 1) something
#         result["references"] = re.findall(
#             r'(?:\[\d+\]|\n\d{1,2}[.)])\s+(.*?)(?=(?:\[\d+\]|\n\d{1,2}[.)])|\Z)',
#             ref_text, re.DOTALL
#         )
#     else:
#         content_text = text

#     # Step 6: Detect Sections
#     section_lines = content_text.splitlines()
#     sections = []
#     section_indices = []

#     for i, line in enumerate(section_lines):
#         clean_line = line.strip()
#         if not clean_line:
#             continue
#         # If looks like: "1. Introduction" OR "Conclusion" OR "Related Work" etc.
#         if (
#             re.match(r'^(\d+\s*[\.\)]|[IVXLC]+\.)?\s*[A-Z][^\n]{1,80}$', clean_line)
#             and len(clean_line.split()) <= 10
#         ):
#             section_indices.append((i, clean_line))

#     for idx, (line_num, heading) in enumerate(section_indices):
#         start = line_num + 1
#         end = section_indices[idx + 1][0] if idx + 1 < len(section_indices) else len(section_lines)
#         content_lines = section_lines[start:end]
#         body = " ".join(l.strip() for l in content_lines if l.strip())
#         sections.append({
#             "heading": heading,
#             "content": body,
#             "subsections": []  # can be filled later if needed
#         })

#     result["sections"] = sections
#     return result