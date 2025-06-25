import docx
import fitz  # PyMuPDF
import zipfile
import os
import re
import subprocess
from pathlib import Path
from collections import OrderedDict





COMMON_SECTIONS = {
    "introduction", "related work", "literature review", "methodology",
    "methods", "results", "discussion", "experiments", "evaluation",
    "conclusion", "future work", "acknowledgment", "acknowledgement"
}

def is_possible_section_heading(text):
    text = text.strip()
    if not text or len(text.split()) > 10:
        return False
    if text.lower() in COMMON_SECTIONS:
        return True
    return bool(re.match(r'^[A-Z][A-Za-z\s\-:]{1,80}$', text))


def parse_pdf(file_path):
    doc = fitz.open(file_path)
    raw_text = "\n".join([page.get_text("text") for page in doc])

    # Normalize and split into lines
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
    in_abstract = False
    in_references = False
    title_found = False
    abstract_collected = []

    for idx, line in enumerate(lines):
        lower = line.lower()

        # Skip author/email lines as section
        if re.search(r'\b(?:[A-Z][a-z]+\s){1,3}[A-Z][a-z]+', line) and '@' in line:
            continue

        # --- Title ---
        if not title_found and not re.match(r'(abstract|keywords?|index terms|references?)', lower):
            result["title"] = line
            title_found = True
            continue

        # --- Abstract ---
        if re.match(r'^abstract\b[:\-]?\s*$', lower):
            in_abstract = True
            continue
        if in_abstract:
            if re.match(r'^(keywords?|index terms|references?)\b', lower) or is_possible_section_heading(line):
                in_abstract = False
                result["abstract"] = " ".join(abstract_collected).strip()
                abstract_collected = []
            else:
                abstract_collected.append(line)
                continue

        # --- Keywords ---
        if re.match(r'^(keywords|index terms)\b[:\-]?', lower):
            result["keywords"] = re.sub(r'^(keywords|index terms)[:\-]?', '', line, flags=re.I).strip()
            continue

        # --- References ---
        if re.match(r'^references\b', lower):
            in_references = True
            if current_section:
                result["sections"].append(current_section)
                current_section = None
            continue
        if in_references:
            result["references"].append(line)
            continue

        # --- Section Headings ---
        if is_possible_section_heading(line):
            if current_section:
                result["sections"].append(current_section)
            current_section = {"heading": line, "content": ""}
        elif current_section:
            current_section["content"] += line + " "

    # Final flush
    if abstract_collected:
        result["abstract"] = " ".join(abstract_collected).strip()
    if current_section:
        result["sections"].append(current_section)

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