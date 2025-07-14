import docx
import re
import os
from uuid import uuid4

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

def extract_images_from_docx(doc, image_dir):
    rels = doc.part.rels
    image_map = {}
    for rel in rels.values():
        if "image" in rel.target_ref:
            image_id = str(uuid4())[:8]
            image_path = os.path.join(image_dir, f"{image_id}.png")
            with open(image_path, "wb") as img_file:
                img_file.write(rel.target_part.blob)
            image_map[rel.rId] = f"/{image_path.replace(os.sep, '/')}"
    return image_map

def find_blip_embeds(element):
    embeds = []
    for child in element.iter():
        if child.tag.endswith('blip'):
            embed = child.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if embed:
                embeds.append(embed)
    return embeds

def table_to_placeholder(table):
    """Convert table to inline placeholder and return table data"""
    table_id = str(uuid4())[:8]
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(cells)
    return f"[TABLE: {table_id}]", table_id, rows

def parse_docx(path):
    doc = docx.Document(path)
    image_dir = f'static/images/{uuid4().hex[:8]}'
    os.makedirs(image_dir, exist_ok=True)
    image_map = extract_images_from_docx(doc, image_dir)
    
    # Store table data with their IDs for inline processing
    table_data = {}

    result = {
        "title": "",
        "abstract": "",
        "keywords": "",
        "sections": [],
        "references": [],
        "table_data": table_data  # Store table data separately
    }

    current_section = None
    current_subsection = None
    in_references = False
    in_abstract = False
    title_found = False
    author_block_ended = False
    author_detected = False

    # Process all elements in document order (paragraphs and tables)
    for element in doc.element.body:
        if element.tag.endswith('p'):  # Paragraph
            para = docx.text.paragraph.Paragraph(element, doc)
            full_text = ""
            for run in para.runs:
                if run.text:
                    full_text += run.text

                # Image extraction from run
                if run._element.xpath(".//pic:pic"):
                    embeds = find_blip_embeds(run._element)
                    for embed in embeds:
                        img_path = image_map.get(embed)
                        if img_path:
                            full_text += f' [IMAGE: {img_path}] '

            text = full_text.strip()
            if not text:
                continue

            # --- Title Detection ---
            if not title_found:
                if para.style.name.lower().startswith("title") or para.style.name.lower().startswith("heading 1"):
                    result["title"] = text
                    title_found = True
                    continue
                elif not re.match(r'(abstract|keywords?|index terms|references?)', text, re.IGNORECASE):
                    result["title"] = text
                    title_found = True
                    continue

            # --- Skip Author Lines ---
            if not author_block_ended:
                if is_author_line(text):
                    author_detected = True
                    continue
                if author_detected:
                    author_block_ended = True
                    continue
                continue

            # --- Abstract ---
            if re.match(r'^abstract\b', text, re.IGNORECASE):
                in_abstract = True
                result["abstract"] = ""
                continue

            if in_abstract:
                if re.match(r'^(keywords?|index terms|references?)\b', text, re.IGNORECASE) or is_possible_heading(text):
                    in_abstract = False
                else:
                    result["abstract"] += text + " "
                    continue

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

            # --- Heading Detection ---
            level = extract_heading_level(text)
            if is_possible_heading(text) and not in_abstract and not in_references:
                if level and '.' in level:
                    if current_subsection:
                        current_section["subsections"].append(current_subsection)
                    current_subsection = {
                        "heading": text,
                        "content": ""
                    }
                else:
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

        elif element.tag.endswith('tbl'):  # Table
            table = docx.table.Table(element, doc)
            table_placeholder, table_id, table_rows = table_to_placeholder(table)
            table_data[table_id] = table_rows
            
            # Add table placeholder to current content
            if current_subsection:
                current_subsection["content"] += table_placeholder + " "
            elif current_section:
                current_section["content"] += table_placeholder + " "

    if current_subsection and current_section:
        current_section["subsections"].append(current_subsection)
    if current_section:
        result["sections"].append(current_section)

    return result
